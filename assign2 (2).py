

from collections import OrderedDict


class TemperaturePlotApp(object):
    """The top-level GUI of the application"""

    def __init__(self, master):
        """The top-level GUI of the application
        Constructor: TemperaturePlotApp(Tk.BaseWindow)
        """
        # self._master lets other functions in this class to access master
        self._master = master
        self._data = TemperatureData()
        self._filename = ''

        master.title("Max Temperature Plotter")

        # Create the menu
        menu_bar = tk.Menu(master)
        master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)

        # Close Window
        master.protocol("WM_DELETE_WINDOW", self.close)

        # DataFrame
        self._DataFrame = DataFrame(master, self._data)

        # Create Canvas and draw lines
        self._Plotter = Plotter(master, self._data, self._DataFrame)
        self._Plotter.pack(side = tk.TOP, fill=tk.BOTH, expand=True)

        # self._Plotter.bind("<ButtonRelease-1>", lambda event: self.display())

        # self._Plotter.bind("<KeyPress>", lambda event: self._Plotter.key_press())

        self._DataFrame.pack(fill=tk.X)


        # SelectionFrame
        self._SelectionFrame = SelectionFrame(master, self._data, self._Plotter, self._DataFrame)
        self._SelectionFrame.pack(fill=tk.X, side=tk.BOTTOM, anchor=tk.N)


    def open_file(self):
        """Open a file.
        TemperaturePlotApp.open_file() -> None
        """
        self._filename = filedialog.askopenfilename()

        if self.validation(self._filename):
            self._data.load_data(self._filename)
            self._Plotter.plot_station_data()
            self._SelectionFrame.add_button()

    def validation(self, filename):
        """ validate the loading file is valid file and no repeat.

            validation(string) --> boolean
        """
        base = os.path.basename(filename)
        if not base.endswith('.txt'):
            msg = filename + " is not a suitable data file"
            messagebox.showerror(title="File Error", message=msg)
            return False

        station_name = base.replace(".txt", "")
        stations = self._data.get_stations()
        if len(stations) != 0:
            if station_name in stations:
                msg = "The data of " + station_name + " has been loaded"
                messagebox.showwarning(title="Re-loading data file", message=msg)
                return False
        return True

    def close(self):
        """Exit the application.
        TemperaturePlotApp.close() -> None
        """
        self._master.destroy()


class TemperatureData():
    """
        This class is used to hold the temperature data for each loaded station. You
        are required to use a dictionary to store the data with the station names
        as keys and Station objects (containing the temperature data) as values.
    """
    def __init__(self):
        """Constructor TemperatureData()"""
        self._stations_list = []
        self._stations_data = []
        self._flag = []

    def load_data(self, filename):
        """ get the data and organize the structure of data to make it usable.

            load_data(str) --> Dict(int:float)
        """
        self._stations_data.append(Station(filename))
        self._flag.append(1)
        station_name = os.path.basename(filename.replace('.txt', ''))
        self._stations_list.append(station_name)

        return load_data_points(filename)

    def get_flag(self):
        """ return self._flag to other objects which is not TemperatureData class.

            get_flag() --> int
        """
        return self._flag

    def get_data(self):
        """ get a OderedDict from the loaded data.

            get_data() --> None
        """
        temp = OrderedDict()
        for i, s in enumerate(self._stations_list):
            temp[s] = self._stations_data[i]

        return temp

    def toggle_selected(self, i):
        """ change the status of display of data line in the canvas

            toggle_selected(int) --> None
        """
        if self._flag[i] == 1:
            self._flag[i] = 0
        elif self._flag[i] == 0:
            self._flag[i] = 1

    def is_selected(self, i):
        """ justifing this station data has been chosen by user

            is_selected(int) --> boolean
        """
        if self._flag[i] == 1:
            return True
        return False

    def get_stations(self):
        """ get the stations list has been loaded.

            get_stations() --> list
        """
        return self._stations_list

    def get_ranges(self):
        """ get the largest ranges of all loaded stations' data.

            get_ranges() --> (int, int, float, float)
        """
        min_years = []
        max_years = []
        min_temps = []
        max_temps = []

        for i in self._stations_data:
            min_years.append(i._min_year)
            max_years.append(i._max_year)
            min_temps.append(i._min_temp)
            max_temps.append(i._max_temp)
        if min_years:
            return min(min_years), max(max_years), min(min_temps), max(max_temps)


