# This is a utility library for converting different games
import subprocess
from pathlib import Path
from exceptions import ChdmanNotInstalledError, SameFileExtensionError, FileFormatNotSupportedError, OutputFileAlreadyExists
from constants import *
from os import remove

# File Formats
CHDMAN_OUTPUT_VERIFICATION = "chdman - MAME Compressed Hunks of Data (CHD) manager"

class FileConverter:
    def __init__(self, debug=False):
        self.debug = debug
        self.conversion_result = None  # Stores the last result of a conversion as a CompletedProcess object
        if not self.__test_chdman_installed():
            raise ChdmanNotInstalledError()

    def convert_file(self, input_file, output_directory, output_format=CHD):
        output_file = output_directory / Path(input_file.stem + output_format)
        intermediary_file = None

        if input_file.suffix not in VALID_FORMATS:
            raise FileFormatNotSupportedError()
        if not input_file.exists():
            raise FileNotFoundError()
        if input_file.suffix == output_format:
            raise SameFileExtensionError()
        if output_file.exists():
            raise OutputFileAlreadyExists()
        
        if input_file.suffix != CHD and output_format != CHD:
            # Have to convert twice, once to CHD then CHD to desired format
            intermediary_file = output_directory / Path(input_file.stem + CHD)
            self.conversion_result = self.__convert_other_to_chd(input_file=input_file, output_file=intermediary_file)
            
            if not self.conversion_result.returncode:
                if output_format == ISO:
                    self.conversion_result = self.__convert_chd_to_iso(input_file=intermediary_file, output_file=output_file)
                else:
                    self.conversion_result = self.__convert_chd_to_gdi_cue(input_file=intermediary_file, output_file=output_file)

        elif output_format == CHD:
            self.conversion_result = self.__convert_other_to_chd(input_file=input_file, output_file=output_file)
        elif input_file.suffix == CHD and output_format == ISO:
            self.conversion_result = self.__convert_chd_to_iso(input_file=input_file, output_file=output_file)
        else:
            self.conversion_result = self.__convert_chd_to_gdi_cue(input_file=input_file, output_file=output_file)
        
        if intermediary_file != None:
                remove(intermediary_file)
                
        if not self.conversion_result.returncode:
            return True, self.conversion_result
        else:
            return False, self.conversion_result

    def __test_chdman_installed(self):
        test_run = subprocess.run(["chdman"], capture_output=True, shell=True, text=True)
        chdman_output = test_run.stdout.splitlines()[0]
        if CHDMAN_OUTPUT_VERIFICATION in chdman_output:
            return True
        else:
            return False

    def __convert_chd_to_gdi_cue(self, input_file, output_file):
        return subprocess.run(
            args=["chdman", "extractcd", "-i", str(input_file), "-o", str(output_file), "--force"],
            capture_output=True
        )

    def __convert_other_to_chd(self, input_file, output_file):
        return subprocess.run(
            args=["chdman", "createcd", "-i", str(input_file), "-o", str(output_file), "--force"],
            capture_output=True,
        )
    
    def __convert_chd_to_iso(self, input_file, output_file):
        return subprocess.run(
            args=["chdman", "extractraw", "-i", str(input_file), "-o", str(output_file), "--force"],
            capture_output=True,
        )
