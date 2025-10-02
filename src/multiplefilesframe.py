from tkinter.filedialog import askdirectory
import customtkinter
from pathlib import Path
import threading
from exceptions import ProgressBarException, SameFileExtensionError, FileFormatNotSupportedError, OutputFileAlreadyExists
from constants import *

NO_DIRECTORY_TEXT = "No directory selected"
PROGRESS_START = "start"
PROGRESS_STOP = "stop"
PROGRESS_SEARCH = "search"
PROGRESS_CONVERT = "convert"

class MultipleFilesFrame(customtkinter.CTkFrame):
    def __init__(self, master, converter, **kwargs):
        super().__init__(master, **kwargs)
    
        self.converter = converter
        self.selected_directory = customtkinter.StringVar(master=self, value=NO_DIRECTORY_TEXT)
        self.file_list = {}
        self.longest_filename = 0
        self.output_format = customtkinter.StringVar(master=self, value=CHD)
        self.scrollable_frame_switches = []  # stores widgets displayed in scrollable list.
        self.label_font = customtkinter.CTkFont(size=15)
        self.result_font = customtkinter.CTkFont(size=15, slant="italic")

        # Directory selection widgets
        self.directory_info_label = customtkinter.CTkLabel(
            master=self,
            text="Select directory:",
            font=self.label_font,
            anchor="w"
        )
        self.directory_browse_button = customtkinter.CTkButton(master=self, text="Select", command=self.get_directory)
        self.directory_label = customtkinter.CTkLabel(
            master=self,
            textvariable=self.selected_directory,
            font=self.result_font,
            width=510,
            anchor="w",
            text_color="darkorange"
        )
        
        # Convert widgets
        self.convert_button = customtkinter.CTkButton(self, text="Convert Files", state="disabled", command=self.convert_files)
        self.progressbar = customtkinter.CTkProgressBar(master=self, mode="indeterminate")
        self.progressbar_text = customtkinter.StringVar(value="")
        self.progressbar_label = customtkinter.CTkLabel(master=self, textvariable=self.progressbar_text, anchor="e")

        # List of selectable files
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Files Found", label_anchor="w")

        # Conversion format
        self.conversion_output_format_label = customtkinter.CTkLabel(
            master=self,
            text="Output conversion format:",
            font=self.label_font
        )
        self.conversion_output_format_selector = customtkinter.CTkOptionMenu(
            master=self, 
            dynamic_resizing=False,
            values=VALID_FORMATS,
            variable=self.output_format 
        )

        # Layout
        self.directory_info_label.grid(row=0, column=0, sticky="e", padx=20, pady=10)
        self.directory_browse_button.grid(row=0, column=1, padx=(20, 10), pady=10, sticky="w")
        self.directory_label.grid(row=0, column=2, padx=(0, 20), pady=10, sticky="w")
        self.convert_button.grid(row=10, column=0, padx=(20, 10), pady=(10, 10), sticky="w")
        self.progressbar.grid(row=10, column=1, columnspan=3, padx=(20, 20), pady=(10, 0), sticky="ew")
        self.progressbar.grid_forget()  # initially hide the progress bar
        self.progressbar_label.grid(row=11, column=1, columnspan=3, padx=(0,20), pady=10, sticky="ew")
        self.scrollable_frame.grid(row=3, column=0, columnspan=4, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.draw_file_list()
        self.conversion_output_format_label.grid(row=4, column=0, padx=20, pady=10, sticky="e")
        self.conversion_output_format_selector.grid(row=4, column=1, padx=20, pady=10,sticky="w")

    def toggle_ui_state(self, ui_state="enabled"):
        self.convert_button.configure(state=ui_state, text="Convert Files")
        self.directory_browse_button.configure(state=ui_state)
        for switch in self.scrollable_frame_switches:
            if isinstance(switch, customtkinter.CTkCheckBox):
                switch.configure(state=ui_state)
        self.conversion_output_format_selector.configure(state=ui_state)

    def interact_with_progressbar(self, state=PROGRESS_START, mode="search"):
        valid_state_inputs = [PROGRESS_START, PROGRESS_STOP]
        valid_mode_inputs = ["search", "convert"]

        if state not in valid_state_inputs or mode not in valid_mode_inputs:
            raise ProgressBarException()
        
        if state == PROGRESS_STOP:
            self.progressbar_text.set("")
            self.progressbar.stop()
            self.progressbar.grid_forget()
        else:
            if mode == PROGRESS_SEARCH:
                self.progressbar.configure(progress_color="darkorange")
                self.progressbar_text.set("Searching directory...")
            else:
                self.progressbar.configure(progress_color="mediumorchid")
                self.progressbar_text.set("Checking files for conversion...")

            self.progressbar.grid(row=10, column=1, columnspan=3, padx=(20, 20), pady=(10, 0), sticky="ew")
            self.progressbar.start()

    def get_directory(self):
        new_dir = askdirectory(mustexist=True)
        if new_dir != "":
            self.selected_directory.set(new_dir)
            self.search_for_files()
        self.directory_browse_button.focus_set()

    def search_for_files(self):
        # Draw a progress bar to distract us and disable 
        # things that shouldn't be clicked while a search is ongoing
        self.toggle_ui_state("disabled")
        self.interact_with_progressbar(state=PROGRESS_START, mode=PROGRESS_SEARCH)
        # Actually walk the path and build a list of components with files.
        def build_file_list():
            self.file_list = {}
            self.longest_filename = 0

            directory_path = Path(self.selected_directory.get())
            for file_path in directory_path.rglob('*'):
                if file_path.is_file() and str.lower(file_path.suffix) in VALID_FORMATS:
                    self.file_list[file_path.as_posix()] = {
                        "filename": file_path.stem,
                        "filetype": file_path.suffix,
                        "convertstate": customtkinter.IntVar(master=self)
                    }

                # used for fixed length display of switch text.
                if len(file_path.stem) > self.longest_filename:
                    self.longest_filename = len(file_path.stem)
            
            # Let the app go back to functioning as normal
            self.toggle_ui_state("enabled")
            self.interact_with_progressbar(state=PROGRESS_STOP)
            self.draw_file_list()

        threading.Thread(target=build_file_list, daemon=True).start()

    def draw_file_list(self):
        # Delete existing list of switches
        for switch in self.scrollable_frame_switches:
            switch.destroy()
        self.scrollable_frame_switches = []

        # Draw new list
        if self.file_list != {}:
            for f in sorted(self.file_list.keys()):
                fname = self.file_list[f]["filename"]
                ftype = self.file_list[f]["filetype"]
                if len(fname) < self.longest_filename:
                    switch_text = f"{fname.ljust(self.longest_filename)}  FORMAT: {ftype}  STATUS: unconverted"
                else:
                    switch_text = f"{fname}  FORMAT: {ftype}  STATUS: unconverted"

                switch = customtkinter.CTkCheckBox(
                    master=self.scrollable_frame,
                    font=customtkinter.CTkFont(family="Courier New", size=12),
                    text=switch_text,
                    variable=self.file_list[f]["convertstate"]
                )
                self.file_list[f]["switch"] = switch  # keep a reference to the switch here. BUG_TEST
                switch.grid(row=len(self.scrollable_frame_switches), column=0, padx=10, pady=(0, 20), sticky="w")
                self.scrollable_frame_switches.append(switch)
        else:
            no_files_found_label = customtkinter.CTkLabel(master=self.scrollable_frame, text="No files found in this directory")
            no_files_found_label.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="w")
            self.scrollable_frame_switches.append(no_files_found_label)

    def convert_files(self):
        """Convert selected files from checkboxes into desired format."""
        conversion_list = [f for f in self.file_list.keys() if self.file_list[f]["convertstate"].get()]
        total_files = len(conversion_list)
        
        if total_files == 0:
            return
        
        # Update UI
        self.toggle_ui_state("disabled")
        self.interact_with_progressbar(state=PROGRESS_START, mode=PROGRESS_CONVERT)
        self.progressbar.grid(row=10, column=1, columnspan=3, padx=(20, 20), pady=(10, 0), sticky="ew")
        
        def run_conversion():
            conversion_counter = 1
            for f in conversion_list:
                error_found = False
                switch = self.file_list[f]["switch"]

                try:
                    self.progressbar_text.set(f"Converting {f} - {conversion_counter}/{total_files}")
                    result, completed_process = self.converter.convert_file(
                        input_file=Path(f),
                        output_directory=Path(f).parent,
                        output_format=self.output_format.get()
                    )
                    error_found = not result
                    if error_found:
                        error_text = f"Error - {str(completed_process.stderr.decode())}"

                except (SameFileExtensionError, FileFormatNotSupportedError, OutputFileAlreadyExists, Exception) as e:
                    error_found = True
                    if type(e) is SameFileExtensionError:
                        error_text = f"Error - Already in format"
                    elif type(e) is FileFormatNotSupportedError:
                        error_text = f"Error - Format not supported"
                    elif type(e) is OutputFileAlreadyExists:
                        error_text = f"Error - Output file already exists cannot overwrite"
                    else:
                        error_text = f"Error - Unknown error"
                finally:
                    current_text = switch.cget("text")
                    current_text = current_text[0:current_text.rfind(":")+1]

                    if error_found:
                        switch.configure(
                            text=current_text+f" "+error_text,
                            text_color="red"
                        )
                    else:
                        switch.configure(
                            text=current_text+f" Converted successfully",
                            text_color="green"
                        )
                    conversion_counter += 1


            self.toggle_ui_state("enabled")
            self.interact_with_progressbar(state=PROGRESS_STOP)
            self.progressbar_text.set(f"Conversion(s) Completed.")
        
        # Begin the conversion in a different thread
        threading.Thread(target=run_conversion, daemon=True).start()
