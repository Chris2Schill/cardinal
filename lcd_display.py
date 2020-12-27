
import I2C_LCD_driver

class LCD_Display:
  def __init__(self, screen_width):
    self.LCD_WIDTH = screen_width
    self.shift = 0
    self.msg_width = 1
    self.message = "                \n                "
    self.clear_screen = False
    self.lcd_driver = I2C_LCD_driver.lcd()

  # Clears the screen on the next frame to avoid lingering
  # chars if a new message has less chars than the previous
  def request_clear_screen(self):
    self.clear_screen = True
    self.shift = 0

  # Sets the message to display on screen. Takes a single string
  # with lines delimited with \n
  def set_message(self, msg):
    if '\n' not in msg: msg = msg + '\n                '
    self.msg_width = 0
    for line in msg.split('\n'):
      self.msg_width = max(self.msg_width, len(line))
    self.message = msg;

  # draw  
  def draw(self):
    if self.clear_screen:
      self.lcd_driver.lcd_display_string("                ", 1)
      self.lcd_driver.lcd_display_string("                ", 2)
      self.clear_screen = False
    else:
      lines = self.message.split('\n')
      for i in range(len(lines)):
        if len(lines[i]) > self.LCD_WIDTH: lines[i] = marquee_line(lines[i], self.shift)
        self.lcd_driver.lcd_display_string(lines[i][:self.LCD_WIDTH], i+1)
      self.shift = (self.shift+1+self.msg_width) % self.msg_width


# end class LCD_Display      

def marquee_line(line, shift):
  return line[shift:len(line)] + line[0:shift]
