import tkinter as tk
import tkinter.ttk as ttk
import datetime
import calendar
import sqlite3
import math
import time
import os
from tkinter import messagebox

Font = ("meiryo", "11")
Fonta = ("meiryo", "15")
Fontb = ("meiryo", "9")
Fontc = ("meiryo", "9")

################################################################
class tokei(tk.Frame):
    def __init__(self, parent):
        self.naka=155
        self.tyo_x=195
        self.tyo_y=165

        super().__init__(parent)
        self.canvas = tk.Canvas(self,width=390, height=330,bg="white",relief="solid",bd=0)
        self.canvas.grid(row=2,column=0,rowspan=4,columnspan=3)

        self.canvas.create_oval(
            self.tyo_x - self.naka, self.tyo_y - self.naka,
            self.tyo_x + self.naka, self.tyo_y + self.naka,
            outline="black", width=2
        )

        #本体
        for i in range(12):
            angle = math.radians(i * 30)
            x = self.tyo_x + (self.naka - 15) * math.sin(angle)
            y = self.tyo_y - (self.naka - 15) * math.cos(angle)

            self.canvas.create_text(x, y, text=str(i if i != 0 else 12), font=("meiryo", 12))
        
        self.update_clock()

#時間の更新
    def update_clock(self):
        current_time = time.localtime()
        hours = current_time.tm_hour % 12
        minutes = current_time.tm_min
        seconds = current_time.tm_sec

        hour_angle = math.radians((hours + minutes / 60) * 30) 
        minute_angle = math.radians((minutes + seconds / 60) * 6) 
        second_angle = math.radians(seconds * 6) 

        self.canvas.delete("hand") 

        #時
        self.draw_hand(hour_angle, self.naka * 0.5, width=4, tag="hand")
        #分
        self.draw_hand(minute_angle, self.naka * 0.7, width=3, tag="hand")
        #秒
        self.draw_hand(second_angle, self.naka * 0.9, width=1, fill="red", tag="hand")

        self.after(1000, self.update_clock)

    def draw_hand(self, angle, length, width=2, fill="black", tag=None):
        x = self.tyo_x + length * math.sin(angle)
        y = self.tyo_y - length * math.cos(angle)
        self.canvas.create_line(
            self.tyo_x, self.tyo_y, x, y,
            width=width, fill=fill, tag=tag
        )

#########################################################################

class HomeFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master,bg=("#F5FEEE"))
        self.master = master
        self.switch_frame = switch_frame

        for row in range(8):
            self.grid_rowconfigure(row, weight=1)
        for col in range(8):
            self.grid_columnconfigure(col, weight=1)

        self.dt_now=datetime.datetime.now()
        self.year=self.dt_now.year
        self.month=self.dt_now.month
        self.day=self.dt_now.day

        label1 = tk.Label(self, text=str(self.year)+"年"+str(self.month)+"月"+str(self.day)+"日", 
                            font=("meiryo", "30"),bd=1,bg=("#F5FEEE"))
        label1.place(x=80,y=40)

        label2 = tk.Label(self, text="今日の予定", font=("meiryo", "20"),
                            relief='solid',bd=1,bg=("#D1FAD6"))
        label2.grid(row=2, column=2, padx=10, pady=10)

        db_label = tk.Label(self, text="", font=("meiryo", "20"),bg=("#D1FAD6"),
                            relief='solid',bd=1,anchor="w",justify="left")
        db_label.grid(row=3, column=2, padx=10, pady=10)

        clock = tokei(self)
        clock.grid(row=3, column=0)
        
        calendar_button = tk.Button(self, text="カレンダー画面へ",bg=("#FFFE70"), font=("meiryo", "15"), command=self.switch_to_calendar)
        calendar_button.grid(row=3, column=6, padx=10, pady=10)

        r = master.search_a(datetime.date.today())
        
        if len(r) == 0:
            return db_label.configure(text = "予定はありません")
        result = ""
        cnt=0
        for row in r:
            if cnt == 0:
                result = "|".join(map(str,row))
            else:
                result += "\n"+"|".join(map(str,row)) #文字列に変換、改行
            cnt+=1
        result=self.get_truncated_text(result)
        db_label.configure(text= result)
        
    def get_truncated_text(self, text, max_length=8, max_lines=5):
        # 複数行のテキストを行ごとに分割
        lines = text.split("\n")
        truncated_lines = []
        truncated_lines = lines[:max_lines]

        # 各行が指定されたmax_lengthより長ければ省略する
        for i in range(len(truncated_lines)):
            if len(truncated_lines[i]) > max_length:
                truncated_lines[i] = truncated_lines[i][:max_length] + "..."
    
        # 行数がmax_linesより多ければ「他」を2行目の最後に追加
        if len(lines) > max_lines:
            # 2行目の最後に「他」を追加
            truncated_lines[-1] = truncated_lines[-1] + f"  他{str(len(lines)-(max_lines))}件"

        # 行ごとに省略を施したテキストを再結合
        return "\n".join(truncated_lines)
        
    def switch_to_calendar(self):
        #カレンダーフレームを開く
        self.switch_frame("CalendarFrame")

