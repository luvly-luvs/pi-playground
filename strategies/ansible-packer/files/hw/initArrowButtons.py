import keyboard
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

def up(channel):
	time.sleep(0.01)
	if GPIO.input(channel) == 0:
		keyboard.press_and_release('up arrow')
		print("up arrow received")

def down(channel):
	time.sleep(0.01)
	if GPIO.input(channel) == 0:
		keyboard.press_and_release('down arrow')
		print("down arrow received")

def main():
	#setup up arrow input
	GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)	

	#setup down arrow input
	GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	#add callback for up arrow
	GPIO.add_event_detect(4, GPIO.FALLING, callback=up, bouncetime=100)


	#add callback for down arrow
	GPIO.add_event_detect(5, GPIO.FALLING, callback=down, bouncetime=100)


	print("GPIO button input setup completed")

	while(True):
		time.sleep(1)

main()
