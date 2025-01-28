from tkinter.filedialog import askdirectory
import customtkinter
from pathlib import Path
import threading
from tools import FileConverter
from exceptions import ProgressBarException

VALID_FILE_TYPES = ['.chd', '.cue', '.gdi', '.iso']
NO_DIRECTORY_TEXT = "No directory selected"

class MultipleFilesFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
    
        self.converter = FileConverter()
        self.selected_directory = customtkinter.StringVar(master=self, value=NO_DIRECTORY_TEXT)
        self.file_list = {}
        self.output_format = customtkinter.StringVar(master=self, value='.chd')
        self.scrollable_frame_switches = []  # stores widgets displayed in scrollable list.
        self.LABEL_FONT = customtkinter.CTkFont(size=15)
        self.RESULT_FONT = customtkinter.CTkFont(size=15, slant="italic")

        # Directory selection widgets
        self.directory_info_label = customtkinter.CTkLabel(
            master=self,
            text="Select directory:",
            font=self.LABEL_FONT,
            anchor="w"
        )
        self.directory_browse_button = customtkinter.CTkButton(master=self, text="Select", command=self.get_directory)
        self.directory_label = customtkinter.CTkLabel(
            master=self,
            textvariable=self.selected_directory,
            font=self.RESULT_FONT,
            width=510,
            anchor="w",
            text_color="darkorange"
        )

        self.directory_info_label.grid(row=0, column=0, sticky="e", padx=20, pady=10)
        self.directory_browse_button.grid(row=0, column=1, padx=(20, 10), pady=10, sticky="w")
        self.directory_label.grid(row=0, column=2, padx=(0, 20), pady=10, sticky="w")
        
        # Convert Widgets
        self.convert_button = customtkinter.CTkButton(self, text="Convert Files", state="disabled", command=self.convert_files)
        self.progressbar = customtkinter.CTkProgressBar(master=self, mode="indeterminate")
        self.progressbar_text = customtkinter.StringVar(value="")
        self.progressbar_label = customtkinter.CTkLabel(master=self, textvariable=self.progressbar_text, anchor="e")

        self.convert_button.grid(row=10, column=0, padx=(20, 10), pady=(10, 10), sticky="w")
        self.progressbar.grid(row=10, column=1, columnspan=3, padx=(20, 20), pady=(10, 0), sticky="ew")
        self.progressbar.grid_forget()
        self.progressbar_label.grid(row=11, column=1, columnspan=3, padx=(0,20), pady=10, sticky="ew")

        # List of selectable files
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Files Found", label_anchor="w")
        self.scrollable_frame.grid(row=3, column=0, columnspan=4, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.draw_file_list()

        # Conversion format
        self.conversion_output_format_label = customtkinter.CTkLabel(
            master=self,
            text="Output conversion format:",
            font=self.LABEL_FONT
        )
        self.conversion_output_format_label.grid(row=4, column=0, padx=20, pady=10, sticky="e")
        self.conversion_output_format_selector = customtkinter.CTkOptionMenu(
            master=self, 
            dynamic_resizing=False,
            values=VALID_FILE_TYPES,
            variable=self.output_format 
        )
        self.conversion_output_format_selector.grid(row=4, column=1, padx=20, pady=10,sticky="w")

    def toggle_ui_state(self, ui_state="enabled"):
        """Enables or diables clickable widgets to prevent strange app behavior during various processes
        ui_state: By default, set to "enabled" to activate widgets, "disabled" to deactivtate the widgets.
        """
        self.convert_button.configure(state=ui_state, text="Convert Files")
        self.directory_browse_button.configure(state=ui_state)
        for switch in self.scrollable_frame_switches:
            if isinstance(switch, customtkinter.CTkCheckBox):
                switch.configure(state=ui_state)
        self.conversion_output_format_selector.configure(state=ui_state)

    def interact_with_progressbar(self, state="start", mode="search"):
        valid_state_inputs = ["start", "stop"]
        valid_mode_inputs = ["search", "convert"]

        if state not in valid_state_inputs or mode not in valid_mode_inputs:
            raise ProgressBarException()
        
        if state == "stop":
            self.progressbar_text.set("")
            self.progressbar.stop()
            self.progressbar.grid_forget()
        else:
            if mode == "search":
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
        self.interact_with_progressbar(state="start", mode="search")
        # Actually walk the path and build a list of components with files.
        def build_file_list():
            self.file_list = {}
            directory_path = Path(self.selected_directory.get())
            for file_path in directory_path.rglob('*'):
                if file_path.is_file() and str.lower(file_path.suffix) in VALID_FILE_TYPES:
                    self.file_list[file_path.as_posix()] = {
                        "filename": file_path.stem,
                        "filetype": file_path.suffix,
                        "convertstate": customtkinter.IntVar(master=self)
                    }
            
            # Let the app go back to functioning as normal
            self.toggle_ui_state("enabled")
            self.interact_with_progressbar(state="stop")
            self.draw_file_list()

        threading.Thread(target=build_file_list, daemon=True).start()

    def draw_file_list(self):
        # Delete existing list of switches
        for switch in self.scrollable_frame_switches:
            switch.destroy()
        self.scrollable_frame_switches = []

        # Draw new list
        if self.file_list != {}:
            for f in self.file_list.keys():
                fname = self.file_list[f]["filename"]
                ftype = self.file_list[f]["filetype"]
                switch = customtkinter.CTkCheckBox(
                    master=self.scrollable_frame, 
                    text=f"{fname} - {ftype}",
                    variable=self.file_list[f]["convertstate"]
                )
                switch.grid(row=len(self.scrollable_frame_switches), column=0, padx=10, pady=(0, 20), sticky="w")
                self.scrollable_frame_switches.append(switch)
        else:
            no_files_found_label = customtkinter.CTkLabel(master=self.scrollable_frame, text="No files found in this directory")
            no_files_found_label.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="w")
            self.scrollable_frame_switches.append(no_files_found_label)

    def convert_files(self):
        """Convert selected files from checkboxes into desired format."""
        # Update UI
        self.toggle_ui_state("disabled")
        self.interact_with_progressbar(state="start", mode="convert")
        conversion_list = [f for f in self.file_list.keys() if self.file_list[f]["convertstate"].get()]
        total_files = len(conversion_list)
        
        # Exit the function and fix UI if there are no files selected for conversion
        if total_files == 0:
            self.toggle_ui_state()
            self.interact_with_progressbar(state="stop")
            return
        
        self.progressbar.grid(row=10, column=1, columnspan=3, padx=(20, 20), pady=(10, 0), sticky="ew")
        
        def run_conversion():
            current_file = 1
            for f in conversion_list:
                self.progressbar_text.set(f"Converting {f} - {current_file}/{total_files}")
                self.converter.convert_file(
                    input_file=Path(f),
                    output_directory=Path(f).parent,
                    output_format=self.output_format.get()
                )
            
            self.toggle_ui_state()
            self.interact_with_progressbar(state="stop")
            self.progressbar_text.set(f"Conversion Completed.")
        
        # Begin the conversion in a different thread
        threading.Thread(target=run_conversion, daemon=True).start()