# カレンダー用のフレーム
class CalendarFrame(tk.Frame):
    def __init__(self, master, switch_frame):

        global kyo

        super().__init__(master)
        self.master = master
        self.switch_frame = switch_frame
#--------------------------------------------------
        self.dt_now=datetime.datetime.now()
        self.year=self.dt_now.year
        self.month=self.dt_now.month
        self.day=self.dt_now.day
        self.nisu=self.urujudge(self.year)

        kyo=str(self.year)+str(self.month)+str(self.day)
        
        for row in range(8):
            self.grid_rowconfigure(row, minsize=90)
        for col in range(7):
            self.grid_columnconfigure(col, minsize=137.5)

        self.kare(self.nisu,self.month,self.year)
    #うるう年の判定
    def urujudge(self, y) :
        noturu = [31,28,31,30,31,30,31,31,30,31,30,31]
        urunisu = [31,29,31,30,31,30,31,31,30,31,30,31]
        if(y%100==0 and y%400!=0 or y%4!=0):
            n=noturu
        else:
            n=urunisu
        return n
        
    def kesu(self):
        for widget in self.winfo_children():
            widget.destroy()
        for lst in [labels_1,labels_11,labels_2,labels_22,labels_3,labels_33]:
            lst.clear()

    #先月画面への移行
    def back_month(self):
        self.kesu()
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.kare(self.urujudge(self.year), self.month, self.year)
    #次月画面への移行
    def go_month(self):
        self.kesu()
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.kare(self.urujudge(self.year), self.month, self.year)
    
    def clicked(self, event=None):
        # クリックしたラベルのグループ名を表示
        label = event.widget
        self.open_settings_window(label.group)#ここから年月日を取得して設定画面に遷移

    def serch(self, y, m, n):
        m = self.monone(m)
        n = self.dayone(n)
        date = y + "-" + m + "-" + n
        r = self.master.search_a(date)
        if len(r) == 0:
            return ""
        result = ""
        for row in r:
            result += "\n"+"|".join(map(str,row))
        return result
        
    def get_truncated_text(self, text, max_length=6, max_lines=3):
        # 複数行のテキストを行ごとに分割
        lines = text.split("\n")
        truncated_lines = []
        
        truncated_lines = lines[:max_lines]

        # 各行が指定されたmax_lengthより長ければ省略する
        for i in range(len(truncated_lines)):
            if len(truncated_lines[i]) > max_length:
                truncated_lines[i] = truncated_lines[i][:max_length] + "..."
    
        # 行数がmax_linesより多ければ「他」を2行目の最後に追加
        if len(lines) > max_lines:
            # 2行目の最後に「他」を追加
            truncated_lines[-1] = truncated_lines[-1] + f"  他{str(len(lines)-(max_lines))}件"

        # 行ごとに省略を施したテキストを再結合
        return "\n".join(truncated_lines)
