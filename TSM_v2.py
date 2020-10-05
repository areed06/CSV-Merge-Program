# program created by Adam Reed
# started on 5-28-2020
# finished on ...

import tkinter  # for the UI
from tkinter import ttk  # for the UI
import csv  # for reading csv files
import json  # for saving data in json files
import os  # for changing the working directory


# ___ Functions & Classes ___

def disable_entry():
    """Disables the directory entry box if the user wants to use the current directory"""

    # this function activates whenever the first check button is pressed

    if var1.get() == 1:

        # instructions for when the saved directory is to be used (check button pressed)

        combiner.get_directory()  # gets the saved directory from the json file
        text = combiner.directory  # stores the directory as a string var
        directory.delete(0, tkinter.END)  # deletes whatever the user had already typed
        directory.insert(0, text)  # displays the saved directory in the entry box
        var2.set(0)  # sets the second check button to its off state
        directory.config(state='disabled')  # disables the entry box
        save_dir.config(state=tkinter.DISABLED)  # disables the second check button

    else:

        # when a new directory is to be used

        directory.config(state='enabled')  # enables entry box
        save_dir.config(state=tkinter.ACTIVE)  # enables check button to have option to save a new directory
        directory.delete(0, tkinter.END)  # if the box is unchecked, any remaining text in the box is deleted


def error_message():
    """Activates a pop-up window to alert user that the given inputs for file names and/or directory were
    not accepted"""

    error_window = tkinter.Toplevel(root)

    main_label = ttk.Label(error_window, text='The following errors occurred:')
    main_label.config(font=('Calibri', 12))

    file_error = ttk.Label(error_window, text='* file(s) could not be found')
    file_error.config(font=('Calibri', 12))

    directory_error = ttk.Label(error_window, text='* invalid directory was provided')
    directory_error.config(font=('Calibri', 12))

    main_label.grid(row=0, column=0, pady=5)

    if not combiner.found_files:
        file_error.grid(row=1, column=0, pady=5, sticky='W')
    if not combiner.valid_dir:
        directory_error.grid(row=2, column=0, pady=5, sticky='W')