class Plotter(tk.Canvas):
    """
        This class is responsible for doing the plotting and should inherit from
        Canvas.
    """
    def __init__(self, master, data, dataframe):
        """Constructor Plotter(Object, OderedDict, Object)"""
        super().__init__(master, bg="white", relief=tk.SUNKEN)
        self._data = data
        self._width = None
        self._height = None
        self._translate = None
        self._year = 0
        self._dataframe = dataframe
        self._fit_point1 = 0
        self._fit_point2 = 0

        self.bind("<Configure>", self.can_resize)
        self.bind("<ButtonPress-1>", self.press)
        self.bind("<B1-Motion>", self.drag_mouse)

        # self.focus_set()
        self.bind_all("<KeyPress>", lambda event: self.key_press())

    def plot_station_data(self):
        """ the main function of this programme. draw the all lines in the plot required,

            plot_station_data() --> None
        """
        self.delete(tk.ALL)

        ranges = self._data.get_ranges()
        if ranges:
            self._translate = CoordinateTranslator(self._width, self._height, *ranges)

        # get station data points
        for index, station in enumerate(self._data.get_stations()):
            station_data = self._data.get_data()[station]
            data_points = station_data.get_data_points()

            initial_year = data_points[0][0]
            year1 = initial_year
            temp1 = data_points[0][1]

            # Has this station been selected
            if self._data.is_selected(index):

                # best_fit line
                if self._fit_point1 != 0 and self._fit_point2 != 0:
                    if self._fit_point1 == self._fit_point2:
                        self._fit_point1 = 0
                        self._fit_point2 = 0
                        messagebox.showerror(title="Input Error", message="The input points should not be the same")
                    else:
                        self.draw_fit_line(initial_year, data_points, index)

                # lines of stations' data
                for d in data_points[1:]:
                    start_x, start_y = self._translate.temperature_coords(year1, temp1)
                    year2 = d[0]
                    temp2 = d[1]
                    end_x, end_y = self._translate.temperature_coords(year2, temp2)
                    self.create_line(start_x, start_y, end_x, end_y, fill=COLOURS[index])
                    year1 = year2
                    temp1 = temp2

        # line of checkline
        if self._year != 0:
            self.draw_line()

    def draw_line(self):
        """ draw a line to show the year you select by pressing and draging mouse

            draw_line(int, list(tuple), int) --> None
        """
        # self._year = self._translate.get_year(self._x)
        ranges = self._data.get_ranges()
        start_x, start_y = self._translate.temperature_coords(self._year, ranges[3])
        end_x, end_y = self._translate.temperature_coords(self._year, ranges[2])
        self.create_line(start_x, start_y, end_x, end_y, fill='black')

    def draw_fit_line(self, initial_year, data_points, index):
        """draw the best fit line between two chosen points by keyboard.

            draw_fit_line(int, list(tuple), int) --> None
        """
        start_year = min(self._fit_point1, self._fit_point2)
        end_year = max(self._fit_point1, self._fit_point2)

        start_index = start_year - initial_year
        if start_index < 0:
            start_index = 0
        end_index = end_year - initial_year
        points = []
        for data in data_points[start_index:end_index+1]:
            points.append(self._translate.temperature_coords(*data))
        self.create_line(best_fit(points), fill=COLOURS[index])

    def get_selected_year(self):
        """ return self._year to other objects which is not Plotter class.

            get_selected_year() --> int
        """
        return self._year

    # event handling function
    def can_resize(self, event):
        """ it is to catch the resize root frame event for canvas which binds with canvas.

            can_resize(event) --> None
        """
        self._width = event.width
        self._height = event.height
        self.plot_station_data()

    def press(self, event):
        """ it is to catch the mouse press(left button) event for canvas which binds with canvas.

            press(event) --> None
        """
        station = self._data.get_stations()
        if station:
            x = event.x
            self._year = self._translate.get_year(x)
            self.plot_station_data()
            self._dataframe.re_display(self._year)

    def drag_mouse(self, event):
        """ it is to catch the mouse drag event for canvas which binds with canvas.

            drag_mouse(event) --> None
        """
        station = self._data.get_stations()
        if station:
            x = event.x
            self._year = self._translate.get_year(x)
            self.plot_station_data()
            self._dataframe.change_temp(self._year)
            self._dataframe.display_year(self._year)

    def key_press(self):
        """ it is to catch the key event for canvas which binds with canvas.
            in bind, use lambda function to hide event parameter, because this function needn't event.

            key_press() --> None
        """
        if self._fit_point1 == 0 and self._fit_point2 == 0:
            self._fit_point1 = self._year

        elif self._fit_point1 != 0 and self._fit_point2 == 0:
            self._fit_point2 = self._year
            self.plot_station_data()

        elif self._fit_point1 != 0 and self._fit_point2 != 0:
            self._fit_point1 = self._year
            self._fit_point2 = 0
            self.plot_station_data()


