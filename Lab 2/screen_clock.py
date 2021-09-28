import time
from datetime import datetime
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from PhysicalImage import PhysicalImage

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

# set blink
blink = False

# these setup the code for our buttons and tell the pi to treat the GPIO pins as digitalIO vs analogIO
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

def set_drinks():
    drinks_list = []
    HOUR = datetime.now().hour
    MINUTE = datetime.now().minute
    SECOND = datetime.now().second
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
        pi = PhysicalImage(image_drink, x, y)
        pi.set_canvas_size(width, height)
        drinks_list.append(pi)
    return drinks_list

def display_drinks(image, drinks_list):
    for drink in drinks_list:
        image.paste(drink.img, (drink.x, drink.y), drink.img)

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

def change_size_by_button():
    global CLIP_SIZE
    if buttonB.value and not buttonA.value:  # just button A pressed
        CLIP_SIZE += 5
    if buttonA.value and not buttonB.value:  # just button B pressed
        CLIP_SIZE -= 5
    if not buttonA.value and not buttonB.value:  # none pressed
        CLIP_SIZE = 30

def press_button(drinks_list):
    global SECOND
    if buttonA.value and buttonB.value:
        return drinks_list
    if datetime.now().second - SECOND < 1:
        return drinks_list
    
    if buttonB.value and not buttonA.value:  # just button A pressed
        for drink in drinks_list:
            drink.random_speed()
        SECOND = datetime.now().second
    if buttonA.value and not buttonB.value:  # just button B pressed
        drinks_list = set_drinks()
        SECOND = datetime.now().second
        # print(drink.vx)
    return drinks_list

HOUR = datetime.now().hour
SECOND = datetime.now().second
drinks_list = set_drinks()
while True:
    if datetime.now().hour != HOUR:
        HOUR = datetime.now().hour
        drink_list = set_drinks()
    drinks_list = press_button(drinks_list)
    for drink in drinks_list:
        drink.update()
    # map(lambda item: item.update(), drinks_list)
    # print(drinks_list[0].x)
    image = image_bg.copy()
    display_drinks(image, drinks_list)
    draw = ImageDraw.Draw(image)

    # blink = not blink
    # change_size_by_button()
    # image_coffee = Image.open("coffee.jpg").resize((CLIP_SIZE, CLIP_SIZE), Image.BICUBIC)
    # image_cocktail = Image.open("cocktail.png").resize((CLIP_SIZE, CLIP_SIZE), Image.BICUBIC)
    # image = image_bg.copy()
    # display_drinks(image)
    # draw = ImageDraw.Draw(image)
    

    #TODO: Lab 2 part D work should be filled in here. You should be able to look in cli_clock.py and stats.py
    
    y = 0
    TIME = time.strftime("%m/%d/%Y %H:%M:%S")

    # Display image.
    disp.image(image, rotation)
    # time.sleep(1)
