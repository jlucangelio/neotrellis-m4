import random
import time

import adafruit_trellism4

trellis = adafruit_trellism4.TrellisM4Express()
NUM_BUTTONS = trellis.pixels.width * trellis.pixels.height

WHITE = (255, 255, 255)
EXPLODE_DELAY = 0.2
FLASH_DELAY = 0.1

ALL_POSITIONS = [[]]

def wheel(pos):
    if pos < 0 or pos > 255:
        return 0, 0, 0
    if pos < 85:
        return int(255 - pos * 3), int(pos * 3), 0
    if pos < 170:
        pos -= 85
        return 0, int(255 - pos * 3), int(pos * 3)
    pos -= 170
    return int(pos * 3), 0, int(255 - (pos * 3))


def set_all_dark(pixels):
    pixels.fill((0, 0, 0))


def set_all_leds_off(leds, pixels):
    leds.clear()
    for x in range(pixels.width):
        leds.append([])
        for y in range(pixels.height):
            leds[x].append(False)


def set_random_half_on(leds, pixels):
    pixels_on = set()
    while len(pixels_on) < NUM_BUTTONS / 2:
        x = random.randint(0, pixels.width - 1)
        y = random.randint(0, pixels.height - 1)
        if (x, y) in pixels_on:
            continue
        pixels_on.add((x, y))
        pixel_index = ((x + (y * 8)) * 256 // 32)
        pixels[x, y] = wheel(pixel_index & 255)
        leds[x][y] = True
    return len(pixels_on)


def explode(pixels):
    for x in range(2):
        for y in range(2):
            gray = 155
            pixels[x+3, y+1] = (gray, gray, gray)

    time.sleep(EXPLODE_DELAY)
    set_all_dark(pixels)

    time.sleep(EXPLODE_DELAY)
    for x in range(4):
        for y in range(4):
            if x > 0 and x < 3 and y > 0 and y < 3:
                continue
            gray = 200
            pixels[x+2, y] = (gray, gray, gray)

    time.sleep(EXPLODE_DELAY)
    set_all_dark(pixels)

    time.sleep(EXPLODE_DELAY)
    for x in range(6):
        for y in range(4):
            if x > 0 and x < 5 and y > 0 and y < 3:
                continue
            gray = 228
            pixels[x+1, y] = (gray, gray, gray)

    time.sleep(EXPLODE_DELAY)
    set_all_dark(pixels)

    time.sleep(EXPLODE_DELAY)
    for x in range(pixels.width):
        pixels[x, 0] = WHITE
        pixels[x, pixels.height - 1] = WHITE
    pixels[0, 1] = WHITE
    pixels[0, 2] = WHITE
    pixels[pixels.width - 1, 1] = WHITE
    pixels[pixels.width - 1, 2] = WHITE

    time.sleep(EXPLODE_DELAY)
    set_all_dark(pixels)


def flash_col(col, pixels):
    print("flash col %d" % col)
    time.sleep(FLASH_DELAY)
    white = (255, 255, 255)
    for r in range(4):
        pixels[col, r] = WHITE
    time.sleep(FLASH_DELAY)
    for r in range(4):
        pixel_index = ((col + (r * 8)) * 256 // 32)
        pixels[col, r] = wheel(pixel_index & 255)


def count_columns(leds, width):
    return dict([(i, sum([int(v) for v in led_on[i]])) for i in range(width)])


led_on = []
set_all_leds_off(led_on, trellis.pixels)
num_on = set_random_half_on(led_on, trellis.pixels)
col_count = count_columns(led_on, trellis.pixels.width)
print("num_on", num_on)

current_press = set()

while True:
    pressed = set(trellis.pressed_keys)

    for press in pressed - current_press:
        x, y = press

        if not led_on[x][y]:
            print("Turning on:", press)
            pixel_index = ((x + (y * 8)) * 256 // 32)
            trellis.pixels[x, y] = wheel(pixel_index & 255)
            led_on[x][y] = True
            num_on += 1
            print("num_on", num_on)
            col_count[x] += 1
            print("col_count[%d]" % x, col_count[x])

            if num_on == trellis.pixels.width * trellis.pixels.height:
                print("all set")
                set_all_dark(trellis.pixels)
                explode(trellis.pixels)
                set_all_leds_off(led_on, trellis.pixels)
                num_on = set_random_half_on(led_on, trellis.pixels)
                col_count = count_columns(led_on, trellis.pixels.width)
            elif col_count[x] == 4:
                flash_col(x, trellis.pixels)

        else:
            print("Turning off:", press)
            trellis.pixels[x, y] = (0, 0, 0)
            led_on[x][y] = False
            num_on -= 1
            print("num_on", num_on)
            col_count[x] -= 1
            print("col_count[%d]" % x, col_count[x])

            if num_on == 0:
                time.sleep(0.5)
                num_on = set_random_half_on(led_on, trellis.pixels)
                col_count = count_columns(led_on, trellis.pixels.width)


    current_press = pressed
