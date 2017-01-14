#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""plc.py"""

from grafcet import *


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
        if type(expression.expression) is ExpressionBinary:
            code += self.convert_expression_binary(expression.expression)

        elif type(expression.expression) is ExpressionUnary:
            code += self.convert_expression_unary(expression.expression)

        elif type(expression.expression) is Input:
            code += 'LD ' + expression.expression.get_plc_index() + '\n'

        elif type(expression.expression) is Step:
            code += 'LD ' + expression.expression.get_plc_index() + '\n'

        elif type(expression.expression) is Delay:
            if expression.expression not in self.delayCodes.keys():
                self.convert_delay(expression.expression)
            code += 'LD ' + 'T' + str(self.delayPlcIndexes[expression.expression]) + '\n'

        elif type(expression.expression) is Constant:
            if expression.expression.value is 1:
                pass

        return code

    def convert_expression_binary(self, expression):
        code = str()
        typeConversion = {'AND': 'ALD', 'OR': 'OLD'}

        for member in expression.members:
            code += self.convert_expression(member)

            if member is not expression.members[0]:
                code += typeConversion[expression.type] + '\n'

        return code

    def convert_expression_unary(self, expression):
        code = self.convert_expression(expression.member)

        if expression.type == 'NOT':
            code += 'NOT\n'

        elif expression.type == 'RE':
            code += 'EU\n'

        elif expression.type == 'FE':
            code += 'ED\n'

        return code

    def convert_delay(self, delay):

        # TODO: add warning if delay_fe is not 0
        if delay.delay_re < self.delayTimeBases[0]:
            # TODO: add error
            pass
        elif delay.delay_re < self.delayTimeBases[1]:
            timeBase = 0
        elif delay.delay_re < self.delayTimeBases[2]:
            timeBase = 1
        else:
            timeBase = 2

        # TODO: add error handler for index overflow
        duration = round(delay.delay_re / self.delayTimeBases[timeBase])
        index = self.delayIndexes[self.delayTimeBases[timeBase]][self.delayIndexesCounters[self.delayTimeBases[timeBase]]]
        self.delayIndexesCounters[self.delayTimeBases[timeBase]] += 1

        code = "LD {}\n".format(delay.step.expression.get_plc_index())
        code += "TON T{}, {}\n".format(index, duration)

        self.delayCodes[delay] = code
        self.delayPlcIndexes[delay] = index

    def write_delays(self):
        code = str()
        for key in self.delayCodes:
            self.networkCounter += 1
            code += "Network {} // Delay \n".format(self.networkCounter)
            code += self.delayCodes[key]

        return code

    def convert_step(self, step):
        self.networkCounter += 1
        code = "Network {} // Step {}\n".format(self.networkCounter, step)

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
        code = "Network {} // Transition {}\n".format(self.networkCounter, transition)

        steps = transition.get_preceding_steps()
        code += "LD {}\n".format(steps[0].get_plc_index())

        for step in steps[1:]:
            code += "A {}\n".format(step.get_plc_index())

        code += self.convert_expression(transition.get_condition())

        code += "ALD\n"
        code += "= {}\n".format(transition.get_plc_index())

        return code

    def convert_output(self, output):
        self.networkCounter += 1
        code = "Network {} // Output {}\n".format(self.networkCounter, output.get_name())

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

        return code
