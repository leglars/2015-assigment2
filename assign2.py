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
import statistics 


class AnimalDataPlotApp(object):

    def __init__(self, master):

        self._master = master
        self._data = AnimalData()
        self._filename = ""

        self._master.title("AnimalDataPlotApp")


        # create the menu
        menu_bar = tk.Menu(self._master)
        self._master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)

        self._left_frame = tk.Frame(self._master, background="white")
        self._right_frame = tk.Frame(master, background="red")

        # right frame start from here
        self._data_display_frame = tk.Frame(self._right_frame)
        self._data_display = DataDisplay(self._data_display_frame)
        self._data_display_frame.pack(fill=tk.X)
        self._Plotter = Plotter(self._right_frame, self._data, self._data_display)

        # left_frame start from here
        tk.Label(self._left_frame, text="Animal Data Sets").pack(fill=tk.X, expand=False)  # first label
        self._SelectionBox = SelectionBox(self._left_frame, self._data)  # init selectionBox

        self._left_button_frame = tk.Frame(self._left_frame)
        self._SelectionButtonFrame = SelectionButtonFrame(self._left_button_frame, self._SelectionBox, self._data, self._Plotter, self._master)
        self._SelectionButtonFrame.add_button()
        self._SelectionButtonFrame.pack(side=tk.TOP, expand=False, fill=tk.X)
        self._left_button_frame.pack()

        self._SelectionBox.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self._left_frame.pack(fill=tk.Y, side=tk.LEFT, anchor=tk.NW)
        # left frame end



        # right frame pack from here
        # self._data_display.pack(fill=tk.X, side=tk.TOP, expand=True)
        self._Plotter.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self._right_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        # close window
        self._master.protocol("WM_DELETE_WINDOW", self.close)

    def open_file(self):
        self._filename = filedialog.askopenfilename()

        if self.check(self._filename):
            self._data.load_data(self._filename)
            self._Plotter.plot_animals_data()
            self._SelectionBox.draw()

    def check(self, filename):
        base = os.path.basename(filename)
        if not base.endswith('.csv'):
            if base:
                msg = filename + " is not a suitable data file"
                messagebox.showerror(title="File Error", message=msg)
                return False
            else: # choose no file
                return False

        animal = base.replace(".csv", "")
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
            weights_min.append(animal_data.get_weight_range()[0])
            weights_max.append(animal_data.get_weight_range()[1])
        if heights_min:
            return min(heights_min), max(heights_max), min(weights_min), max(weights_max)

    def to_tabbed_string(self, index):
        if self._selected[index] == 1:
            return LABEL_FORMAT.format(self._animals_list[index],
                                       len(self.get_animal(self._animals_list[index])._points),
                                       "Visible")
        else:
            return LABEL_FORMAT.format(self._animals_list[index],
                                       len(self.get_animal(self._animals_list[index])._points),
                                       "Hidden")


class Plotter(tk.Canvas):

    def __init__(self, master, data, data_frame):
        super(Plotter, self).__init__(master, bg="white", width=650)
        self._data = data
        self._data_frame = data_frame
        self._width = None
        self._high = None
        self._translator = None
        self._height = 0.0
        self._weight = 0.0
        self._x = 0.0
        self._y = 0.0
        self._dot_width = 5

        self.bind("<Configure>", self.can_resize)
        self.bind("<Motion>", self.mouse_move)
        self.bind("<Leave>", self.mouse_leave)

    def plot_animals_data(self):
        """ the main function of this programme. draw the all lines in the plot required,

            plot_station_data() --> None
        """
        self.delete(tk.ALL)

        ranges = self._data.get_ranges()
        if ranges:
            self._translator = CoordinateTranslator(self._width, self._high, *ranges)

        # get station data points
        for index, animal in enumerate(self._data.get_animal_names()):
            animal_data = self._data.get_animal(animal)
            data_points = animal_data.get_data_points()

            if self._data.is_selected(index):

                for d in data_points:
                    height = d[0]
                    weight = d[1]
                    start_x, start_y = self._translator.get_coords(height, weight)
                    start_x -= 2
                    start_y -= 2
                    end_x, end_y = start_x + self._dot_width, start_y + self._dot_width
                    self.create_rectangle(start_x, start_y, end_x, end_y, fill=COLOURS[index], outline="")
        if self._x and self._y:
            self.draw_line()

    def draw_line(self):
        ranges = self._data.get_ranges()

        # horizontal line
        start_x, start_y = 0, self._y
        end_x, end_y = 10000, self._y
        self.create_line(start_x, start_y, end_x, end_y, fill='black')

        #vertical line
        start_x, start_y = self._x, 0
        end_x, end_y = self._x, 10000
        self.create_line(start_x, start_y, end_x, end_y, fill='black')

    def can_resize(self, event):
        """ it is to catch the resize root frame event for canvas which binds with canvas.

        can_resize(event) --> None
        """
        self._width = event.width
        self._high = event.height
        self.plot_animals_data()

    def mouse_move(self, event):
        if self._data.get_animal_names():
            self._x = event.x
            self._y = event.y
            self.plot_animals_data()

            self._height = round(self._translator.get_height(self._x), 2)
            self._weight = round(self._translator.get_weight(self._y), 2)
            self._data_frame.draw(self._height, self._weight)

    def mouse_leave(self, event):
        self._x = 0.0
        self._y = 0.0
        self.plot_animals_data()


