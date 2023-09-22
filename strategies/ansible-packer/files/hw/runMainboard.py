import datetime
import mainboardCtrl
import time
import RPi.GPIO as GPIO
import asyncio
import websockets
from jsonrpcserver import method, async_dispatch as dispatch, Success
from jsonrpcclient.clients.websockets_client import WebSocketsClient
import json
import database
import os
import threading
#import updates
import LUSO11_updates_16v2


def str2bool(string):
    print("string: %s ..." %string)
    if (string == "True" or string == "true"):
        return True
    if  (string == "False" or string == "false"):
        return False
    else:
        raise Exception("Invalid parameter: %s , must be True or False string" %string)

def highPriorityMailbox(channel):
    print("HIGH PRIORITY CALLBACK DETECTED")
    text = ""
    #get the first 6 bytes to determine the type of data sent
    msg = ""
    resp = board.readData(5)
    #print(resp)
    for i in resp:
        text = text + chr(i[0])
    for key in board.data_lengths:
        if key in text:
            #if key in the text lookup the length of reads required and read that amount
            board.data[key] = board.readData(board.data_lengths[key])
            msg = key
    print ("MSG: %s" %msg)
    if (msg == "RRL1"):
        print(board.data[msg][0][0])
        update_relay1_status(board.data[msg][0][0])
    if (msg == "RRL2"):
        print(board.data[msg][0][0])
        update_relay2_status(board.data[msg][0][0])
    if (msg == 'WIE1'):
        #print("WIEGAND1 DETECTED")
        code = board.parseWiegand1Input()

        print (code)
        message = json.dumps({"method": "facility", "params": [1, code]})
        print(message)

        # if (wiring_scheme == "relay"):
        loop = asyncio.new_event_loop() #the reader already repeats the code, so this is only required when it is wired relay
        asyncio.set_event_loop(loop)  #setup async event loop
        loop.run_until_complete(sendMessage(message)) #call sendMessage async function , runs until complete
        loop.close()
        # else:
        #    pass
    if (msg == "SWIE"):
        #print("WIEGAND CODE SENT")
        pass

    if (msg == "ACLX"):
        #print("ACCELEROMETER DETECTED")
        database.logAccelEvent(datetime.datetime.now(), "TRIGGERED")
        #If accelerometer is detected it takes 3 pictures and saves them to camera_images_accelerometer folder
        update_accelerometer.take_pictures()
        pass


def lowPriorityMailbox(channel):
    #print("low priority callback")
    text = ""
    #get the first 6 bytes to determine the type of data sent
    msg = ""
    resp = board.readData(5)
    print(resp)
    for i in resp:
        text = text + chr(i[0])
    for key in board.data_lengths:
        if key in text:
            #if key in the text lookup the length of reads required and read that amount
            board.data[key] = board.readData(board.data_lengths[key])
            msg = key
    print ("MSG: %s" %msg)
        #This is used for the Tamper switch part of Updates1.6.2
        #Print and log eeprom memory
    if (msg == "EPRM"):
        try:
            board.readEeprom()
            database.logEEPROM(datetime.datetime.now(), board.readEeprom())
        except:
            database.logEEPROM(datetime.datetime.now(), "FAILED EEPROM READ")
        with open("EEPROM_memory.txt","a") as file:
            file.write(board.readEeprom())
        pass
    if (msg == "TAMO"):
        print("FRONT PANEL OPEN")
        database.logTamperData(datetime.datetime.now(), "FRONT PANEL OPEN")
        pass
    if (msg == "TAMC"):
        print("FRONT PANEL CLOSED")
        database.logTamperData(datetime.datetime.now(), "FRONT PANEL CLOSED")
        pass
    #This is used for the Key switch part of Updates1.6.2
    if (msg == "KEYC"):
        #update_key_switch.KEYC_logic()
        pass
    if (msg == "KEYO"):
        #update_key_switch.KEYO_logic()
        pass
    #This controls the screen dimming behaviour
    if (msg == "NOMO"):
        update_motion.NOMO_()
        pass
    if (msg == "EXMO"):
        update_motion.EXMO_()
        pass
    if (msg == "AACK"):
        #SEND NACK
        update_keepalive.sendNACK()
        update_keepalive.log_WD("AACK_received")
        database.logPIC18Data(datetime.datetime.now(), "OK", "WAIT")
        pass

relay1_status = None
relay2_status = None
def update_relay1_status(new_status):
    global relay1_status
    #print("Passed in status:", new_status)
    #print("Old relay1_status:", relay1_status)
    relay1_status = new_status
    #print("New relay1_status:", relay1_status)

def update_relay2_status(new_status):
    global relay2_status
    #print("Passed in status:", new_status)
    #print("Old relay2_status:", relay2_status)
    relay2_status = new_status
    #print("New relay2_status:", relay2_status)

