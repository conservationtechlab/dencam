import csv
import os


def get_solardisplay_info():
    if not os.path.exists('/home/pi/dencam/solar.csv'):
        return "File Not Found"
    with open('/home/pi/dencam/solar.csv') as file:
        heading = next(file)
        reader_obj = csv.reader(file)
        last_row = ''
        for row in reader_obj:
            last_row = row
        if len(last_row) == 1:
            return last_row
        solar_text = last_row[0] + '\n' + last_row[1] + last_row[2]
        solar_text += '\n' + last_row[3] + last_row[4]
        solar_text += '\n' + last_row[9] + last_row[10]
        return solar_text


