import datetime
import logging
import os
import platform  # For getting the operating system name
import re
import shutil
import subprocess  # For executing a shell command
import time
from datetime import date
import database

import RPi.GPIO as GPIO
import boto3
from botocore.exceptions import ClientError

import mainboardCtrl


class setup_:
    # move monitoring_configuration file to non-volatile partition
    def __init__(self):
        try:
            shutil.move('./monitoring_configuration.txt', '/data/monitoring_configuration.txt')
            shutil.move('./reset_log.txt', '/data/reset_log.txt')
        except:
            return print('Data logged in non-volatile partition')

    """Looks for information in /data/monitoring_configuration.txt"""

    def Screen_PWM_setting(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[0].split('=')
        # return the number as a int
        return int(r[1])

    def Wiegand_repeat(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[1].split('=')
        # return the number as a int
        return int(r[1])

    def Watchdog_enable(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[2].split('=')
        # return the number as a int
        return int(r[1])

    def Auto_motion_enabled(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[3].split('=')
        # return the number as a int
        return int(r[1])

    def Watchdog_reset_limit_time(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[4].split('=')
        # return the number as a int
        return int(r[1])

    def Watchdog_NACK_send_time(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[5].split('=')
        # return the number as a int
        return int(r[1])

    def Watchdog_reset_block_time(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[6].split('=')
        # return the number as a int
        return int(r[1])

    def fan_temp_threshold(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[7].split('=')
        # return the number as a int
        return int(r[1])

    def hardware_check_timer(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[8].split('=')
        # return the number as a int
        return int(r[1])

    def check_ethernet_connection(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[9].split('=')
        # return the number as a int
        return int(r[1])

    def status_check_timer(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[10].split('=')
        # return the number as a int
        return int(r[1])

    def screen_type(self):
        f = open("/data/monitoring_configuration.txt")
        # obtain the lines
        c = f.read().split('\n')
        f.close()
        # take the first line and split it from =
        r = c[11].split('=')
        # return the number as a int
        return int(r[1])

    def timestamp(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")


class power_:
    """controls the power cycle, uses info from /data/monitoring_configuration.txt and deltas from last entry to current time /// call as power.power_cycle(maximum time between cycles, tag for power cycle)"""

    # added to reboot_unit() in 11 board, 07 board wont restart due to the PIC12 and PIC 18 firmware being outdated
    def reboot_unit(self):
        board.sendData('>MRST')  # master reset from PIC12
        self.unit_reset_pin = 13
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.unit_reset_pin, GPIO.OUT)  # 11 board resets here

    # If there is no log, create it and write to it else append it to the same file
    # example of txt file
    # file_created@123456789
    # power_cycle@345671234

    def log_reset(self, tag):  # works fine
        database.logResetData(datetime.datetime.now(), tag)
        with open("/data/reset_log.txt", 'a+') as file:
            file.write('{0}_{1}@{2}\n'.format(datetime.datetime.now(), tag, time.time()))
            time.sleep(5)
        return print("updated log")

    def delta_time(self):
        """The difference between the last time it restarted and current time"""
        for i in range(1, 5):
            try:
                with open('/data/reset_log.txt') as file:
                    lines = file.readlines()
                    last_line = lines[-i].strip().split('@')[1]
                    last_reset_time = float(last_line)
                    delta = time.time() - last_reset_time
                    return delta
            # This exception was added to avoid issues with logging going crazy ^@^@^@^@
            # If it reads something weird it erases that line and saves the file again and continues to the next run
            except:
                with open('/data/reset_log.txt') as file:
                    lines = file.readlines()
                    del lines[-i]
                    with open('/data/reset_log.txt', 'a+') as new_file:
                        for line in lines:
                            new_file.write(line)
                continue
        # if it gets this far, there is an issue with the reset_log.txt file
        return print('Error in reset_log.txt')

    # log current time in /data/reset_log.txt
    # Go to /data/reset_log.txt and find the last log
    # Compare it to the current time (separated by @)
    # if the delta is more than an time_threshold_to_restart, reboot_unit
    # else continue
    def power_cycle(self, time_threshold_to_restart, reason_to_power_cycle):
        try:
            if self.delta_time() >= time_threshold_to_restart:  # data for time limits comes from /data/monitoring_configuration.txt
                self.log_reset(reason_to_power_cycle)  # tags what caused the powercycle
                print(f'Reboot_init:{reason_to_power_cycle}')
                time.sleep(30)
                board.buzzCtrl('1')  # testing purposes only
                time.sleep(5)
                self.reboot_unit()
        except:
            print("Restart attempt, limit reached")


class fan_updates_:

    # This gets the temperature using a shell command and splits it into a float number
    def get_temperature(self):
        tem = os.popen("/usr/bin/vcgencmd measure_temp").read()
        # Testing purposes
        # print(tem)
        tem = tem.split("=")
        tam = tem[1]
        tam = tam.split("'")
        tam = float(tam[0])
        return tam

    def Fan_cycle(self):
        # Get temperature and if over threshold turn fan ON
        temp = self.get_temperature()
        if (temp >= Instatiate_setup.fan_temp_threshold()):
            board.setfanCtrl("on")  # PIC18 has to be updated for this function to work
            time.sleep(60)
            board.setfanCtrl("off")
            # print('Fan off')
            # print("FAN ON")
            # start_timer()

    def main(self):
        while True:
            self.Fan_cycle()
            # print("Fan cycle COMPLETE")
            time.sleep(1)  # THIS SHOULD BE IN /data/monitoring_configuration.txt


class ethernet_:
    """Pings google/duckduckgo, resets ethernet and powercycles"""

    def ping1(self):
        # By pingging local host we know if the router is down
        host = 'localhost'
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """
        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', host]
        if subprocess.call(command) == 0:
            return True
        else:
            return False

    def ping2(self):
        # By pingging the exterior we know if there are ISP issues
        host = '1.1.1.1'
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """
        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', host]
        if subprocess.call(command) == 0:
            return True
        else:
            return False

    def reset_ethernet(self):
        # It will turn off the ethernet using GPIO23 and after 3 seconds set it back to high
        ethernet_reset_pin = 23
        cellmodule_reset_pin = 38
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ethernet_reset_pin, GPIO.OUT)
        GPIO.setup(cellmodule_reset_pin, GPIO.OUT)
        time.sleep(1)
        GPIO.output(ethernet_reset_pin, 0)  # this turns off the ethernet
        GPIO.output(cellmodule_reset_pin, 0)  # this turns off the cell module
        time.sleep(3)
        GPIO.output(ethernet_reset_pin, 1)  # Ethernet back ON
        GPIO.output(cellmodule_reset_pin, 1)  # this turns ON cell module
        time.sleep(3)

    def log(self, a):
        database.logPingData(datetime.datetime.now(), a)
        with open('/data/Ethernet_log.txt', 'a+') as file:
            file.write('{0}_{1}@{2}\n'.format(datetime.datetime.now(), a, time.time()))
        # print("Updated: /data/Ethernet_log.txt")

    def check_ethernet_status(self):
        # uses a scoring system --> c = score
        # using "if ping1 and ping2:" wont work for some reason
        c = 0
        for i in range(0, 2):
            if self.ping2():
                self.log('Succesfull Ping')
                return
                # return print('Succesfull ping')
            else:
                time.sleep(3)
                if self.ping1():
                    self.log('Succesfull Ping')
                    return
                    # return print('Succesfull ping')
                else:
                    c += 1
                    self.log('Failed ping')
        if c == 1:
            # Reboot ethernet
            self.log('Ethernet rebooting')
            self.reset_ethernet()
        if c == 2:
            # power cycle
            power_instatiated.power_cycle(Instatiate_setup.Watchdog_reset_block_time(),
                                          'Failed_ping')  # normally 3600 or 1800 for twice an hour

    def main(self):
        while True:
            self.check_ethernet_status()
            # Go to /data/monitoring_configuration.txt and wait for specified time for hardware
            time.sleep(Instatiate_setup.check_ethernet_connection())


class hardware_:
    """Monitors periferals: Keypad,Camera,PIC18,Screen presence [Touch or not], Type of unit[GEN1/2/3], Audio codec, Cellphone module"""

    def __init__(self):
        self.camera = 'Microdia'
        self.pic18 = 'Microchip'
        self.keypad = 'Chesen'
        self.camera_flag = 0
        self.audio_flag = 0
        self.touchscreen_flag = 0
        self.pic_flag = 0
        self.keypad_flag = 0
        return
        # return print('Harware monitoring set')

    def check_cell_module(self):
        cell_module_pin = 38  # SHDN pin on audio codec
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(cell_module_pin, GPIO.IN)
        if GPIO.input(cell_module_pin):
            return print('Cellphone_module ON')
        return print('Cellphone_module OFF')  # PIN 38 is the cellcard status

    def restart_usb_devices(self):  # requires usbreset.c file in the app folder
        os.system('cc usbreset.c -o usbreset')
        time.sleep(0.2)
        os.system('chmod +x usbreset')
        time.sleep(0.2)
        os.system('sudo ./usbreset /dev/bus/usb/001/002')
        time.sleep(0.2)
        print('USB devices restarted')
        # raise SystemExit

    def log(self, a):
        #a = ['Microdia', 'Microchip', 'Chesen', 'GEN3', 'Screen_name', 'Cell_module_Enabled', 'Audio_codec ON', 'TIME_STAMP']
        if "Microdia" in a:
            camera = "OK"
        else:
            camera = "FAIL"
        if "Microchip" in a:
            PIC18= "OK"
        else:
            PIC18= "FAIL"
        if "Chesen" in a:
            keypad = "OK"
        else:
            keypad = "FAIL"
        if "Cell_module_Enabled" in a:
            cell = "OK"
        else:
            cell = "FAIL"
        if "Audio_codec ON" in a:
            audio = "OK"
        else:
            audio = "FAIL"

        unitType = a[3]
        database.logHardwareData(datetime.datetime.now(),PIC18,unitType,cell,audio,camera,keypad)
        with open('/data/Hardware_log.txt', 'a+') as file:
            file.write('{0}\n'.format(a))
        return
        # return print('Hardware log updated')

    def check_audio(self):
        audio_reset_pin = 43  # SHDN pin on audio codec
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(audio_reset_pin, GPIO.IN)
        if GPIO.input(audio_reset_pin) == 0:
            return 'Audio_codec OFF'
        return 'Audio_codec ON'  # normally high

    def restart_audio(self):
        """check for the sound codec"""
        audio_reset_pin = 43
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(audio_reset_pin, GPIO.OUT)
        GPIO.output(audio_reset_pin, 1)
        GPIO.output(audio_reset_pin, 0)
        GPIO.output(audio_reset_pin, 1)
        print('Audio restarted')

    # ILITEK ILITEK-TP name of the screen
    def check_touchscreen(self):
        usb_comp = os.popen("dmesg | grep usb").read()
        if len(usb_comp) > 1:
            print("touchscreen detected")
            return True
        return False

    def check_usb(self):
        """ lsusb and parse all peripherals, then log the current state into /data/Hardware_log.txt"""
        usb_comp = os.popen("lsusb").read()
        data_hardware = []
        sniffer = []
        # finds Camera,Pic18 and Keypad
        suspects = [self.camera, self.pic18, self.keypad]
        for i in suspects:  # i is correct looking for microdia, microchip and chesen
            if i in usb_comp:
                data_hardware.append(i)
                time.sleep(0.2)
        data_hardware.append(os.getenv('SMARTKNOX_MODEL'))  # returns smartknox model GEN3 or TOUCH
        time.sleep(0.2)
        data_hardware.append(os.popen("/usr/bin/tvservice -n").read())  # returns screen display name
        time.sleep(0.2)
        # look for a touch screen and flag it
        if [x for x in data_hardware if 'TOUCH' in x]:
            print('Touchscreen detected')
            # self.touchscreen_flag = 1
        time.sleep(0.2)
        if self.check_cell_module() == 'Cellphone_module ON':
            data_hardware.append('Cell_module_Enabled')
        else:
            data_hardware.append('Cell_module_Disabled')
        time.sleep(0.2)
        data_hardware.append(self.check_audio())  # Adds codec status
        data_hardware.append(Instatiate_setup.timestamp())
        return data_hardware  # ['Microdia', 'Microchip', 'Chesen', 'GEN3', 'Screen_name', 'Cell_module_Enabled', 'Audio_codec ON', 'TIME_STAMP']

    # Evaluate if anything is missing and restart a USB power cycle
    # USB power cycle is done by calling usbreset.c
    def evaluate_data(self, data):
        """Check the list of periferals and restarts the usb driver or power cycles depending on the number of ocurrences (flags)"""
        if self.pic18 not in data:
            print('PIC18: Undetected')
            self.restart_usb_devices()
            self.pic_flag += 1
        if self.pic_flag > 1:
            power_instatiated.power_cycle(Instatiate_setup.Watchdog_reset_block_time(), 'Undetected_PIC18')

        # To avoid keypad reboots in a touchscreen
        if 'TOUCH' in data:
            if os.popen("/usr/bin/tvservice -n").read():
                print(os.popen("/usr/bin/tvservice -n").read())
            else:
                power_instatiated.power_cycle(Instatiate_setup.Watchdog_reset_block_time(), 'Undetected_Touchscreen')
        else:
            if self.keypad not in data:
                print('Keypad: Undetected')
                self.restart_usb_devices()
                self.keypad_flag += 1
            if self.keypad_flag > 1:
                power_instatiated.power_cycle(Instatiate_setup.Watchdog_reset_block_time(), 'Undetected_Keypad')

        if self.camera not in data:
            print('Camera: Undetected')
            self.restart_usb_devices()
            self.camera_flag += 1
        if self.camera_flag > 1:
            power_instatiated.power_cycle(Instatiate_setup.Watchdog_reset_block_time(), 'Undetected_Camera')

        if 'Audio_codec ON' not in data:  # device_name=NHD-NHD-10_1_HDMI for normal screen
            print('Audio codec: Undetected')
            self.restart_audio()
            self.audio_flag += 1
        if self.audio_flag > 1:
            power_instatiated.power_cycle(Instatiate_setup.Watchdog_reset_block_time(), 'Undetected_audio')
        return
        # return print('Periferals Analysed')

    def main(self):
        while True:
            self.log(self.check_usb())
            self.evaluate_data(self.check_usb())
            time.sleep(Instatiate_setup.hardware_check_timer())


class keep_alive:
    """Is in charge of everything AACK/NACK related"""

    def __init__(self):
        # Sends a NACK at boot
        board.sendData(">NACK")
        board.sendData(">NACK")
        self.readEEPROM()

        os.makedirs('/data', exist_ok=True)
        # Write the first one so it doenst reboot the first loop
        with open('/data/PIC_watchdog.txt', 'a+') as file:
            file.write('{0}_{1}@{2}\n'.format(datetime.datetime.now(), 'Watchdog_initialized', time.time()))
            # print("PIC_watchdog.txt:Updated succefully")
        return print('AACK - NACK initialized')

    def log_WD(self, a):
        with open('/data/PIC_watchdog.txt', 'a+') as file:
            file.write('{0}_{1}@{2}\n'.format(datetime.datetime.now(), a, time.time()))
            # print("PIC_watchdog.txt:Updated succefully")

    # send NACK to PIC18
    def sendNACK(self):
        try:
            board.sendData('>NACK')
            board.sendData('>NACK')
            time.sleep(0.3)
            database.logPIC18Data(datetime.datetime.now(), "WAIT", "OK")
            self.log_WD('Sent_NACK')
        except:
            database.logPIC18Data(datetime.datetime.now(), "WAIT", "FAIL")
        # resp = board.data['NACK']
        return

        # Create a file for PIC memory

    # check if PIC_mem.txt exist, if not create it and write eeprom
    def readEEPROM(self):
        board.sendData(">EPRM")
        #Add a function to save EEPROM in database
        return

    def checkWD(self):
        # Find the last AACK_received time in PIC_watchdog.txt
        with open('/data/PIC_watchdog.txt', 'r') as file:
            i = -1
            # go line by line looking for the last AACK_received
            while "AACK_received" not in file.readlines()[i]:
                i -= 1
                # Calculate delta time from last AACK [-2]
                last_AACK = float(file.readlines()[i].split('@')[1])
        delta = time.time() - last_AACK

        # Go find the <Watchdog_reset-limit-time> and compare it to current time delta
        reader = open('/data/monitoring_configuration.txt')
        lim = reader.readlines()[5].split('=')[1]

        # Watchdog_reset-limit-time = 300 by default, lim = 300
        if delta > int(lim):
            power_instatiated.power_cycle(Instatiate_setup.Watchdog_reset_block_time(),
                                          'Timeout No response AACK from PIC18')
        return

    # Send NACK and log sequence
    def check_COM(self):
        self.checkWD()
        self.sendNACK()

    def main(self):
        print(f'Watchdog enabled 1/0:{Instatiate_setup.Watchdog_enable()}')
        while (Instatiate_setup.Watchdog_enable() == 1):
            self.check_COM()
            # print("Keep alive cycle COMPLETE")
            time.sleep(Instatiate_setup.Watchdog_NACK_send_time())
        # print('error')


class status_monitoring_:
    """Logs status of the TE unit in /data/Status_log.txt using shell commands"""

    def __init__(self):
        self.status_log = {
            'Time_stamp': '',
            'RPCM_voltage': '',
            'RPCM_temperature': '',
            'RPCM_screen_resolution': '',
            'RPCM_get_memory': '',
            'RPCM_get_screen_name': ''
        }
        return print('Status monitoring set')

    def collect_data(self):
        Instatiate_setup = setup_()  # DONT FORGET TO ADD THE PARENTHESIS AT THE END OF CLASS NAME ()!!!!!
        self.status_log.update({
            'Time_stamp': Instatiate_setup.timestamp(),
            'RPCM_voltage': os.popen("/usr/bin/vcgencmd measure_volts").read(),  # measures RPCM voltage,
            'RPCM_temperature': os.popen("/usr/bin/vcgencmd measure_temp").read(),  # measures RPCM temperature ,
            'RPCM_screen_resolution': os.popen("/usr/bin/vcgencmd get_lcd_info").read(),  # returns screen resolution
            'RPCM_get_memory': os.popen("/usr/bin/vcgencmd get_mem arm").read(),  # returns available memory
            'RPCM_get_screen_name': os.popen("/usr/bin/tvservice -n").read()  # returns screen display name
        })
        # after obtaining the json data log in /data/Status_log.txt
        self.log(self.parseLineForValues(self.status_log))

    def log(self, a):
        database.logStatusData(datetime.datetime.now(), a["RPCM_voltage"], a["RPCM_temperature"], a["RPCM_get_memory"])
        with open('/data/Status_log.txt', 'a+') as file:  # needs to be saved as .csv
            file.write('{0}\n'.format(a))
        return
        # return print("Status_log: Updated")

    def parseLineForValues(self, line):
        # print('-----PARSING LINE FOR VALUES-----')
        dirtyStrings = 'volt|=|\n|temp|arm|device_name'
        for x in line:
            line[x] = re.sub(dirtyStrings, '', line[x])
        return line

    def main(self):
        while True:
            self.collect_data()
            # Go to /data/monitoring_configuration.txt and wait for specified time for hardware
            time.sleep(Instatiate_setup.status_check_timer())


class Tamper_switch:
    """This item was solved adding TAMO and TAMC to runMainboard.py, also added TAMC and TAMO to the dictionary in mainboardCtrl.py"""
    pass


class key_switch:
    """Key logic for managers opening the gate using a key, Card reader LED's and Buzzers will turn on/off"""

    # Added command to dictionary in mainboardCtrl.py
    # set a log for key events
    def log_key_events(self, a):
        with open("/data/key_events.txt", 'a+') as file:
            file.write('{0}_{1}@{2}\n'.format(datetime.datetime.now(), a, time.time()))
        print("/data/key_events.txt:Updated succefully")

    def both(self, state):
        board.relay1Ctrl(f'{state}')
        board.relay2Ctrl(f'{state}')

    def switch(self, selection, state):
        if selection == "1":
            return board.relay1Ctrl(f'{state}'),
        elif selection == "2":
            return board.relay2Ctrl(f'{state}'),
        elif selection == "3":
            return print('Nothing'),
        elif selection == "4":
            return self.both(f'{state}')
        else:
            return print('INVALID SELECTION')

    def KEYC_logic(self):
        # Add logic to trigger the correct relay
        envVar = os.getenv(
            'KeySwitch')  # this is the Balena enviromental value that will define the behaviour of the KeySwitch
        self.switch(envVar, 'on')
        # RPCM logs the event into local database
        self.log_key_events("Key CLOSED")
        # Log state of key in /data/data.db
        database.logKeyEvent(datetime.datetime.now(), "Key CLOSED")
        # Add logic to turn on the green LED on the card reader green
        board.readerLedOn()
        # RPCM turns on the buzzer
        board.readerPulseBuzzer()
        # UI prints "Key Switch Enabled, Gate is Open”
        print('Key Switch Enabled, Gate is Open')
        return

    def KEYO_logic(self):
        # Add logic to trigger the correct relay
        envVar = os.getenv('KeySwitch')
        self.switch(envVar, 'off')
        # RPCM logs the event into local database
        self.log_key_events("Key OPEN")
        # Log state of key in /data/data.db
        database.logKeyEvent(datetime.datetime.now(), "Key OPEN")
        # Add logic to turn on the red LED on the card reader green
        board.readerLedOff()
        # RPCM turns on the buzzer
        board.readerPulseBuzzer()
        # UI prints "Key Switch Enabled, Gate is Open”
        print('Key Switch Disabled, Gate is Closed')
        return


class Motion_:
    """Only print in screen state of display, PIC18 does everything else"""

    def NOMO_(self):
        print('No motion detected in 5 min\nDimming screen')

    def EXMO_(self):
        print('Motion detected\nScreen brightness up')


class accelerometer_:
    """When the accelerometer is called on the mailbox this function takes 3 pictures"""

    # Make a directory
    def __init__(self):
        uuid = os.getenv('RESIN_DEVICE_UUID')
        self.MYDIR = ("/data/camera_images_accelerometer")
        self.CHECK_FOLDER = os.path.isdir(self.MYDIR)
        # Get access codes from Balena env variables
        self.ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
        self.SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        print(self.ACCESS_KEY)
        print(self.SECRET_KEY)
        print(self.MYDIR)
        # If folder doesn't exist, then create it.
        if not self.CHECK_FOLDER:
            os.makedirs(self.MYDIR)
            print(f"created folder :{self.MYDIR}")
        else:
            print("{MYDIR}folder already exists.")

    # upload to AWS S3 bucket
    def upload_file(self, file_name, bucket, object_name=None):
        """This needs to be set with the correct permissions in AWS to upload the files safely"""
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)
        # Upload the file
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def take_pictures(self):
        print('taking pictures')
        for i in range(0, 3):
            image_name = str(date.today()) + '-{0}-{1}'.format(self.uuid, i) + '.jpg'  # 2021-08-13-1.jpg
            time.sleep(3)
            try:
                os.system(
                    f"fswebcam /data/camera_images_accelerometer/{image_name}")  # os.system(f"fswebcam /data/camera_images_accelerometer/test{i}.jpg")
            except:
                os.system("echo no camera,{0}".format(Instatiate_setup.timestamp()))
                database.logAccelEvent(datetime.datetime.now(), "NO CAMERA FOUND!")
            time.sleep(1)
            self.upload_file(f"/data/camera_images_accelerometer/{image_name}", "telephone-entry-accelerometer-log",
                             f"{image_name}")


power_instatiated = power_()
Instatiate_setup = setup_()
board = mainboardCtrl.Mainboard(type='telephone-entry-non-touch', standalone=False)
