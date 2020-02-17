# -*- coding: utf-8 -*-
import Image


def resize_image( pathname, width=None, height=None ):
    img = Image.open( pathname )
    img_width = img.size[ 0 ]
    img_height = img.size[ 1 ]
    if width and height:
        w = width
        h = height
        img_resized = img.resize( (w, h), Image.ANTIALIAS )
        img_resized.save( pathname )
        return w, h

    if width:
        ratio = float( width ) / img_width
    elif height:
        ratio = float( height ) / img_height
    if ratio < 1.0:
        w = int( img_width * ratio )
        h = int( img_height * ratio )
        img_resized = img.resize( (w, h), Image.ANTIALIAS )
        img_resized.save( pathname )
        return w, h
    return None, None

