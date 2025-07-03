#!/usr/bin/env python3

import sys
import hasel
import numpy as np 
from PIL import Image
from numba import jit
from pathlib import Path

def load_img(path):
    img = np.array(Image.open(path).convert("RGB"))
    return img

@jit
def conditions(x, lower, upper):
    lower, upper = lower, upper
    if x >= lower and x <= upper:
        return True
    else:
        return False 

@jit
def hsl_cond(hsl, hl, hu, sl, su, ll, lu):
    if conditions(hsl[0], hl, hu) and \
       conditions(hsl[1], sl, su) and \
       conditions(hsl[2], ll, lu):
        return True
    else:
        return False

@jit
def shift_value(x, shift):
    x += shift
    if x > 1:
        x -= 1
    elif x < 0:
        x += 1
    return x

@jit
def transform(hsl, hl, hu, sl, su, ll, lu, shift_h, shift_s, shift_l):
    if hsl_cond(hsl, hl/360, hu/360, sl, su, ll, lu):
        hsl[0] = shift_value(hsl[0], shift_h/360)
        hsl[1] = shift_value(hsl[1], shift_s)
        hsl[2] = shift_value(hsl[2], shift_l)
    return hsl

@jit
def transform_loop(img_hsl, hl, hu, sl, su, ll, lu, shift_h, shift_s, shift_l):
    for hline in img_hsl:
        for pixel in hline:
            pixel = transform(pixel, hl, hu, sl, su, ll, lu, shift_h, shift_s, shift_l)
    return img_hsl

def shift_image(path, hl, hu, sl, su, ll, lu, shift_h, shift_s, shift_l, savename):
    img = load_img(path)
    print("loaded image")
    img_hsl = hasel.rgb2hsl(img)
    print("converted to hsl")
    img_hsl_new = transform_loop(img_hsl, hl, hu, sl, su, ll, lu, shift_h, shift_s, shift_l)
    print("completed shift")
    img_rgb = hasel.hsl2rgb(img_hsl_new)
    print("converted to rgb")
    new_img = Image.fromarray(img_rgb).convert("RGBA")
    print("created new image")
    new_img.save(savename)

if __name__ == "__main__":
    try:
        path = Path(sys.argv[1])
        hl, hu = int(sys.argv[2]), int(sys.argv[3])
        sl, su = float(sys.argv[4]), float(sys.argv[5])
        ll, lu = float(sys.argv[6]), float(sys.argv[7])
        shift_h, shift_s, shift_l = int(sys.argv[8]), float(sys.argv[9]), float(sys.argv[10])
        new = path.with_stem(path.stem + "_shifted")
        shift_image(path, hl, hu, sl, su, ll, lu, shift_h, shift_s, shift_l, new)
    except Exception as e:
        print("Please provide a valid command")
        print(e)
