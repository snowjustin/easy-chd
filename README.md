# Easy CHD

This utility provides a graphical interface for converting files between different compression algorithms using the chdman utility created for [MAME](https://docs.mamedev.org/tools/chdman.html).

## Setup Instructions

- _3rd party requirement_: Install the _chdman_ utility following your platforms instructions found [here](https://wiki.recalbox.com/en/tutorials/utilities/rom-conversion/chdman).
  - Test that the installtion is correct by executing the command `chdman` from a terminal. The first line of output should be similar to the following if installed correctly:
    ```
    chdman - MAME Compressed Hunks of Data (CHD) manager X.XXX (unknown)
    ```

- Binaries are available for both intel and arm64 flavors of macOS.

- If downloading the source to run the application:
  - Runs with verion *3.11+* of Python
  - Install required python packages using `pip install -r requirements.txt`
  - Run `python app.py` from a terminal