#------------------------------------------------
    def kare(self,nisu,month,year):
        global num,labels_1,labels_11,labels_2,labels_22,labels_3,labels_33
        num=0

        labels_1 = [
            tk.Label(
            self,
            text=str(''),
            padx=5,
            font=Fontc,
            anchor="sw",
            justify="left",
            relief=tk.SOLID,
)
            for num in range(nisu[month-2],
                            nisu[month-2]-(calendar.weekday(year,month,1)+1),-1)]

    # クリックイベントをバインド
        for index, label in enumerate(reversed(labels_1),#リストを逆順に
                            start=nisu[month-2]-(calendar.weekday(year,month,1))):
            if self.month == 1:     # グループに年月日をリストで設定
                label.group = [self.year-1, 12, index]
                label.config(text = self.get_truncated_text(
                        self.serch(str(self.year-1), '12', str(index))))
                #スケジュールをその日のラベルに表示
            else:
                label.group = [self.year, self.month-1, index] 
                label.config(text = self.serch(str(self.year), str(self.month-1), str(index)))
            label.bind('<1>', self.clicked)

        labels_11 = [
            tk.Label(
            self,
            fg='#aaaaaa',
            text=str(num),
            relief=tk.SOLID,
            font=("Helvetica",15)
            )
            for num in range(nisu[month-2],
                            nisu[month-2]-(calendar.weekday(year,month,1)+1),-1)]

    # クリックイベントをバインド
        for index, label in enumerate(reversed(labels_11),#リストを逆順に
                            start=nisu[month-2]-(calendar.weekday(year,month,1))):
            if self.month == 1:     # グループに年月日を設定
                label.group = [self.year-1, 12, index]
            else:
                label.group = [self.year, self.month-1, index]
            label.bind('<1>', self.clicked)
#-----------------------------------------------------
        labels_2 = [
            tk.Label(
            self,
            text=str(''),
            padx=5,
            font=Fontc,
            anchor="sw",
            justify="left",
            relief=tk.SOLID
            )
            for num in range(0,nisu[month-1],1)]
        
    # クリックイベントをバインド
        for index, label in enumerate(labels_2):
            label.group = [self.year, self.month, index+1]  # グループに年月日を設定
            label.config(text = self.get_truncated_text(
                self.serch(str(self.year), str(self.month), str(index+1))))
            label.bind('<1>', self.clicked)

        labels_22 = [
            tk.Label(
            self,
            text=str(num+1),
            relief=tk.SOLID,
            font=("Helvetica",15)
            )
            for num in range(0,nisu[month-1],1)]
        
    # クリックイベントをバインド
        for index, label in enumerate(labels_22):
            label.group = [self.year, self.month, index+1]  # グループに年月日を設定
            label.bind('<1>', self.clicked)
#-----------------------------------------------------
        labels_3 = [
            tk.Label(
            self,
            text=str(''),
            padx=5,
            font=Fontc,
            anchor="sw",
            justify="left",
            relief=tk.SOLID
            )
            for num in range(0,
                42-((calendar.weekday(year,month,1)+1)+nisu[month-1]),1)]
        
    # クリックイベントをバインド
        for index, label in enumerate(labels_3):
            if self.month == 12:    # グループに年月日を設定
                label.group = [self.year+1, 1, index+1]
                label.config(text = self.serch(str(self.year+1), '1', str(index+1)))
            else:
                label.group = [self.year, self.month+1, index+1]
                label.config(text = self.serch(str(self.year), str(self.month+1), str(index+1)))
            label.bind('<1>', self.clicked)

        labels_33 = [
            tk.Label(
            self,
            fg='#aaaaaa',
            text=str(num+1),
            relief=tk.SOLID,
            font=("Helvetica",15)
            )
            for num in range(0,
                42-((calendar.weekday(year,month,1)+1)+nisu[month-1]),1)]
        
    # クリックイベントをバインド
        for index, label in enumerate(labels_33):
            if self.month == 12:    # グループに年月日を設定
                label.group = [self.year+1, 1, index+1]
            else:
                label.group = [self.year, self.month+1, index+1]
            label.bind('<1>', self.clicked)
