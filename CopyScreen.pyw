# -*- coding: utf-8 -*-
import wx
#import _winreg


# showBmp和Bmp 应该是何种联系？



class MainFrame(wx.Frame):
    def __init__(self):
       # arr = Reg.Get() or (10, 10, 800, 500)
        wx.Frame.__init__(self, None, wx.NewId(), u"截图")

        # 图片列表，在imgs文件中,svg格式图片
        
        self.copyFrame = None
        self.Bmp = None
        self.ShowBmp = None
        self.IsSaved = False

        
        self.SetMinSize(wx.Size(800, 500))
        #self.SetIcon(self.ImgList[0])
        #self._CreateToolBar()
        self.paintPanel = PaintPanel(self)
        #self.CreateStatusBar()


        #self.Bind(wx.EVT_CLOSE, self.On_Close)

   

 
        if self.ShowBmp and not self.IsSaved:
            re = wx.MessageBox(u'截图还未复制或保存，确定要继续吗？', u'信息', wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
            if re == wx.CANCEL:
                return
        self.Hide()
        self.IsSaved = False
        self.ShowBmp = None
        self.Bmp = self.Get_Screen_Bmp()
        self.copyFrame = CopyFrame(self)
        self.copyFrame.Show()

    # 复制图片
    # 对self.ShowBmp 进行处理
    
    def On_ToolButton_Copy_Click(self, event):
        if not self.ShowBmp:
            wx.MessageBox(u'请先点击截图按钮开始截图！', u'信息', wx.OK | wx.ICON_INFORMATION)
            return
        cb = wx.Clipboard()
        if cb.Open():
            cb.SetData(wx.BitmapDataObject(self.ShowBmp))
            cb.Flush()
            cb.Close()
            self.IsSaved = True
            wx.MessageBox(u'已将图片复制到剪贴板！', u'信息', wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox(u'剪贴板访问错误！', u'信息', wx.OK | wx.ICON_INFORMATION)

    # 保存图片
    # self.ShowBmp
    def On_ToolButton_Save_Click(self, event):
        if not self.ShowBmp:
            wx.MessageBox(u'请先点击截图按钮开始截图！', u'信息', wx.OK | wx.ICON_INFORMATION)
            return
        dlg = wx.FileDialog(self, u'保存', style=wx.SAVE | wx.OVERWRITE_PROMPT, wildcard=u'位图文件(*.bmp)|*.bmp')
        rel = dlg.ShowModal()
        if rel == wx.ID_OK:
            self.ShowBmp.SaveFile(dlg.GetPath(), wx.BITMAP_TYPE_BMP)
            self.IsSaved = True

    # 清除图片
    # 将self.ShowBmp赋值为None,   再更新面板
    def On_ToolButton_Clear_Click(self, event):
        if not self.ShowBmp:
            wx.MessageBox(u'请先点击截图按钮开始截图！', u'信息', wx.OK | wx.ICON_INFORMATION)
            return
        if not self.IsSaved:
            re = wx.MessageBox(u'截图还未复制或保存，确定要清除吗？', u'信息', wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
            if re == wx.CANCEL:
                return
        self.ShowBmp = None
        self.paintPanel.RefreshRect(self.paintPanel.GetClientRect(), True)
        self.paintPanel.Update()
        self.paintPanel.SetScrollbars(1, 1, 0, 0)

    # 关于 ，软件生产信息
    def On_ToolButton_About_Click(self, event):
        info = wx.AboutDialogInfo()
        info.Name = u'CopyScreen'
        info.Version = u'1.0.0'
        info.Copyright = u'(C) 2013 Programmers and Coders Everywhere'
        info.Description = u'警告：\n      本程序未经制作人授权不得擅自复制和传播，\n否则将到道德的谴责，情节重者将受到法律的制裁。'
        info.WebSite = (u'http://www.baidu.com', u'百度一下！')
        info.Developers = [u'醉仙灵芙', ]
        wx.AboutBox(info)

    # 得到屏幕截图
    def Get_Screen_Bmp(self):
        s = wx.GetDisplaySize()
        bmp = wx.EmptyBitmap(s.x, s.y)
        dc = wx.ScreenDC()
        memdc = wx.MemoryDC()
        memdc.SelectObject(bmp)
        memdc.Blit(0,0, s.x, s.y, dc, 0,0)
        memdc.SelectObject(wx.NullBitmap)
        return bmp

# 画板    
class PaintPanel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, wx.NewId(), style= wx.FULL_REPAINT_ON_RESIZE | wx.SUNKEN_BORDER)
        self.parent = parent
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.On_Paint)

    # 生产矩形，选取框
    def On_Paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(255,255,255)))
        dc.Clear()
        if not self.parent.ShowBmp: return
        self.DoPrepareDC(dc)
        cS = self.GetClientSize()
        iS = self.parent.ShowBmp.GetSize().Get()
        x = (0 if cS[0] <= iS[0] else (cS[0] - iS[0]) / 2) + 5
        y = (0 if cS[1] <= iS[1] else (cS[1] - iS[1]) / 2) + 5
        dc.DrawBitmap(self.parent.ShowBmp, x, y)
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0), wx.TRANSPARENT))
        dc.DrawRectangle(x, y, iS[0], iS[1])

