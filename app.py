#!/usr/bin/env python3

import wx
import wx.html
from wand.image import Image as WImage
from io import BytesIO
from glob import glob
import os


def insensitive_glob(pattern):
    def either(c):
        return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c
    return glob(''.join(map(either, pattern)))


def start_match_len(str_a, str_b):
    if len(str_a) * len(str_b) == 0:
        return 1
    if len(str_a) > len(str_b):
        return start_match_len(str_b, str_a)
    str_a = str_a.lower()
    str_b = str_b.lower()
    count = 0
    while str_a[count] == str_b[count]:
        count += 1
        if count == len(str_a):
            break
    return count


def get_abs_path(path):
    if len(path) == 0:
        return os.path.expanduser('~/')
    if path[0] == '/':
        return path
    return os.path.expanduser('~/' + path)


class Frame(wx.Frame):
    def __init__(
        self, image, parent=None, id=-1, pos=wx.DefaultPosition,
        title='Sort Out Scans'
    ):
        self.LoadHistory()
        self.history_cursor = -1
        self.history_estimate_latency = 3
        temp = image.ConvertToBitmap()
        size = temp.GetWidth(), temp.GetHeight()
        self.col_width = 850
        self.inter_space = 10
        self.line_height = 30
        wx.Frame.__init__(self, parent, id, title, pos, size)
        self.bmp = wx.StaticBitmap(parent=self, bitmap=temp)
        self.control = wx.TextCtrl(
            self, size=(self.col_width, self.line_height),
            pos=(self.inter_space + size[0], self.inter_space),
            style=wx.TE_PROCESS_ENTER
        )
        self.html_window = wx.html.HtmlWindow(
            self, pos=(
                size[0] + self.inter_space,
                2*self.inter_space + self.line_height
            ),
            size=(self.col_width, 800),
            style=wx.html.HW_SCROLLBAR_NEVER
        )

        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnterPress, self.control)
        self.Bind(wx.EVT_TEXT, self.OnTextChange, self.control)
        self.control.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)

        self.SetClientSize(
            (size[0] + 2*self.inter_space + self.col_width, size[1])
        )

        self.OnEnterPress(None)

    def OnTextChange(self, event):
        self.UpdateView()

    def UpdateView(self):
        possible_objects = self.GetPossibleFilesystemObjects(
            self.control.GetValue()
        )
        self.SetHTMLWindow(possible_objects)

    def SetHTMLWindow(self, object_list):
        object_list = [os.path.basename(o) for o in object_list]
        html_string = ''
        if len(object_list) == 1:
            html_string = os.path.basename(object_list[0])
        elif len(object_list) > 1:
            for i in range(len(object_list)):
                nbr_bold = 0
                if i > 0:
                    nbr_bold = max(
                        nbr_bold,
                        start_match_len(object_list[i], object_list[i-1]) + 1
                    )
                if i < len(object_list) - 1:
                    nbr_bold = max(
                        nbr_bold,
                        start_match_len(object_list[i], object_list[i+1]) + 1
                    )
                html_string += '<b>'
                html_string += object_list[i][:nbr_bold].replace(' ', '&nbsp;')
                html_string += '</b>'
                html_string += object_list[i][nbr_bold:].replace(' ', '&nbsp;')
                html_string += '&emsp;'
            html_string = html_string[:-6]
        html_string += '<br><br>'
        counter = 0
        for h in self.history[::-1]:
            if counter == self.history_cursor:
                html_string += '<b>'
            html_string += h
            if counter == self.history_cursor:
                html_string += '</b>'
            html_string += '<br>'
            counter += 1
        self.html_window.SetPage(html_string)

    def OnKeyPress(self, event):
        if event.GetKeyCode() == wx.WXK_TAB:
            self.OnTabPress(event)
        elif event.GetKeyCode() == wx.WXK_BACK:
            self.OnBackPress(event)
        elif event.GetKeyCode() == wx.WXK_DOWN:
            self.OnDownPress(event)
        elif event.GetKeyCode() == wx.WXK_UP:
            self.OnUpPress(event)
        else:
            event.Skip()

    def OnDownPress(self, event):
        if self.history_cursor < len(self.history) - 1:
            self.history_cursor += 1
        self.control.SetValue(self.history[-self.history_cursor-1])
        wx.CallLater(1, self.control.SetInsertionPointEnd)

    def OnUpPress(self, event):
        if self.history_cursor >= 0:
            self.history_cursor -= 1
        if self.history_cursor == -1:
            self.control.SetValue(self.GetHistoryEstimate())
            self.UpdateView()
        else:
            self.control.SetValue(self.history[-self.history_cursor-1])
        wx.CallLater(1, self.control.SetInsertionPointEnd)

    def OnEnterPress(self, event):
        self.history_cursor = -1
        if event is not None:
            if self.control.GetValue() in self.history:
                del self.history[self.history.index(self.control.GetValue())]
            self.history.append(self.control.GetValue())
        self.WriteHistory()
        self.control.SetValue(self.GetHistoryEstimate())
        wx.CallLater(1, self.control.SetInsertionPointEnd)
        self.UpdateView()

    def OnBackPress(self, event):
        if self.control.GetInsertionPoint() != self.control.GetLastPosition():
            event.Skip()
            return
        substr = self.control.GetValue()[:-1]
        if '/' not in substr:
            self.control.SetValue('')
            self.UpdateView()
        else:
            idx = substr[::-1].index('/')
            self.control.SetValue(self.control.GetValue()[:-idx-1])
        wx.CallLater(1, self.control.SetInsertionPointEnd)

    def OnTabPress(self, event):
        new_path = self.GetPossibleFilesystemObjects(
            self.control.GetValue()
        )[0]
        if os.path.isfile(get_abs_path(new_path)):
            self.control.SetValue(new_path)
        elif os.path.isdir(get_abs_path(new_path)):
            self.control.SetValue(new_path+'/')
        else:
            raise ValueError('This should not ought to happen!')
        wx.CallLater(1, self.control.SetInsertionPointEnd)

    def LoadHistory(self):
        self.history = []
        with open('.sos_history', 'r') as f:
            for line in f.readlines():
                self.history.append(line.rstrip())

    def WriteHistory(self):
        with open('.sos_history', 'w') as f:
            for h in self.history:
                f.write(h)
                f.write('\n')

    def GetHistoryEstimate(self):
        history_estimate = self.history[-1]
        for i in range(self.history_estimate_latency):
            n = start_match_len(history_estimate, self.history[-i-1])
            history_estimate = history_estimate[:n]
        return history_estimate

    def GetPossibleFilesystemObjects(self, path):
        abs_path = get_abs_path(path)
        home_dir = os.path.expanduser('~/')
        pattern = abs_path + '*'
        result = [
            f[len(home_dir):] if f[:len(home_dir)] == home_dir else f
            for f in insensitive_glob(pattern)
        ]
        return sorted(result, key=lambda s: os.path.basename(s).lower())


class App(wx.App):
    def OnInit(self):
        with BytesIO() as bytesio:
            with WImage(filename='Abiturzeugnis.pdf[2]', resolution=60) as img:
                img.format = 'jpg'
                img.save(file=bytesio)
            bytesio.seek(0)
            self.pdfpageimage = wx.Image(bytesio, type=wx.BITMAP_TYPE_JPEG)
        self.frame = Frame(self.pdfpageimage)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


app = App()
app.MainLoop()
