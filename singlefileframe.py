from tkinter.filedialog import askopenfilename
import customtkinter
from pathlib import Path
import threading
from exceptions import ProgressBarException, SameFileExtensionError, FileFormatNotSupportedError

VALID_FILE_TYPES = ['.chd', '.cue', '.gdi', '.iso']
NO_FILE_TEXT = "No file selected"



class SingleFileFrame(customtkinter.CTkFrame):
    def __init__(self, master, converter, **kwargs):
        super().__init__(master, **kwargs)

        self.converter = converter
        self.selected_file = customtkinter.StringVar(master=self, value=NO_FILE_TEXT)
        self.output_format = customtkinter.StringVar(master=self, value='.chd')
        self.LABEL_FONT = customtkinter.CTkFont(size=15)
        self.RESULT_FONT = customtkinter.CTkFont(size=15, slant="italic")

        # File selection widgets
        self.file_info_label = customtkinter.CTkLabel(
            master=self,
            text="Select file:",
            font=self.LABEL_FONT,
            anchor="w"
        )
        self.file_browse_button = customtkinter.CTkButton(master=self, text="Select", command=self.get_file)
        self.file_label = customtkinter.CTkLabel(
            master=self,
            textvariable=self.selected_file,
            font=self.RESULT_FONT,
            width=510,
            anchor="center",
            text_color="darkorange"
        )
        
        # Convert widgets
        self.convert_button = customtkinter.CTkButton(self, text="Convert File", state="disabled", command=self.convert_file)
        self.progressbar = customtkinter.CTkProgressBar(master=self, mode="indeterminate")
        self.progressbar_text = customtkinter.StringVar(value="")
        self.progressbar_label = customtkinter.CTkLabel(master=self, textvariable=self.progressbar_text, anchor="center")

        # Conversion format
        self.conversion_output_format_label = customtkinter.CTkLabel(
            master=self,
            text="Output conversion format:",
            font=self.LABEL_FONT
        )
        self.conversion_output_format_selector = customtkinter.CTkOptionMenu(
            master=self, 
            dynamic_resizing=False,
            values=VALID_FILE_TYPES,
            variable=self.output_format 
        )

        # Layout
        self.file_info_label.grid(row=0, column=0, sticky="e", padx=20, pady=10)
        self.file_browse_button.grid(row=0, column=1, padx=(10, 20), pady=10, sticky="w")
        self.file_label.grid(row=10, column=0, columnspan=2, padx=20, pady=10)
        self.conversion_output_format_label.grid(row=20, column=0, padx=(20, 10), pady=10, sticky="e")
        self.conversion_output_format_selector.grid(row=20, column=1, padx=(10, 20), pady=10,sticky="w")
        self.convert_button.grid(row=30, column=0, columnspan=2, padx=(20, 20), pady=10)
        self.progressbar.grid(row=31, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="ew")
        self.progressbar.grid_forget()  # initially hide the progress bar
        self.progressbar_label.grid(row=32, column=0, columnspan=2, padx=20, pady=10)

    def toggle_ui_state(self, ui_state="enabled"):
        """Enables or disables clickable widgets to prevent strange app behavior during various processes
        ui_state: By default, set to "enabled" to activate widgets, "disabled" to deactivtate the widgets.
        """
        self.convert_button.configure(state=ui_state, text="Convert Files")
        self.file_browse_button.configure(state=ui_state)
        self.conversion_output_format_selector.configure(state=ui_state)

    def interact_with_progressbar(self, state="start"):
        valid_state_inputs = ["start", "stop"]

        if state not in valid_state_inputs:
            raise ProgressBarException()
        
        if state == "stop":
            self.progressbar_text.set("")
            self.progressbar.stop()
            self.progressbar.grid_forget()
        else:
            self.progressbar.configure(progress_color="mediumorchid")
            self.progressbar_text.set("Checking file for conversion...")
            self.progressbar.grid(row=31, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="ew")
            self.progressbar.start()

    def get_file(self):
        new_dir = askopenfilename()
        if new_dir != "":
            self.selected_file.set(new_dir)
            self.convert_button.configure(state="enabled")
        self.file_browse_button.focus_set()

    def convert_file(self):
        """Convert selected files from checkboxes into desired format."""
        # Update UI
        self.toggle_ui_state("disabled")
        self.interact_with_progressbar(state="start")
        
        def run_conversion():
            output_format = self.output_format.get()
            
            try:
                self.progressbar_text.set(f"Converting file...")
                results = self.converter.convert_file(
                    input_file=Path(self.selected_file.get()),
                    output_directory=Path(self.selected_file.get()).parent,
                    output_format=output_format
                )
                
                if results[0]:
                    result_text = f"Conversion Completed"
                else:
                    
                    result_text = f"Conversion Failed"
            except (SameFileExtensionError, FileFormatNotSupportedError) as e:
                if type(e) is SameFileExtensionError:
                    result_text = f"Conversion Failed - File already has type of {output_format}"
                else:
                    result_text = f"Conversion Failed - Selected file can not be converted"
            finally:
                self.toggle_ui_state()
                self.interact_with_progressbar(state="stop")
                self.progressbar_text.set(result_text)
        
        # Begin the conversion in a different thread
        threading.Thread(target=run_conversion, daemon=True).start()
