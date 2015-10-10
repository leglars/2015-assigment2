import tkinter as tk
from assign2_support import *
from tkinter import filedialog
from tkinter import messagebox
from functools import reduce
import statistics

class AnimalData(object):
    """
    A class to store the animal data(height, weight, range, status, etc) for each animal
    """
    def __init__(self):
        self._animal_names = []
        self._flag = []
        self._animal_obj = []

    def load_data(self,filename):
        """
        Load data from the given files

        load_data(str) --> list(int)
        """
        animal_name = os.path.basename(filename.replace('.csv', ''))

        if animal_name not in self._animal_names:
            self._flag.append(1)
            self._animal_obj.append(AnimalDataSet(filename))
            self._animal_names.append(animal_name)
        else:
            for i, s in enumerate(self._animal_names):
                if s == animal_name:
                    self._flag[i] = 1
                else:
                    self._flag[i] = 0
        return load_data_set(filename)

    def get_animal_names(self):
        """
        Return the loaded animal names

        get_animal_names() --> list(str)
        """
        return self._animal_names

    def get_animal(self, animal):
        """
        Returns the animal data set of the animal

        get_animal(str) --> str
        """
        reference = {}
        for i in self._animal_names:
            reference[i] = AnimalDataSet(i+'.csv')
        return reference[animal]

    def get_animals(self):
        """
        Returns the dictionary that store the reference between animal and its data set

        get_animals(str) --> dict(str:str)
        """
        reference = {}
        for i in self._animal_names:
            reference[i] = AnimalDataSet(i+'.csv')
        return reference
    
    def is_selected(self, index):
        """
        Judge if the animal of the given index is selected or not

        is_selected(int) --> boolean
        """
        if self._flag[index] == 1:
            return True
        return False
        
    def select(self, index):
        """
        Select an animal with the given index

        select(int) --> None
        """
        self._flag[index] = 1

    def deselect(self, index):
        """
        Deselect an animal with the given index

        deselect(int) --> None
        """
        self._flag[index] = 0       
        
    def get_ranges(self):
        """
        Returns the ranges of the height and weight of the selected animals.

        get_ranges() --> tuple(str,str,str,str)
        """
        list1 = []
        list2 = []
        list3 = []
        list4 = []

        if 1 not in self._flag:
            return None,None,None,None

        else:
            for i,j in enumerate(self._flag):
                if j == 1:
                    list1.append(self._animal_obj[i]._mins[0])
                    list2.append(self._animal_obj[i]._maxs[0])
                    list3.append(self._animal_obj[i]._mins[1])
                    list4.append(self._animal_obj[i]._maxs[1])

            min_height = min(list1)
            max_height = max(list2)
            min_weight = min(list3)
            max_weight = max(list4)

            return min_height, max_height, min_weight, max_weight

    def to_tabbed_string(self, index):
        """
        Show the name, points, and display status of the animal with the given index

        to_tabbed_string(int) --> str
        """
        if self._flag[index] == 1:
            return '{0: <20}{1: <10}{2: <15}'.format(self._animal_names[index],\
                                                     len(AnimalDataSet(self._animal_names[index]+'.csv')._points),\
                                                     'Visible')
        else:
            return '{0: <20}{1: <10}{2: <15}'.format(self._animal_names[index],\
                                                     len(AnimalDataSet(self._animal_names[index]+'.csv')._points),\
                                                     'Hidden')

        
