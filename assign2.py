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

        #create the menu
        menu_bar = tk.Menu(master)
        master.config(menu = menu_bar)

        file_menu = tk.Menu(menu_bar)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)

        #close window
        master.protocol("WM_DELETE_WINDOW", self.close)

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

class AnimalData ():


    def __init__(self):
        pass


    def load_data(self, filename):
        pass


    def get_animal_names(self):
        pass


    def get_animal(self, animal):
        pass


    def is_selected(self, index):
        pass


    def select(self, index):
        pass


    def deselect(self, index):
        pass


    def get_ranges(self):
        pass


    def to_tabbed_string(self, index):
        pass



class Plotter():

    def __init__(self):
        pass



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