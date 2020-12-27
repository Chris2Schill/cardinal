
import I2C_LCD_driver

class LCD_Display:

  lcd_driver = I2C_LCD_driver.lcd()
  clear_screen = False
  message = "                \n                "
  msg_width = 1
  shift = 0
  LCD_WIDTH = 16

  def request_clear_screen(self):
    self.clear_screen = True
    self.shift = 0


  def set_message(self, msg):
    if '\n' not in msg: msg = msg + '\n                '
    self.msg_width = 0
    for line in msg.split('\n'):
      self.msg_width = max(self.msg_width, len(line))
    self.message = msg;

  
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
