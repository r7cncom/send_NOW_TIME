# UART Tx/Rx demo
import tkinter as tk
from tkinter import ttk  # from tkinter import ttk      #加上ttk美化界面
import serial
import threading
import time
import datetime as dt

# import time  # 引入time模块

# A simple Information Window  消息提示窗口
class InformWindow:
    def __init__(self, informStr):
        self.window = tk.Tk()
        self.window.title("提示")
        self.window.geometry("200x50")
        label = tk.Label(self.window, text=informStr)
        buttonOK = tk.Button(self.window, text="OK", command=self.processButtonOK)
        label.pack(side=tk.TOP)
        buttonOK.pack(side=tk.BOTTOM)
        self.window.mainloop()

    def processButtonOK(self):
        self.window.destroy()


# 主显示GUI界面窗口
class mainGUI:
    def __init__(self):
        window = tk.Tk()
        window.title("时间校准上位机程序")
        self.uartState = False  # is uart open or not
        self.bytes485ToSend = {}
        self.i = 0

        # a frame contains COM's information, and start/stop button
        frame_COMinf = tk.Frame(
            window)  # Frame：框架，用来承载放置其他GUI元素，就是一个容器，是一个在 Windows 上分离小区域的部件, 它能将 Windows 分成不同的区,然后存放不同的其他部件
        frame_COMinf.grid(row=1, column=1)
        labelCOM = tk.Label(frame_COMinf, text="串口号: ")  # 第4步，在图形界面上创建一个标签用以显示内容并放置
        self.COM = tk.StringVar(value="COM3")  # 将label标签的内容设置为字符类型，用var来接收hit_me函数的传出内容用以显示在标签上
        # ertryCOM = tk.Entry(frame_COMinf, textvariable=self.COM) #Entry是tkinter类中提供的的一个单行文本输入域，用来输入显示一行文本，收集键盘输入(类似 HTML 中的 text)。
        comboCOM = ttk.Combobox(frame_COMinf, width=17, textvariable=self.COM)
        comboCOM["values"] = ("COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10")
        comboCOM["state"] = "readonly"
        labelCOM.grid(row=1, column=1, padx=5,
                      pady=3)  # row 为行，colum 为列，padx 就是单元格左右间距，pady 就是单元格上下间距，ipadx是单元格内部元素与单元格的左右间距，ipady是单元格内部元素与单元格的上下间距。
        # ertryCOM.grid(row=1, column=2, padx=5, pady=3)#row 为行，colum 为列，padx 就是单元格左右间距，pady 就是单元格上下间距，ipadx是单元格内部元素与单元格的左右间距，ipady是单元格内部元素与单元格的上下间距。
        comboCOM.grid(row=1, column=2, padx=5,
                      pady=3)  # row 为行，colum 为列，padx 就是单元格左右间距，pady 就是单元格上下间距，ipadx是单元格内部元素与单元格的左右间距，ipady是单元格内部元素与单元格的上下间距。

        labelBaudrate = tk.Label(frame_COMinf, text="波特率: ")  # 第4步，在图形界面上创建一个标签用以显示内容并放置
        self.Baudrate = tk.IntVar(value=115200)  # 定义var1整型变量用来存放选择行为返回值
        comboBaudrate = ttk.Combobox(frame_COMinf, width=17, textvariable=self.Baudrate)
        # ertryBaudrate = tk.Entry(frame_COMinf, textvariable=self.Baudrate)
        comboBaudrate["values"] = ("9600", "115200")
        comboBaudrate["state"] = "readonly"
        labelBaudrate.grid(row=1, column=3, padx=5, pady=3)
        # ertryBaudrate.grid(row=1, column=4, padx=5, pady=3)
        comboBaudrate.grid(row=1, column=4, padx=5, pady=3)

        labelParity = tk.Label(frame_COMinf, text="校验位: ")
        self.Parity = tk.StringVar(value="NONE")
        comboParity = ttk.Combobox(frame_COMinf, width=17, textvariable=self.Parity)
        comboParity["values"] = ("NONE", "ODD", "EVEN", "MARK", "SPACE")
        comboParity["state"] = "readonly"
        labelParity.grid(row=2, column=1, padx=5, pady=3)
        comboParity.grid(row=2, column=2, padx=5, pady=3)

        labelStopbits = tk.Label(frame_COMinf, text="停止位: ")
        self.Stopbits = tk.StringVar(value="1")
        comboStopbits = ttk.Combobox(frame_COMinf, width=17, textvariable=self.Stopbits)
        comboStopbits["values"] = ("1", "1.5", "2")
        comboStopbits["state"] = "readonly"
        labelStopbits.grid(row=2, column=3, padx=5, pady=3)
        comboStopbits.grid(row=2, column=4, padx=5, pady=3)

        self.buttonSS = tk.Button(frame_COMinf, text="打开串口", command=self.processButtonSS)
        self.buttonSS.grid(row=3, column=4, padx=5, pady=3, sticky=tk.E)
        #####################################################################################################################
        self.AD1 = tk.StringVar(value=" ")  # 将label标签的内容设置为字符类型，用var来接收hit_me函数的传出内容用以显示在标签上
        labelAD1 = tk.Label(frame_COMinf, text="当前时间: ")
        labelAD1.grid(row=4, column=1, padx=3, pady=2)
        ertryAD1 = tk.Entry(frame_COMinf,
                            textvariable=self.AD1)  # Entry是tkinter类中提供的的一个单行文本输入域，用来输入显示一行文本，收集键盘输入(类似 HTML 中的 text)。
        ertryAD1.grid(row=4, column=2, padx=3,
                      pady=2)  # row 为行，colum 为列，padx 就是单元格左右间距，pady 就是单元格上下间距，ipadx是单元格内部元素与单元格的左右间距，ipady是单元格内部元素与单元格的上下间距。

        self.AD2 = tk.StringVar(value=" ")  # 将label标签的内容设置为字符类型，用var来接收hit_me函数的传出内容用以显示在标签上
        labelAD2 = tk.Label(frame_COMinf, text="发送格式: ")
        labelAD2.grid(row=4, column=3, padx=3, pady=2)
        ertryAD2 = tk.Entry(frame_COMinf,
                            textvariable=self.AD2)  # Entry是tkinter类中提供的的一个单行文本输入域，用来输入显示一行文本，收集键盘输入(类似 HTML 中的 text)。
        ertryAD2.grid(row=4, column=4, padx=3,
                      pady=2)  # row 为行，colum 为列，padx 就是单元格左右间距，pady 就是单元格上下间距，ipadx是单元格内部元素与单元格的左右间距，ipady是单元格内部元素与单元格的上下间距。

        self.button_ok = tk.Button(frame_COMinf, text='开始校准', width=8, command=self.ok)  # .place(x=320, y=80)
        self.button_ok.grid(row=8, column=4, padx=5, pady=10, sticky=tk.E)
        #self.button_cancel = tk.Button(frame_COMinf, text='结束校准', width=8, command=self.cancel)  # .place(x=320, y=100)
        #self.button_cancel.grid(row=13, column=4, padx=5, pady=10, sticky=tk.E)
        ##############################################################################################################
        # serial object
        self.ser = serial.Serial()
        # serial read threading
        self.ReadUARTThread = threading.Thread(target=self.ReadUART)
        #self.ReadUARTThread.start()
        #self.sendUARTThsendAD = threading.Thread(target=self.SendUARTAD)
        #self.sendUARTThsendAD.start()
        self.ReadUARTThread.start()

        ################################################################################################################
        frameRecv = tk.Frame(window)  # frameRecv的父节点是window
        frameRecv.grid(row=2, column=1)  # 整个窗口用grid布局，接收文本框在第二列
        labelOutText = tk.Label(frameRecv, text="接收数据:")
        labelOutText.grid(row=1, column=1, padx=3, pady=2, sticky=tk.W)
        frameRecvSon = tk.Frame(frameRecv)
        frameRecvSon.grid(row=2, column=1)
        scrollbarRecv = tk.Scrollbar(frameRecvSon)
        scrollbarRecv.pack(side=tk.RIGHT, fill=tk.Y)  # 滑动条只能用pack布局
        self.OutputText = tk.Text(frameRecvSon, wrap=tk.WORD, width=60, height=8, yscrollcommand=scrollbarRecv.set)
        self.OutputText.pack()

        frameTrans = tk.Frame(window)
        frameTrans.grid(row=3, column=1)
        labelInText = tk.Label(frameTrans, text="发送数据:")
        labelInText.grid(row=1, column=1, padx=3, pady=2, sticky=tk.W)
        frameTransSon = tk.Frame(frameTrans)
        frameTransSon.grid(row=2, column=1)
        scrollbarTrans = tk.Scrollbar(frameTransSon)
        scrollbarTrans.pack(side=tk.RIGHT, fill=tk.Y)
        self.InputText = tk.Text(frameTransSon, wrap=tk.WORD, width=60, height=2, yscrollcommand=scrollbarTrans.set)
        self.InputText.pack()

        self.buttonSend = tk.Button(frameTrans, text="Send", command=self.processButtonSend)
        self.buttonSend.grid(row=3, column=1, padx=5, pady=3, sticky=tk.E)
        window.mainloop()

    def ok(self):
        if (self.uartState):
            try:
                ZT = "AT+"
                zh =ZT+dt.datetime.strftime(dt.datetime.now(), '%Y%m%d%H%M%S')
                self.ser.write(zh.encode("ascii"))
            except:
                infromStr = "发送失败"
                InformWindow(infromStr)
        else:
            infromStr = "串口未连接!，请连接串口"
            InformWindow(infromStr)
    #def cancel(self):
        #self.bytesToSend = bytes.fromhex('CE CE BB BB')
        #@self.ReadUARTThread.stop()

    # 按键处理SS
    def processButtonSS(self):
        # print(self.Parity.get())
        if (self.uartState):
            self.ser.close()
            self.buttonSS["text"] = "打开串口"
            self.uartState = False
        else:
            # restart serial port
            self.ser.port = self.COM.get()
            self.ser.baudrate = self.Baudrate.get()

            strParity = self.Parity.get()
            if (strParity == "NONE"):
                self.ser.parity = serial.PARITY_NONE;
            elif (strParity == "ODD"):
                self.ser.parity = serial.PARITY_ODD;
            elif (strParity == "EVEN"):
                self.ser.parity = serial.PARITY_EVEN;
            elif (strParity == "MARK"):
                self.ser.parity = serial.PARITY_MARK;
            elif (strParity == "SPACE"):
                self.ser.parity = serial.PARITY_SPACE;

            strStopbits = self.Stopbits.get()
            if (strStopbits == "1"):
                self.ser.stopbits = serial.STOPBITS_ONE;
            elif (strStopbits == "1.5"):
                self.ser.stopbits = serial.STOPBITS_ONE_POINT_FIVE;
            elif (strStopbits == "2"):
                self.ser.stopbits = serial.STOPBITS_TWO;

            try:  # 打开接口
                self.ser.open()
                self.ser.timeout = 0.01
                self.ser.writeTimeout = 0.01
            except:  # 如果打不开接口提示
                infromStr = "不能打开串口 " + self.ser.port
                InformWindow(infromStr)

            if (self.ser.isOpen()):  # open success接口打开成功提示
                self.buttonSS["text"] = "关闭串口"
                self.uartState = True

    def processButtonSend(self):  # 发送按钮处理函数
        if (self.uartState):
            strToSend = self.InputText.get(1.0, tk.END)
            bytesToSend = strToSend[0:-1].encode(encoding='ascii')
            try:
                self.ser.write(bytesToSend)
            except:
                infromStr = "发送失败"
                InformWindow(infromStr)
        else:
            infromStr = "串口未连接!，请连接串口"
            InformWindow(infromStr)

    def ReadUART(self):  # 读取串口数据函数
            while True:
                xh = dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d %H:%M:%S')
                yh = dt.datetime.strftime(dt.datetime.now(), '%Y%m%d%H%M%S')
                self.AD1.set(xh)
                self.AD2.set(yh)
                if (self.uartState):
                    try:
                        ch = self.ser.read().decode(encoding='ascii')
                        print(ch, end='')
                        self.OutputText.insert(tk.END, ch)
                    except:
                        infromStr = "Something wrong in receiving."
                        InformWindow(infromStr)
                        self.ser.close()  # close the serial when catch exception
                        self.buttonSS["text"] = "Start"
                        self.uartState = False


mainGUI()
