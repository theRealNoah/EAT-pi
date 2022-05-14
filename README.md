# Extraterrestrial Automated Terrarium (EAT-PI)

## University of South Florida 2021-2022

## Electrical Engineering Senior Design

---

### Created by:

- James Hunter Ireland - [LinkedIn](https://www.linkedin.com/in/jhireland/)

- Noah Hamilton - [LinkedIn](https://www.linkedin.com/in/noah--hamilton/)

- Emalia Tack - [LinkedIn](https://www.linkedin.com/in/emalia-tack/)

- Kai Jesson - [LinkedIn](https://www.linkedin.com/in/kai-jesson1/)

---

## Overview

Through the Florida Space Grant Consortium and collaboration with the National Aeronautical and Space Administration’s (NASA) Kennedy Space Center (KSC), this project provides a plant life sciences CubeSat research platform to study the effects of nutritious crop production in transit to lunar orbit.

---

## Project Website

[https://usfcsli.wixsite.com/home](https://usfcsli.wixsite.com/home)

---

## Getting Setup

This project requires two main programs to be run in order for the EAT System to operate as intended.

Assuming the Raspberry Pi Zero 2 is already configured following the document "Pi Connections" found in the SharePoint.

### **Dependencies**

The following packages and files are dependencies for `eatMain.py`

**Local File**

- DF_Oxygen.py is a local library file that must be in the same directory

**Packages**

- sensor https://github.com/nickoala/sensor
- RPi.GPIO https://pypi.org/project/RPi.GPIO/
- matplotlib https://matplotlib.org/stable/index.html
- numpy https://numpy.org/
- Need specific version 1.20.0 to work with Python 3.9
- gpiozero https://gpiozero.readthedocs.io/en/stable/index.html
- pyDrive https://pythonhosted.org/PyDrive/

```
packages = [
    "sensor",
    "RPi.GPIO",
    "matplotlib",
    "numpy==1.20.0",
    "gpiozero",
    "pydrive"
]
```

Run the following setup script to install necessary packages and cleanup the GPIO pins.

```
python eatSetup.py
```

To operate EAT normally run:

```
python eatMain.py
```

Notes:
This project uploads images and plots to Google Drive, you will need to re-download the client-secrets from the Project's Google Account before rerunning this code.

Following this page for Authentication:
https://www.projectpro.io/recipes/upload-files-to-google-drive-using-python

Hint: You'll need to create the `settings.yml` file and download the `client_secrets.json` file

---

## File Breakdown

- `breatheTest.py`
  - Used for an experiment of the temperature/humidity sensor and oxygen sensor
- `calOxy.py`
  - Used to calibrate the oxgyen sensor for it's very first time use, corrects the baseline per manufacturer specification
- `DF_Oxygen.py`
  - Local File used to fetch oxygen data in the code from the manufacturer
- `eatMain.py`
  - Main Script for operating the EAT System
- `eatMainReverse.py`
  - Copy of Main Script for operating the EAT system pump in Reverse
- `eatSetup.py`
  - Setup Script for initial turn-on of the EAT systme
- `motor_test.py`
  - Testing the Stepper Motors
- `parseLog.py`
  - Script for exporting TXT file to CSV for plotting in MATLAB from O2 Calibration
- `testKill.py`
  - Script for testing Software Shutdown of Raspberry Pi
- `upload_log.py`
  - Script to test uploading files to Google Drive

---

For questions or concerns on information found in this repository contact Noah Hamilton at consultnoahhamilton@gmail.com

---
