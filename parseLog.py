# # open text file in read mode
# text_file = open("o2BeforeCal2.txt", "r")

# open text file in read mode
text_file = open("o2AfterCal2.txt", "r")

# read whole file to a string
data = text_file.read()

# close file
text_file.close()

dataList = data.split(',')

goodData = dataList[-180:]

print(goodData)
print(len(goodData))

import pandas as pd

df = pd.DataFrame(goodData)
# df.to_csv('beforeCal.csv')
df.to_csv('afterCal.csv')