# 截屏
class CopyFrame(wx.Frame):
    def __init__(self, mainFrame):
        wx.Frame.__init__(self, mainFrame, wx.NewId(), pos=(0, 0), size=wx.GetDisplaySize(), style=wx.NO_BORDER | wx.STAY_ON_TOP)
        self.mainFrame = mainFrame
        self.firstP = wx.Point(0, 0)    #记录截图相对的第一个点
        self.lastP = wx.Point(0, 0)     #记录截图相对的最后一个点
        self.MouseP = wx.Point(0, 0)    #就鼠标的当前位置
        self.TempP = wx.Point(0, 0)     #
        self.MoveP = wx.Point(0, 0)     #当拖动矩形选框时临时记录鼠标的位置用于矩形框的拖动
        self.IsStartCopy = False        #记录是否一开始截图
        self.IsInRectLT = True          #鼠标是否在左上角的小矩形中
        self.IsInRectTR = True          #鼠标是否在右上角的小矩形中
        self.IsInRectRB = True          #鼠标是否在右下角的小矩形中
        self.IsInRectBL = True          #鼠标是否在左下角的小矩形中
        self.IsInRectT = False
        self.IsInRectR = False
        self.IsInRectB = False
        self.IsInRectL = False
        self.IsInRectCopy = False       #鼠标是否在矩形选框中

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.On_Paint)
        self.Bind(wx.EVT_RIGHT_DOWN, self.On_Mouse_RightDown)
        self.Bind(wx.EVT_LEFT_DOWN, self.On_Mouse_LeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.On_Mouse_LeftUp)
        self.Bind(wx.EVT_MOTION, self.On_Mouse_Move)
        self.Bind(wx.EVT_LEFT_DCLICK, self.On_Mouse_LeftDblClick)

    def On_Paint(self, event):
        dc = wx.GCDC(wx.BufferedPaintDC(self))
        self.Paint_CopyRect(dc)
        
    def Paint_CopyRect(self, dc):
        rect = self.GetClientRect()
        co = wx.Colour(0, 0, 0, 120)
        w, h = rect.width, rect.height
        minx, miny = min(self.firstP.x, self.lastP.x), min(self.firstP.y, self.lastP.y)
        maxx, maxy = max(self.firstP.x, self.lastP.x), max(self.firstP.y, self.lastP.y)

        #画出整个桌面的截图
        dc.DrawBitmap(self.mainFrame.Bmp, 0, 0)
        
        #画阴影部分，不需要截图的部分
        dc.SetPen(wx.Pen(co))
        dc.SetBrush(wx.Brush(co))
        dc.DrawRectangleList([
            (0, 0, maxx, miny),
            (maxx, 0, w - minx, maxy),
            (minx, maxy, w - minx, h - maxy),
            (0, miny, minx, h - miny)
        ])

        #画出需要截图的选择框
        dc.SetPen(wx.Pen(wx.Colour(255, 0, 0)))
        dc.SetBrush(wx.Brush(co, wx.TRANSPARENT))
        dc.DrawRectangle(minx, miny, maxx - minx, maxy - miny)

        #画出小矩形
        if self.IsStartCopy:
            dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))
            dc.DrawRectangleList([
                (minx - 2, miny - 2, 5, 5),
                (maxx / 2 + minx / 2 - 2, miny - 2, 5, 5),
                (maxx - 2, miny - 2, 5, 5),
                (maxx - 2, maxy / 2 + miny / 2 - 2, 5, 5),
                (maxx - 2, maxy - 2, 5, 5),
                (maxx / 2 + minx / 2 - 2, maxy - 2, 5, 5),
                (minx - 2, maxy - 2, 5, 5),
                (minx - 2, maxy / 2 + miny / 2 - 2, 5, 5)
            ])

        #画出截图的一些信息
        if self.IsStartCopy:
            co = wx.Colour(0, 0, 0, 180)
            dc.SetPen(wx.Pen(co))
            dc.SetBrush(wx.Brush(co, wx.SOLID))
            iw, ih = 140, 43
            currCo = dc.GetPixel(self.MouseP.x, self.MouseP.y).Get()
            s = u'区域大小：' + str(maxx - minx) + '*' + str(maxy - miny)
            s += u'\n鼠标位置：(' + str(self.MouseP.x) + ',' + str(self.MouseP.y) + ')'

            dc.DrawRectangle(
                minx,
                miny - ih - 5 if miny - 5 > ih else miny + 5,
                iw,
                ih
            )

            dc.SetTextForeground(wx.Colour(255, 255, 255))
            dc.DrawText(s, minx + 5, (miny - ih - 5 if miny - 5 > ih else miny + 5) + 5)
        
    def On_Mouse_RightDown(self, event):
        if self.IsStartCopy:
            self.firstP = wx.Point(0, 0)
            self.lastP = wx.Point(0, 0)
            self.MouseP = wx.Point(0, 0)
            self.TempP = wx.Point(0, 0)
            self.IsStartCopy = False
            self.IsInRectLT = True
            self.IsInRectTR = True
            self.IsInRectRB = True
            self.IsInRectBL = True
            self.IsInRectT = False
            self.IsInRectR = False
            self.IsInRectB = False
            self.IsInRectL = False
            self.NewUpdate()
        else:
            self.mainFrame.Show()
            self.Close()

    def On_Mouse_LeftDown(self, event):
        if not self.IsStartCopy:
            self.firstP = event.GetPosition()
            self.lastP = event.GetPosition()
            self.IsStartCopy = True
        else:
            p = event.GetPosition()
            minx, miny = min(self.firstP.x, self.lastP.x), min(self.firstP.y, self.lastP.y)
            maxx, maxy = max(self.firstP.x, self.lastP.x), max(self.firstP.y, self.lastP.y)
            if wx.Rect(minx - 2, miny - 2, 5, 5).Inside(p):
                self.firstP = wx.Point(maxx, maxy)
                self.IsInRectLT = True
            elif wx.Rect(maxx / 2 + minx / 2 - 2, miny - 2, 5, 5).Inside(p):
                self.firstP = wx.Point(maxx, maxy)
                self.TempP = wx.Point(minx, miny)
                self.IsInRectT = True
            elif wx.Rect(maxx - 2, miny - 2, 5, 5).Inside(p):
                self.firstP = wx.Point(minx, maxy)
                self.IsInRectTR = True
            elif wx.Rect(maxx - 2, maxy / 2 + miny / 2 - 2, 5, 5).Inside(p):
                self.firstP = wx.Point(minx, maxy)
                self.TempP = wx.Point(maxx, miny)
                self.IsInRectR = True
            elif wx.Rect(maxx - 2, maxy - 2, 5, 5).Inside(p):
                self.firstP = wx.Point(minx, miny)
                self.IsInRectRB = True
            elif wx.Rect(maxx / 2 + minx / 2 - 2, maxy - 2, 5, 5).Inside(p):
                self.firstP = wx.Point(minx, miny)
                self.TempP = wx.Point(maxx, maxy)
                self.IsInRectB = True
            elif wx.Rect(minx - 2, maxy - 2, 5, 5).Inside(p):
                self.firstP = wx.Point(maxx, miny)
                self.IsInRectBL = True
            elif wx.Rect(minx - 2, maxy / 2 + miny / 2 - 2, 5, 5).Inside(p):
                self.firstP = wx.Point(maxx, miny)
                self.TempP = wx.Point(minx, maxy)
                self.IsInRectL = True
            elif wx.Rect(minx, miny, maxx - minx, maxy - miny).Inside(p):
                self.firstP = wx.Point(minx, miny)
                self.lastP = wx.Point(maxx, maxy)
                self.MoveP = p
                self.IsInRectCopy = True
            else:
                self.IsInRectLT = False
                self.IsInRectTR = False
                self.IsInRectRB = False
                self.IsInRectBL = False
                self.IsInRectT = False
                self.IsInRectR = False
                self.IsInRectB = False
                self.IsInRectL = False
                self.IsInRectCopy = False

    def On_Mouse_LeftUp(self, event):
        self.IsInRectLT = False
        self.IsInRectTR = False
        self.IsInRectRB = False
        self.IsInRectBL = False
        self.IsInRectT = False
        self.IsInRectR = False
        self.IsInRectB = False
        self.IsInRectL = False
        self.IsInRectCopy = False
        
    def On_Mouse_Move(self, event):
        p = event.GetPosition()
        self.MouseP = p
        rect = self.GetClientRect()
        w, h = rect.width, rect.height
        minx, miny = min(self.firstP.x, self.lastP.x), min(self.firstP.y, self.lastP.y)
        maxx, maxy = max(self.firstP.x, self.lastP.x), max(self.firstP.y, self.lastP.y)
        if self.IsStartCopy and (wx.Rect(minx - 2, miny - 2, 5, 5).Inside(p) or wx.Rect(maxx - 2, maxy - 2, 5, 5).Inside(p)):
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENWSE))
        elif self.IsStartCopy and (wx.Rect(maxx - 2, miny - 2, 5, 5).Inside(p) or wx.Rect(minx - 2, maxy - 2, 5, 5).Inside(p)):
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENESW))
        elif self.IsStartCopy and (wx.Rect(maxx / 2 + minx / 2 - 2, miny - 2, 5, 5).Inside(p) or wx.Rect(maxx / 2 + minx / 2 - 2, maxy - 2, 5, 5).Inside(p)):
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))
        elif self.IsStartCopy and (wx.Rect(maxx - 2, maxy / 2 + miny / 2 - 2, 5, 5).Inside(p) or wx.Rect(minx - 2, maxy / 2 + miny / 2 - 2, 5, 5).Inside(p)):
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
        elif wx.Rect(minx, miny, maxx - minx, maxy - miny).Inside(p):
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
        else:
            self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

        if event.LeftIsDown():
            if self.IsInRectLT or self.IsInRectRB:
                if (self.lastP.x - self.firstP.x) * (self.lastP.y - self.firstP.y) >= 0:
                    self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENWSE))
                self.lastP = event.GetPosition()
            elif self.IsInRectTR or self.IsInRectBL:
                if (self.lastP.x - self.firstP.x) * (self.lastP.y - self.firstP.y) < 0:
                    self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENESW))
                self.lastP = event.GetPosition()
            elif self.IsInRectT:
                self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))
                self.lastP = wx.Point(self.TempP.x, p.y)
            elif self.IsInRectR:
                self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
                self.lastP = wx.Point(p.x, self.TempP.y)
            elif self.IsInRectB:
                self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))
                self.lastP = wx.Point(self.TempP.x, p.y)
            elif self.IsInRectL:
                self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
                self.lastP = wx.Point(p.x, self.TempP.y)
            elif self.IsInRectCopy:
                tw, th = self.lastP.x - self.firstP.x, self.lastP.y - self.firstP.y
                fx = min(max(0, minx + p.x - self.MoveP.x), w - tw)
                fy = min(max(0, miny + p.y - self.MoveP.y), h - th)
                self.firstP = wx.Point(fx, fy)
                self.lastP = wx.Point(fx + tw, fy + th)
                self.MoveP = p
        self.NewUpdate()

    # 双击
    def On_Mouse_LeftDblClick(self, event):
        if self.firstP.x - self.lastP.x != 0 and self.firstP.y - self.lastP.y != 0:
            self.mainFrame.ShowBmp = self.mainFrame.Bmp.GetSubBitmap(wx.Rect(
                min(self.firstP.x, self.lastP.x),
                min(self.firstP.y, self.lastP.y),
                abs(self.firstP.x - self.lastP.x),
                abs(self.firstP.y - self.lastP.y)
            ))
            iS = self.mainFrame.ShowBmp.GetSize().Get()
            self.mainFrame.paintPanel.SetScrollbars(1, 1, iS[0] + 10, iS[1] + 10)
            self.mainFrame.paintPanel.SetScrollRate(10, 10)
        self.Close()
        self.mainFrame.Show()
        
    def NewUpdate(self):
        self.RefreshRect(self.GetClientRect(), True)
        self.Update()

def main():
    app = wx.App()
    mainFrame = MainFrame()
    mainFrame.Show()
    app.SetTopWindow(mainFrame)
    app.MainLoop()

if __name__ == '__main__':
    main()
