import serial
import time
import signal
import threading
import sys
import msvcrt


line = [] 

#define connection
PORT = 'COM3' 
BAUD = 115200 

exitThread      = False

#
def handler(signum, frame):
     print("handler !!!")
     global exitThread
     exitThread = True

#wait read
def readThread(ser):
    global line
    global exitThread

    while not exitThread:
        for c in ser.read():
            if(ser.inWaiting() != 0): #exist waiting data 
                 if(ord(c) == 13):
                    print("")
                    del line[:]
                 elif(ord(c)== 10):
                    pass
                 else:
                    line.append(c)
                    sys.stdout.write(c) #print on console

            else:
                 pass

#wait writing
def writeThread(ser):
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
         
        

if __name__ == "__main__":

    ser = serial.Serial(PORT, BAUD)

    rthread = threading.Thread(target=readThread, args=(ser,))
    rthread.start()

    wthread = threading.Thread(target=writeThread, args=(ser,))
    wthread.start()
    
    
