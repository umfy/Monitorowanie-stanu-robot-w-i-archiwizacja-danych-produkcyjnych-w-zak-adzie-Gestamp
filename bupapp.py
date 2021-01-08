import tkinter as tk
from tkinter import tix
from ftplib import FTP
import os
import os.path
import datetime
import time
import pandas as pd
import numpy as np
import io
import threading


df = pd.read_csv('FTP_IP2.csv', sep=';')
AL1 = pd.read_csv('ASStable441.csv', header=None)
AL2 = pd.read_csv('ASStable442.csv', header=None)
AL = pd.concat([AL1, AL2])

ASS_List1 = []
ASS_List2 = []
for i in range(len(AL1)):
    ASS_List1.append(list(AL1.iloc[i,:]))
for i in range(len(AL2)):
    ASS_List2.append(list(AL2.iloc[i,:]))

        
def init_date():
    my_date = datetime.date.today()
    year,week,day = my_date.isocalendar()
    save_dir = r'backup' + str(year) + 'WEEK' + str(week)
    return save_dir

def connect_ftp(ip):
    try:
        ftp = FTP(ip, timeout=1)
        ftp.login('STUDENCI1', '3344')
        ftp.pwd()
        print(ftp.getwelcome())
    except Exception as e:
        print(e)
        return False, e
    return True, ftp

def get_robot_info(location):
    robot = location.split('.')
    # eg. robot[0] == Lin1 ; robot[1] == R1
    #print(robot)
    LINE = robot[0]
    ROBOT = robot[1]
    Line_num = df.columns.get_loc(robot[0])
    Rob_num = Line_num + 1
    Ip_num = Line_num + 2 
    robots_col = df.iloc[:, Rob_num]
    index = robots_col.isin([robot[1]])
    IP = df.iloc[:, Ip_num][index]
    # remove index and spacebars
    IP = IP.to_string(index=False).replace(' ', '')
    print('Laczenie z ', LINE, ROBOT, IP)
    return LINE, ROBOT, IP

