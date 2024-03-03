import framebuf
import time
from machine import Pin, SPI

# Pin definition
SCK = 4
MOSI = 6
RST = 7
CS = 8
DC = 9

# Assuming 16-bit color depth
COLOR_DEPTH = 16
BYTES_PER_PIXEL = COLOR_DEPTH // 8

#color is BGR
RED = 0x00F8
GREEN = 0xE007
BLUE = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000
YELLOW = 0xe0ff

class RGB_OLED(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 128
        self.height = 128
        
        # Adjust buffer size for RGB (16-bit per pixel)
        #self.buffer = bytearray(self.width * self.height * BYTES_PER_PIXEL)
        
        # Initialize pins
        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)
        self.dc = Pin(DC, Pin.OUT)
        
        # Initialize SPI
        self.spi = SPI(1, 16000000, polarity=0, phase=0, sck=Pin(SCK), mosi=Pin(MOSI), miso=None)
        self.buffer = bytearray(self.height * self.width * 2)

        # Initialize the framebuffer with RGB565 configuration
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        
        self.init_display()
        #self.SetWindows(0, 0, self.width-1, self.height-1)

    def write_cmd(self, cmd):
        self.cs(0)
        self.dc(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, data):
        self.cs(0)
        self.dc(1)
        if isinstance(data, int):
            self.spi.write(bytearray([data]))  # If data is a single byte
        else:
            self.spi.write(data)  # If data is already a bytes or bytearray object
        self.cs(1)  # End transmission

    def init_display(self):
        # Reset the display
        self.rst(1)
        time.sleep_ms(20)
        self.rst(0)
        time.sleep_ms(200)
        self.rst(1)

        # Send initialization commands
        # Turn on the display
        self.write_cmd(0xAF)
        self.write_cmd(0x00)# Set low column address
        self.write_cmd(0x10)# Set high column address
    
        self.write_cmd(0x20)# Set memory addressing mode
        self.write_cmd(0x00)# Horizontal addressing mode
        
        self.write_cmd(0xA8)# Set multiplex ratio
        self.write_cmd(0x3F)# Set ratio to 63
        
        self.write_cmd(0xD3)# Set display offset
        self.write_cmd(0x00)# Offset value is 0        
        self.write_cmd(0xD5)# Set display clock divide ratio/oscillator frequency
        self.write_cmd(0x80)# Default divide ratio
    
        self.write_cmd(0xD9)# Set pre-charge period
        self.write_cmd(0x22)# Default value
    
        self.write_cmd(0xDA)# Set COM pin configuration
        self.write_cmd(0x12)# Default configuration
    
        self.write_cmd(0xDB)# Set VCOMH
        self.write_cmd(0x40)# Default value
        
        self.write_cmd(0xA1)# Set segment remap
        #self.write_cmd(0xAE)# Turn off the display
        
    def reset(self):
        self.rst(1)
        time.sleep(0.2) 
        self.rst(0)
        time.sleep(0.2)         
        self.rst(1)
        time.sleep(0.2)
        
    def fill_screen(self, color):
        self.fill(color)
        self.show()
        
    def show(self):
        # Set column address range
        self.write_cmd(0x15)  # Column address set command for SSD1357
        self.write_data(0x00)  # Start column
        self.write_data(self.width - 1 )  # End column

        # Set row address range
        self.write_cmd(0x75)  # Row address set command for SSD1357
        self.write_data(0x00)  # Start row
        self.write_data(self.height - 1 )  # End row

        # Write data to RAM
        self.write_cmd(0x5C)  # Write to RAM command for SSD1357

        # Write the buffer data
        self.cs(0)
        self.dc(1)  # Data mode
        self.spi.write(self.buffer)
        self.cs(1)

    def SetWindows(self, Xstart, Ystart, Xend, Yend):#example max:0,0,159,79
        Xstart=Xstart+2
        Xend=Xend+2
        Ystart=Ystart+1
        Yend=Yend+1
        self.write_cmd(0x2A);
        self.write_data((Xstart >> 8) & 0xFF);
        self.write_data(Xstart & 0xFF);
        self.write_data(((Xend-1) >> 8) & 0xFF);
        self.write_data((Xend-1) & 0xFF);

        self.write_cmd(0x2B);
        self.write_data((Ystart >> 8) & 0xFF);
        self.write_data(Ystart & 0xFF);
        self.write_data(((Yend  ) >> 8) & 0xFF);
        self.write_data((Yend  ) & 0xFF);

        self.write_cmd(0x2C) 
        
    def write_text(self,text,x,y,size,color):
        background = self.pixel(x,y)
        info = []
        # Creating reference charaters to read their values
        self.text(text,x,y,color)
        for i in range(x,x+(8*len(text))):
            for j in range(y,y+8):
                # Fetching amd saving details of pixels, such as
                # x co-ordinate, y co-ordinate, and color of the pixel
                px_color = self.pixel(i,j)
                info.append((i,j,px_color)) if px_color == color else None
        # Clearing the reference characters from the screen
        self.text(text,x,y,background)
        # Writing the custom-sized font characters on screen
        for px_info in info:
            self.fill_rect(size*px_info[0] - (size-1)*x , size*px_info[1] - (size-1)*y, size, size, px_info[2]) 

# Main execution
if __name__ == '__main__':
    oled = RGB_OLED()
    oled.fill_screen(0xFFFF)
    oled.SetWindows(0,0,127,127)
    oled.write_text("Hello @ 0",0,20,1,GREEN)    
    oled.show()
    time.sleep(1)
    oled.fill_screen(RED)
    oled.show()
    time.sleep(1)
    oled.fill_screen(YELLOW)
    oled.show()
    time.sleep(1)    
    oled.fill_rect(0,0,128,14,RED)
    oled.rect(0,0,128,14,RED)
    
    oled.fill_rect(0,14,128,14,BLUE)
    oled.rect(0,14,128,14,BLUE)
    
    oled.fill_rect(0,28,128,14,GREEN)
    oled.rect(0,28,128,14,GREEN)
    
    oled.fill_rect(0,42,128,14,0X07FF)
    oled.rect(0,42,128,14,0X07FF)
    oled.fill_rect(0,56,128,14,0xF81F)
    oled.rect(0,56,128,14,0xF81F)
    oled.fill_rect(0,70,128,14,0x7FFF)
    oled.rect(0,70,128,14,0x7FFF)
    oled.fill_rect(0,84,128,14,0xFFE0)
    oled.rect(0,84,128,14,0xFFE0)
    oled.fill_rect(0,98,128,14,0XF0F0)
    oled.rect(0,98,128,14,0XF0F0)
    oled.fill_rect(0,112,128,16,0XF0EF)
    oled.rect(0,112,128,16,0XF0EF)
    oled.write_text("12345678",31,0,1,WHITE)
    oled.write_text("2",31,9,1,WHITE)
    oled.write_text("3",31,18,1,WHITE)
    oled.write_text("4",31,27,1,BLACK)
    oled.write_text("5",31,36,1,BLACK)
    oled.write_text("6",31,45,1,BLACK)
    oled.write_text("7",31,54,1,BLACK)
    #text and rect can start from x = 31 and can fit 8 characters
    oled.show()

