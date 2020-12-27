import I2C_LCD_driver
import os
from time import sleep
import signal
import sys
import hashlib
import socket
import requests
import shutil
import threading
from threading import Thread, Lock

SERVER_URL = 'http://chris-schilling.com/cardinal/mom/'
CONFIG_PATH = 'config.json'

LCD_WIDTH = 16
shift = 0
msg_hash = 0
mylcd = I2C_LCD_driver.lcd()
quit = False
messageLock = Lock()
screenLock = Lock()
message = "                \n                "
clearScreen = False

	

def signal_handler(sig, frame):
  global quit
  print('Exiting...')
  quit = True


def main():
  global message
  global clearScreen
  signal.signal(signal.SIGINT, signal_handler)

  t = Thread(target = url_request_thread)
  t.start()

  while(not quit):
    try:
      with messageLock:
        msg = message
      if clearScreen: 
        mylcd.lcd_display_string("                ", 1)
        mylcd.lcd_display_string("                ", 2)
        clearScreen = False
        
      displayMessage(msg)
    except Exception as e:
      print(e)
    sleep(0.25)


def url_request_thread():
  global quit
  while(not quit):
    try:
      if is_connected("1.1.1.1"):
        config = requests.get(SERVER_URL+CONFIG_PATH).json()
        writeNetworkConfig(config['ssid'], config['passwd'])
        msg = config['message']

        if messageChanged(msg):
          getAndSaveAudioTweet(SERVER_URL+config['tweet'])
          os.system('aplay tweet.wav &')
          print('Got new message:[' + ','.join(msg.split('\n')) + ']')
          clearScreen = True
      else:
        msg = '  NO INTERNET   \n  CONNECTION    '
    except Exception as e:
      print(e)
      msg = str(e)
    updateMessage(msg)
    sleep(1)


def updateMessage(msg):
  global message
  with messageLock:
    message = msg

	
def getAndSaveAudioTweet(url):
  response = requests.get(url, stream=True)
  with open("tweet.wav", "wb") as audio_file:
    shutil.copyfileobj(response.raw, audio_file)


def is_connected(hostname):
  try:
    # see if we can resolve the host name == tells us if there is
    # DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually reachable
    s = socket.create_connection((host, 80), 2)
    s.close()
    return True
  except:
    pass
  return False


def writeNetworkConfig(ssid, passwd):
  config_str = ('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n'
                'update_config=1\n'
                'country=US\n'
                'network={\n'
                '   ssid="'+ssid+'"\n'
                '   psk="'+passwd+'"\n'
                '   key_mgmt=WPA-PSK\n'
                '}\n')
  file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "w")
  file.write(config_str)
  file.close()


def messageChanged(message):
  global msg_hash
  global shift
  hash = hashlib.md5(message).hexdigest()
  if hash != msg_hash:
    msg_hash = hash;
    shift = 0
    return 1
  return 0


def displayMessage(msg):
  global shift

  if '\n' not in msg: msg = msg + '\n                '

  lines = msg.split('\n')

  msg_width = 0
  for i in range(len(lines)):
    msg_width = max(msg_width, len(lines[i]))
    if len(lines[i]) > LCD_WIDTH: lines[i] = marqueeLine(lines[i], shift)
    mylcd.lcd_display_string(lines[i][:LCD_WIDTH], i+1)

  shift = (shift+1+msg_width) % msg_width
  

def marqueeLine(line, shift):
  return line[shift:len(line)] + line[0:shift]


if __name__ == "__main__":
  main()
