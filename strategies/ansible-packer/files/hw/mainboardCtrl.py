### This is the class for the Mainboard peripheral functions. This code can be re-used across Telephone entry versions (touch and non-touch) and future products. Most of the functions read or send data to the AUX microcontroller on board via SPI.  Additional functions may be redundant (camera, audio) since the client application will include some of those.
###


import spidev
#import cv2
#import numpy as np
import os
import io
import time
from time import sleep
import sounddevice as sd
import wave
#import urllib.request
#from scipy.io.wavfile import write
#import pyaudio
#from playsound import playsound
import RPi.GPIO as GPIO
import codecs
#import LUSO11_updates_16v2
#from picamera.array import PiRGBArray
#from picamera import PiCamera

class Mainboard():
    def __init__(self, type, standalone, bus=1, device=0, channel=0):
        self.sendData_counter = 0
        self.index = 0
        self.type = type
        self. standalone = standalone
        self.bus, self.device, self.channel = bus, device, channel
        self.spi = spidev.SpiDev()
        self.accelDetected = False
        self.code = 0
        #the data structure for all data recieved from the AUX micro
        self.data = {
            "NONE":[],
            "TMPR":[],
            "RELH":[],
            "ACLX":[],
            "ACLY":[],
            "ACLZ":[],
            "SETX":[],
            "SETY":[],
            "SETZ":[],
            "AMLR":[],
            "SETL":[],
            "12V1":[],
            "12V2":[],
            "FANC":[],
            "LEDB":[],
            "RLY1":[],
            "RLY2":[],
            "RLY3":[],
            "RRL1":[],
            "RRL2":[],
            "MRST":[],
            "16VL":[],
            "VBAT":[],
            "SWIE":[],
            "WIE1":[],
            "WIE2":[],
            "RTCG":[],
            "RTCA":[],
            "RTCY":[],
            "RTCM":[],
            "RTCD":[],
            "RTCH":[],
            "RTCN":[],
            "RTCS":[],
            "BUZZ":[],
            "GSWR":[],
            "MOTC":[],
            "AACK":[],
            "NOMO":[],
            "TAMO":[],
            "TAMC":[],
            "KEYC":[],
            "KEYO":[],
            "EXMO":[],
            "LPLS":[],
            "BPLS":[],
            "LDON":[],
            "LDOF":[],
            "SDIM":[],
            "CONF":[],
            "RDCF":[],
            "EPRM":[],
            "NACK":[]
            }
        self.data_lengths = {
        #subtract 5 from the total length since we've already read the first 5 bytes
            "NONE":0,
            "TMPR":4,
            "RELH":4,
            "ACLX":4,
            "ACLY":4,
            "ACLZ":4,
            "SETX":2,
            "SETY":2,
            "SETZ":2,
            "AMLR":4,
            "SETL":2,
            "12V1":2,
            "12V2":2,
            "FANC":2,
            "LEDB":2,
            "RLY1":2,
            "RLY2":2,
            "RLY3":2,
            "RRL1":2,
            "RRL2":2,
            "MRST":2,
            "16VL":2,
            "VBAT":2,
            "SWIE":2,
            "WIE1":6,
            "WIE2":6,
            "RTCG":4,
            "RTCA":2,
            "RTCY":2,
            "RTCM":2,
            "RTCD":2,
            "RTCH":2,
            "RTCN":2,
            "RTCS":2,
            "BUZZ":2,
            "GSWR":4,
            "MOTC":2,
            "AACK":2,
            "NOMO":2,
            "TAMO":2,
            "TAMC":2,
            "KEYC":2,
            "KEYO":2,
            "EXMO":2,
            "LPLS":2,
            "BPLS":2,
            "LDON":2,
            "LDOF":2,
            "SDIM":3,
            "CONF":2,
            "RDCF":6,
            "EPRM":66,
            "NACK":6 
        }
        try:
            self.spi.close()
            self.spi.open(self.bus, self.device)
            self.spi.max_speed_hz = 50000
            self.spi.mode = 0
        except:
            print("ERROR SPI not initialized")

    def resetAUX(self):
        #reset AUX upon initialization
        self.AUX_reset_pin = 24
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.AUX_reset_pin,GPIO.OUT)
        time.sleep(1)
        GPIO.output(self.AUX_reset_pin, 1)
        time.sleep(3)
        GPIO.output(self.AUX_reset_pin, 0)
        time.sleep(3)

    def sendData(self,data_in, field1bit = -999, field8bit = -999, field16bit = -999, field32bit = -999):
        #this function takes a string of ASCII characters in and sends the data as hex over SPI
        self.sendData_counter = self.sendData_counter + 1
        print("SENDING DATA. Package#", self.sendData_counter, " | data: ", data_in,field1bit,field8bit,field16bit,field32bit)
        msg = []
        #loop through each ASCII character
        for i in (data_in):
            #msg.append("0x" + codecs.encode(i, 'hex_codec'))
            msg.append("0x" + i.encode("utf-8").hex()) #append each hex value to a list
        #the data in the 5th byte should be input as binary, but since it's more convenient to have the user input all characters, byte 5 or byte 5 and 6 need to be converted back to a binary value and sent as binary values
        if (field1bit != -999):
            #msg.append("0x" + codecs.encode(i, 'hex_codec'))
            msg.append("0x" + chr(field1bit).encode("utf-8").hex())
        if (field8bit != -999):
            temp = field8bit | 256 #bitwise or with 1 followed by 8 zeros
            temp1 = "0x%X" %temp #convert to hex
            temp2 = temp1[3:] #grab the second two bytes
            #raw_input("stop here")
            msg.append(temp2) #add to message
        if (field16bit != -999):
            temp = field16bit | 65536 #bitwise or with 1 followed by 16 zeros
            temp1 = "0x%X" %temp #convert to hex
            temp2 = temp1[3:5] #grab the first two bytes
            temp3 = temp1[5:] #grab the second two bytes
            msg.append(temp2) #add to message
            msg.append(temp3)
        if (field32bit != -999):
            temp = field32bit | 4294967296 #bitwise or with 1 followed by 32 zeros
            temp = temp << 1
            temp1 = "0x%X" %temp #convert to hex
            temp2 = temp1[3:5] #grab the first set of bytes
            temp3 = temp1[5:7] #grab the second set of bytes
            temp4 = temp1[7:9] #grab the second set of bytes
            temp5 = temp1[9:11] #grab the second set of bytes
            msg.append(temp2) #add to message
            msg.append(temp3)
            msg.append(temp4)
            msg.append(temp5)

        #each msg needs a carriage return and a line feed after each command
        msg.append('0x0D')
        msg.append('0x0A')
        #print(msg)
        for j in msg:
            hex_int = int(j,16)
            self.spi.writebytes([hex_int])
        return 1

    def readData(self,num_bytes):
        #helper function
        read_msg = []
        for i in range(0,num_bytes):
            read_msg.append(self.spi.readbytes(1))
            time.sleep(0.01)
        #print(read_msg)
        return read_msg

    def getData(self):
        if self.standalone:
            return '0x1111222233334444556677'
        else:
            self.sendData('>GDAT')
            time.sleep(0.1)
            resp = self.data['NONE']
            return resp

    def getTemperature(self): #celsius
        if self.standalone:
            return 37.2
        else:
            self.sendData('>TMPR')
            time.sleep(0.2)
            resp = self.data['TMPR']
            val = (resp[0][0] << 8) + resp[1][0]
            #temp = (((val-3686)*(-45-125))/(409-3686))+125
            calc = ((val - 409) * 0.05187672)-45
            return round(calc,1)

    def getHumidity(self): #percentage
        if self.standalone:
            return 51
        else:
            self.sendData('>RELH')
            time.sleep(0.2)
            resp = self.data['RELH']
            val = (resp[0][0] << 8) + resp[1][0]
            #temp = (((val-3686)*(-45-125))/(409-3686))+125
            calc = ((val - 409) * 0.03051572)
            return round(calc,1)

    def getAccelX(self): #0 to 2 G
        if self.standalone:
            return 1.1
        else:
            self.sendData('>ACLX')
            time.sleep(0.1)
            resp = self.data['ACLX']
            print (resp)
            val = (resp[0][0] << 8) + resp[1][0]
            #temp = (((val-3686)*(-45-125))/(409-3686))+125
            calc = ((val *2) / 65535) #65535 = hex 
            return round(calc,2)

    def getAccelY(self): #0 to 2 G
        if self.standalone:
            return 1.4
        else:
            self.sendData('>ACLY')
            time.sleep(0.1)
            resp = self.data['ACLY']
            print (resp)
            val = (resp[0][0] << 8) + resp[1][0]
            #temp = (((val-3686)*(-45-125))/(409-3686))+125
            calc = ((val *2) / 65535)
            return round(calc,2)

    def getAccelZ(self): #0 to 2 G
        if self.standalone:
            return 1.5
        else:
            self.sendData('>ACLZ')
            time.sleep(0.1)
            resp = self.data['ACLZ']
            print (resp)
            val = (resp[0][0] << 8) + resp[1][0]
            #temp = (((val-3686)*(-45-125))/(409-3686))+125
            calc = ((val *2) / 65535)
            return round(calc,2)

    def setAccelXThreshold(self, threshold): #0 to 2 G
        #validate input is within range:
        if ((threshold < 0) | (threshold > 2)):
            return 0
        if self.standalone:
                print ("Accel X  Threshold is set to:",threshold)
        else:
            #convert threshold to scaled value
            value = int(threshold / 0.0078125)
            self.sendData('>SETX', field8bit = value)
            time.sleep(0.1)
            resp = self.data['SETX']
            text = ""
            for i in resp:
                text = text + chr(i[0])
            if (text == "\r\n"): #we really only care if the response contains SETZ
                return threshold
            else:
                return 0

    def setAccelYThreshold(self, threshold): #0 to 2 G
        #validate input is within range:
        if ((threshold < 0) | (threshold > 2)):
            return 0
        if self.standalone:
                print ("Accel Y  Threshold is set to:",threshold)
        else:
            #convert threshold to scaled value
            value = int(threshold / 0.0078125)
            self.sendData('>SETY', field8bit = value)
            time.sleep(0.1)
            resp = self.data['SETY']
            text = ""
            for i in resp:
                text = text + chr(i[0])
            if (text == "\r\n"): #we really only care if the response contains SETY
                return threshold
            else:
                return 0

    def setAccelZThreshold(self, threshold):
        #validate input is within range:
        if ((threshold < 0) | (threshold > 2)):
            return 0
        if self.standalone:
                print ("Accel Z  Threshold is set to:",threshold)
        else:
            #convert threshold to scaled value
            value = int(threshold / 0.0078125)
            self.sendData('>SETZ', field8bit = value)
            time.sleep(0.1)
            resp = self.data['SETZ']
            text = ""
            for i in resp:
                text = text + chr(i[0])
            if (text == "\r\n"): #we really only care if the response contains SETZ
                return threshold
            else:
                return 0

    def getAmbientLight(self): #returns value 0 to 100
        if self.standalone:
            return 51
        else:
            self.sendData('>AMLR')
            time.sleep(0.2)
            resp = self.data['AMLR']
            print (resp)
            val = (resp[0][0] << 8) + resp[1][0]
            print(val)
            calc = ((val )*(100/(4500)))
            return round(calc,1)

    def setAmbientLightThreshold(self, threshold):
        #validate input is within range:
        if ((threshold < 0) | (threshold > 100)):
            return 0
        if self.standalone:
                print ("Ambient Light Threshold is set to:",threshold)
        else:
            #convert threshold to scaled value
            value = int(threshold / 0.0222)
            self.sendData('>SETL', field16bit = value)
            time.sleep(0.1)
            resp = self.data['SETL']
            text = ""
            for i in resp:
                text = text + chr(i[0])
            print(text)
            if (text == "\r\n"): #we really only care if the response contains SETZ
                return threshold
            else:
                return 0
