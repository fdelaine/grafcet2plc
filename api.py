#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""api.py"""


class Api:
    name = "None"


class Simatic_S7_200(Api):

    name = "Simatic S7-200"

    def get_code(cls, grafcet):
        code = ''

        return code

    get_code = classmethod(get_code)