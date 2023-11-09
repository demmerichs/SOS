#!/usr/bin/env python3

import wx
import wx.html
from wand.image import Image as WImage
from io import BytesIO
from glob import glob
import os
import sys
from PyPDF2 import PdfReader, PdfWriter
import re
import textract
from shutil import copyfile


script_path = os.path.dirname(os.path.realpath(__file__))
watermarkPdf = PdfReader(
    open(os.path.join(script_path, "sos_watermark.pdf"), "rb")
)


month_names = [
    'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August',
    'September', 'Oktober', 'November', 'Dezember'
]
year_regex = r"((?:19|20|21)\d{2})"
nbr_month_regex = r"(0?[1-9]|1[0-2])"
text_month_regex = r"(%s)" % '|'.join(month_names)
day_regex = r"(0?[1-9]|[1-2][0-9]|3[0-1])"
date_regex_text = r"%s\. %s %s" % (day_regex, text_month_regex, year_regex)
date_regex_nbr = r"%s\.%s\.%s" % (day_regex, nbr_month_regex, year_regex)


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


def get_dates_and_values(text):
    dates_and_values = []
    matches = re.finditer(date_regex_text, text, re.MULTILINE)
    for match in matches:
        value = (
            int(match.group(3)) * int(1e4) +
            (month_names.index(match.group(2)) + 1) * int(1e2) +
            int(match.group(1))
        )
        value = str(value)
        date = match.group()
        dates_and_values.append((date, value))
    matches = re.finditer(date_regex_nbr, text, re.MULTILINE)
    for match in matches:
        value = (
            int(match.group(3)) * int(1e4) +
            int(match.group(2)) * int(1e2) +
            int(match.group(1))
        )
        value = str(value)
        date = match.group()
        dates_and_values.append((date, value))
    matches = re.finditer(r"[\. ]"+year_regex+r"[\. ]", text, re.MULTILINE)
    for match in matches:
        value = match.group(1)
        dates_and_values.append((value, value))
    return sorted(dates_and_values, key=lambda x: -int(x[1]))


