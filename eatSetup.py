import sys
import subprocess

# Local File
# DF_Oxygen.py is a local library file that must be in the same directory

# Packages
# - sensor https://github.com/nickoala/sensor
# - RPi.GPIO https://pypi.org/project/RPi.GPIO/
# - matplotlib https://matplotlib.org/stable/index.html
# - numpy - Need specific version to work with Python 3.9

packages = [
    "sensor",
    "RPi.GPIO",
    "matplotlib",
    "numpy==1.20.0",
]

for package in packages:
    # implement pip as a subprocess to install packages needed
    subprocess.check_call([sys.executable, '-m', 'pip', 'install',
    package])
