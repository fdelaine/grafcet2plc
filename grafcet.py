#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""grafcet.py"""

import warnings
from functools import partial


class Grafcet:
    """Represents a GRAFCET"""

    def __init__(self, name=None):
        self.name = name

        self.steps = dict()
        self.transitions = dict()

        self.inputs = dict()
        self.outputs = dict()

        self.indexPlcReset = None

    def __str__(self):
        return 'Grafcet {}'.format(self.name)

    def __repr__(self):
        return str(self)

    def get_plc_reset_index(self):
        return self.indexPlcReset

    def add_step(self, step):
        if step not in self.steps:
            self.steps[step.get_index()] = step
        else:
            warnings.warn("{} already existing as step for {}".format(step, self), UserWarning)

    def delete_step(self, step):
        self.steps.pop(step.get_index())
        del step

    def add_transition(self, transition):
        if transition not in self.transitions:
            self.transitions[transition.get_index()] = transition
        else:
            warnings.warn("{} already existing as transition for {}".format(transition, self), UserWarning)

    def delete_transition(self, transition):
        self.transitions.pop(transition.get_index())
        del transition

    def check_consistency(self):
        pass

    def generate(self):
        code = ('myGrafcet', [1], (1, 2, 3), (4, 5, 6), [(1, 4), (2, 5), (3, 6)], [(4, 2), (4, 3), (5, 1), (6, 1)])

        self.name = code[0]
        for index in code[2]:
            step = Step(index)
            if index in code[1]:
                step.set_initial()

            self.add_step(step)

        for index in code[3]:
            transition = Transition(index)
            self.add_transition(transition)

        for couple in code[4]:
            indexStep = couple[0]
            indexTransition = couple[1]

            if (indexStep in self.steps.keys()) and (indexTransition in self.transitions.keys()):
                self.transitions[indexTransition].add_preceding_step(self.steps[indexStep])
                self.steps[indexStep].add_succeeding_transition(self.transitions[indexTransition])

        for couple in code[5]:
            indexTransition = couple[0]
            indexStep = couple[1]

            if (indexStep in self.steps.keys()) and (indexTransition in self.transitions.keys()):
                self.transitions[indexTransition].add_succeeding_step(self.steps[indexStep])
                self.steps[indexStep].add_preceding_transition(self.transitions[indexTransition])

    def preprocess_expression(self, rawExpression):

        expression = list()
        expression.append(rawExpression[0])
        if rawExpression[0] == ('AND' or'OR'):
            members = list()

            for member in rawExpression[1]:
                members.append(self.preprocess_expression(member))

            expression.append(members)

        elif rawExpression[0] == ('NOT' or 'RE' or 'FE'):
            expression.append(self.preprocess_expression(rawExpression[1]))

        elif rawExpression[0] == 'CONST':
            expression.append(rawExpression[1])

        elif rawExpression[0] == ('DE' or 'DU'):
            subexpression = list(rawExpression[1])
            if subexpression[1] in self.steps.keys():
                subexpression[1] = self.steps[subexpression [1]]
                expression.append(subexpression)

        elif rawExpression[0] == 'IN':
            if rawExpression[1] in self.inputs.keys():
                expression.append(self.inputs[rawExpression[1]])

        elif rawExpression[0] == 'OU':
            if rawExpression[1] in self.outputs.keys():
                expression.append(self.outputs[rawExpression[1]])

        else:
            print("unknown expression identifier")

        return expression


class Step:
    """Step of a GRAFCET"""

    def __init__(self, index, initial=False, commentary=None, actions=None, plcIndex=None):
        self.index = index
        self.initial = initial
        self.plcIndex = plcIndex
        self.commentary = commentary
        self.actions = actions

        if self.actions is None:
            self.actions = list()

        self.precedingTransitions = list()
        self.succeedingTransitions = list()

    def __str__(self):
        return 'X{}'.format(self.index)

    def __repr__(self):
        return str(self)

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

    def set_initial(self):
        self.initial = True

    def unset_initial(self):
        self.initial = False

    def is_initial(self):
        return self.initial

    def set_plc_index(self, plcIndex):
        self.plcIndex = plcIndex

    def get_plc_index(self):
        return self.plcIndex

    def add_action(self, action):
        self.actions.append(action)

    def remove_action(self, action):
        self.actions.remove(action)

    def get_actions(self):
        return self.actions

    def add_preceding_transitions(self, transitions):
        for transition in transitions:
            self.add_preceding_transition(transition)

    def add_preceding_transition(self, transition):
        if transition not in self.precedingTransitions:
            self.precedingTransitions.append(transition)
        else:
            warnings.warn("{} already existing as preceding transition for {}".format(transition, self), UserWarning)

    def get_preceding_transitions(self):
        return self.precedingTransitions

    def remove_preceding_transitions(self):
        self.precedingTransitions.clear()

    def remove_preceding_transition(self, transition):
        self.precedingTransitions.remove(transition)

    def add_succeeding_transitions(self, transitions):
        for transition in transitions:
            self.add_succeeding_transition(transition)

    def add_succeeding_transition(self, transition):
        if transition not in self.succeedingTransitions:
            self.succeedingTransitions.append(transition)
        else:
            warnings.warn("{} already existing as succeeding transition for {}".format(transition, self), UserWarning)

    def get_succeeding_transitions(self):
        return self.succeedingTransitions

    def remove_succeeding_transitions(self):
        self.succeedingTransitions.clear()

    def remove_succeeding_transition(self, transition):
        self.succeedingTransitions.remove(transition)


