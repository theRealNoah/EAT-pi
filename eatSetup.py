import sys
import subprocess

# Local File
# DF_Oxygen.py is a local library file that must be in the same directory

# Packages
# - sensor https://github.com/nickoala/sensor
# - RPi.GPIO https://pypi.org/project/RPi.GPIO/
# - matplotlib https://matplotlib.org/stable/index.html
# - numpy https://numpy.org/
#   - Need specific version 1.20.0 to work with Python 3.9
# - gpiozero https://gpiozero.readthedocs.io/en/stable/index.html
# - pyDrive https://pythonhosted.org/PyDrive/

packages = [
    "sensor",
    "RPi.GPIO",
    "matplotlib",
    "numpy==1.20.0",
    "gpiozero",
    "pydrive"
]

for package in packages:
    # implement pip as a subprocess to install packages needed
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