#----------------------------------------------------
        karega=['matu.png','mame.png','hisi.png','sakura.png','koi.png','aji.png','amakawa.png','semi.png','thuki.png','haro.png','momiji.png','yuki.png']

        label_1=tk.Label(self,fg='#ff0000',text='日',relief=tk.SOLID,font=("Helvetica",20))
        label_1.grid(column=0,row=1,sticky='sew')
        label_2=tk.Label(self,text='月',relief=tk.SOLID,font=("Helvetica",20))
        label_2.grid(column=1,row=1,sticky='sew')
        label_3=tk.Label(self,text='火',relief=tk.SOLID,font=("Helvetica",20))
        label_3.grid(column=2,row=1,sticky='sew')
        label_4=tk.Label(self,text='水',relief=tk.SOLID,font=("Helvetica",20))
        label_4.grid(column=3,row=1,sticky='sew')
        label_5=tk.Label(self,text='木',relief=tk.SOLID,font=("Helvetica",20))
        label_5.grid(column=4,row=1,sticky='sew')
        label_6=tk.Label(self,text='金',relief=tk.SOLID,font=("Helvetica",20))
        label_6.grid(column=5,row=1,sticky='sew')
        label_7=tk.Label(self,fg='#0000ff',text='土',relief=tk.SOLID,font=("Helvetica",20))
        label_7.grid(column=6,row=1,sticky='sew')

        image_path=os.path.join(os.path.dirname(__file__), karega[month-1])
        image =tk.PhotoImage(file=image_path)
        gazo = tk.Label(self,image=image)
        gazo.image = image
        gazo.grid(column=0,row=0,columnspan=7)

        label_0=tk.Label(self,text=month,font=("Helvetica",50),bg=("#D1FAD6"))
        label_0.grid(column=3, row=0,sticky=tk.NSEW)
        label_8=tk.Label(self,text=str(year)+'年',relief=tk.FLAT,font=("Helvetica",25),bg=("#D1FAD6"))
        label_8.grid(column=0, row=0,columnspan=3)

        button_L = tk.Button(self,text='◀',bg="#D4D3D1",command=lambda:self.back_month())
        button_L.grid(column=2,row=0)
        button_R = tk.Button(self,text='▶',bg="#D4D3D1",command=lambda:self.go_month())
        button_R.grid(column=4,row=0)
        home_button = tk.Button(self, text="ホーム画面へ",bg=("#D4D3D1"), command=self.switch_to_home)
        home_button.place(x=10,y=10)#gridだと列の幅がおかしくなるのでこれだけplace
        #配置は変更されるかも
#-----------------------------------------------------------------
        co=(calendar.weekday(year,month,1))
        count=0
        while co>-1:

            labels_1[count].grid(column=co, row=2, sticky=tk.NSEW)
            labels_11[count].grid(column=co, row=2, sticky='new')
            if(co==0):
                labels_11[count].config(fg="#ff7777",bg="#FEC3C3")
            elif(co==6):
                labels_11[count].config(fg="#7777ff",bg="#DBE3FF")
            text=labels_11[count].cget("text")
            if(str(year)+str(month-1)+f"{text}"==kyo):
                labels_1[count].config(bg="##ffffaa")
                labels_11[count].config(bg="##ffffaa")
            count=count+1
            co=co-1
#--------------------------------------------------------------------
        co=(calendar.weekday(year,month,1)+1)
        ro=2
        count=0
        while ro<=7 and count<nisu[month-1]:
            while co<=6 and count<nisu[month-1]:
                labels_2[count].grid(column=co, row=ro, sticky=tk.NSEW)
                labels_22[count].grid(column=co, row=ro, sticky='new')
                if(co==0):
                    labels_22[count].config(fg="#ff0000",bg="#FEC3C3")
                elif(co==6):
                    labels_22[count].config(fg="#0000ff",bg="#DBE3FF")
                text = labels_22[count].cget("text")
                #print(str(year)+str(month)+f"{text}")
                if(str(year)+str(month)+f"{text}"==kyo):
                    labels_2[count].config(bg="#ffffaa")
                    labels_22[count].config(bg="#ffffaa")
                count=count+1
                co=co+1
            co=0
            ro=ro+1
