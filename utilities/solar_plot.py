"""Plot some useful data from solar logs

Example usage: python solar_plot.py /home/pi/dencam/solar.csv

"""
import argparse
import sys

import matplotlib.pyplot as plt
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-f',
                    '--filepath',
                    required=True,
                    help="Path to solar data CSV file.")
parser.add_argument('-c',
                    '--column',
                    required=True,
                    help="Column of CSV to plot.")
args = parser.parse_args()

file_path = args.filepath
column_to_plot = args.column


def _get_x_axis_label(date, time):
    date_time_label = []
    for i in range(len(date)):
        date_time_label.append(str(date[i])[5:] + ':' + time[i][:3])
    return date_time_label


data_frame = pd.read_csv(file_path)

plt.rcParams["figure.figsize"] = [800, 6]
plt.rcParams["figure.autolayout"] = True
plt.xticks(rotation=90)
plt.rc('axes', labelsize=5)

date_list = data_frame["Date"].tolist()
time_list = data_frame["Time"].tolist()
date_time_label = _get_x_axis_label(date_list, time_list)

plt.title(column_to_plot)
plt.plot(date_time_label, data_frame[column_to_plot], 'g--', label=column_to_plot)
plt.scatter(date_time_label, data_frame[column_to_plot], marker='o')
plt.xticks(date_time_label[::5])
plt.show()
