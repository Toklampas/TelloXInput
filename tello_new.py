# XInput:
# https://github.com/Zuzu-Typ/XInput-Python
# Tello SDK:
# https://terra-1-g.djicdn.com/2d4dce68897a46b19fc717f3576b7c6a/Tello%20%E7%BC%96%E7%A8%8B%E7%9B%B8%E5%85%B3/For%20Tello/Tello%20SDK%20Documentation%20EN_1.3_1122.pdf

import threading
import socket
import XInput
from time import sleep

host = ''
port = 9000
locaddr = (host, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
	sock.bind(locaddr)
except Exception:
	print("Warning: There are multiple instances of this program running at the same time. Please close any other "
	      "instances of the program to continue.")
event = ''

leftStickX = 0
leftStickY = 0
rightStickX = 0
rightStickY = 0
controllerConnected = False
printResponse = False
printSent = False
tempprintResponse = False
debugMode = False


# Colored output---------
def colored(r, g, b, text):
	return f"\033[38;2;{r};{g};{b}m{text}\033[38;2;255;255;255m"


# Rumble function----------
def controller_rumble(duration, strength_left=0, strength_right=65535):
	XInput.set_vibration(0, strength_left, strength_right)
	sleep(duration)
	XInput.set_vibration(0, 0, 0)


# Get response-------------
def recv():
	while True:
		try:
			data, server = sock.recvfrom(1518)
			response = data.decode(encoding="utf-8")
			if printResponse or tempprintResponse:
				print("Response: ", response)
		except Exception:
			print('\nAn exception occured while waiting for incoming packets.\n')
			break


# Send UDP packet--------
def udpsend(messagetosend):
	if messagetosend == "ask":  # manual input
		msg = input("\nType a custom command here > ")
	else:
		msg = messagetosend  # controller input
	messageinhex = msg.encode("utf-8").hex()
	if printSent:
		print("Command sent:", msg, "( HEX:", messageinhex, ")")
	msg = msg.encode(encoding="utf-8")
	sent = sock.sendto(msg, tello_address)


recvThread = threading.Thread(target=recv)
recvThread.start()

# Setup -------------------
targetip = input(colored(100, 160, 250, "Enter target IP > "))  # Input a custom IP, "tello" or "laptop"
if targetip == "tello":  # If tello
	UDP_IP = "192.168.10.1"
	UDP_PORT = 8889
elif targetip == "laptop":  # If laptop "192.168.1.13"
	UDP_IP = "192.168.1.13"
	UDP_PORT = 8889
else:  # Otherwise, ask for a custom port
	targetport = int(input(colored(100, 160, 250, "Enter target port > ")))
	UDP_IP = targetip
	UDP_PORT = targetport
print("> Will send packets to:", UDP_IP, "-", UDP_PORT)
tello_address = (UDP_IP, UDP_PORT)
pressedbuttononcontroller = "none"

# If there is a controller detected, output its state and make it rumble. If not, print out a warning.
for event in XInput.get_events():
	if event.type == XInput.EVENT_CONNECTED:
		controllerConnected = True
		print(colored(0, 210, 0, "\n> Controller detected! Battery status: " + str(XInput.get_battery_information(0))))
		initialRumbleStrength = 0
		num = 20
		for i in range(num):
			XInput.set_vibration(0, 0, initialRumbleStrength)
			sleep(0.05)
			initialRumbleStrength += 2500
		XInput.set_vibration(0, 0, 0)
		sleep(0.3)
		controller_rumble(0.3, 65000, 45000)
if not controllerConnected:
	print(colored(210, 0, 0, "\n> Warning: Controller isn't detected. Is it turned on and set as player 1?"))

# Setup drone settings---
print(colored(0, 210, 0, "\n> Starting setup..."))
sleep(0.5)
udpsend("command")
sleep(0.5)
udpsend("streamoff")
sleep(0.5)
udpsend("speed 100")
sleep(0.5)
print(colored(0, 210, 0, "> Setup finished!\n"))
sleep(1)

# Check for input-------
while True:
	sleep(0.005)
	for event in XInput.get_events():
		if event.type == XInput.EVENT_BUTTON_PRESSED:  # If a button is pressed
			if event.button == "BACK":
				if debugMode:
					print('back pressed')
				udpsend("land")
				tempprintResponse = False
			elif event.button == "START":
				if debugMode:
					print('start pressed')
				udpsend("takeoff")
				tempprintResponse = False
			elif event.button == "DPAD_LEFT":
				if debugMode:
					print('dpad left pressed')
				udpsend("flip l")
				tempprintResponse = False
			elif event.button == "DPAD_RIGHT":
				if debugMode:
					print('dpad right pressed')
				udpsend("flip r")
				tempprintResponse = False
			elif event.button == "DPAD_UP":
				if debugMode:
					print('dpad up pressed')
				udpsend("flip f")
				tempprintResponse = False
			elif event.button == "DPAD_DOWN":
				if debugMode:
					print('dpad down pressed')
				udpsend("flip b")
				tempprintResponse = False
			elif event.button == "A":
				if debugMode:
					print('A pressed')
				udpsend("ask")
				tempprintResponse = True
			elif event.button == "B":
				if debugMode:
					print('B pressed')
				udpsend("battery?")
				tempprintResponse = True
			elif event.button == "Y":
				if debugMode:
					print('Y pressed')
				udpsend("temp?")
				tempprintResponse = True
			elif event.button == "X":
				if debugMode:
					print('X pressed')
				udpsend("tof?")
				tempprintResponse = True
			elif event.button == "LEFT_THUMB":
				if not debugMode:
					debugMode = True
					printResponse = True
					printSent = True
					print(colored(245, 245, 44, "Debug mode is now turned on. Press L3 to deactivate."))
				else:
					debugMode = False
					printResponse = False
					printSent = False
					print("L3 pressed")
					print(colored(245, 245, 44, "Debug mode is now turned off. Press L3 to activate."))
			elif event.button == "RIGHT_THUMB":
				if debugMode:
					print("R3 pressed")
				udpsend("wifi?")
				tempprintResponse = True
		elif event.type == XInput.EVENT_STICK_MOVED:  # If a stick is moved
			if event.stick == XInput.RIGHT:
				if debugMode:
					print("Right stick X >", event.x)
					print("Right stick Y >", event.y)
				rightStickX = round(event.x * 100)
				rightStickY = round(event.y * 100)
			if event.stick == XInput.LEFT:
				if debugMode:
					print("Left stick X >", event.x)
					print("Left stick Y >", event.y)
				leftStickX = round(event.x * 100)
				leftStickY = round(event.y * 100)
			udpsend("rc " + str(leftStickX) + " " + str(leftStickY) + " " + str(rightStickY) + " " + str(rightStickX))
			tempprintResponse = False