class Frame(wx.Frame):
    def __init__(
        self, filename, parent=None, id=-1, pos=wx.DefaultPosition,
        title='Sort Out Scans'
    ):
        super(Frame, self).__init__()
        self.filename = filename
        self.history_cursor = -1
        self.date_cursor = -1
        self.page_cursor = 0
        self.history_estimate_latency = 3
        self.col_width = 850
        self.inter_space = 10
        self.line_height = 30
        self.pdfFile = PdfReader(filename, 'r')
        self.watermarkedPdfFile = PdfWriter()

        extracttext = textract.process(filename).decode('utf-8')
        self.page_texts = extracttext.split('\f')
        assert len(self.page_texts[-1]) == 0
        self.page_texts = self.page_texts[:-1]
        assert len(self.page_texts) == len(self.pdfFile.pages)

        self.LoadHistory()
        temp = self.GetCurrentBitmap()
        size = temp.GetWidth(), temp.GetHeight()
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
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.SetClientSize(
            (size[0] + 2*self.inter_space + self.col_width, size[1])
        )

        self.OnEnterPress(None)

    def GetCurrentBitmap(self):
        if len(self.pdfFile.pages) == self.page_cursor:
            self.Close()
            return None
        with BytesIO() as bytesio:
            with WImage(
                filename='%s[%d]' % (self.filename, self.page_cursor),
                resolution=120
            ) as img:
                img.format = 'jpg'
                img.save(file=bytesio)
            bytesio.seek(0)
            image = wx.Image(bytesio, type=wx.BITMAP_TYPE_JPEG)
        return image.ConvertToBitmap()

    def GetTextOCR(self):
        return self.page_texts[self.page_cursor]

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
        dates_and_values = get_dates_and_values(self.GetTextOCR())
        counter = 0
        for date, value in dates_and_values:
            if counter == self.date_cursor:
                html_string += '<b>'
            html_string += value + '&emsp;' + date
            if counter == self.date_cursor:
                html_string += '</b>'
            html_string += '<br>'
            counter += 1
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

    def OnTextChange(self, event):
        self.UpdateView()

    def OnKeyPress(self, event):
        if event.GetKeyCode() == wx.WXK_TAB:
            self.OnTabPress(event)
        elif event.GetKeyCode() == wx.WXK_BACK:
            self.OnBackPress(event)
        elif event.GetKeyCode() == wx.WXK_DOWN:
            self.OnDownPress(event)
        elif event.GetKeyCode() == wx.WXK_UP:
            self.OnUpPress(event)
        elif event.GetKeyCode() == wx.WXK_PAGEUP:
            self.OnPageUpPress(event)
        elif event.GetKeyCode() == wx.WXK_PAGEDOWN:
            self.OnPageDownPress(event)
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

    def OnPageDownPress(self, event):
        dates_and_values = get_dates_and_values(self.GetTextOCR())
        if self.date_cursor == -1:
            prev_val = ''
        else:
            prev_val = dates_and_values[self.date_cursor][1]
        if len(prev_val) == 8:
            prev_val += '_'
        elif len(prev_val) == 4:
            prev_val += '/'
        if self.date_cursor < len(dates_and_values) - 1:
            self.date_cursor += 1
        new_val = dates_and_values[self.date_cursor][1]
        if len(new_val) == 8:
            new_val += '_'
        elif len(new_val) == 4:
            new_val += '/'
        if len(prev_val) == 0:
            self.control.SetValue(self.control.GetValue() + new_val)
        else:
            old_string = self.control.GetValue()
            self.control.SetValue(old_string.replace(prev_val, new_val))
        self.UpdateView()
        wx.CallLater(1, self.control.SetInsertionPointEnd)

    def OnPageUpPress(self, event):
        dates_and_values = get_dates_and_values(self.GetTextOCR())
        prev_val = dates_and_values[self.date_cursor][1]
        if len(prev_val) == 8:
            prev_val += '_'
        elif len(prev_val) == 4:
            prev_val += '/'
        if self.date_cursor >= 0:
            self.date_cursor -= 1
        if self.date_cursor == -1:
            new_val = ''
        else:
            new_val = dates_and_values[self.date_cursor][1]
        if len(new_val) == 8:
            new_val += '_'
        elif len(new_val) == 4:
            new_val += '/'
        old_string = self.control.GetValue()
        self.control.SetValue(old_string.replace(prev_val, new_val))
        self.UpdateView()
        wx.CallLater(1, self.control.SetInsertionPointEnd)

    def ProcessPage(self):
        cur_page = self.pdfFile.pages[self.page_cursor]
        if os.path.splitext(self.control.GetValue())[1] == '.pdf':
            abs_path = get_abs_path(self.control.GetValue())
            new = PdfWriter()
            if os.path.isfile(abs_path):
                old = PdfReader(abs_path, 'r')
                for i in range(len(old.pages)):
                    new.add_page(old.pages[i])
            new.add_page(cur_page)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, 'wb') as f:
                new.write(f)
            cur_page.merge_page(watermarkPdf.pages[0])
        self.watermarkedPdfFile.add_page(cur_page)
        self.page_cursor += 1
        if self.GetCurrentBitmap() is not None:
            self.bmp.SetBitmap(self.GetCurrentBitmap())

    def OnEnterPress(self, event):
        self.history_cursor = -1
        if event is not None:
            if (
                os.path.splitext(self.control.GetValue())[1] == '.pdf' or
                self.control.GetValue() == ''
            ):
                self.ProcessPage()
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
        if os.path.exists(os.path.join(script_path, '.sos_history')):
            with open(os.path.join(script_path, '.sos_history'), 'r') as f:
                for line in f.readlines():
                    self.history.append(line.rstrip())

    def WriteHistory(self):
        with open(os.path.join(script_path, '.sos_history'), 'w') as f:
            for h in self.history:
                f.write(h)
                f.write('\n')

    def GetHistoryEstimate(self):
        if len(self.history) < self.history_estimate_latency:
            return ''
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

    def OnClose(self, event):
        print('Finishung up and closing app...')
        while self.page_cursor < len(self.pdfFile.pages):
            self.watermarkedPdfFile.add_page(
                self.pdfFile.pages[self.page_cursor]
            )
            self.page_cursor += 1
        with open(filename, 'wb') as ostream:
            self.watermarkedPdfFile.write(ostream)
        print('Closed!')
        event.Skip()


class App(wx.App):
    def __init__(self, filename):
        self.filename = filename
        super(App, self).__init__()

    def OnInit(self):
        self.frame = Frame(self.filename)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    filename = sys.argv[1]
    assert(os.path.isfile(filename))
    assert(os.path.splitext(filename)[1].lower() == '.pdf')

    if not os.path.exists(filename + '.bak'):
        copyfile(filename, filename + '.bak')
        print('Created backup file: %s.bak' % filename)
    app = App(filename)
    app.MainLoop()
