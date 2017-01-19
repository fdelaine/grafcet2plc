#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""grafcet2plc.py"""

import csv

from grafcetparser import GrafcetParser
from plc import *

introduction = '''
================== grafcet2plc =======================

This is a example of how to use this software.

It will use the files in the folder named "example".

======================================================
'''

print(introduction)

print(">>> Opening input file…")
file = open("example/inputGrafcet.txt", 'r', encoding='latin1')
data = file.read()
file.close()

print(">>> Decoding input file…")
decode = GrafcetParser.parser_cadepa()
dataDecoded = decode(data)

print(">>> Data decoded:")
print(dataDecoded)

print(">>> Generate Grafcet…")
grafcet = Grafcet()
grafcet.generate(dataDecoded)

print(">>> Add PLC symbols to the grafcet…")
print("\t* Inputs…")
with open('example/inputs.csv', newline='') as csvfile:
    contentInputs = csv.reader(csvfile, delimiter=';', quotechar='"')
    grafcet.import_plc_data_inputs(contentInputs)

print("\t* Outputs…")
with open('example/outputs.csv', newline='') as csvfile:
    contentOutputs = csv.reader(csvfile, delimiter=';', quotechar='"')
    grafcet.import_plc_data_outputs(contentOutputs)

print("\t* Steps…")
with open('example/steps.csv', newline='') as csvfile:
    contentSteps = csv.reader(csvfile, delimiter=';', quotechar='"')
    grafcet.import_plc_data_steps(contentSteps)

print("\t* Transitions…")
with open('example/transitions.csv', newline='') as csvfile:
    contentTranstitions = csv.reader(csvfile, delimiter=';', quotechar='"')
    grafcet.import_plc_data_transitions(contentTranstitions)

print("\t* PLC reset…")
with open('example/plcReset.csv', newline='') as csvfile:
    contentReset = csv.reader(csvfile, delimiter=';', quotechar='"')
    grafcet.import_plc_data_reset(contentReset)

print(">>> Converting Grafcet in S7-200 code…")
plc = Simatic_S7_200()
code = plc.get_code(grafcet)

print(">>> Result:")
print(code)

print(">>> Writing result file in 'example/result.awl'…")
with open('example/result.awl', 'w', encoding='utf-8') as file:
    file.write(code)

print(">>> Conversion DONE")
print(">>> Exit")
