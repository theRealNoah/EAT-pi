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


### __Dependencies__ 

The following packages and files are dependencies for `eatMain.py`


__Local File__
- DF_Oxygen.py is a local library file that must be in the same directory

__Packages__
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
