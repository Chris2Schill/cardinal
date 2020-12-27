import lcd_display
import os
import signal
import sys
import socket
import requests
import shutil
import threading
from threading import Thread, Lock
from time import sleep

SERVER_URL = 'http://chris-schilling.com/cardinal/mom/'
CONFIG_PATH = 'config.json'
TWEET_FILENAME = 'tweet.wav'
quit = False
mutex = Lock()
message = "                \n                "


lcd_display = lcd_display.LCD_Display(screen_width = 16)
	

def signal_handler(sig, frame):
  global quit
  print('Exiting...')
  quit = True


def main():
  signal.signal(signal.SIGINT, signal_handler)

  t = Thread(target = url_request_thread)
  t.start()

  while(not quit):
    try:
      with mutex:
        lcd_display.draw()
    except Exception as e:
      print(e)
    sleep(0.25)


def url_request_thread():
  while(not quit):
    try:
      if is_connected("1.1.1.1"):
        config = requests.get(SERVER_URL+CONFIG_PATH).json()
        write_network_config(config['ssid'], config['passwd'])
        msg = config['message']

        global message
        if msg != message:
          download_file(SERVER_URL+config['tweet'], TWEET_FILENAME)
          os.system('aplay ' + TWEET_FILENAME + ' &')
          print('Received new message:[' + ','.join(msg.split('\n')) + ']')
          with mutex:
            lcd_display.request_clear_screen()
          message = msg
      else:
        msg = '  NO INTERNET   \n  CONNECTION    '
    except Exception as e:
      print(e)
      msg = str(e)

    with mutex:
      lcd_display.set_message(msg)
    sleep(1)

	
def download_file(url, filename):
  response = requests.get(url, stream=True)
  with open(filename, "wb") as file:
    shutil.copyfileobj(response.raw, file)


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


def write_network_config(ssid, passwd):
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


if __name__ == "__main__":
  main()