#-------------------------------------------------------------------
        if(month==12):
            month=0
            year=year+1

        co=(calendar.weekday(year,month+1,1)+1)

        count=0
        ro=ro-1
        while ro<=7 and count<nisu[month]-1:
            while co<=6 and count<nisu[month]-1:
                labels_3[count].grid(column=co, row=ro, sticky=tk.NSEW)
                labels_33[count].grid(column=co, row=ro, sticky='new')
                if(co==0):
                    labels_33[count].config(fg="#ff7777",bg="#FEC3C3")
                elif(co==6):
                    labels_33[count].config(fg="#7777ff",bg="#DBE3FF")
                text = labels_33[count].cget("text")
                #print(str(year)+str(month+1)+f"{text}")
                if(str(year)+str(month+1)+f"{text}"==kyo):
                    labels_3[count].config(bg="#ffffaa")
                    labels_33[count].config(bg="#ffffaa")
                count=count+1
                co=co+1
            co=0
            ro=ro+1
            
    def dayone(self, day):#日が一桁だった場合の処理
        if int(day) < 10:
            return '0'+ day#1を01にする
        else:
            return day
        
    def monone(self, mon):#月が一桁だった場合の処理
        if int(mon) < 10:
            return '0'+ mon
        else:
            return mon
            
    def switch_to_home(self):
        self.switch_frame("HomeFrame")
        
    def open_settings_window(self, date):
        # 設定ウィンドウを開く
        #settingswindowに年月日を渡して呼び出す
        settings_window = SettingsWindow(self.master, date[0], date[1], date[2], self.update_month)
        settings_window.grab_set()  # 他のウィンドウを操作できなくする

    def update_month(self):
        self.kesu()
        self.kare(self.urujudge(self.year), self.month, self.year)

