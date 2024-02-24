"""Plot some useful data from solar logs

Example usage: python solar_plot.py /home/pi/dencam/solar.csv

"""
import argparse

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

dataframe = pd.read_csv(file_path)
dataframe['datetime'] = pd.to_datetime(dataframe.Date + ' ' + dataframe.Time)

# plt.rcParams["figure.autolayout"] = True

fig, ax = plt.subplots(figsize=(800, 6))
fig.canvas.manager.set_window_title('Plot of One Column of DenCam Solar data')
ax.set_title(column_to_plot)
ax.plot(dataframe['datetime'],
        dataframe[column_to_plot],
        'g--',
        label=column_to_plot)
ax.scatter(dataframe['datetime'],
           dataframe[column_to_plot],
           marker='o')

ax.tick_params(labelrotation=60)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=6))
ax.tick_params(axis='both', which='major', labelsize=10,
               width=2.5, length=10)
ax.tick_params(axis='x', which='minor', labelsize=10,
               width=1.5, length=5, pad=30)

# plt.gcf().autofmt_xdate()
plt.show()
