from GlobalLink import ClassNames
import os
import csv

class_codes = []
class_codes_names = {}

with open(os.path.join(ClassNames, 'classes-bbox.txt'), 'r') as file:
    for line in file:
        class_codes.append(line.strip())

with open(os.path.join(ClassNames, 'class-descriptions.csv'), newline='', encoding='utf-8') as file:
    csvreader = csv.reader(file)
    for line in csvreader:
        code = line[0].strip()
        name = line[1].strip()
        class_codes_names[code] = name

with open(os.path.join(ClassNames, 'classes-600-names.txt'), 'w') as file:
    for code in class_codes:
        file.write(class_codes_names[code] + ', ')