# 設定画面用のウィンドウ
class SettingsWindow(tk.Toplevel):
    def __init__(self, master, dyear, dmonth, dday, update_month_callback):
        super().__init__(master)
        self.master = master
        self.update_month_callback = update_month_callback
        global listbox, entry_date, entry_sche, combobox_1, combobox_2, combobox_3

        self.title("設定画面")
        self.geometry("480x320")
        self.resizable(False, False)#リサイズ不可
        

        self.frame_1 = tk.Frame(self,bg=("#F5FEEE"))
        self.frame_1.place(relheight=1.0, relwidth=1.0)

        self.frame_2 = tk.Frame(self,bg=("#F5FEEE"))
        self.frame_2.place(relheight=1.0, relwidth=1.0)

        year = [num for num in range(2024,2100)]
        higetu= [num for num in range(1,13)]
        hiniti= [num for num in range(1,32)]
        #年月日の選択
        #ここからデータベース検索（未実装）
        #年の数字のコンボボックス
        combobox_1 = ttk.Combobox(
        self.frame_1,
        state='normal',
        values=year,
        font=Font,
        width=5)
        combobox_1.current(0)
        if dyear != 0:
            combobox_1.set(dyear)
        combobox_1.place(x=50, y=10)

        label_1 = tk.Label(
        self.frame_1,
        text='年',
        bg=("#F5FEEE"),
        font=Font)
        label_1.place(x=130, y=10)
        
        #月の数字のコンボボックス
        combobox_2 = ttk.Combobox(
        self.frame_1,
        state='normal',
        values=higetu,
        font=Font,
        width=3)
        combobox_2.current(0)
        if dmonth != 0:
            combobox_2.set(dmonth)
        combobox_2.place(x=160, y=10)

        label_2 = tk.Label(
        self.frame_1,
        text='月',
        bg=("#F5FEEE"),
        font=Font)
        label_2.place(x=220, y=10)

        #日の数字のコンボボックス
        combobox_3 = ttk.Combobox(
        self.frame_1,
        state='normal',
        values=hiniti,
        font=Font,
        width=3)
        combobox_3.current(0)
        if dday != 0:
            combobox_3.set(dday)
        combobox_3.place(x=250, y=10)
            
        label_3 = tk.Label(
        self.frame_1,
        text='日',
        bg=("#F5FEEE"),
        font=Font)
        label_3.place(x=310, y=10)

        # リストボックスの作成
        listbox = tk.Listbox(self.frame_1, font=Font, height=10,width=40)
        listbox.place(x=50,y=50)
    
        # スクロールバーの作成
        scrollbar = tk.Scrollbar(self.frame_1)
        scrollbar.place(x=420,y=50)
        self.update()
        scrollbar = tk.Scrollbar(
        self.frame_1, width=20, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.place(x=420, y=50, height=listbox.winfo_height())
        # スクロールバーとリストボックスの連携
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)



        label_0 = tk.Label(
        self.frame_2,
        font=Fonta,
        bg=("#F5FEEE"),
        text="選択中"
        )
        label_0.place(x=50, y=10)

        self.label_date = tk.Label(
        self.frame_2,
        font=Fonta,
        bg=("#F5FEEE")
        )
        self.label_date.place(x=50, y=40)

        self.label_sche = tk.Label(
        self.frame_2,
        font=Fonta,
        bg=("#F5FEEE"),
        )
        self.label_sche.place(x=50, y=70)
        #入力ボックス
        #日付
        entry_date = tk.Entry(
        self.frame_2,
        font=Font,
        width=25)
        #entry_date.place(x=50, y=200)
        
        #年の数字のコンボボックス
        self.combobox_4 = ttk.Combobox(
        self.frame_2,
        state='normal',
        values=year,
        font=Font,
        width=5)
        self.combobox_4.current(0)
        self.combobox_4.place(x=40, y=200)

        label_4 = tk.Label(
        self.frame_2,
        text='年',
        bg=("#F5FEEE"),
        font=Font)
        label_4.place(x=110, y=200)
        
        #月の数字のコンボボックス
        self.combobox_5 = ttk.Combobox(
        self.frame_2,
        state='normal',
        values=higetu,
        font=Font,
        width=3)
        self.combobox_5.current(0)
        self.combobox_5.place(x=133, y=200)

        label_5 = tk.Label(
        self.frame_2,
        text='月',
        bg=("#F5FEEE"),
        font=Font)
        label_5.place(x=185, y=200)

        #日の数字のコンボボックス
        self.combobox_6 = ttk.Combobox(
        self.frame_2,
        state='normal',
        values=hiniti,
        font=Font,
        width=3)
        self.combobox_6.current(0)
        self.combobox_6.place(x=207, y=200)
            
        label_6 = tk.Label(
        self.frame_2,
        text='日',
        bg=("#F5FEEE"),
        font=Font)
        label_6.place(x=260, y=200)
        
        #スケジュール内容
        entry_sche = tk.Entry(
        self.frame_2,
        font=Font,
        width=25)
        entry_sche.place(x=40, y=230)

        
        label_7 = tk.Label(
        self.frame_2,
        text='──────────────────────────────────────────────────────',
        bg=("#F5FEEE"),
        font=Font)
        label_7.place(x=-10, y=140)

        
        label_8 = tk.Label(
        self.frame_2,
        text='ここから入力',
        bg=("#F5FEEE"),
        font=Font)
        label_8.place(x=20, y=160)


        #追加ボタン
        button_1 = tk.Button(
        self.frame_2,
        text='追加',
        width=6,
        font=Fontb,
        bg=("#D4D3D1"),
        command=lambda:self.setadd()) 
        button_1.place(x=300, y=190)

        #編集ボタン
        button_2 = tk.Button(
        self.frame_2,
        text='編集',
        width=6,
        font=Fontb,
        bg=("#D4D3D1"),
        command=lambda:self.setedit())
        button_2.place(x=300, y=230)

        #削除ボタン
        button_3 = tk.Button(
        self.frame_2,
        text='削除',
        width=6,
        font=Fontb,
        bg=("#FE807E"),
        command=lambda:self.setdelete())
        button_3.place(x=400, y=220)

        # ボタン
        button_close = tk.Button(self.frame_2, text="戻る",bg=("#93FDF8"), command=self.clearandraise)
        button_close.place(x=400,y=10)
        
        entry_date.insert(0, combobox_1.get() +'-'+ self.one(combobox_2) +'-'+ self.one(combobox_3))
        
        #リストボックスのクリックに対応
        listbox.bind('<Double-1>', self.on_listbox_select)#ダブルクリックじゃないと不具合でる
        #コンボボックス選択でリストボックス更新
        combobox_1.bind('<<ComboboxSelected>>', lambda e:self.update_listbox())
        combobox_2.bind('<<ComboboxSelected>>', lambda e:self.update_listbox())
        combobox_3.bind('<<ComboboxSelected>>', lambda e:self.update_listbox())

        # リストボックスを後ろに配置
        listbox.lower()

        self.update_listbox()

        self.frame_1.tkraise()

        self.protocol("WM_DELETE_WINDOW", self.close)
    
        # 日付が選択された時にリストボックスに対応するデータを表示する
            # 選択された年、月、日を取得
    def update_listbox(self):
        selected_year = combobox_1.get()
        selected_month = self.one(combobox_2)
        selected_day = self.one(combobox_3)

        # リストボックスをクリア
        listbox.delete(0, tk.END)

        # 選択された日付に対応するデータをリストボックスに追加
        date_key = (selected_year +'-'+ selected_month +'-'+ selected_day)
        r = self.master.search_a(date_key)
        if len(r) != 0: 
            for i in range(len(r)):
                l = "|".join(map(str,r[i]))
                listbox.insert(tk.END, l)
            listbox.insert(tk.END, "＋追加")
        else:
            listbox.insert(tk.END, "＋追加")
    
        # リストボックスで選択したアイテムをエントリに表示する処理
    def on_listbox_select(self, event): 
        self.label_date.config(text="日付："+
                                    combobox_1.get()+"年"#フレーム２のラベル更新
                                    +combobox_2.get()+"月"
                                    +combobox_3.get()+"日")
        self.frame_2.tkraise()#フレーム２に遷移
        selected_index = listbox.curselection()#選択したリストボックスのインデックス番号を取得
        self.l = "".join(map(str,listbox.get(selected_index)))#選択した項目を整形
        entry_sche.delete(0, tk.END)# 既存のテキストを削除
        entry_date.delete(0, tk.END)
        self.combobox_4.set(combobox_1.get())
        self.combobox_5.set(combobox_2.get())
        self.combobox_6.set(combobox_3.get())
        if listbox.get(selected_index) == "＋追加":
            self.label_sche.config(text="予定：追加してください")
        elif selected_index:
            entry_sche.insert(0, listbox.get(selected_index)) # 選択したアイテムを挿入 
            self.label_sche.config(text="予定："+self.l)

    def one(self, combo):#日が一桁だった場合の処理
        if int(combo.get()) < 10:
            return '0'+combo.get()#1を01にする
        else:
            return combo.get()
        
    def setadd(self):#アプリケーションクラスの追加関数を呼び出す
        #追加できない場合の処理
        if self.master.search_b(self.combobox_4.get()+'-'
                    +self.one(self.combobox_5)+'-'
                    +self.one(self.combobox_6),  
                            entry_sche.get() )!= 0:
            return messagebox.showwarning('!','同じ予定を入れないでください',parent=self)
        elif entry_sche.get() == "":
            return messagebox.showwarning('!','入力してください',parent=self)
        self.master.add(self.combobox_4.get()+'-'
                    +self.one(self.combobox_5)+'-'
                    +self.one(self.combobox_6), 
                    entry_sche.get())
        self.update_month_callback()
        self.after(100, self.update_listbox())

    def setedit(self):#アプリケーションクラスの編集関数を呼び出す
        #編集できない場合の処理
        if self.master.search_b(combobox_1.get()+'-'
                            +self.one(combobox_2)+'-'
                            +self.one(combobox_3), 
                            self.l )== 0:
            return messagebox.showwarning('!','編集できません',parent=self)
        elif entry_sche.get() == "":
            return messagebox.showwarning('!','入力してください',parent=self)
        self.master.edit(combobox_1.get()+'-'
                    +self.one(combobox_2)+'-'
                    +self.one(combobox_3),
                    self.l,
                    self.combobox_4.get()+'-'
                    +self.one(self.combobox_5)+'-'
                    +self.one(self.combobox_6),
                    entry_sche.get()
                    )
        self.update_month_callback()
        self.label_sche.config(text="選択中の予定 : "+ entry_sche.get())
        self.after(100, self.update_listbox())
    
    def setdelete(self):#アプリケーションクラスの削除関数を呼び出す
        #削除できない場合の処理
        if self.master.search_b(combobox_1.get()+'-'
                            +self.one(combobox_2)+'-'
                            +self.one(combobox_3), 
                            entry_sche.get()) == 0:
            return messagebox.showwarning('!','削除できません',parent=self)
        #削除する場合の警告
        kotae=messagebox.askyesno('警告','本当に削除しますか？',parent=self)
        if  kotae==True:
            self.master.delete(combobox_1.get()+'-'
                        +self.one(combobox_2)+'-'
                        +self.one(combobox_3), 
                        entry_sche.get())
            self.after(100, self.update_listbox())
            entry_sche.delete(0, tk.END)
            self.label_sche.config(text="選択した予定を削除しました")
            self.update_month_callback()
        


    def clearandraise(self):
        self.frame_1.tkraise()
        listbox.selection_clear(0, tk.END)

    def close(self):
        self.destroy()

    
    

