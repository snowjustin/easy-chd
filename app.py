from tkinter.filedialog import askdirectory
import customtkinter
from pathlib import Path
import threading
from tools import FileConverter

# Theme settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

#  CONSTANTS
VALID_FILE_TYPES = ['.chd', '.cue', '.gdi', '.iso']
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 630
APP_TITLE = "Easy CHD"
NO_DIRECTORY_TEXT = "No directory selected"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.title(APP_TITLE)
        self.converter = FileConverter()
        self.selected_directory = customtkinter.StringVar(master=self, value=NO_DIRECTORY_TEXT)
        self.file_list = {}
        self.output_format = customtkinter.StringVar(master=self, value='.chd')
        self.scrollable_frame_switches = []  # stores widgets displayed in scrollable list.

        # set grid layout 4x4
        self.grid_columnconfigure((2,3), weight=1)
        self.grid_columnconfigure((0,1), weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=17)

        # App title settings
        self.app_title_label = customtkinter.CTkLabel(
            master=self,
            text=APP_TITLE,
            font=customtkinter.CTkFont(size=30, weight="bold"),
            height=50
        )
        self.app_title_label.grid(
            row=0, 
            column=0, 
            columnspan=4, 
            padx=20, 
            pady=(10, 10), 
            sticky="nsew"
        )

        # Tab creation
        self.tabview = customtkinter.CTkTabview(master=self)
        self.tabview.grid(
            row=1,
            column=0,
            columnspan=4,
            padx=20,
            pady=(0,20),
            sticky="nsew"
        )
        self.sf_tab = self.tabview.add("Single File")
        self.mf_tab = self.tabview.add("Multiple Files")
        self.tabview.set("Multiple Files")

        # Directory selection
        self.directory_info_label = customtkinter.CTkLabel(
            master=self.mf_tab,
            text="Select directory:",
            font=customtkinter.CTkFont(size=15),
            anchor="w"
        )
        self.directory_info_label.grid(row=0, column=0, sticky="e", padx=20)
        self.directory_browse_button = customtkinter.CTkButton(master=self.mf_tab, text="Select", command=self.get_directory)
        self.directory_browse_button.grid(row=0, column=1, padx=(20, 10), pady=10, sticky="w")
        self.directory_label = customtkinter.CTkLabel(
            master=self.mf_tab,
            textvariable=self.selected_directory,
            font=customtkinter.CTkFont(size=15, slant="italic", weight="bold"),
            width=510,
            anchor="w"
        )
        self.directory_label.grid(row=0, column=2, padx=(0, 20), pady=10, sticky="w")
        self.search_progressbar = customtkinter.CTkProgressBar(master=self.mf_tab, mode="indeterminate")
        self.search_progressbar.grid(row=1, column=2)# columnspan=3, padx=(20, 20), pady=(10, 0), sticky="ew")
        self.search_progressbar.grid_forget()
        self.search_text = customtkinter.StringVar(value="")
        self.search_text_label = customtkinter.CTkLabel(master=self.mf_tab, textvariable=self.search_text, anchor="e")
        self.search_text_label.grid(row=1, column=1, sticky="ew", padx=(20,10), pady=10)

        # Progress bar components
        self.convert_button = customtkinter.CTkButton(self.mf_tab, text="Convert Files", state="disabled", command=self.convert_files)
        self.convert_button.grid(row=10, column=0, padx=(20, 10), pady=(10, 10), sticky="w")
        self.convert_progressbar = customtkinter.CTkProgressBar(master=self.mf_tab, width=510)
        self.convert_progressbar.grid(row=10, column=1, columnspan=3, padx=(20, 20), pady=(10, 0), sticky="ew")
        self.convert_progressbar.grid_forget()
        self.convert_progress_text = customtkinter.StringVar(value="")
        self.convert_progress_label = customtkinter.CTkLabel(master=self.mf_tab, textvariable=self.convert_progress_text, anchor="e", width=510)
        self.convert_progress_label.grid(row=11, column=1, columnspan=3, padx=(0,20), pady=10, sticky="ew")

        # List of selectable files
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self.mf_tab, label_text="Files Found", label_anchor="w")
        self.scrollable_frame.grid(row=3, column=0, columnspan=4, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.draw_file_list()

        # Conversion format
        self.conversion_output_format_label = customtkinter.CTkLabel(
            master=self.mf_tab,
            text="Output conversion format:",
            font=customtkinter.CTkFont(size=15)
        )
        self.conversion_output_format_label.grid(row=4, column=0, padx=20, pady=10, sticky="e")
        self.conversion_output_format_selector = customtkinter.CTkOptionMenu(
            master=self.mf_tab, 
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
        self.search_text.set("Searching...")
        self.search_progressbar.grid(row=2, column=2, padx=20, pady=20, sticky="ew")
        self.search_progressbar.start()
        
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
            self.draw_file_list()
            self.search_progressbar.stop()
            self.search_text.set("")
            self.search_progressbar.grid_forget()

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
        self.convert_progress_text.set(f"Checking files for conversion")
        conversion_list = [f for f in self.file_list.keys() if self.file_list[f]["convertstate"].get()]
        total_files = len(conversion_list)
        
        # Exit the function and fix UI if there are no files selected for conversion
        if total_files == 0:
            self.toggle_ui_state()
            self.convert_progress_text.configure(text="")
            return
        
        # Determinate speed is a value divided by 50 for whatever reason in the customtkinter code.
        # Here I am essentially changing that value from 50 to the number of total files so that the
        # progress bar should increment once for each file that is being converted.
        self.convert_progressbar.configure(determinate_speed=50/total_files)  
        self.convert_progressbar.set(value=0)
        self.convert_progressbar.grid(row=10, column=1, columnspan=3, padx=(20, 20), pady=(10, 0), sticky="ew")
        
        def run_conversion():
            for f in conversion_list:
                self.convert_progress_text.set(f"Converting {f}")
                self.convert_progressbar.step()
                self.converter.convert_file(
                    input_file=Path(f),
                    output_directory=Path(f).parent,
                    output_format=self.output_format.get()
                )
            
            self.toggle_ui_state()
            self.convert_progress_text.set(f"Conversion Completed.")
        
        # Begin the conversion in a different thread
        threading.Thread(target=run_conversion, daemon=True).start()


if __name__ == "__main__":
    app = App()
    app.eval('tk::PlaceWindow . center')
    app.mainloop()
