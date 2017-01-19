# grafcet2plc
## Presentation

grafcet2plc is a Python software to generate source code for programmable logic controllers (PLC) based on GRAFCETs.

GRAFCET is a graphical specification language for the functional description of the
behaviour of the sequential part of the control systems.

Usually, once you entered a GRAFCET with a dedicated edition software for analysis for example, the very same GRAFCET must entered with the PLC constructor's software to implement the automaton if it is not supported by the edition software. The purpose of this software is giving an interface between edition softwares and PLC requirements to accelerate PLC programming.

It is currently developped for an old version of CADEPA and a Siemens Simatic S7-200.

## Standards
This software aims to respect the NF EN 60848 which defines the GRAFCET. Currently, some properties are not defined in grafcet.py but it is planned for a future realease. I had no time to check on some aspects of CADEPA, which does not support some properties of GRAFCETs.

A project is to implement the outputs defined by the CEI 61131-3 standard.

## How to generate PLC code with an export from an edition software
The file grafcet2plc.py gives an example of how to perform that. No script is available yet to select an input and an output format and to do the operation as only one input format and one output exist. (In fact I've been a bit lazy).

## My PLC is not available. What should I do?
Code the class dumbass! I won't do that for every PLC.

### How to add a PLC
Create a class on the model of plc.Simatic_S7-200 in plc.py.

## My input format is not available. What should I do?
Again, code it.

### How to add an input format
This time it is a class method in GrafcetParser that must be added. It is based on Simple Parser (http://www.cdsoft.fr/sp/) so use its documentation and the model for CADEPA.

## License
Copyright (C) 2017  Florentin Delaine

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

This software uses Simple Parser (http://www.cdsoft.fr/sp/) distributed under LGPL license.

## Contact
Florentin Delaine: florentin.delaine@gmail.com
