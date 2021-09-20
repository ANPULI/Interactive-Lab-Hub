import time
from datetime import datetime
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image_bg = Image.new("RGB", (width, height), color=(255, 255, 255))

rotation = 90
disp.image(image_bg, rotation)

CLIP_SIZE = 30
image_coffee = Image.open("coffee.jpg").resize((CLIP_SIZE, CLIP_SIZE), Image.BICUBIC)
image_cocktail = Image.open("cocktail.png").resize((CLIP_SIZE, CLIP_SIZE), Image.BICUBIC)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

def display_drinks(image):
    HOUR = datetime.now().hour
    MINUTE = datetime.now().minute
    if 8 <= HOUR < 20:
        image_drink = image_coffee.copy()
        n = HOUR - 7
    else:
        image_drink = image_cocktail.copy()
        n = HOUR + 5 if HOUR < 8 else HOUR - 19
    for i in range(n):
        if i < 5:
            x_times, y_times = i, 0
        elif i < 9:
            x_times, y_times = i - 5, 1
        elif i < 12:
            x_times, y_times = i - 9, 2
        x, y = x_times * CLIP_SIZE, y_times * CLIP_SIZE + 5
        if i == n - 1:
            image_drink = image_drink.crop((0, int(CLIP_SIZE*(1 - MINUTE/60)), CLIP_SIZE, CLIP_SIZE))
            y += int(CLIP_SIZE*(1 - MINUTE/60))
        image.paste(image_drink, (x,y), image_drink)

def get_lines():
    first_line = "IT IS"
    to_or_past = "PAST"
    MINUTE = datetime.now().minute
    HOUR = datetime.now().hour
    HOUR = HOUR if HOUR == 12 else HOUR % 12
    if MINUTE > 30:
        MINUTE = 65 - MINUTE
        to_or_past = "TO"
        HOUR += 1
    span = MINUTE // 5
    lookup1 = ["", "FIVE", "TEN", "A QUARTER", "TWENTY", "TWENTY FIVE", "HALF"]
    second_line = lookup1[span]
    # third line
    lookup2 = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE"]
    if span == 0:
        third_line =  "{} O'CLOCK".format(lookup2[HOUR])
    else:
        third_line = "{} {}".format(to_or_past, lookup2[HOUR])
    return first_line, second_line, third_line
    
while True:
    # Draw a black filled box to clear the image.
    # draw.rectangle((0, 0, width, height), outline=0, fill=0)
    image = image_bg.copy()
    # image.paste(image_coffee, (0,0), image_coffee)
    # image.paste(image_drink, (0,0),image_drink)
    display_drinks(image)
    draw = ImageDraw.Draw(image)
    

    #TODO: Lab 2 part D work should be filled in here. You should be able to look in cli_clock.py and stats.py
    
    y = 0
    TIME = time.strftime("%m/%d/%Y %H:%M:%S")

    # draw.text((width-font.getsize("TWELVE O'CLOCK")[0], 45), "TWELVE O'CLOCK", font=font, fill="#000000")
    first_line, second_line, third_line = get_lines()
    draw.text((width-font.getsize(first_line)[0]-padding, 0.5*CLIP_SIZE), first_line, font=font, fill="#000000")
    draw.text((width-font.getsize(second_line)[0]-padding, 1.5*CLIP_SIZE), second_line, font=font, fill="#000000")
    draw.text((width-font.getsize(third_line)[0]-padding, 2.5*CLIP_SIZE), third_line, font=font, fill="#000000")
    
    # Display image.
    disp.image(image, rotation)
    time.sleep(60)
