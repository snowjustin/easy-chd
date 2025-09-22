# This is a utility library for converting different games
import subprocess
from pathlib import Path
from exceptions import ChdmanNotInstalledError, SameFileExtensionError, FileFormatNotSupportedError
from constants import *

# File Formats
CHDMAN_OUTPUT_VERIFICATION = "chdman - MAME Compressed Hunks of Data (CHD) manager"

class FileConverter:
    def __init__(self, debug=False):
        self.debug = debug
        self.conversion_result = None  # Stores the last result of a conversion as a CompletedProcess object
        if not self.__test_chdman_installed():
            raise ChdmanNotInstalledError()

    def convert_file(self, input_file, output_directory, output_format=CHD):
        # TODO: Evaluate the best way to handle undesired inputs. Most likely
        # new exceptions would be best here.

        if input_file.suffix not in VALID_FORMATS:
            raise FileFormatNotSupportedError()
        if not input_file.exists():
            raise FileNotFoundError()
        if input_file.suffix == output_format:
            raise SameFileExtensionError()

        output_file = output_directory / Path(input_file.stem + output_format)
        if output_format == CHD:
            self.conversion_result = self.__convert_other_to_chd(input_file=input_file, output_file=output_file)
        else:
            self.conversion_result = self.__convert_chd_to_other(input_file=input_file, output_file=output_file)
        
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

    def __convert_chd_to_other(self, input_file, output_file):
        return subprocess.run(
            args=["chdman", "extractcd", "-i", str(input_file), "-o", str(output_file), "--force"],
            capture_output=True
        )

    def __convert_other_to_chd(self, input_file, output_file):
        return subprocess.run(
            args=["chdman", "createcd", "-i", str(input_file), "-o", str(output_file), "--force"],
            capture_output=True,
        )