# メインアプリケーションウィンドウ
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry("960x720")

        for row in range(1):
            self.grid_rowconfigure(row, weight=1)
        for col in range(1):
            self.grid_columnconfigure(col, weight=1)

        # ウィンドウのリサイズ不可にする
        self.resizable(False, False)  # 幅と高さ両方のリサイズを禁止

        # 各画面を管理するための辞書
        self.frames = {}

        #データベース接続とテーブル生成
        self.conn = sqlite3.connect('schedule.db')
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
            Date DATE NOT NULL,
            Schedule TEXT NOT NULL,
            PRIMARY KEY(Date, Schedule)
            );""")
        self.conn.commit()
        
        # フレーム切り替え用の関数
        self.switch_frame = self._switch_frame
        
        # 最初に表示するフレームの作成
        self.create_frame("HomeFrame")

    # フレームを作成して配置する関数
    def create_frame(self, frame_name):
        frame = None
        if frame_name == "HomeFrame":
            frame = HomeFrame(self, self.switch_frame)
        elif frame_name == "CalendarFrame":
            frame = CalendarFrame(self, self.switch_frame)

        
        if frame:
            # 既存のフレームがあれば非表示にする
            for f in self.frames.values():
                f.grid_forget()
            
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, rowspan=10, columnspan=10, sticky='nsew')

    # フレームを切り替える関数
    def _switch_frame(self, frame_name):
        self.create_frame(frame_name)

    #データベース
    #検索関数
    def search_a(self, date) :
        sql="SELECT Schedule FROM schedule WHERE Date=?"
        day=self.conn.execute(sql,(date,))
        r = day.fetchall()
        return r
    
    #既にデータベースに存在するか検索
    def search_b(self, date, sche) :
        sql="SELECT Schedule FROM schedule WHERE Date=? AND Schedule=?"
        day=self.conn.execute(sql,(date,sche,))
        r = day.fetchall()
        return len(r)#存在するスケジュールの個数を返す

    #追加関数
    def add(self, date, sche):
        sql = "INSERT INTO schedule(Date, Schedule) VALUES (?, ?)"
        self.conn.execute(sql, (date,sche,))
        self.conn.commit()
        print('追加')

    #編集関数
    def edit(self, beferdate, befersche, afterdate, aftersche):
        sql = "UPDATE schedule SET Date=?, Schedule =? WHERE Date=? AND Schedule=?"
        self.conn.execute(sql, (afterdate, aftersche, beferdate, befersche))
        self.conn.commit()
        print('編集')

    #削除関数
    def delete(self, date, sche):
        sql = "DELETE FROM schedule WHERE Date=? AND Schedule=?"
        self.conn.execute(sql, (date,sche,))
        self.conn.commit()
        print('削除')

# アプリケーション終了時にデータベース接続を閉じる
    def on_closing(self):
        self.conn.close()  # データベース接続を閉じる
        self.destroy()   # アプリケーションを終了

# アプリケーションを実行
if __name__ == "__main__":
    app = Application()
    app.title("スケジュールアプリ")
    app.protocol("WM_DELETE_WINDOW", app.on_closing)  # ウィンドウを閉じるときに on_closing を呼ぶ
    app.mainloop()