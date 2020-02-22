#!/usr/bin/env python3

# Alexander Brook CS-255 coursework - a script to explore the CThead dataset.

import math
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

import cProfile

class App(tk.Frame):
    Z_LEN = 113
    Y_LEN = 256
    X_LEN = 256

    ZOOM_START = 1
    ZOOM_MIN = 0.1 
    ZOOM_MAX = 2 
    ZOOM_RES = 0.0001

    TOP_VIEW_LBL = "Transverse Plane"
    FRONT_VIEW_LBL = "Coronal Plane"
    SIDE_VIEW_LBL = "Sagittal Plane"

    SLICE_LBL = "<Slice>"
    ZOOM_LBL = "<Zoom>"
    ZOOM_BTN_LBL = "Apply"
    MIP_BTN_LBL = "MIP"

    THUMB_PER_ROW = 30
    THUMB_SF = 0.2
        
    # --PUBLIC METHODS-- 

    def __init__(self, fname, master=None):
        super().__init__(master)
        
        self.cthead = None
        self.pixels = None
        self.load_dataset(fname)
        self.load_widgets()

    def load_widgets(self):
        """Definitions for gui elements"""
        mip_button = tk.Button(self.master, text=self.MIP_BTN_LBL, command=self.mip)
        mip_button.pack()

        self.load_top_view_widgets()
        self.load_front_view_widgets()
        self.load_side_view_widgets()
        self.pack()

    def load_top_view_widgets(self):
        top_group = tk.LabelFrame(self.master, text=self.TOP_VIEW_LBL)
        self.zoom_top = tk.Scale(top_group, from_=self.ZOOM_MIN, to=self.ZOOM_MAX, orient=tk.HORIZONTAL, label=self.ZOOM_LBL, resolution=self.ZOOM_RES)
        self.zoom_top_button = tk.Button(top_group, text=self.ZOOM_BTN_LBL, command=self.resize_top_view)
        self.zoom_top.set(self.ZOOM_START)
        self.scale_top = tk.Scale(top_group, from_=0, to=self.Z_LEN - 1, command=self.update_top_slice, orient=tk.HORIZONTAL, label=self.SLICE_LBL)
        self.top_view = tk.Label(top_group)
        self.top_view.been_resized = False
        self.update_top_slice(0)
        self.zoom_top.pack(anchor="e", fill=tk.X)
        self.zoom_top_button.pack()
        self.scale_top.pack(anchor="e", fill=tk.X)
        self.top_view.pack()
        top_group.pack(side=tk.LEFT)

    def load_front_view_widgets(self):
        front_group = tk.LabelFrame(self.master, text=self.FRONT_VIEW_LBL)
        self.zoom_front = tk.Scale(front_group, from_=self.ZOOM_MIN, to=self.ZOOM_MAX, orient=tk.HORIZONTAL, label=self.ZOOM_LBL, resolution=self.ZOOM_RES) 
        self.zoom_front.set(self.ZOOM_START)
        self.zoom_front_button = tk.Button(front_group, text=self.ZOOM_BTN_LBL, command=self.resize_front_view)
        self.scale_front = tk.Scale(front_group, from_=0, to=self.Y_LEN - 1, command=self.update_front_slice, orient=tk.HORIZONTAL, label=self.SLICE_LBL)
        self.front_view = tk.Label(front_group)
        self.front_view.been_resized = False
        self.update_front_slice(0)
        self.zoom_front.pack(anchor="e", fill=tk.X)
        self.zoom_front_button.pack()
        self.scale_front.pack(anchor="e", fill=tk.X)
        self.front_view.pack()
        front_group.pack(side=tk.LEFT)

    def load_side_view_widgets(self):
        side_group = tk.LabelFrame(self.master, text=self.SIDE_VIEW_LBL)
        self.zoom_side = tk.Scale(side_group, from_=self.ZOOM_MIN, to=self.ZOOM_MAX, orient=tk.HORIZONTAL, label=self.ZOOM_LBL, resolution=self.ZOOM_RES) 
        self.zoom_side.set(self.ZOOM_START)
        self.zoom_side_button = tk.Button(side_group, text=self.ZOOM_BTN_LBL, command=self.resize_side_view)
        self.scale_side = tk.Scale(side_group, from_=0, to=self.X_LEN -1, command=self.update_side_slice, orient=tk.HORIZONTAL, label=self.SLICE_LBL)
        self.side_view = tk.Label(side_group)
        self.side_view.been_resized = False
        self.update_side_slice(0)
        self.zoom_side.pack(anchor="e", fill=tk.X)
        self.zoom_side_button.pack()
        self.scale_side.pack(anchor="e", fill=tk.X)
        self.side_view.pack()
        side_group.pack(side=tk.LEFT)

    def load_dataset(self, fname):
        self.cthead = np.fromfile(fname, dtype="<i2", count=-1, sep="", offset=0)
        mx = np.amax(self.cthead)
        mn = np.amin(self.cthead)
        #def map_rgb(x): return np.round((x - mn) / (mx - mn) * 255).astype(np.uint8)
        def map_rgb(x): return (x - mn) / (mx - mn) * 255
        self.pixels = map_rgb(self.cthead).reshape(self.Z_LEN, self.Y_LEN, self.X_LEN)

    def get_top_slice(self, i):
        return self.pixels[int(i)]

    def get_front_slice(self, i):
        return self.pixels[:, int(i), :]

    def get_side_slice(self, i):
        return self.pixels[:, :, int(i)]

    def set_top_view(self, img):
        img = Image.fromarray(img)
        tk_image = ImageTk.PhotoImage(img)
        self.top_view.configure(image=tk_image)
        self.top_view.image = img
        self.top_view.tk_image = tk_image

    def set_front_view(self, img):
        img = Image.fromarray(img)
        tk_image = ImageTk.PhotoImage(img)
        self.front_view.configure(image=tk_image)
        self.front_view.image = img
        self.front_view.tk_image = tk_image

    def set_side_view(self, img):
        img = Image.fromarray(img)
        tk_image = ImageTk.PhotoImage(img)
        self.side_view.configure(image=tk_image)
        self.side_view.image = img
        self.side_view.tk_image = tk_image

    def update_top_slice(self, i):
        self.zoom_top.set(self.ZOOM_START)
        self.set_top_view(self.get_top_slice(i))
        self.top_view.been_resized = False

    def update_front_slice(self, i):
        self.zoom_front.set(self.ZOOM_START)
        self.set_front_view(self.get_front_slice(i))
        self.front_view.been_resized = False

    def update_side_slice(self, i):
        self.zoom_side.set(self.ZOOM_START)
        self.set_side_view(self.get_side_slice(i))
        self.side_view.been_resized = False
    
    def mip(self):
        self.set_top_view(np.amax(self.pixels, axis=0))
        self.set_front_view(np.amax(self.pixels, axis=1))
        self.set_side_view(np.amax(self.pixels, axis=2))
        
        self.top_view.been_resized = False
        self.front_view.been_resized = False
        self.side_view.been_resized = False

        self.zoom_top.set(self.ZOOM_START)
        self.zoom_front.set(self.ZOOM_START)
        self.zoom_side.set(self.ZOOM_START)

    def resize_top_view(self):
        if self.top_view.been_resized:
            self.top_view.image = self.top_view.unscaled_image
        else:
            self.top_view.unscaled_image = self.top_view.image
            self.top_view.been_resized = True

        orig = self.top_view.image
        sf = float(self.zoom_top.get())
        self.set_top_view(App.resize(orig, sf))

    def resize_front_view(self):
        if self.front_view.been_resized:
            self.front_view.image = self.front_view.unscaled_image
        else:
            self.front_view.unscaled_image = self.front_view.image
            self.front_view.been_resized = True

        orig = self.front_view.image
        sf = float(self.zoom_front.get())
        self.set_front_view(App.resize(orig, sf))

    def resize_side_view(self):
        if self.side_view.been_resized:
            self.side_view.image = self.side_view.unscaled_image
        else:
            self.side_view.unscaled_image = self.side_view.image
            self.side_view.been_resized = True

        orig = self.side_view.image
        sf = float(self.zoom_side.get())
        self.set_side_view(App.resize(orig, sf))

    def get_top_thumbnails(self):
        imgs = [App.thumbnail(self.get_top_slice(i)) for i in range(0,App.Z_LEN)]
        y, x = imgs[0].shape
        App.thumbnails(imgs, y, x, App.Z_LEN)
        return imgs

    def get_front_thumbnails(self):
        pass

    def get_side_thumbnails(self):
        pass

    @staticmethod
    def thumbnails(img_arr, y, x, n):
        collage = Image.new("F", (y*n, x*n))
        collage.show()

    @staticmethod
    def thumbnail(img):
        return App.resize(img, App.THUMB_SF) 

    @staticmethod
    def __lerp(v1, v2, p1, p2, p):
        if v1 == v2 or p1 == p2:
            return v1
        else:
            return v1 + (((v2 - v1) * (p - p1)) // (p2 - p1))

    @staticmethod
    def __berp(old, sf, y, x):
        y /= sf
        min_y = math.floor(y)
        max_y = min(math.ceil(y), old.shape[0] - 1)
        x /= sf
        min_x = math.floor(x)
        max_x = min(math.ceil(x), old.shape[0] - 1)
        top_value = App.__lerp(old[min_y, min_x], old[min_y, max_x], min_x, max_x, x)
        bot_value = App.__lerp((old[max_y, min_x]), old[max_y, max_x], min_x, max_x, x)
        fin_value = App.__lerp(top_value, bot_value, min_y, max_y, y)
        return fin_value

    @staticmethod
    def __direct_map(old, sf, y, x):
        # if it is on the border OR direct map back to the old array
        border = y == 0 or x == 0 or y == (old.shape[0] * sf - 1) or x == (old.shape[1] * sf - 1)
        maps  = np.mod((y/sf), 1) == 0 and np.mod((x/sf), 1) == 0
        return border or maps 

    @staticmethod
    def __closest_pixel(old, sf, y, x):
        return old[min(int(round(y/sf)), old.shape[0]-1), min(int(round(x/sf)), old.shape[1]-1)]
    
    @staticmethod
    def resize(img, sf):
        """Return an image that is created by scaling an image (img) by a scale factor (sf)""" 
        return App.resize_bl(img, sf)

    @staticmethod
    def resize_nn(img, sf):
        """Resize an image using the nearest neighbour algorithm"""
        old = np.asarray(img)
        new_shape = (int(old.shape[0] * sf) + 1, int(old.shape[1] * sf) + 1)
        new = np.fromfunction(np.vectorize(lambda y, x: App.__closest_pixel(old, sf, y, x)), new_shape)
        return new

    @staticmethod
    def resize_bl(img, sf):
        """Resize an image using the bilinear interpolation algorithm"""
        old = np.asarray(img)
        new_shape = (int(old.shape[0] * sf), int(old.shape[1] * sf))
        new = np.fromfunction(np.vectorize(
            lambda y, x: App.__closest_pixel(old, sf, y, x) if App.__direct_map(old, sf, y, x)
            else App.__berp(old, sf, y, x)), new_shape)
        return new

pr = cProfile.Profile()
pr.enable()
app = App("CThead")
app.get_top_thumbnails()
app.mainloop()
pr.disable()
pr.print_stats()