async def sendMessage(message):
    #for each client added to CLIENTS in the main async method, send the message
    await asyncio.gather(
            *[ws.send(message) for ws in CLIENTS],
            return_exceptions = False,
            )
    #await asyncio.sleep(2)

@method
async def enable_relay(relayPosition=1):
    print(f'opening relay {relayPosition}')
    board.relayCtrl(value="on", relayPosition=relayPosition)
    time.sleep(relay1_striketime)
    print(f'closing relay {relayPosition}')
    board.relayCtrl(value="off", relayPosition=relayPosition)
    time.sleep(relay2_delay)
    print(f'done with relay {relayPosition}')
    return 1

@method
async def enable_relay1():
    if (relay1_enable):
        board.relay1Ctrl("on")
        time.sleep(relay1_striketime)
        board.relay1Ctrl("off")
    if (relay1_enable and relay2_enable):
        time.sleep(relay2_delay)
    if (relay2_enable):
        board.relay2Ctrl("on")
        time.sleep(relay2_striketime)
        board.relay2Ctrl("off")
    return 1

@method
async def gate_open():
    if (relay1_enable):
        board.relay1Ctrl("on")
    if (relay1_enable and relay2_enable):
        time.sleep(relay2_delay)
    if (relay2_enable):
        board.relay2Ctrl("on")
    return 1

@method
async def gate_close():
    if (relay1_enable):
        board.relay1Ctrl("off")
    if (relay1_enable and relay2_enable):
        time.sleep(relay2_delay)
    if (relay2_enable):
        board.relay2Ctrl("off")
    return 1

@method
async def gate_status():
    board.sendData(">RRL1")
    time.sleep(0.5)
    board.sendData(">RRL1")
    time.sleep(1)
    board.sendData(">RRL2")
    time.sleep(0.5)
    board.sendData(">RRL2")
    time.sleep(1)

    print("relay1_enable: ", relay1_enable)
    print("relay2_enable: ", relay2_enable)
    print("relay1_status: ", relay1_status)
    print("relay2_status: ", relay2_status)

    if relay1_enable and relay2_enable:
        if relay1_status == 1 or relay2_status == 1:
            return "open"
        elif relay1_status == 0 and relay2_status == 0:
            return "closed"
        else:
            return "unknown"
    elif relay1_enable:
        if relay1_status == 0:
            return "closed"
        elif relay1_status == 1:
            return "open"
        else:
            return "unknown"
    elif relay2_enable:
        if relay2_status == 0:
            return "closed"
        elif relay2_status == 1:
            return "open"
        else:
            return "unknown"
    else:
        return "relays not enabled"

   # if (gate_status_var == "open"):
   #     return "open"
   # else:
   #     return "closed"


@method
async def wiegand(sitecode, usercode):
    print("sitecode: %s , usercode: %s" %(sitecode,usercode))
    board.sendWiegandOutput(code=usercode)
    board.sendWiegandOutput(code=usercode)
    board.sendWiegandOutput(code=usercode)
    board.sendWiegandOutput(code=usercode)
    return 1

@method
async def handle_user_code(userCode, shouldSendWiegand, shouldEnableRelay1, shouldEnableRelay2):
    print("handle_user_code", userCode, shouldSendWiegand, shouldEnableRelay1, shouldEnableRelay2, flush=True)
    if shouldSendWiegand:
        await wiegand(0, userCode)
        print('handle_user_code: wiegand done', flush=True)
    if shouldEnableRelay1:
        await enable_relay(1)
        print('handle_user_code: enable_relay 1 done', flush=True)
    if shouldEnableRelay2:
        await enable_relay(2)
        print('handle_user_code: enable_relay 2 done', flush=True)
    return Success(1)

async def main(websocket, path):
    #adds client websocket objects to the set
    CLIENTS.add(websocket)
    #listen for incoming requests , e.g., "enable_relay1"
    response = await dispatch(await websocket.recv())
    if response:
        await websocket.send(str(response))


#Create default value for gateStatus
#gateStatus = None


#Create objects for every updated class in LUSO11 1.6v2
update_fan= LUSO11_updates_16v2.fan_updates_()
update_power=LUSO11_updates_16v2.power_()
update_setup=LUSO11_updates_16v2.setup_()
update_ethernet=LUSO11_updates_16v2.ethernet_()
update_hardware=LUSO11_updates_16v2.hardware_()
update_keepalive=LUSO11_updates_16v2.keep_alive()
update_status_monitoring=LUSO11_updates_16v2.status_monitoring_()
update_key_switch= LUSO11_updates_16v2.key_switch()
update_motion= LUSO11_updates_16v2.Motion_()
update_accelerometer= LUSO11_updates_16v2.accelerometer_()