class Transition:
    """Transition of a GRAFCET"""

    def __init__(self, index, condition=None, plcIndex=None):
        self.index = index
        self.plcIndex = plcIndex
        self.condition = condition

        self.precedingSteps = list()
        self.succeedingSteps = list()

    def __str__(self):
        return 'Y{}'.format(self.index)

    def __repr__(self):
        return str(self)

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

    def set_plc_index(self, plcIndex):
        self.plcIndex = plcIndex

    def get_plc_index(self):
        return self.plcIndex

    def get_condition(self):
        return self.condition

    def add_preceding_steps(self, steps):
        for step in steps:
            self.add_preceding_step(step)

    def add_preceding_step(self, step):
        if step not in self.precedingSteps:
            self.precedingSteps.append(step)
        else:
            warnings.warn("{} already existing as preceding step for {}".format(step, self), UserWarning)

    def get_preceding_steps(self):
        return self.precedingSteps

    def remove_preceding_steps(self):
        self.precedingSteps.clear()

    def remove_preceding_step(self, step):
        self.precedingSteps.remove(step)

    def add_succeeding_steps(self, steps):
        for step in steps:
            self.add_succeeding_step(step)

    def add_succeeding_step(self, step):
        if step not in self.succeedingSteps:
            self.succeedingSteps.append(step)
        else:
            warnings.warn("{} already existing as succeeding step for {}".format(step, self), UserWarning)

    def get_succeeding_steps(self):
        return self.succeedingSteps

    def remove_succeeding_steps(self):
        self.succeedingSteps.clear()

    def remove_succeeding_step(self, step):
        self.succeedingSteps.remove(step)


class Action:

    types = {0: "continuous", 1: "on activation", 2: "on deactivation", 3: "on event"}

    def __init__(self, step, type="continuous", condition=None, output=None, plcIndex=None):
        self.step = step
        self.type = type
        self.condition = condition
        self.output = output
        self.plcIndex = plcIndex

    def __str__(self):
        return self.step

    def __repr__(self):
        return str(self)

    def set_step(self, step):
        self.step = step

    def get_step(self):
        return self.step

    def set_type(self, index):
        self.types = Action.types[index]

    def get_type(self):
        return self.type

    def set_condition(self, expression):
        self.condition = expression

    def get_condition(self):
        return self.condition

    def set_output(self, output):
        self.output = output

    def remove_output(self):
        self.output = None

    def get_output(self):
        return self.output

    def set_plc_index(self, plcIndex):
        self.plcIndex = plcIndex

    def get_plc_index(self):
        return self.plcIndex


class ExpressionBinary:

    def __init__(self, type, expression):
        self.type = type

        self.members = list()

        for member in expression:
            self.members.append(Expression(member))


class ExpressionUnary:

    def __init__(self, type, expression):
        self.type = type
        self.member = Expression(expression)

    def __str__(self):
        return "{} of {}".format(self.type, self.member)

    def __repr__(self):
        return str(self)


class Constant:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)


class Delay:

    def __init__(self, expression):
        self.delay_re = expression[0]
        self.step = expression[1]
        self.delay_fe = expression[2]

    def __str__(self):
        return "{}/{}/{}".format(self.delay_fe, self.step, self.delay_re)

    def __repr__(self):
        return str(self)

    def get_step(self):
        return self.step


class Duration:

    def __init__(self, expression):
        self.duration = expression[0]
        self.step = expression[1]

    def __str__(self):
        return "{}/{}".format(self.duration, self.step)

    def __repr__(self):
        return str(self)


class Input:

    def __init__(self, name, plcIndex=None):
        self.name = name
        self.plcIndex = plcIndex

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_plc_index(self, plcIndex):
        self.plcIndex = plcIndex

    def get_plc_index(self):
        return self.plcIndex


class Output:

    def __init__(self, name, plcIndex=None):
        self.name = name
        self.plcIndex = plcIndex

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_plc_index(self, plcIndex):
        self.plcIndex = plcIndex

    def get_plc_index(self):
        return self.plcIndex


class Expression:

    cases = {'AND': partial(ExpressionBinary, 'AND'),
             'OR': partial(ExpressionBinary, 'OR'),
             'NOT': partial(ExpressionUnary, 'NOT'),
             'RE': partial(ExpressionUnary, 'RE'),
             'FE': partial(ExpressionUnary, 'FE'),
             'CONST': Constant,
             'DE': Delay,
             'DU': Duration,
             'IN': Input,
             'OU': Output}

    def __init__(self, expression):
        self.expression = self.cases[expression[0]](expression[1])