class DataDisplay(tk.Frame):

    def __init__(self, master):

        self._master = master
        self._label = tk.Label(self._master, text="")
        self._label.pack(fill=tk.X, expand=True)



    def draw(self, height, weight):
        label = "Height: " + str(height) + "cm,  Weight: " + str(weight) + "kg"
        self._label.configure(text=label)


class SelectionBox(tk.Listbox):

    def __init__(self, master, data):
        super(SelectionBox, self).__init__(master, bg="white")

        self._master = master
        self._data = data

    def draw(self):

        name_list = self._data.get_animal_names()
        list_size = self.size()

        if name_list:
            if list_size:
                for index in range(list_size):
                    self.delete(0)
            for index, name in enumerate(name_list):
                self.insert(index, self._data.to_tabbed_string(index))
                self.configure(font=SELECTION_FONT)
                self.itemconfig(index, foreground=COLOURS[index])


class SelectionButtonFrame(tk.Frame):

    def __init__(self, master, selection_box, data, plotter, root):
        super().__init__(master)

        self._master = master
        self._root =root
        self._selection = None
        self._deselection = None
        self._summery = None

        self._selection_box = selection_box
        self._data = data
        self._plotter = plotter

        self._summery_window_opened = False

    def add_button(self):
        self._selection = tk.Button(self._master, text="  Selection  ")
        self._selection.pack(fill=tk.X, side=tk.LEFT)
        self._deselection = tk.Button(self._master, text="  Deselection  ")
        self._deselection.pack(fill=tk.X, side=tk.LEFT)
        self._summery = tk.Button(self._master, text="  Summery  ")
        self._summery.pack(fill=tk.X, side=tk.LEFT)

        self._selection.bind("<Button-1>", self.set_selection)
        self._deselection.bind("<Button-1>", self.set_deselection)
        self._summery.bind("<Button-1>", self.show_summary)

    def set_selection(self, event):
        if self._data.get_animal_names() and self._selection_box.curselection():
            index = self._selection_box.curselection()[0]
            self._data.select(index)
            self._plotter.plot_animals_data()
            self._selection_box.draw()

    def set_deselection(self, event):
        if self._data.get_animal_names() and self._selection_box.curselection():
            index = self._selection_box.curselection()[0]
            self._data.deselect(index)
            self._plotter.plot_animals_data()
            self._selection_box.draw()

    def show_summary(self, event):
        if not self._summery_window_opened:
            summary = SummaryWindow(self._root, self._data, self)
            summary.summarise(self._selection_box.curselection()[0])
            self._summery_window_opened = True

    def close_summary_window(self):
        self._summery_window_opened = False


class SummaryWindow():

    def __init__(self, master, data, selection_button_frame):
        self._summary_window = tk.Toplevel(master)

        self._data = data
        self._selection_button_frame = selection_button_frame
        self._summary_window.title("Animal Statistic Summary")
        self._frame = tk.Frame(self._summary_window)
        self._frame.pack()


        self._animalNameLabel = tk.Label(self._frame, text = "")
        self._animalNameLabel.pack()
        self._dataPointsLabel = tk.Label(self._frame, text = "")
        self._dataPointsLabel.pack()
        self._weightMeansLabel = tk.Label(self._frame, text = "")
        self._weightMeansLabel.pack()
        self._heightMeansLabel = tk.Label(self._frame, text = "")
        self._heightMeansLabel.pack()
        self._weightStdLabel = tk.Label(self._frame, text = "")
        self._weightStdLabel.pack()
        self._heightStdLabel = tk.Label(self._frame, text = "")
        self._heightStdLabel.pack()

        self._summary_window.protocol("WM_DELETE_WINDOW", self.close)

    def summarise(self, index):
        animal_name = self._data.get_animal_names()[index]
        points = self._data.get_animal(animal_name).get_data_points()
        data_points = len(points)

        heights = [x for x, y in points]
        weights = [y for x, y in points]
        weight_mean = round(statistics.mean(weights), 2)
        weight_std = round(statistics.pstdev(weights), 2)
        height_mean = round(statistics.mean(heights), 2)
        height_std = round(statistics.pstdev(heights), 2)

        print(weight_mean, weight_std, height_mean, height_std)

        self._animalNameLabel.config(text="Animal:     " + animal_name)
        self._dataPointsLabel.config(text="Data points:      " + str(data_points))
        self._weightMeansLabel.config(text="Weight means:     " + str(weight_mean))
        self._heightMeansLabel.config(text="Height means:     " + str(height_mean))
        self._weightStdLabel.config(text="Weight std dev:     " + str(weight_std))
        self._heightStdLabel.config(text="Height std dev:     " + str(height_std))

    def close(self):
        self._selection_button_frame.close_summary_window()
        self._summary_window.destroy()



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