class LogsheetCombiner:

    def __init__(self):
        """Initializes variables in the LogsheetCombiner class"""

        self.log_location = None  # file name of logsheet file
        self.update_location = None  # file name of logsheet updates file
        self.output_name = None  # desired name of output file
        self.logsheet_data = list()  # list to store logsheet info
        self.updates_data = list()  # list to store logsheet updates info
        self.master_list = list()  # master list to be written to the output file
        self.should_create_output = True  # boolean for whether output file should be created
        self.directory = None  # stores the directory as a string
        self.valid_dir = True  # boolean for whether valid directory has been given
        self.found_files = True  # boolean for whether input files were found

    def format_file_names(self):
        """Formats file names to include .csv extension"""

        self.log_location = logsheet.get() + ".csv"
        self.update_location = logsheet_update.get() + ".csv"
        self.output_name = output.get() + ".csv"

    def store_file_data(self):
        """Stores data from both files in lists"""

        try:
            # tries to open both files and store their contents in lists

            with open(self.log_location, newline='') as logfile:
                self.logsheet_data = list(csv.reader(logfile))
            with open(self.update_location, newline='') as update_file:
                self.updates_data = list(csv.reader(update_file))

            # deletes the header row from each file
            del self.logsheet_data[0]
            del self.updates_data[0]

            self.should_create_output = True

        # if an error occurs in finding the files, an output file will
        # not be created if the button is pressed

        except FileNotFoundError:
            self.should_create_output = False
            self.found_files = False
            print("Error occurred, no files were processed")  # for debugging only

    def store_directory(self):
        """Stores the directory the user would like to use"""

        original_dir = os.getcwd()

        json_file = 'current_directory.json'
        desired_directory = directory.get()

        local_app_data = os.getenv('LOCALAPPDATA')
        folder = 'LogsheetCombiner'

        folder_path = os.path.join(local_app_data, folder)

        try:
            os.mkdir(folder_path)
        except FileExistsError:
            pass

        with open(os.path.join(folder_path, json_file), 'w') as file:
            json.dump(desired_directory, file)

        os.chdir(original_dir)

    def get_directory(self):
        """Gets the current directory from json file"""

        json_file = 'current_directory.json'

        original_dir = os.getcwd()

        app_data_path = os.getenv('LOCALAPPDATA')
        data_folder = 'LogsheetCombiner'

        data_path = os.path.join(app_data_path, data_folder)

        try:
            with open(os.path.join(data_path, json_file)) as file:
                self.directory = json.load(file)

        except FileNotFoundError:
            self.directory = ""
            pass

        os.chdir(original_dir)

    def change_directory(self):
        """Changes directory if an entry is given"""

        # only changes the directory if something has been typed into the box
        if self.directory:
            try:
                os.chdir(self.directory)
                self.valid_dir = True
                self.should_create_output = True

            # FileNotFoundError occurs when the directory cannot be changed based on the text entry
            except FileNotFoundError:
                print("This is an invalid directory")
                self.valid_dir = False
                self.should_create_output = False

    def sort_files(self):
        """Sorts the logsheet data and logsheet updates based on the log_id in each row
           * log_id increases in order chronologically based on when the log in/out event was processed"""

        self.logsheet_data = sorted(self.logsheet_data, key=lambda x: x[13])
        self.updates_data = sorted(self.updates_data, key=lambda x: x[1])

    def examine_files(self):
        """Places all logsheet updates into the master list in the appropriate place"""

        start_point = 0  # initial starting row in logsheet updates

        # goes through every row of the logsheet data
        for row in range(len(self.logsheet_data)):

            # add the current row from logsheet data to master list
            self.master_list.append(self.logsheet_data[row])

            # go through ever row in the logsheet updates starting at the start point
            # start point allows the loop to skip over rows that have already been used in the master list
            for update_row in range(start_point, len(self.updates_data)):

                # if the log_ids match, the update gets added after the main logsheet
                if self.updates_data[update_row][1] == self.logsheet_data[row][13]:
                    add_before = False
                    add_after = True
                    start_point = update_row + 1

                # if the log_id is before the latest main logsheet entry and it was deleted,
                # it gets added after the main entry
                elif (self.updates_data[update_row][1] < self.logsheet_data[row][13] and
                        self.updates_data[update_row][22] == 'deleted'):
                    add_before = True
                    add_after = False
                    start_point = update_row + 1

                # if the log_id is in between the current entry and next entry from the logsheet data,
                # it gets added after the current entry
                elif row + 1 < len(self.logsheet_data):
                    if (self.logsheet_data[row][13] < self.updates_data[update_row][1] <
                            self.logsheet_data[row + 1][13]):
                        add_before = False
                        add_after = True
                        start_point = update_row + 1

                    else:
                        add_before = False
                        add_after = False

                # default mode is that the update should not be added to the master list yet
                else:
                    add_before = False
                    add_after = False

                # formats the row from logsheet updates to be added to the master list
                to_be_added = self.updates_data[update_row]
                formatted_addition = [to_be_added[2], to_be_added[3], to_be_added[4], to_be_added[5],
                                      to_be_added[6], to_be_added[7], to_be_added[8], to_be_added[9],
                                      to_be_added[10], to_be_added[11], to_be_added[12], to_be_added[13],
                                      to_be_added[14], to_be_added[1], to_be_added[15], to_be_added[16],
                                      to_be_added[17], to_be_added[18], to_be_added[19], to_be_added[20],
                                      to_be_added[0], to_be_added[21], to_be_added[22]]

                # adds the entry to the master list
                if add_before:
                    self.master_list.insert(row, formatted_addition)

                elif add_after:
                    self.master_list.append(formatted_addition)

    def create_output_file(self):
        """creates output file using the master list"""

        with open(self.output_name, mode='w') as output_file:
            output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                       lineterminator='\n')

            # labels for the columns
            output_writer.writerow(['employee_firstname', 'employee_lastname', 'employee_number',
                                    'log_in_out', 'date_time', 'job_number', 'job_name', 'task_number',
                                    'caller_id', 'latitude', 'longitude', 'radius', 'location_acceptance',
                                    'log_id', 'location_accuracy', 'mileage', 'operating_system',
                                    'os_version', 'device_model', 'app_version', 'id', 'created_at',
                                    'method'])

            # prints each row of the master list sequentially
            for row in range(len(self.master_list)):
                output_writer.writerow(self.master_list[row])

    def when_button_pressed(self):
        """This is the master function which will trigger all functionality when the button is pressed"""

        if var1.get() == 1:
            self.get_directory()  # gets saved directory if first check box is clicked
        else:
            self.directory = directory.get()  # otherwise, directory is retrieved from typed entry

        self.change_directory()

        if var2.get() == 1 and self.valid_dir:
            self.store_directory()  # stores only a valid directory name (that doesn't pass errors)

        self.format_file_names()
        self.store_file_data()

        # only creates output file if no errors were passed in finding files
        if self.should_create_output:
            self.sort_files()
            self.examine_files()
            self.create_output_file()
            self.check_for_success()
        else:
            error_message()

    def check_for_success(self):
        if os.path.isfile(f"{self.directory}\\{self.output_name}"):
            success = tkinter.Toplevel(root)
            success_label = ttk.Label(success, text="Success!")
            success_label.config(font=('Calibri', 12))

            success_label.grid(row=0, column=0, pady=5, sticky='NSWE')


