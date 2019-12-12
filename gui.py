import tkinter as tk
from tkinter.filedialog import askdirectory
import sys
import pyperclip
import youtube_dl_
import os
import getpass
from tkinter.messagebox import showerror
import sprit_downloader
import configparser
from concurrent import futures


class Input(tk.Frame):

    def __init__(self, master=None):

        if os.path.exists('settings.ini'):
            self.config_ini = configparser.ConfigParser()
            self.config_ini.read('settings.ini', encoding='utf-8')
            user_name = getpass.getuser()
            try:
                self.setting_directory = self.config_ini.get('DEFAULT', 'Directory').replace('*', user_name)
            except configparser.NoOptionError:
                self.config_ini.set('DEFAULT', 'Directory', '')
            #print(self.setting_directory)

        else:
            showerror('エラー', 'settins.iniが見つかりません。')
            sys.exit()

        tk.Frame.__init__(self, master)
        master.geometry('400x800')
        self.frame_input = tk.LabelFrame(master, text='①　URL入力')
        self.frame_download = tk.LabelFrame(master, text='②　画質選択')
        self.frame_seve_dorectory = tk.LabelFrame(master, text='③　保存先選択')
        self.frame_start = tk.LabelFrame(master, text='④　ダウンロード')

        self.init()

        self.frame_input.pack()
        self.frame_download.pack()
        self.frame_seve_dorectory.pack()
        self.frame_start.pack()

        self.pack()

    def init(self):
        self.menu()
        self.input()
        self.set_directory()
        self.set_name()
        self.download_button()

    def menu(self):
        self.menu_root = tk.Menu(self.master)

        self.file = tk.Menu(self.menu_root, tearoff=False)
        self.edit = tk.Menu(self.menu_root, tearoff=False)

        self.master.configure(menu=self.menu_root)

        self.menu_root.add_cascade(label='file', menu=self.file)
        self.menu_root.add_cascade(label='edit', menu=self.edit)

        self.file.add_command(label='Exit', command=sys.exit)

        self.edit.add_command(label='Preferences', command=self.preferences)  #

    def preferences(self):

        directory_change = tk.StringVar()

        def ask_dir():
            directory_change = askdirectory()
            #print(directory_change)
            if directory_input.get() == '':
                pass
            else:
                directory_input.delete(0, tk.END)
            directory_input.insert(tk.END, directory_change)

        def button_OK():
            self.config_ini.set('DEFAULT', 'Directory', directory_change)
            if self.setting_directory != directory_change:
                with open('settings.ini', 'w') as file:
                    self.config_ini.write(file)
            pref.destroy()

        pref = tk.Toplevel()
        pref.geometry('200x300')

        top_menu = tk.Label(pref, text='設定一覧')
        top_menu.pack()

        directory = tk.Frame(pref)

        directory_label = tk.Label(directory, text='保存先')
        directory_label.pack()

        directory_input = tk.Entry(directory)
        directory_input.pack()
        directory_input.insert(tk.END, self.setting_directory)

        directory_input_button = tk.Button(directory, text='参照', command=ask_dir)
        directory_input_button.pack()

        directory.pack(side=tk.LEFT)

        buttons = tk.Frame(pref)
        buttons.pack()

        ok_button = tk.Button(buttons, text='OK', command=button_OK)
        ok_button.pack()

        cancel_button = tk.Button(buttons, text='キャンセル', command=lambda: pref.destroy())
        cancel_button.pack()

    def input(self):
        self.input_entry = tk.Entry(self.frame_input)

        paste_button = tk.Button(self.frame_input)
        paste_button.configure(text='paste', command=self.paste)

        input_button = tk.Button(self.frame_input)
        input_button.configure(text='OK', command=self.set_url)
        self.input_entry.bind('<Return>', self.set_url)
        self.input_entry.focus_set()

        self.input_entry.pack()
        paste_button.pack()
        input_button.pack()

    def set_url(self, *event):
        self.input_link = self.input_entry.get()
        widgets = self.frame_download.winfo_children()
        if widgets:
            for child in widgets:
                #print(child)
                child.destroy()
        try:
            self.analyser_mp4ANDm4a(self.input_link)
        except :
            showerror(title='エラー', message='urlが正しくありません。')
            self.input_entry.delete(0, tk.END)

    def paste(self):
        self.input_entry.delete('0', 'end')
        self.input_entry.insert(tk.END, pyperclip.paste())

    def analyser_mp4ANDm4a(self, url):
        self.module = youtube_dl_.extract_information()
        result = self.module.extract_(url)
        formats = self.module.extract_formats(result)
        self.movie_title = result['title']
        self.list = self.module.return_only_mp4(formats) + self.module.return_only_m4a(formats)

        self.title = tk.Label(self.frame_download, text='タイトル:' + self.movie_title)
        self.title.pack()

        self.choosen_format_index = tk.IntVar()
        self.choosen_format_index.set(-1)

        for data in self.list:
            format = self.module.return_format(data)
            amount = self.module.get_data_amount(data, round_=True)
            #print(amount)
            if amount != False:
                box = tk.Radiobutton(self.frame_download)
                #print(self.module)
                box.configure(text='画質：{}　サイズ:{}Mb'.format(format, amount), variable=self.choosen_format_index,
                              value=self.list.index(data))
                box.pack()

    def detect_url(self):
        index = self.choosen_format_index.get()
        if index != -1:
            return self.list[index]['url']
        else:
            return False

    def set_directory(self):
        self.output_link = tk.StringVar()

        self.output_entry = tk.Entry(self.frame_seve_dorectory)
        self.output_entry.bind('<Return>', self.set_folder)
        self.output_entry.pack()

        self.output_entry.insert(tk.END, self.setting_directory)

        choose_folder_button = tk.Button(self.frame_seve_dorectory)
        choose_folder_button.configure(text='フォルダを選択', command=self.choose_folder_gui)
        choose_folder_button.pack()

    def set_name(self):
        set_title = tk.Label(self.frame_seve_dorectory, text='保存名を入力（省略可）')
        set_title.pack()

        self.title_entry = tk.Entry(self.frame_seve_dorectory)
        self.title_entry.pack()

    def choose_folder_gui(self):
        output_link = askdirectory()
        if self.output_entry != '':
            self.output_entry.delete(0, tk.END)
        self.output_entry.insert(tk.END, output_link)
        self.set_folder()

    def set_folder(self, *args):
        self.output_directory = self.output_entry.get()
        if os.path.exists(self.output_directory):
            return self.output_directory
        else:
            return False

    def check_download_is_ok(self):
        self.buttton_no = self.choosen_format_index.get()
        folder = self.set_folder()
        self.title_output = self.title_entry.get()
        if self.title_output == '':
            self.title_output = self.movie_title
        #print(self.title_output)
        if folder:
            if self.buttton_no != -1:
                return True
            else:
                tk.messagebox.showerror(title='エラー', message='画質を選択してください')
                return False
        elif folder == '':
            tk.messagebox.showerror(title='エラー', text='保存先を入力してください')
            return False
        else:
            tk.messagebox.showerror(title='エラー', message='ファイル保存先が存在しません')
            return False

    def download_button(self):
        dl_button = tk.Button(self.frame_start, text='ダウンロード', command=self.download_queue)
        dl_button.pack()

    def dl_movie(self):
        if self.check_download_is_ok():
            quality = self.buttton_no
            list = self.list
            choiced = list[quality]
            num = self.whether_video_only(choiced)
            audio = self.detect_audio(list)
            if num == 2:

                queue_list = [2, choiced, list[audio]]
            elif num == 3:
                queue_list = [3, choiced]
            else:
                queue_list = [1, list[audio]]

            return queue_list

    def whether_video_only(self, data):  # 1は音声のみ2は動画のみ3は両方あり
        if data['acodec'] == 'none':
            return 2
        elif data['vcodec'] == 'none':
            return 1
        else:
            return 3

    def detect_audio(self, list):
        max = 0
        for n in list:
            if n['vcodec'] == 'none':
                if max > 0:
                    break
                max += 1
                return list.index(n)

    def download_queue(self):
        queue_list = self.dl_movie()
        if queue_list[0] == 1:
            self.download_(queue_list[1])
        if queue_list[0] == 2:
            for queue in queue_list[1:]:
                self.download_(queue)
        if queue_list[0] == 3:
            self.download_(queue_list[1])

    def download_(self, queue):
        sl = sprit_downloader.DLmanager(queue, 8, self.output_directory)
        name = sl.name
        ext = sl.ext
        title = self.title_output
        ex_path = self.output_directory + '/' + name + '.' + ext
        output_path = self.output_directory + '/' + title + '.' + ext
        os.rename(ex_path, output_path)





win = tk.Tk()
app = Input(master=win)
app.mainloop()