class Plotter(tk.Canvas):
    """
    This class is responsible for doing the plotting and it's inherited from Canvas
    """
    def __init__(self, master, data, app):
        """
        Create a plotter with the given master, bind the mouse event

        Constructor: Plotter(tk(object), AnimalData(object), AnimalDataPlotApp(object))
        """
        super().__init__(master, bg='white')
        self._master = master
        self._data = data
        self._app = app
        
        self._height = None
        self._width = None
        self._convert = None
        
        self.bind('<Configure>', self.resize)
        self.bind('<Motion>', self.movemouse)
        self.bind('<Leave>', self.deleteline)

    def plot_animal_data(self):
        """
        Plot the loaded animal data on canvas, draw small rectangles

        plot_animal_data() --> None
        """
        self.delete(tk.ALL)
        ranges = self._data.get_ranges()
        self._convert = CoordinateTranslator(self._width, self._height, *ranges)

        radius = 5

        for i in list(self._data.get_animals().keys()):
            animal_obj = self._data.get_animals()[i]
            animal_points = animal_obj.get_data_points()
            #coords_list = []

            names= self._data.get_animal_names()
            pos = names.index(i)

            colour = COLOURS[pos]

            if self._data.is_selected(pos):
                for c, j in enumerate(animal_points):
                    startX = self._convert.get_coords(j[0],j[1])[0]-radius/2
                    startY = self._convert.get_coords(j[0],j[1])[1]-radius/2
                    endX = self._convert.get_coords(j[0],j[1])[0]+radius/2
                    endY = self._convert.get_coords(j[0],j[1])[1]+radius/2
                    self.create_rectangle([startX, startY, endX, endY], width=0, fill=colour)

    def resize(self, e):
        """
        Plot the loaded animal data when resizing canvas

        resize() --> None
        """
        self._width = e.width
        self._height = e.height
        if (len(self._data.get_animals())!=0):
            self.plot_animal_data()

    def movemouse(self, e):
        """
        Create two lines when hover on the canvas, convert the coordinates of the position that
        mouse hovers at to height and weight

        movemouse() --> None
        """
        self.delete('vline')
        self.delete('hline')
        self._x = e.x
        self._y = e.y
        
        ranges = self._data.get_ranges()
        self._convert = CoordinateTranslator(self._width, self._height, *ranges)
        
        vertical_startX = self._x
        vertical_startY = 0
        vertical_endX = self._x
        vertical_endY = 10000
        self.create_line([vertical_startX, vertical_startY, vertical_endX, vertical_endY],\
                         width=0, tag="vline", fill="black")

        horizontal_startX = 0
        horizontal_startY = self._y
        horizontal_endX = 10000
        horizontal_endY = self._y
        self.create_line([horizontal_startX, horizontal_startY, horizontal_endX, horizontal_endY],\
                         tag="hline", width=0, fill="black")

        height = round(self._convert.get_height(self._x),2)
        weight = round(self._convert.get_weight(self._y),2)
        self._app.displayhwLabel(height,weight)

    def deleteline(self, e):
        """
        Delete the two lines when the cursor leaves canvas

        deleteline() --> None
        """
        self.delete('vline')
        self.delete('hline')

    
class SelectionBox(tk.Listbox):
    """
    This class is responsible for displaying the list of animal data sets and should inherit from
    Listbox.
    """
    def __init__ (self, master, data, plotter):
        """
        Create a selection with the given master

        Constructor: SelectionBox(tk(object), AnimalData(object), Plotter(object))
        """
        super().__init__(master)
        self._master = master
        self._data = data
        self._plotter = plotter

    def add_list(self):
        """
        Add items to the listbox

        add_list() --> None
        """
        self.delete(0, tk.END)
        for i, s in enumerate(self._data.get_animal_names()):
            self.insert(i, self._data.to_tabbed_string(i))
            self.configure(font = SELECTION_FONT)
            self.itemconfig(i, foreground=COLOURS[i])

    def get_selected(self):
        """
        Get the index of the selected item

        get_selected() --> int
        """
        selected_index = int(self.curselection()[0])
        return selected_index
    
    def select_item(self):
        """
        Select an item of the listbox

        select_item() --> None
        """
        selected_index = int(self.curselection()[0])
        self._data._flag[selected_index] = 1
        self.add_list()
        self._plotter.plot_animal_data()

    def deselect_item(self):
        """
        Deselect an item of the listbox

        deselect_item() --> None
        """
        selected_index = int(self.curselection()[0])
        self._data._flag[selected_index] = 0
        self.add_list()
        self._plotter.plot_animal_data()

    
class SummaryWindow(tk.Toplevel):
    """
    Show the data summary of a specific animal on a child window
    """
    def __init__(self, master, data):
        """
        Create a child window

        Constructor: SummaryWindow(tk(object), AnimalData(object))
        """
        self._master = master
        self._frame = tk.Frame(self._master)
        self._frame.pack()
        self._master.title('Animal Statistic Summary')
        self._data = data

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

    def summarise(self, index):
        """
        Summarise the statistics of an animal

        summarise(int) --> None
        """
        self._animal_names = self._data.get_animal_names()[index]
        self._data_points = len(load_data_set(self._data.get_animal_names()[index]+'.csv'))
        self._weight_list = [i[1] for i in load_data_set(self._data.get_animal_names()[index]+'.csv')]
        self._weight_mean = round(reduce(lambda x,y:x+y, self._weight_list) / len(self._weight_list),2)
        self._weight_std = round(statistics.pstdev(self._weight_list),2)
        self._height_list = [i[0] for i in load_data_set(self._data.get_animal_names()[index]+'.csv')]
        self._height_mean = round(reduce(lambda x,y:x+y, self._height_list) / len(self._height_list),2)
        self._height_std = round(statistics.pstdev(self._height_list),2)

    def display_data(self):
        """
        Display the labels on the summary window

        display_data() --> None
        """
        self._animalNameLabel.config(text = "Animal: " + self._animal_names)
        self._dataPointsLabel.config(text = "Data points:      " + str(self._data_points))
        self._weightMeansLabel.config(text = "Weight means:     " + str(self._weight_mean))
        self._heightMeansLabel.config(text = "Height means:     " + str(self._height_mean))
        self._weightStdLabel.config(text = "Weight std dev:     " + str(self._weight_std))
        self._heightStdLabel.config(text = "Height std dev:     " + str(self._height_std))


