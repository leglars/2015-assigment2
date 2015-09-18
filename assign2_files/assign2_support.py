import tkinter as tk
import os.path
from random import choice
from tkinter import filedialog
from tkinter import messagebox

# colours for drawing lines and text
COLOURS = ['#1505ff', '#e80606', '#1ace10', '#ffff16', '#ffa405', '#b116ff',\
           '#16dcff','#ef16ff']
LABEL_FORMAT = "{0:<15}{1:<5}{2:<10}"
PAD_FACTOR = 0.1
SELECTION_FONT = s_font = ("Courier", 10)


class FileExtensionException(Exception):
    pass

def load_data_set(filename):
    """
    Loads data set from the given filename.

    Precondition: filename exists and contains valid data.

    load_data_set(str) -> list<tuple<float, float> >
    """

    f = open(filename, "r")
    data = []
    for line in f:
        values = line.strip().split(',', 1)
        data.append((float(values[0]), float(values[1])))
    f.close()
    return data

class AnimalDataSet(object):
    """
    A class responsible for the storing of Animal height and weight data
    """
    def __init__(self, filename):
        """
        Constructor: AnimalDataSet(str)
        """
        self._points = load_data_set(filename)
        all_points = [x for x, y in self._points], [y for x, y in self._points]
        self._mins = (min(all_points[0]), min(all_points[1]))
        self._maxs = (max(all_points[0]), max(all_points[1]))

        base = os.path.basename(filename)
        if not base.endswith('.csv'):
            raise(FileExtensionException())
        self._name = base.replace(".csv", "")

    def get_height_range(self):
        """
        Returns the range of height data in the set.

        get_height_range() -> tuple<float, float>
        """
        return self._mins[0], self._maxs[0]

    def get_weight_range(self):
        """
        Returns the range of weight data in the set.

        get_weight_range() -> tuple<float, float>
        """
        return self._mins[1], self._maxs[1]

    def get_data_points(self):
        """
        Returns all of the data points in the set.

        get_data_points() -> list<tuple<float, float> >
        """
        return self._points

    def get_name(self):
        """
        Returns the name of the data set.

        get_name() -> str
        """
        return self._name

    def __repr__(self):
        return "AnimalDataSet({0})".format(self._name)

class CoordinateTranslator(object):
    """
    A class which manages translation of data values into canvas-usable
    coordinates.

    The application manages real-world data (height, weight), but the Canvas 
    drawings require (x, y) coordinates. This class converts between the two.
    """

    def __init__(self, width, height, min_height, max_height,
                min_weight, max_weight):
        """
        Create a CoordinateTranslator with the given canvas width/height,
        the smallest and largest heights and 
        the smallest and largest weights

        Constructor: CoordinateTranslator(int, int, float, float, float, float)
        """
        self._min_height = min_height - PAD_FACTOR * (max_height - min_height)
        self._max_height = max_height + PAD_FACTOR * (max_height - min_height)
        self._min_weight = min_weight - PAD_FACTOR * (max_weight - min_weight)
        self._max_weight = max_weight + PAD_FACTOR * (max_weight - min_weight)
        self.resize(width, height)

    def resize(self, width, height):
        """
        Adjust the scaling factors to account for a new width/height.

        After the Canvas resizes, call this method to fix the scaling.
        """
        self._xscale = (self._max_height - self._min_height) / width
        self._yscale = (self._max_weight - self._min_weight) /\
                height
        self._width = width
        self._height = height

    def get_coords(self, height, weight):
        """
        Given a height and weight,
        return (x, y) coordinates to plot

        get_coords(float, float) -> (float, float)
        """
        return ((height - self._min_height) / self._xscale,\
                self._height - (weight - self._min_weight) / self._yscale)

    def get_height(self, x):
        """
        Given an x coordinate on the Canvas, returns the height that it
        corresponds to.

        get_height(float) -> float
        """
        return (x * self._xscale) + self._min_height

    def get_weight(self, y):
        """
        Given a y coordinate on the Canvas, returns the weight that it
        corresponds to.

        get_weight(float) -> float
        """
        return ((self._height - y) * self._yscale) + self._min_weight