relay1_enable = str2bool(os.getenv('RELAY1_ENABLED'))
relay1_striketime = int(os.getenv('RELAY1_STRIKETIME'))
relay2_delay = int(os.getenv('RELAY2_DELAY'))
relay2_enable = str2bool(os.getenv('RELAY2_ENABLED'))
relay2_striketime = int(os.getenv('RELAY2_STRIKETIME'))
#wiring_scheme = (os.getenv('WIRING_SCHEME'))
print("RELAY1_ENABLED: %s" %relay1_enable)
print("RELAY1_STRIKETIME: %s" %relay1_striketime)
print("RELAY2_DELAY: %s" %relay2_delay)
print("RELAY2_ENABLED: %s" %relay2_enable)
print("RELAY2_STRIKETIME: %s" %relay2_striketime)

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

CLIENTS = set()
strikeTime = 3  #in seconds


#Main Function
board = mainboardCtrl.Mainboard(type='telephone-entry-non-touch', standalone=False)

#do a reset of the AUX and power
board.resetAUX()
time.sleep(2)

#setup the mailbox flag callback
GPIO.add_event_detect(27, GPIO.RISING, callback=highPriorityMailbox)
GPIO.add_event_detect(0, GPIO.RISING, callback=lowPriorityMailbox)
time.sleep(2)
#print(board.getTemperature())
#print("AUX Firmware Version: %s" %board.getAuxSwVersion())
time.sleep(2)

#set the relays to default disabled position
#if (relay1_enable):
#    board.relay1Ctrl(relay1_disactivate)
#time.sleep(2)
#if (relay2_enable):
#    board.relay2Ctrl(relay2_disactivate)

#print(board.getPicConf())

#board.sendWiegandOutput(code=65535)



#board.picBoardReset()


#board.picBoardReset()
#board.readEeprom()

time.sleep(1)
#board.setPicConf("ABCDABCD")

#time.sleep(1)

#print(board.getPicConf())
#time.sleep(1)
#board.setPicConf("0")

#time.sleep(1)

#print(board.getPicConf())
#board.setPicConf("FFFFFFFF")

#time.sleep(1)

#print(board.getPicConf())
#board.setPicConf("0")


#board.readerPulseLed()
#time.sleep(2)
#board.readerLedOff()
#time.sleep(2)
#board.readerLedOn()
#time.sleep(5)
#board.readerLedOff()
#time.sleep(2)
#board.readerPulseBuzzer()

#time.sleep(1)
#board.setRTCyear(21)
#time.sleep(1)
#board.setRTCmonth(8)
#time.sleep(1)
#board.setRTCday(20)
#time.sleep(1)
#board.setRTChour(5)
#time.sleep(1)
#board.setRTCminute(13)
#time.sleep(1)
#board.setRTCseconds(20)

##uncomment these two sections to get the time
#while(1):
#    print(board.getRTCData())
#    time.sleep(0.7)

#for i in range(0,20):
#    print(board.getRTCData())
#    time.sleep(0.5)

##basic PWM test
#while(1):
#    board.setScreenPwm(100)
#    print('100%')
#    time.sleep(3)
#    board.setScreenPwm(50)
#    print('50%')
#    time.sleep(3)
#    board.setScreenPwm(0)
#    print('0%')
#    time.sleep(3)

#while(1):
#    print('waiting')
#    time.sleep(10)


#start monitoring temperature and controling fan
fan=threading.Thread(target=update_fan.main,args=(),daemon=True)
#start monitoring ethernet and loggin the information into Hardware_log.txt as 'succesfull PING'
eth=threading.Thread(target=update_ethernet.main,args=(),daemon=True)
#start monitoring hardware and loggin the information into Hardware_log.txt as necessary for each camera, keypad, PIC18, screen type
hrdw=threading.Thread(target=update_hardware.main,args=(),daemon=True)
#AACK NACK between PIC18 and RPCM, will log 2 kinds of data:
staying_alive=threading.Thread(target=update_keepalive.main,args=(),daemon=True)
#All resets by power cycle are saved to reset_log.txt, tagged with the reason and time of occurrance
#Doctor checkup for the voltage,temp,etc
monitor_status=threading.Thread(target=update_status_monitoring.main,args=(),daemon=True)

#Start threads for different functions
fan.start()
eth.start()
hrdw.start()
staying_alive.start()
monitor_status.start()

### Test code ###
#
#def relay_status_print():
#    while True:
#        time.sleep(5)
#        print("relay1 status:",relay1_status)
#        print("relay2 status:",relay2_status)
#        print("gate_status_var:",gate_status_var)
#
#
#monitor_relay_status=threading.Thread(target=relay_status_print,args=(),daemon=True)
#monitor_relay_status.start()
##


#start the web server and run forever >>NOTHING UNDER THIS WILL EVER RUN!!!!<<<<<<<<<<<<
start_server = websockets.serve(main, "localhost", 3012)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