########################################################
#FOR USE LATER WHEN THE FIELDBIT IS SET IN THE PIC18 FIRMWARE
#    def BPLS(self,value):
#        if value == "on":
#            self.sendData('>BPLS')
#            time.sleep(0.1)
#        if value == "off":
#            self.sendData('>BPLS')
#            time.sleep(0.1)
#        resp = self.data['BPLS']
#        return resp
#
#    def LDOF(self,value):
#        if value == "on":
#            self.sendData('>LDOF',field1bit=1)
#            time.sleep(0.1)
#        if value == "off":
#            self.sendData('>LDOF',field1bit=0)
#            time.sleep(0.1)
#        resp = self.data['LDOF']
#        return resp 
#
#    def LDON(self,value):
#        if value == "on":
#            self.sendData('>LDON',field1bit=1)
#            time.sleep(0.1)
#        if value == "off":
#            self.sendData('>LDON',field1bit=0)
#            time.sleep(0.1)
#        resp = self.data['LDON']
#        return resp
#
#    def LPLS(self,value):
#        if value == "on":
#            self.sendData('>LPLS',field1bit=1)
#            time.sleep(0.1)
#        if value == "off":
#            self.sendData('>LPLS',field1bit=0)
#            time.sleep(0.1)
#        resp = self.data['LPLS']
#        return resp
########################################################
#FOR TESTING PURPOSES
    def LPLS(self):
        self.LDON()
        time.sleep(2)
        self.LDOF()

    def BPLS(self):
        self.sendData('>BPLS')
        time.sleep(0.3)
        resp = self.data['BPLS']
    
    def LDON(self):
        self.sendData('>LDON')
        time.sleep(0.3)
        resp = self.data['LDON']

    def LDOF(self):
        self.sendData('>LDOF')
        time.sleep(0.3)
        resp = self.data['LDOF']
