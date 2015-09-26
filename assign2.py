#!/usr/bin/env python3
###################################################################
#
#   CSSE1001/7030 - Assignment 2
#
#   Student Username: s4340998
#
#   Student Name: Xi Chen
#
###################################################################

#####################################
# Support given below - DO NOT CHANGE
#####################################

from assign2_support import *

#####################################
# End of support 
#####################################

# Add your code here

from collections import OrderedDict


class AnimalDataPlotApp(object):

    def __init__(self, master):

        self._master = master
        self._data = AnimalData()
        self._filename = ""

        master.title("AnimalDataPlotApp")

        # create the menu
        menu_bar = tk.Menu(master)
        master.config(menu = menu_bar)

        file_menu = tk.Menu(menu_bar)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)

        # close window
        master.protocol("WM_DELETE_WINDOW", self.close)

        # plotter window
        self._Plotter = Plotter(master, self._data)
        self._Plotter.pack(side = tk.RIGHT, fill = tk.Y, expand = False)

    def open_file(self):
        self._filename = filedialog.askopenfilename()

        if self.check(self._filename):
            self._data.load_data(self._filename)
            self._Plotter.plot_animal_data()
            self._SelectionBox.add_button()

    def check(self, filename):
        base = os.path.basename(filename)
        if not base.endswith('.txt'):
            if base:
                msg = filename + " is not a suitable data file"
                messagebox.showerror(title="File Error", message=msg)
                return False
            else:
                return False

        animal = base.replace(".txt", "")
        animals = self._data.get_animal_names()
        if len(animals) != 0:
            if animal in animals:
                msg = "The data of " + animal + " has been loaded"
                messagebox.showwarning(title="Re-loading data file", message=msg)
                return False
        return True

    def close(self):
        self._master.destroy()


class AnimalData (object):

    def __init__(self):
        self._animals_list = []
        self._animals_data = []
        self._selected = []

    def load_data(self, filename):
        self._animals_data.append(AnimalDataSet(filename))
        self._selected.append(1)
        animal_name = AnimalDataSet(filename).get_name()
        self._animals_list.append(animal_name)

    def get_animal_names(self):
        return self._animals_list

    def get_animal(self, animal):
        temp = OrderedDict()
        for i, s in enumerate(self._animals_list):
            temp[s] = self._animals_data[i]

        return temp[animal]

    def is_selected(self, index):
        if self._selected[index] == 1:
            return True
        return False

    def select(self, index):
        if self._selected[index] == 0:
            self._selected[index] = 1

    def deselect(self, index):
        if self._selected[index] == 1:
            self._selected[index] = 0

    def get_ranges(self):
        heights_min = []
        heights_max = []
        weights_min = []
        weights_max = []

        for animal_data in self._animals_data:
            heights_min.append(animal_data.get_height_range()[0])
            heights_max.append(animal_data.get_height_range()[1])
            weights_min.append(animal_data.get_width_range()[0])
            weights_max.append(animal_data.get_height_range()[1])
        if heights_min:
            return min(heights_min), max(heights_max), min(weights_min), max(weights_max)

    def to_tabbed_string(self, index):
        pass


class Plotter(tk.Canvas):

    def __init__(self, master, data):
        super(Plotter, self).__init__(master, bg="white", relief=tk.SUNKEN)
        self._data = data
        self._width = None
        self._height = None


class SelectionBox():

    def __init__(self):
        pass


class SummaryWindow():

    def __init__(self):
        pass



##################################################
# !!!!!! Do not change (or add to) the code below !!!!!
# 
# This code will run the interact function if
# you use Run -> Run Module  (F5)
# Because of this we have supplied a "stub" definition
# for interact above so that you won't get an undefined
# error when you are writing and testing your other functions.
# When you are ready please change the definition of interact above.
###################################################

def main():
    root = tk.Tk()
    app = AnimalDataPlotApp(root)
    root.geometry("800x400")
    root.mainloop()

if __name__ == '__main__':
    main()