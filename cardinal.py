import I2C_LCD_driver
import os
from time import sleep
import urllib
import hashlib

LCD_WIDTH = 16
MESSAGE_URL = 'http://chris-schilling.com'
shift = 0
msg_hash = 0
mylcd = I2C_LCD_driver.lcd()

def main():
  while(1):
    message = getMessage()
    if messageChanged(message):
      os.system("aplay cardinal_tweet.wav &")
      mylcd.lcd_display_string("                ", 1)
      mylcd.lcd_display_string("                ", 2)
    displayMessage(message)
    sleep(0.3)


def getMessage():
  return urllib.urlopen(MESSAGE_URL).read()

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