class SelectionFrame(tk.Frame):
    """ This class is the 'widget' used for selecting which stations data is to be displayed
        and should inherit from Frame. It consists of a label and a Checkbutton for each loaded station
        (in the order loaded).
    """
    def __init__(self, master, data, plotter, dataframe):
        """ Constructor SelectionFrame(object, OderedDict, object, object)"""
        super().__init__(master)
        lab = tk.Label(text='Station Selection: ')
        lab.pack(side=tk.LEFT)
        self._data = data
        self._plotter = plotter
        self._dataframe = dataframe
        self._flag = self._data.get_flag()
        self._variable = []

    def add_button(self):
        """ add a checkbutton widget into selectionframe when a new station data loaded

            add_button() --> None
        """

        for checkbutton in self.winfo_children():
            checkbutton.destroy()

        for index, station in enumerate(self._data.get_stations()):
            var = tk.IntVar()
            if self._flag[index] == 1:
                var.set(1)
            else:
                var.set(0)
            self._variable.append(var)

            tk.Checkbutton(self, text=station, foreground=COLOURS[index], variable=var, onvalue=1, offvalue=0,
                           command=lambda sta=station: self.toggle(sta)).pack(side=tk.LEFT)

    def toggle(self, station):
        """this function lets the checkbutton as a toggle to control the display of specific station's line in canvas.

            toggle(self, str)-->None
        """
        index = self._data.get_stations().index(station)
        self._data.toggle_selected(index)
        self._plotter.plot_station_data()
        self._dataframe.draw()


class DataFrame(tk.Frame):
    """
        This class is the 'widget' used for displaying the temperatures for a chosen
        year for each selected station.
    """

    def __init__(self, master, data):
        """Constructor DataFrame(Object, OrderedDict[string:list(tuple)])"""
        super().__init__(master)

        self._master = master
        self._data = data
        self._year = 0
        self._all_label = []

        self._year_label = tk.Label(self, text="")
        self._year_label.pack(side=tk.LEFT)

    def draw(self):
        """ This function is built for toggle to call re_display without year parameter

            draw() --> None
        """
        if self._year:
            self.re_display(self._year)

    def re_display(self, year):
        """ re-draw the whole DataFrame part

            re_display(year) --> None
        """
        self.display_year(year)
        self.create_temp()

    def display_year(self, year):
        """ display and fresh the year label of DataFrame.

            display_year(year) --> None
        """
        self._year = year
        date = "Data Output " + str(self._year)
        self._year_label.config(text=date)

    def create_temp(self):
        """ re-draw the temperature label of DataFrame part.

            create_temp() --> None
        """
        if self._all_label:
            for j in self._all_label:
                j.destroy()

            self._all_label = []

        for index, station in enumerate(self._data.get_stations()):
            station_data = self._data.get_data()[station]
            data_temp = station_data.get_temp(self._year)

            stations = self._data.get_stations()
            temp_label = tk.Label(self, text="\000\000\000\000", foreground=COLOURS[index])
            temp_label.pack(side=tk.LEFT, ipadx=20)
            self._all_label.append(temp_label)

            if self._data.is_selected(stations.index(station)):
                temp_label.config(text=data_temp)

    def change_temp(self, year):
        """ update the new temperature data catch by the mouse drag event.

            change_temp(year) --> None
        """
        self._year = year
        for index, station in enumerate(self._data.get_stations()):
            station_data = self._data.get_data()[station]
            data_temp = station_data.get_temp(self._year)

            stations = self._data.get_stations()

            if self._data.is_selected(stations.index(station)):
                min_year, max_year = station_data.get_year_range()
                if min_year > self._year or max_year < self._year:
                    self._all_label[index].config(text="")
                else:
                    self._all_label[index].config(text=str(data_temp))





##################################################
# !!!!!! Do not change (or add to) the code below !!!!!
###################################################

def main():
    root = tk.Tk()
    app = TemperaturePlotApp(root)
    root.geometry("800x400")
    root.mainloop()

if __name__ == '__main__':
    main()