class AnimalDataPlotApp(object):
    """
    This is the top-level class for the GUI. This is responsible for creating
    and managing instances of the above classes
    """
    def __init__(self, master):
        """
        Creating the instances of the above classes

        Constructor: AnimalDataPlotApp(object)
        """
        self._master = master
        self._master.title('AnimalDataPlotApp')
        self._data = AnimalData()

        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open", command=self.open_file)

        self._rFrame = tk.Frame(self._master)

        self._Plotter = Plotter(self._rFrame, self._data, self)
        self._trFrame = tk.Frame(self._rFrame)
        self._dimentionsLabel = tk.Label(self._trFrame,  text='')
        self._dimentionsLabel.pack(fill=tk.X, expand=True)
        self._trFrame.pack(side= tk.TOP,expand= False)
        #self._dimentions = tk.Label('Height:'+str(self.))
        self._Plotter.pack(side = tk.TOP, fill= tk.BOTH, expand = 1)

        self._rFrame.pack(side = tk.RIGHT, expand=True, fill = tk.BOTH)


        self._lFrame = tk.Frame(self._master, width=10)

        self._tlFrame = tk.Frame(self._lFrame)
        self._labelADS = tk.Label(self._tlFrame, text='Animal Data Sets')
        self._labelADS.pack(fill=tk.X)
        self._tlFrame.pack(side= tk.TOP,expand= False)

        self._clFrame = tk.Frame(self._lFrame)
        self._SelectionBox = SelectionBox(self._lFrame, self._data, self._Plotter)
        selectBut = tk.Button(self._clFrame, width=10, text='Select', command = self._SelectionBox.select_item)
        selectBut.pack(side=tk.LEFT,expand= True, fill = tk.X)
        deselectBut = tk.Button(self._clFrame, width=10, text='Deselect', command = self._SelectionBox.deselect_item)
        deselectBut.pack(side=tk.LEFT,expand= True, fill = tk.X)
        summaryBut = tk.Button(self._clFrame, width=10, text='Summary', command = self.showSummary)
        summaryBut.pack(side=tk.LEFT,expand= True, fill = tk.X)
        self._clFrame.pack(side =tk.TOP,expand= False, fill = tk.X)

        self._SelectionBox.pack(side = tk.TOP, expand=True, fill = tk.BOTH)

        self._lFrame.pack(side = tk.LEFT, expand=True, fill = tk.BOTH)

    def open_file(self):
        """
        Open file, if correct, execute the following functions; if not, show error message

        open_file() --> None
        """
        filename = filedialog.askopenfilename(filetypes=[('All Files','*')])
        base = os.path.basename(filename)
        
        if filename:
            if not base.endswith('.csv'):
                messagebox.showwarning('File Error','You opened a wrong file!')
                raise(FileExtensionException())
            else:
                self._data.load_data(filename)
                self._Plotter.plot_animal_data()
                self._SelectionBox.add_list()

    def displayhwLabel(self, height, weight):
        """
        Display the label above the canvas to show the instant height and weight

        displayhwLabel() --> None
        """
        labelInfo = 'Height: '+str(height)+" cm, Weight:"+str(weight)+" kg"
        self._dimentionsLabel.config(text = labelInfo)

    def showSummary(self):
        """
        Instantiate a SummaryWindow and display the corresponding animal data on it

        showSummary() --> None
        """
        summary = SummaryWindow(tk.Toplevel(), self._data)
        summary.summarise(self._SelectionBox.curselection()[0])
        summary.display_data()



root = tk.Tk()
app = AnimalDataPlotApp(root)
root.geometry('800x400')
root.mainloop()
