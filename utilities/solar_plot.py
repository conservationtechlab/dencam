import sys

import matplotlib.pyplot as plt
import pandas as pd


def _get_x_axis_label(date, time):
    date_time_label = []
    for i in range(len(date)):
        date_time_label.append(str(date[i])[5:] + ':' + time[i][:3])
    return date_time_label


def _get_argument():
    return sys.argv[1]


file_path = "/home/pi/dencam/solar.csv"  # path to solar goes here


plt.rcParams["figure.figsize"] = [800, 6]
plt.rcParams["figure.autolayout"] = True
plt.xticks(rotation=90)
plt.rc('axes', labelsize=5)

data_frame = pd.read_csv(file_path)
date_list = data_frame["Date"].tolist()
time_list = data_frame["Time"].tolist()
date_time_label = _get_x_axis_label(date_list, time_list)

solar_data = str(_get_argument())

plt.title(solar_data)
plt.plot(date_time_label, data_frame[solar_data], 'g--', label=solar_data)
plt.scatter(date_time_label, data_frame[solar_data], marker='o')
plt.xticks(date_time_label[::5])
plt.show()