# ___ Normal Code ___

combiner = LogsheetCombiner()  # creates instance of the combiner class

# ___ User Interface Code ___

# creates the base of the UI
root = tkinter.Tk()
root.title("Logsheet Combiner")

# labels for each entry box
ttk.Label(root, text="Logsheet File").grid(row=0, column=0, padx=5, pady=5)
ttk.Label(root, text="Update Log File").grid(row=1, column=0, padx=5, pady=5)
ttk.Label(root, text="Working Directory").grid(row=2, column=0, padx=5, pady=5)
ttk.Label(root, text="Output File Name").grid(row=4, column=0, padx=5, pady=5)

# entries for file names and directory location
logsheet = ttk.Entry(root, width=25)
logsheet_update = ttk.Entry(root, width=25)
directory = ttk.Entry(root, width=50)
output = ttk.Entry(root, width=25)

# places entries in the UI
logsheet.grid(row=0, column=1, columnspan=2, sticky='W', padx=5, pady=10)
logsheet_update.grid(row=1, column=1, columnspan=2, sticky='W', padx=5, pady=10)
directory.grid(row=2, column=1, columnspan=2, sticky='W', padx=5, pady=10)
output.grid(row=4, column=1, columnspan=2, sticky='W', padx=5, pady=10)

# create check buttons for saving a new directory location
var1 = tkinter.IntVar(0)
var2 = tkinter.IntVar(0)
use_current_dir = ttk.Checkbutton(root, text="Use saved directory", variable=var1, onvalue=1, offvalue=0,
                                  command=disable_entry)
save_dir = ttk.Checkbutton(root, text="Save new directory", variable=var2, onvalue=1, offvalue=0)

# places check buttons in the UI
use_current_dir.grid(row=3, column=1, padx=5, sticky='W')
save_dir.grid(row=3, column=2, sticky='W')

# combine button
combine_button = ttk.Button(root, text="Merge Files", width=30, command=combiner.when_button_pressed)
combine_button.grid(row=5, column=0, columnspan=3, ipady=3, pady=5)

root.mainloop()  # runs the UI
