import I2C_LCD_driver
import os
from time import sleep
import signal
import sys
import urllib
import hashlib

LCD_WIDTH = 16
MESSAGE_URL = 'http://chris-schilling.com/cardinal/mom/'
MESSAGE_PATH = 'message.txt'
TWEET_PATH = 'tweet.wav'
NETWORK_CONFIG_PATH = 'network_config.txt'
shift = 0
msg_hash = 0
mylcd = I2C_LCD_driver.lcd()

quit = 0

def signal_handler(sig, frame):
  global quit
  print("You pressed Ctrl+C!")
  quit = 1
	

def main():
  signal.signal(signal.SIGINT, signal_handler)
  while(quit == 0):
    try:
      writeNetworkConfig()
      message = getMessage()
      if messageChanged(message):
        audioClip = urllib.urlopen(MESSAGE_URL+TWEET_PATH).read()
        audio_file = open("tweet.wav", "w");
        audio_file.write(audioClip)
        audio_file.close()
        os.system("aplay tweet.wav &")
        mylcd.lcd_display_string("                ", 1)
        mylcd.lcd_display_string("                ", 2)
      displayMessage(message)
    except Exception as e:
	displayMessage(e)
	print(e)
    sleep(0.25)

def writeNetworkConfig():
  config = urllib.urlopen(MESSAGE_URL+NETWORK_CONFIG_PATH).read().split('\n')
  SSID = config[0]
  pswd = config[1]
  config_str = "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=US\nnetwork={\nssid=\""+SSID+"\"\npsk=\""+pswd+"\"\nkey_mgmt=WPA-PSK\n}\n"
  file = 	open("/etc/wpa_supplicant/wpa_supplicant.conf", "w")
  file.write(config_str)
  file.close()


def getMessage():
  return urllib.urlopen(MESSAGE_URL+MESSAGE_PATH).read()


def messageChanged(message):
  global msg_hash
  global shift
  hash = hashlib.md5(message).hexdigest()
  if hash != msg_hash:
    msg_hash = hash;
    shift = 0
    return 1
  return 0


def displayMessage(message):
  global shift
  msg_lines = message.split('\n')
  msg_width = getMessageWidth(msg_lines[0], msg_lines[1])

  lcd_line1 = marqueeLine(msg_lines[0], shift) if shouldLineMarquee(msg_lines[0]) else msg_lines[0]
  lcd_line2 = marqueeLine(msg_lines[1], shift) if shouldLineMarquee(msg_lines[1]) else msg_lines[1]

  mylcd.lcd_display_string(lcd_line1[:LCD_WIDTH], 1)
  mylcd.lcd_display_string(lcd_line2[:LCD_WIDTH], 2)
  shift = (shift+1+msg_width) % msg_width

def shouldLineMarquee(line):
  return len(line) > LCD_WIDTH

def marqueeLine(line, shift):
  return line[shift:len(line)] + line[0:shift]
  
def getMessageWidth(line1, line2):
  return max(len(line1), len(line2))

if __name__ == "__main__":
  main()
