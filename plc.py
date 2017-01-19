#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""plc.py"""

import warnings

from grafcet import *


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class TimerError(Error):
    """Exception raised for index overflow of timers.

    Attributes:
        baseType -- concerned type
    """

    def __init__(self, baseType):
        self.baseType = baseType


class PlcIndexError(Error):
    """Exception raised for missing plc indexes.

    Attributes:
        object -- object concerned
    """

    def __init__(self, object):
        self.object = object

class PlcResetError(Error):
    """Exception raised for missing plc reset information.

    Attributes:
        object -- object concerned
    """

    def __init__(self, object):
        self.object = object


class Plc:
    name = "None"


class Simatic_S7_200(Plc):

    name = "Simatic S7-200"

    def __init__(self):
        self.networkCounter = 0
        self.plcResetIndex = None
        self.delayTimeBases = [0.001, 0.01, 0.1]
        self.delayIndexes = {self.delayTimeBases[0]: [32, 96],
                             self.delayTimeBases[1]: list(range(33, 37)) + list(range(97, 101)),
                             self.delayTimeBases[2]: list(range(37, 64)) + list(range(101, 256))}
        self.delayIndexesCounters = {self.delayTimeBases[0]: 0,
                                     self.delayTimeBases[1]: 0,
                                     self.delayTimeBases[2]: 0}

        self.delayCodes = dict()
        self.delayPlcIndexes = dict()

    def convert_expression(self, expression):
        code = str()

        expression = expression.get_expression()

        try:
            if type(expression) is ExpressionBinary:
                code += self.convert_expression_binary(expression)

            elif type(expression) is ExpressionUnary:
                code += self.convert_expression_unary(expression)

            elif type(expression) is Input:
                code += 'LD ' + expression.get_plc_index() + '\n'

            elif type(expression) is Step:
                code += 'LD ' + expression.get_plc_index() + '\n'

            elif type(expression) is Delay:
                if expression not in self.delayCodes.keys():
                    self.convert_delay(expression)
                code += 'LD ' + 'T' + str(self.delayPlcIndexes[expression]) + '\n'

            elif type(expression) is Constant:
                if expression.get_value() is 1:
                    pass  # TODO: Manage values
            else:
                raise TypeError("{} conversion in expression is not managed".format(type(expression)))

            return code
        except TypeError as err:
            print(err)

    def convert_expression_binary(self, expression):
        code = str()
        typeConversion = {'AND': 'ALD', 'OR': 'OLD'}

        try:
            assert expression.get_type() in typeConversion.keys()
            type = typeConversion[expression.get_type()]
            members = expression.get_members()

            for member in members:
                code += self.convert_expression(member)

                if member is not members[0]:
                    code += type + '\n'

            return code
        except AssertionError:
            print("Expression type is not known for binary expressions")

    def convert_expression_unary(self, expression):
        code = self.convert_expression(expression.get_member())

        typesConversion = {'NOT': 'NOT\n', 'RE': 'EU\n', 'FE': 'ED\n'}

        type = expression.get_type()

        try:
            assert type in typesConversion.keys()
            code += typesConversion[type]
            return code

        except AssertionError:
            print("Expression type is not known for unary expressions")

    def convert_delay(self, delay):

        delay_re = delay.get_delay_re()
        delay_fe = delay.get_delay_fe()

        try:
            if delay_fe != 0:
                warnings.warn("Falling edge delay of {} is not null."
                              " Currently falling edge conversion is not implemented. Issues may occur".format(delay))
                # TODO: manage delays with FE
            assert delay_re > self.delayTimeBases[0]

            if delay_re < self.delayTimeBases[1]:
                timeBase = 0
            elif delay_re < self.delayTimeBases[2]:
                timeBase = 1
            else:
                timeBase = 2

            duration = round(delay_re / self.delayTimeBases[timeBase])

            if self.delayIndexesCounters[self.delayTimeBases[timeBase]] > len(self.delayIndexes[self.delayTimeBases[timeBase]]):
                raise TimerError(timeBase)

            index = self.delayIndexes[self.delayTimeBases[timeBase]][self.delayIndexesCounters[self.delayTimeBases[timeBase]]]

            self.delayIndexesCounters[self.delayTimeBases[timeBase]] += 1

            code = self.convert_expression(delay.get_expression())
            code += "TON T{}, {}\n".format(index, duration)

            self.delayCodes[delay] = code
            self.delayPlcIndexes[delay] = index

        except AssertionError:
            print("Rising edge delay is smaller than the smallest timer time base of the PLC")
        except TimerError as err:
            print("Index overflow for timer of base type {}".format(err.baseType))

    def write_delays(self):
        code = str()
        for key in self.delayCodes:
            self.networkCounter += 1
            code += "Network {} // Delay \n".format(self.networkCounter)
            code += self.delayCodes[key]

        return code

    def convert_step(self, step):
        self.networkCounter += 1
        code = "Network {} // {}\n".format(self.networkCounter, step)

        precedingTransitions = step.get_preceding_transitions()
        succeedingTransitions = step.get_succeeding_transitions()

        code += "LD {}\n".format(precedingTransitions[0].get_plc_index())
        for transition in precedingTransitions[1:]:
            code += "O {}\n".format(transition.get_plc_index())

        if step.is_initial():
            code += """LD {}
            EU
            OLD""".format(self.plcResetIndex)

        code += "LD {}\n".format(succeedingTransitions[0].get_plc_index())
        for transition in succeedingTransitions[1:]:
            code += "O {}\n".format(transition.get_plc_index())

        code += "ON {}\n".format(self.plcResetIndex)

        code += "NOT\nA {}\nOLD\n= {}\n".format(step.get_plc_index(), step.get_plc_index())

        return code

    def convert_transition(self, transition):
        self.networkCounter += 1
        code = "Network {} // {}\n".format(self.networkCounter, transition)

        steps = transition.get_preceding_steps()
        code += "LD {}\n".format(steps[0].get_plc_index())

        for step in steps[1:]:
            code += "A {}\n".format(step.get_plc_index())

        expressionConverted = self.convert_expression(transition.get_condition())

        if expressionConverted is not '':
            code += expressionConverted + "ALD\n"

        code += "= {}\n".format(transition.get_plc_index())

        return code

    def convert_output(self, output):
        self.networkCounter += 1
        code = "Network {} // {}\n".format(self.networkCounter, output.get_name())

        actions = output.get_actions()

        code += "LD {}\n".format(actions[0].get_step().get_plc_index())
        if actions[0].get_condition() is not None:
            code += "LD {}\n".format(actions[0].get_step().get_plc_index())
            code += self.convert_expression(actions[0].get_condition())
            code += "ALD\n"

        for action in actions[1:]:
            if action.get_condition() is not None:
                code += "LD {}\n".format(action.get_step().get_plc_index())
                code += self.convert_expression(action.get_condition())
                code += "ALD\n"
                code += "OLD\n"
            else:
                code += "O {}\n".format(action.get_step().get_plc_index())

        code += "= {}\n".format(output.get_plc_index())

        return code

    def get_code(self, grafcet):
        if grafcet.check_consistency() and self.check_grafcet_plc_indexes(grafcet):
            self.plcResetIndex = grafcet.get_plc_reset().get_plc_index()

            code = "SUBROUTINE_BLOCK Mode_Auto:SBR0\n"
            code += "TITLE=COMMENTAIRES DE SOUS-PROGRAMME\n"
            code += "BEGIN\n"

            transitions = grafcet.get_transitions()

            for key in transitions:
                transition = transitions[key]

                code += self.convert_transition(transition)

            steps = grafcet.get_steps()

            for key in steps:
                step = steps[key]
                code += self.convert_step(step)

            outputs = grafcet.get_outputs()

            for key in outputs:
                output = outputs[key]
                code += self.convert_output(output)

            code += self.write_delays()

            code += "END_SUBROUTINE_BLOCK\n"

            code = self.simplify_code(code)

            return code
        else:
            return None

    def check_grafcet_plc_indexes(self, grafcet):

        steps = grafcet.get_steps()
        transitions = grafcet.get_transitions()
        inputs = grafcet.get_inputs()
        outputs = grafcet.get_outputs()

        try:
            if grafcet.get_plc_reset() is None:
                raise PlcResetError(grafcet)

            elif grafcet.get_plc_reset().get_plc_index() is None:
                raise PlcIndexError(grafcet.get_plc_reset())

            for key in steps:
                if steps[key].get_plc_index() is None:
                    raise PlcIndexError(steps[key])

            for key in transitions:
                if transitions[key].get_plc_index() is None:
                    raise PlcIndexError(transitions[key])

            for key in inputs:
                if inputs[key].get_plc_index() is None:
                    raise PlcIndexError(inputs[key])

            for key in outputs:
                if outputs[key].get_plc_index() is None:
                    raise PlcIndexError(outputs[key])

            return True

        except PlcResetError as err:
            print("Missing PLC reset information for {}".format(err.object))
            sys.exit(1)  # TODO: Be nicer here
        except PlcIndexError as err:
            print("Missing PLC index information for {}".format(err.object))
            sys.exit(1)  # TODO: Be nicer here

    def simplify_code(self, code):

        codeSimplified = str()
        codeLines = code.splitlines(True)
        indexes = iter(range(len(codeLines)))

        for index in indexes:
            if codeLines[index][0:2] == 'LD':
                if codeLines[index+1][0:3] == 'ALD':
                    codeSimplified += codeLines[index].replace('LD', 'A')
                    next(indexes)
                elif codeLines[index+1][0:3] == 'OLD':
                    codeSimplified += codeLines[index].replace('LD', 'O')
                    next(indexes)
                else:
                    codeSimplified += codeLines[index]
            else:
                codeSimplified += codeLines[index]

        return codeSimplified
