import serial
import time
import signal
import threading
import sys
import msvcrt
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QWaitCondition
from PyQt5.QtCore import QMutex
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot




exitThread      = False
line = [] 

form_class = uic.loadUiType("Pyserial_QT.ui")[0]

class Thread(QThread):
    
    set_txt = pyqtSignal('QString')
    
    def __init__(self , ser_port, t_browser):
        QThread.__init__(self)
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self.ser = ser_port
        
        print("QThread Initialized!!")
        
    def __del__(self):
        self.wait()

    def run(self):
        print("QThread Start!!")
        global exitThread
        line = []
        while not exitThread:
            self.mutex.lock()
            for c in self.ser.read():
                if(self.ser.inWaiting() != 0): #exist waiting data 
                     if(ord(c) == 13):
                        self.set_txt.emit('\n')
                     elif(ord(c)== 10):
                        pass
                     else:
                        self.set_txt.emit(c) #self.textBrowser.insertPlainText(c)
                else:
                     pass
            self.mutex.unlock()
        print("QThread finish!!")



class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self.pushConnectButton.clicked.connect(self.Connect_btn_clicked)
        self.pushDisConnectButton.clicked.connect(self.Disconnect_btn_clicked)
        self.pushSendButton.clicked.connect(self.Send_btn_clicked)
        self.pushTestButton.clicked.connect(self.Test_btn_clicked)
        self.pushDisConnectButton.setEnabled(False)
        self.pushConnectButton.setEnabled(True)
        
        #define connection
        self.PORT = 'COM3'
        self.BAUD = 115200

        self.ser = []
        self.rthread = []
        self.wthread = []
        

        self.scrollBar = self.textBrowser.verticalScrollBar()
        
        self.before_pos = self.textBrowser.textCursor().position()
        
    

    def handler(signum, frame):
        print("handler !!!")
        global exitThread
        exitThread = True

    #wait writing on console (not using)
    def writeThread(self,ser):
        global line
        global exitThread

        while not exitThread:
             time.sleep(0.05)
             try:
                  ch=msvcrt.getch()
                  ser.write(ch)
                  sys.stdout.write(ch) #print on console
                  
             except KeyboardInterrupt:
                  print("key inter")
                  exitThread = True
    
    def Connect_btn_clicked(self):
        print("Connect")
        
        self.BAUD = int(self.comboBox_Baud.currentText())
        self.PORT = self.comboBox_Port.currentText()
        print("%s %s" % (self.BAUD, self.PORT))
        self.ser = serial.Serial(self.PORT, self.BAUD)

        #QThread
        self.rthread = Thread(self.ser, self.textBrowser)
        self.rthread.start()
        self.rthread.set_txt.connect(self.Insert_text_browser) #Signal slot (inser&cursor move)
        
        #write Thread on console
        #self.wthread = threading.Thread(target=self.writeThread, args=(self.ser,))
        #self.wthread.start()
        
        self.pushDisConnectButton.setEnabled(True)
        self.pushConnectButton.setEnabled(False)

    
    def Disconnect_btn_clicked(self):
        print("Disconnect")
        global exitThread
        exitThread = True #Qthread Exit (exit reading thread)
        self.ser.__exit__()
        
        self.pushDisConnectButton.setEnabled(False)
        self.pushConnectButton.setEnabled(True)
    
    def Send_btn_clicked(self):
        send_txt = self.lineEdit_Msg.text() + '\n'
        send_txt = send_txt.encode("utf-8")
        self.ser.write(send_txt)

        self.lineEdit_Msg.clear()
        
    
    def Test_btn_clicked(self):
        #Test button
        pass
        
    def Insert_text_browser(self, str):
        self.textBrowser.insertPlainText(str)
        self.scrollBar.setValue(self.scrollBar.maximum())
        
        
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

