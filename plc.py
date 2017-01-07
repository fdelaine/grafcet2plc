#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""plc.py"""


class Plc:
    name = "None"


class Simatic_S7_200(Plc):

    name = "Simatic S7-200"

    def get_code(cls, grafcet):
        code = ''

        return code

    get_code = classmethod(get_code)