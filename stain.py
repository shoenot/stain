#!/usr/bin/env python3

from numba.core.types import range_state32_type
import hasel
import textwrap
import argparse
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
    if hsl_cond(hsl, hl/360, hu/360, sl/100, su/100, ll/100, lu/100):
        hsl[0] = shift_value(hsl[0], shift_h/360)
        hsl[1] = shift_value(hsl[1], shift_s/100)
        hsl[2] = shift_value(hsl[2], shift_l/100)
    return hsl

@jit
def transform_loop(img_hsl, hl, hu, sl, su, ll, lu, shift_h, shift_s, shift_l):
    for hline in img_hsl:
        for pixel in hline:
            pixel = transform(pixel, hl, hu, sl, su, ll, lu, shift_h, shift_s, shift_l)
    return img_hsl

def shift_image(path, filter_h, filter_s, filter_l, shift_h, shift_s, shift_l, savename):
    hl, hu = filter_h
    sl, su = filter_s
    ll, lu = filter_l
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

def main():
    parser = argparse.ArgumentParser(prog="stain",
                                     description=textwrap.dedent('''\
                                     Filter pixels by h, s, and l values, and then shift those values by a specified amount.
                                     Use the filter options (-fh, -fs, -fl) to set the ranges.
                                     Use the shift options (-s, -ss, -sl) to shift them.
                                     Hues are between 0 and 360. Saturations and Lightnesses are between 0 and 100.
                                     Shifting supports negative values.\n
                                     Example: ./stain.py art.png -fh 30 70 -fs 0 50 -sh 240 -o new_art.png
                                     (Selects pixels in art.png with hues between 30 and 70, saturations between 0 and 50,
                                     shifts the hues by 240 degrees and saves the output in new_art.png)'''),
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage="%(prog)s path [options]")
    parser.add_argument("path", metavar="path", help="Path to png image")
    parser.add_argument("-fh", "--filter_h", nargs=2, type=int, default=[0, 360], metavar=("lower_limit", "upper_limit"))
    parser.add_argument("-fs", "--filter_s", nargs=2, type=int, default=[0, 100], metavar=("lower_limit", "upper_limit"))
    parser.add_argument("-fl", "--filter_l", nargs=2, type=int, default=[0, 100], metavar=("lower_limit", "upper_limit"))
    parser.add_argument("-sh", "--shift_h", type=int, default=0, metavar="shift_h")
    parser.add_argument("-ss", "--shift_s", type=int, default=0, metavar="shift_s")
    parser.add_argument("-sl", "--shift_l", type=int, default=0, metavar="shift_l")
    parser.add_argument("-o", "--output", metavar="output_path", default=False)
    args = parser.parse_args()
    path = Path(args.path)
    if args.output:
        try:
            newpath = Path(args.output)
            if newpath.suffix.lower() != ".png":
                print("Output file must have a png extension")
                exit()
        except Exception as e:
            print("Please provide a valid output path")
            exit()
    else:
        newpath = path.with_stem(path.stem + "_shifted")
    shift_image(path,
                args.filter_h, args.filter_s, args.filter_l,
                args.shift_h, args.shift_s, args.shift_l,
                newpath)

if __name__ == "__main__":
    main()