##########################################################

    def setfanCtrl(self,value):
        if self.standalone:
            resp = value
            #if self.debugmode:
            print ("The Fan is set to:",value,'%') #%value
        else:
            if value == "on":
                self.sendData('>FANC',field1bit=1)
                time.sleep(0.1)
            if value == "off":
                self.sendData('>FANC',field1bit=0)
                time.sleep(0.1)
        resp = self.data['FANC']
        return resp

    def ledBrightnessCtrl(self, value): #value is 0 to 100
        if self.standalone:
            print ("LED Brightness is set to:",value,'%')
        else:
            resp = self.spi.xfer2([0x3E, 0x41434C59, 0x0D, 0x0A])
            return resp
        return True


    def relayCtrl(self, value=None, relayPosition=1):
        if value == "on":
            self.sendData(f'>RLY{relayPosition}',field1bit=1)
            time.sleep(0.1)
            resp = self.data[f'RLY{relayPosition}']
        elif value == "off":
            self.sendData(f'>RLY{relayPosition}',field1bit=0)
            time.sleep(0.1)
            resp = self.data[f'RLY{relayPosition}']
        else:
            resp = 'WARNING: no value set'
        print(resp)
        return resp

    def relay1Ctrl(self, value):
        if self.standalone:
            return True
        else:
            if value == "on":
                self.sendData('>RLY1',field1bit=1)
                time.sleep(0.1)
                resp = self.data['RLY1']
            if value == "off":
                self.sendData('>RLY1',field1bit=0)
                time.sleep(0.1)
                resp = self.data['RLY1']
            return resp

    def relay2Ctrl(self, value):
        if self.standalone:
            return True
        else:
            if value == "on":
                self.sendData('>RLY2',field1bit=1)
                time.sleep(0.1)
                resp = self.data['RLY2']
            if value == "off":
                self.sendData('>RLY2',field1bit=0)
                time.sleep(0.1)
                resp = self.data['RLY2']
            return resp

    def relay3Ctrl(self, value):
        if self.standalone:
            return True
        else:
            if value == "on":
                self.sendData('>RLY3',field1bit=1)
                time.sleep(0.1)
                resp = self.data['RLY3']
            if value == "off":
                self.sendData('>RLY3',field1bit=0)
                time.sleep(0.1)
                resp = self.data['RLY3']
            return resp
    #This command restars the board using the PIC18
    def sendMRST(self):
            self.sendData('>RLY4',field1bit=1)
            time.sleep(0.1)
            return

    def get16VLevel(self): #returns value in voltage
        if self.standalone:
            return 16.7
        else:
            self.sendData('>16VL')
            resp = self.data['16VL']
            return resp

    def getVbatLevel(self):
        if self.standalone:
            return 13.2
        else:
            self.sendData['>VBAT']
            resp = self.data['VBAT']
            return resp

    def readWiegand1Interrupt(self):
        resp = self.readData(6)
        err = 0
        if (resp[0][0] > 0):
            err = 1
        print (resp)
        val = (resp[1][0] << 16) + (resp[2][0] << 8) + resp[3][0]
        print (val)
        val = val >> 1  #remove parity bit
        val = val & 65535  #get 16 bit code (the MSB are facility codes, not needed now)
        return err,val

    def parseWiegand1Input(self):
        data = self.data['WIE1']
        val = (data[1][0] << 16) + (data[2][0] << 8) + data[3][0]
        val = val >> 1  #remove parity bit
        val = val & 65535  #get 16 bit code (the MSB are facility codes, not needed now)
        return val

    def readWiegand1Input(self):
        resp = self.readData(11)
        print (resp)
        val = (resp[6][0] << 16) + (resp[7][0] << 8) + resp[8][0]
        print (val)
        val = val >> 1  #remove parity bit
        val = val & 65535  #get 16 bit code (the MSB are facility codes, not needed now)
        return val


    def getWiegand1Input(self):
        if self.standalone:
            return 11223344
        else:
            self.sendData('>WIE1')
            time.sleep(0.3)
            resp = self.data["WIE1"]
            val = (resp[1][0] << 16) + (resp[2][0] << 8) + resp[3][0]
            return val

    def getWiegand2Input(self):
        if self.standalone:
            return 55667788
        else:
            resp = self.spi.xfer2([0x3E, 0x41434C59, 0x0D, 0x0A])
            return resp

    def sendWiegandOutput(self,code):
        if self.standalone:
            return "<SWIE"
        else:
            self.sendData('>SWIE', field32bit=code)
            return self.data['SWIE']

    def speakerCtrl(self):
        if self.standalone:
            mixer.init()
            mixer.music.load('testaudio.wav')
            mixer.music.play()
            #sleep(0.05)
            #mixer.init()
            #mixer.music.load("youGotmail.wav")
            #mixer.music.play()

            return True

    def micCtrl(self):
        if self.standalone:
            fs = 44100 #sample rate
            seconds = 3
            timestr = time.strftime("%m-%d-%Y %H:%M:%S")
            filename = (str(timestr)+'.wav')
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()
            #write('output.wav',fs,myrecording)
            write(filename,fs,myrecording)
            path_exists = os.path.exists(filename)
            return path_exists
            #return True

    def getCameraFrame(self):
        if self.standalone:
            timestr = time.strftime("%m-%d-%Y %H:%M:%S")
            filename = (str(timestr)+'.png')
            camera = cv2.VideoCapture(0)
            for i in range(10):
                    return_value, image = camera.read()
                    cv2.imwrite(filename,image)
            path_exists = os.path.exists(filename)
            return path_exists

    def getCameraVideo(self):
        if self.standalone:
            cap = cv2.VideoCapture(0)
            timestr = time.strftime("%m-%d-%Y %H:%M:%S")
            video_file = (str(timestr)+'.avi')
            stop = time.time() +2
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(video_file,fourcc, 20.0, (640,480))
            while(cap.isOpened()):
                ret, frame = cap.read()
                if ret==True:
                    out.write(frame)
                    cv2.imshow('frame',frame)
                    if time.time() > stop:
                        break
                else:
                    break
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            video_file_exists = os.path.exists(video_file)
            return video_file_exists


    def screenBrightnessCtrl(self):
        if self.standalone:
            return True

    def getMotion(self):
        if self.standalone:
            return 1

    def ethSwitchCtrl(self):
        if self.standalone:
            host = 'https://google.com'
            try:
                urllib.request.urlopen(host)
                return True
            except:
                return False

    def getAUXAnalogInput(self):
        if self.standalone:
            return 0.0334

    def getAUXDigitalInput(self):
        if self.standalone:
            return  1

    def setAUXDigitalOutput(self):
        if self.standalone:
            return True

            resp = value
            #if self.debugmode:
            print ("12V Port 1 is: ",value,'%')
        else:
            if value == "on":
                self.sendData('>12V1',field1bit=1)
                time.sleep(0.3)
            if value == "off":
                self.sendData('>12V1',field1bit=0)
                time.sleep(0.3)
        resp = self.data['12V2']   
        return resp

    def MOTC(self,value):
        if self.standalone:
            resp = value
            #if self.debugmode:
            #print ("12V Port 2 is: ",value,'%')
        else:
            if value == 1:
                self.sendData('>MOTC',field1bit=1)
                time.sleep(0.3)
            if value == 0:
                self.sendData('>MOTC',field1bit=0)
                time.sleep(0.3)
        resp = self.data['MOTC']   
        return resp

    def buzzCtrl(self, value):
        if value == 1:
            self.sendData('>BUZZ',field1bit=1)
            time.sleep(0.3)
        if value == 0:
            self.sendData('>BUZZ',field1bit=0)
            time.sleep(0.3)        
        resp = self.data['BUZZ']
    #Works for the fan in shcematic activates J6
    def twelveVOut1Ctrl(self,value):
        if self.standalone:
            resp = value
            #if self.debugmode:
            print ("12V Port 1 is: ",value,'%')
        else:
            if value == "off":
                self.sendData('>12V1',field1bit=1)
                time.sleep(0.3)
            if value == "on":
                self.sendData('>12V1',field1bit=0)
                time.sleep(0.3)
        resp = self.data['12V1']   
        return resp

    def twelveVOut2Ctrl(self,value):
        if self.standalone:
            resp = value
            #if self.debugmode:
            print ("12V Port 2 is: ",value,'%')
        else:
            if value == "off":
                self.sendData('>12V2',field1bit=1)
                time.sleep(0.3)
            if value == "on":
                self.sendData('>12V2',field1bit=0)
                time.sleep(0.3)
        resp = self.data['12V2']   
        return resp

    def getAuxSwVersion(self):
        if self.standalone:
            return "1.0"
        else:
            self.sendData('>GSWR')
            time.sleep(0.1)
            resp = self.data['GSWR']
            return ("%s.%s" %(resp[0][0], resp[1][0]))

    """"added Joes PIC18 commands"""
        
    def readerPulseLed(self):
        self.sendData('>LPLS')
        time.sleep(0.3)
        resp = self.data['LPLS']
    
    def readerPulseBuzzer(self):
        self.sendData('>BPLS')
        time.sleep(0.3)
        resp = self.data['BPLS']
    
    def readerLedOn(self):
        self.sendData('>LDON')
        time.sleep(0.3)
        resp = self.data['LDON']

    def readerLedOff(self):
        self.sendData('>LDOF')
        time.sleep(0.3)
        resp = self.data['LDOF']

    def getRTCData(self):
        if self.standalone:
            return 2012231359
        else:
            self.sendData('>RTCG')
            time.sleep(0.3)
            resp = self.data['RTCG']
            return resp
    #This function doesnt do anything with the data given
    def setRTCData(self, year, month, day, hour, minutes, seconds):
        if self.standalone:
            return 2008190531
        else:
            self.sendData('>RTCS', fieldbit32 = 0) 
            return resp
    
    def setRTCyear(self, value):
        if self.standalone:
            return 2008190531
        else:
            self.sendData('>RTCY', field8bit = value)
            resp = self.data['RTCY']
            return resp
    
    def setRTCmonth(self, value):
        if self.standalone:
            return 2008190531
        else:
            self.sendData('>RTCM', field8bit = value)
            resp = self.data['RTCM']
            return resp
    
    def setRTCday(self, value):
        if self.standalone:
            return 2008190531
        else:
            self.sendData('>RTCD', field8bit = value)
            resp = self.data['RTCD']
            return resp

    def setRTChour(self, value):
        if self.standalone:
            return 2008190531
        else:
            self.sendData('>RTCH', field8bit = value)
            resp = self.data['RTCH']
            return resp
    
    def setRTCminute(self, value):
        if self.standalone:
            return 2008190531
        else:
            self.sendData('>RTCN', field8bit = value)
            resp = self.data['RTCN']
            return resp
    
    def setRTCseconds(self, value):
        if self.standalone:
            return 2008190531
        else:
            self.sendData('>RTCS', field8bit = value)
            resp = self.data['RTCS']
            return resp
    
    def setScreenPwm(self, value):
        self.sendData('>SDIM', field8bit = value)
       

    def setPicConf(self, value):
        #this function takes a hex input as a string ,e.g., "FFFF"
        value = int(value,16)
        print(value)
        self.sendData('>CONF', field32bit = value)

    def getPicConf(self):
        self.sendData('>RDCF')
        time.sleep(1)
        resp = self.data['RDCF']
        print(resp)
        val = (resp[1][0] << 24) + (resp[2][0] << 16) + (resp[3][0] << 8) + resp[4][0]
        val = val & 4294967295
        return val

    def picBoardReset(self):
        self.sendData('>MRST')
        time.sleep(1)
       
    def readEeprom(self):
        self.sendData('>EPRM')
        time.sleep(1)
        resp_dec = self.data['EPRM']
        resp_hex = []
        for i in range(0,len(resp_dec)):
            #resp_hex.append(int(str(resp_dec[i][0]),16))  #since the PIC keeps the eeprom record in hex that's the best way to read the eeprom
            whole = hex(resp_dec[i][0])
            parts = whole.split("x")
            val = parts[1]
            resp_hex.append(val)  #since the PIC keeps the eeprom record in hex that's the best way to read the eeprom
        print(resp_hex)
        with open('/data/EEPROM_database.txt','a+') as file: #Write EEPROM TO MEMORY
            file.write(f'{resp_hex}\n')
        debug = True
        if (debug == True):
            #pretty prints the eeprom output
            counter = 0
            for i in range (0,8):
                for j in range (0,8):
                    print("%s" %resp_hex[counter], end=" ")
                    counter = counter + 1
                print("")

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.spi.close()