######################################################################################################
class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.makeCheckList(ASS_List=ASS_List1)
        self.makeCheckList2(ASS_List=ASS_List2)
        self.cl.pack()
        self.location = ''
        self.LT = tk.Label(leftFrame, text=0)
        self.LT.pack(side='bottom')
        self.initial_threads = threading.active_count()
        self.LT.after(1000, self.refresh_LT)
    def create_widgets(self):

        #RADIOBUTTONS
        #initialise variables for 2 groups of radiobuttons
        self.var1 = tk.IntVar()
        self.var2 = tk.IntVar()
        self.var1.set(0)
        self.var2.set(0)

        self.A1 = tk.Radiobutton(leftFrame, text='NETWORK 1', variable=self.var1, value=0, command=self.choose_n1)
        self.A1.pack(side = 'top')
        self.A2 = tk.Radiobutton(leftFrame, text='NETWORK 2', variable=self.var1, value=1, command=self.choose_n2)
        self.A2.pack(side = 'top')
        
        self.B3 = tk.Radiobutton(rightFrame, text='Pobierz cmos', variable=self.var2, value=1)
        self.B3.pack()
        self.B2 = tk.Radiobutton(rightFrame, text='Pobierz pliki  ', variable=self.var2, value=2)
        self.B2.pack()
        self.B1 = tk.Radiobutton(rightFrame, text='Check connec', variable=self.var2, value=0)
        self.B1.pack()

        #button
        self.select_all = tk.Button(topFrame, text='Select All', command=self.press_select_all)
        self.select_all.pack(side='bottom')

        self.test = tk.Button(rightFrame, text='Run', command=self.press_test)
        self.test.pack(side='bottom')

        #text
        # Create text widget and specify size. 
        self.T = tk.Text(rightBotFrame, height = 20, width = 50, highlightcolor='blue')
        #output = buffer.getvalue()
        self.T.pack(side='bottom', pady=5)
        #self.T.insert(tk.END, robot_list) 

        # error text
        self.TE = tk.Text(leftBotFrame, height = 20, width =50, fg='red', highlightcolor='red')
        self.TE.pack(side='bottom', pady=5)

        #label & button
        self.L1 = tk.Label(leftBotFrame, text='          NOT OK', font='Helvetica 18 bold')
        self.L1.pack(side='left')
        self.B1 = tk.Button(leftBotFrame, text='save log', command=self.press_log_errors)
        self.B1.pack(side='right')

        self.L2 = tk.Label(rightBotFrame, text='          OK', font='Helvetica 18 bold' )
        self.L2.pack(side='left')
        self.B2 = tk.Button(rightBotFrame, text='save log', command=self.press_log)
        self.B2.pack(side='right')

        #self.threads_running = tk.IntVar()
        #self.LT = tk.Label(leftFrame, textvariable=self.threads_running)
        #self.threads_running.set(threading.active_count())
        #self.LT.pack(side='bottom')


    def refresh_LT(self):
        self.LT.configure(text='Aktywne połączenia: %i' %(threading.active_count() - self.initial_threads))
        self.LT.after(1000, self.refresh_LT)


    def press_log_errors(self):
        with open(save_dir + '//' + str(datetime.date.today()) +'_error_log.txt', 'a') as f:
            f.write(self.TE.get('1.0', 'end'))
        self.TE.delete('1.0', 'end')

    def press_log(self):
        with open(save_dir + '//' + str(datetime.date.today()) +'_log.txt', 'a') as f:
            f.write(self.T.get('1.0', 'end'))
        self.T.delete('1.0', 'end')


    # RadioButtons LEFT
    def choose_n1(self):
        self.cl2.pack_forget()
        self.cl.pack()
        
    def choose_n2(self):
        self.cl.pack_forget()
        self.cl2.pack()
        
    # CHECKLIST

    def makeCheckList(self, ASS_List):
        self.cl = tix.CheckList(topFrame, browsecmd=self.selectItem, width=200, height=250,
                                options='hlist.columns 1', highlightthickness=1, highlightcolor='#B7D9ED')
        #self.cl.pack()
        self.cl.hlist.config(bg='white', bd=0, selectmode='none', selectbackground='white',
                                selectforeground='black', drawbranch=True, pady=1)

        for line in ASS_List:
            self.cl.hlist.add(line[0], text=line[0])
            self.cl.setstatus(line[0], 'off')
            for robot in df.loc[:,line[1]].dropna():
                self.cl.hlist.add(str(line[0]) + '.' + str(robot), text=robot)
                self.cl.setstatus(str(line[0]) + '.' + str(robot), 'off')
                
        self.cl.autosetmode()

    def makeCheckList2(self, ASS_List):
        self.cl2 = tix.CheckList(topFrame, browsecmd=self.selectItem, width=200, height=250,
                                options='hlist.columns 1', highlightthickness=1, highlightcolor='#B7D9ED')
        #self.cl.pack()
        self.cl2.hlist.config(bg='white', bd=0, selectmode='none', selectbackground='white',
                                selectforeground='black', drawbranch=True, pady=1)

        for line in ASS_List:
            self.cl2.hlist.add(line[0], text=line[0])
            self.cl2.setstatus(line[0], 'off')
            for robot in df.loc[:,line[1]].dropna():
                self.cl2.hlist.add(str(line[0]) + '.' + str(robot), text=robot)
                self.cl2.setstatus(str(line[0]) + '.' + str(robot), 'off')
                
        self.cl2.autosetmode()

    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
    def check_connection(self):
        if self.location not in (list(AL.iloc[:, 0])):
            LINE, ROBOT, IP = get_robot_info(self.location)
            ftp_status, ftp = connect_ftp(IP)
            if ftp_status == True:
                print(f'CONNECTED: {LINE}/{ROBOT} ({IP})')
                self.T.insert(tk.END,f'CONNECTED: {LINE}/{ROBOT} ({IP})\n')
                ftp.quit()
            else:
                print(f'FTP ERROR: {ftp} {LINE}/{ROBOT} ({IP})')
                self.TE.insert(tk.END, f'FTP ERROR: {ftp} {LINE}/{ROBOT} ({IP})\n')

    def get_cmos(self):
        loc = self.location
        if loc not in (list(AL.iloc[:, 0])):
            LINE, ROBOT, IP = get_robot_info(loc)

            save_dir_full = os.path.join(save_dir, LINE, ROBOT)
            if not(os.path.exists(save_dir_full +'/'+'cmosbk.bin')):
                try:
                    os.makedirs(save_dir_full)
                except:
                    #print('katalog juz istnieje')
                    pass
                ftp_status, ftp = connect_ftp(IP)
                if ftp_status == True:
                    try:
                        ftp.cwd('ROBOT/')
                        ftp.cwd('/spdrv')
                    except Exception as e:
                        self.TE.insert(tk.END, f'CWD ERROR: {e} {LINE}/{ROBOT} ({IP})\n')
                        print(f'CWD ERROR: {e} {LINE}/{ROBOT} ({IP})')
                        return -1
                    with open(save_dir_full + '//' + 'cmosbk.bin', 'wb') as lf:
                        try:
                            ftp.retrbinary('RETR ' + 'cmosbk.bin', lf.write)
                            self.T.insert(tk.END, (f'SAVED  ON: {save_dir_full}\n'))
                            print(f'SAVED  ON: {save_dir_full}')
                        except Exception as e:
                            self.TE.insert(tk.END, f'CMOSBK.BIN ERROR: {e} {LINE}/{ROBOT} ({IP})\n')
                            print(f'CMOSBK.BIN ERROR: {e} {LINE}/{ROBOT} ({IP})')
                    ftp.quit()
                else:
                    self.TE.insert(tk.END, f'FTP ERROR: {ftp} {LINE}/{ROBOT} ({IP})\n')
                    print(f'FTP ERROR: {ftp} {LINE}/{ROBOT} ({IP})')
            else:
                self.T.insert(tk.END, f'BACKUP EXISTS: {LINE}/{ROBOT} ({IP})\n')
                print(f'BACKUP EXISTS: {LINE}/{ROBOT} ({IP})')

    def get_files(self):
        loc = self.location
        if loc not in (list(AL.iloc[:, 0])):
            LINE, ROBOT, IP = get_robot_info(loc)

            save_dir_full = os.path.join(save_dir, LINE, ROBOT)
            if not(os.path.exists(save_dir_full +'/'+'LOG')):
                ftp_status, ftp = connect_ftp(IP)
                if ftp_status == True:
                    try:
                        ftp.cwd('ROBOT/')
                    except Exception as e:
                        self.TE.insert(tk.END, f'CWD ERROR: {e} {LINE}/{ROBOT} ({IP})\n')
                        print(f'CWD ERROR: {e} {LINE}/{ROBOT} ({IP})')
                        return -1                        
                    Folder_List = ftp.nlst()
                    for folder in Folder_List:
                        if not(os.path.exists(save_dir_full +'/'+folder)):
                            try:
                                os.makedirs(save_dir_full +'/'+folder)
                            except:
                                #print('katalog juz istnieje')
                                pass
                        ftp.cwd(folder)
                        filenames = ftp.nlst() # get filenames within the directory
                        #print('...pobieranie folderu ', folder)
                        for filename in filenames:
                            local_filename = os.path.join(save_dir_full +'/'+folder+'/'+ filename)
                            file = open(local_filename, 'wb')
                            try:
                                ftp.retrbinary('RETR '+ filename, file.write)
                            except Exception as e:
                                #self.TE.insert(tk.END, f'DIR ERROR: {e} {LINE}/{ROBOT} ({IP})\n')
                                print(f'DIR ERROR: {e} {LINE}/{ROBOT} ({IP}) : {filename}')
                                
                            file.close()
                        ftp.cwd('..')
                    #handle cases when downloading files is blocked:

                    #good route:
                    self.T.insert(tk.END, f'SAVED  ON: {save_dir_full}\n')
                    print(f'SAVED ON: {save_dir_full}')
                    ftp.quit()
                else:
                    self.TE.insert(tk.END, f'FTP ERROR: {ftp} {LINE}/{ROBOT} ({IP})\n')
                    print(f'FTP ERROR: {ftp} {LINE}/{ROBOT} ({IP})')
            else:
                self.T.insert(tk.END, f'FILES EXISTS: {LINE}/{ROBOT} ({IP})\n')
                print(f'FILES EXISTS: {LINE}/{ROBOT} ({IP})')

    def selectItem(self, item):
        if self.cl.winfo_ismapped():
            for line in (ASS_List1):
                if item == line[0]:
                    for robot in df.loc[:,line[1]].dropna():
                        if self.cl.getstatus(item) == 'on':
                            self.cl.setstatus(str(line[0]) + '.' + str(robot), 'on')
                            container.add(str(line[0]) + '.' + str(robot))
                        if self.cl.getstatus(item) == 'off':
                            self.cl.setstatus(str(line[0]) + '.' + str(robot), 'off')
                            container.discard(str(line[0]) + '.' + str(robot))
            # Single clicks:
            if self.cl.getstatus(item) == 'on':
                container.add(item)
            if self.cl.getstatus(item) == 'off':
                container.discard(item)
                
        if self.cl2.winfo_ismapped():
            for line in (ASS_List2):
                if item == line[0]:
                    for robot in df.loc[:,line[1]].dropna():
                        if self.cl2.getstatus(item) == 'on':
                            self.cl2.setstatus(str(line[0]) + '.' + str(robot), 'on')
                            container.add(str(line[0]) + '.' + str(robot))
                        if self.cl2.getstatus(item) == 'off':
                            self.cl2.setstatus(str(line[0]) + '.' + str(robot), 'off')
                            container.discard(str(line[0]) + '.' + str(robot))
            # Single clicks:                            
            if self.cl2.getstatus(item) == 'on':
                container.add(item)
            if self.cl2.getstatus(item) == 'off':
                container.discard(item)
        
    def press_select_all(self):
        #check if cl widget is visible
        if self.cl.winfo_ismapped():
            for line in ASS_List1:
                for robot in df.loc[:,line[1]].dropna():
                    self.cl.setstatus(str(line[0]), 'on')                       # check all lines
                    self.selectItem(str(line[0]))
        if self.cl2.winfo_ismapped():
            for line in ASS_List2:
                for robot in df.loc[:,line[1]].dropna():
                    self.cl2.setstatus(str(line[0]), 'on')
                    self.selectItem(str(line[0]))                     
        

    def press_test(self):
        robot_list = list(container)
        # CHECK CONNECTION
        if self.var2.get() == 0:
            for location in robot_list:
                self.location = location
                thread = threading.Thread(target=self.check_connection)
                thread.start()

        # GET CMOS     
        if self.var2.get() == 1:
            for location in robot_list:
                self.location = location
                thread = threading.Thread(target=self.get_cmos)
                thread.start()

        # GET FILES   
        if self.var2.get() == 2:
            for location in robot_list:
                self.location = location
                thread = threading.Thread(target=self.get_files)
                thread.start()
                time.sleep(0.01)
                
save_dir = init_date()
container = set()

buffer = io.StringIO()
output = buffer.getvalue()
print (save_dir)
root = tix.Tk()
root.title('BACKUP MANAGER')

topFrame = tk.Frame(root)
topFrame.pack(side='top')

bottomFrame = tk.Frame(root)
bottomFrame.pack(side='bottom')

leftBotFrame = tk.Frame(bottomFrame)
leftBotFrame.pack(side='left')

rightBotFrame = tk.Frame(bottomFrame)
rightBotFrame.pack(side='right')

leftFrame = tk.Frame(topFrame)
leftFrame.pack(side='left')

rightFrame = tk.Frame(topFrame)
rightFrame.pack(side='right')

root.geometry('1000x800')

app = Application(master=root)


app.mainloop()
