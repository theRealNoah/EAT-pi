from DF_Oxygen import *
def checkOxygen():
    # print("No oxygen, help!")
    while(True):
        IIC_MODE = 0x01  # default use IIC1
        COLLECT_NUMBER = 10
        oxygen = DFRobot_Oxygen_IIC(IIC_MODE, ADDRESS_3)
        oxygen_data = oxygen.get_oxygen_data(COLLECT_NUMBER)
        print("oxygen concentration is %4.2f %%vol" % oxygen_data)
        time.sleep(1)
checkOxygen()