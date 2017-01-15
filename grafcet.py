#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""grafcet.py"""

import warnings
import csv
from functools import partial


class Grafcet:
    """Represents a GRAFCET"""

    def __init__(self, name=None):
        self.name = name

        self.steps = dict()
        self.transitions = dict()

        self.inputs = dict()
        self.outputs = dict()

        self.plcReset = None

    def __str__(self):
        return 'Grafcet {}'.format(self.name)

    def __repr__(self):
        return str(self)

    def set_plc_reset(self, plcReset):
        self.plcReset = plcReset

    def get_plc_reset(self):
        return self.plcReset

    def add_step(self, step):
        if step not in self.steps:
            self.steps[step.get_index()] = step
        else:
            warnings.warn("{} already existing as step for {}".format(step, self), UserWarning)

    def delete_step(self, step):
        self.steps.pop(step.get_index())
        del step

    def get_steps(self):
        return self.steps

    def add_transition(self, transition):
        if transition not in self.transitions:
            self.transitions[transition.get_index()] = transition
        else:
            warnings.warn("{} already existing as transition for {}".format(transition, self), UserWarning)

    def delete_transition(self, transition):
        self.transitions.pop(transition.get_index())
        del transition

    def get_transitions(self):
        return self.transitions

    def check_consistency(self):
        pass

    def generate(self, code):

        self.name = code[0]

        for rawStep in code[2]:
            step = Step(rawStep[0][1], commentary=rawStep[2])
            if rawStep[0] in code[1]:
                step.set_initial(True)

            self.add_step(step)

        for rawTransition in code[3]:
            transition = Transition(rawTransition[0][1])
            self.add_transition(transition)

        for precedingRelation in code[4]:
            couple = precedingRelation[1]
            indexStep = couple[0][1]
            indexTransition = couple[1][1]

            if (indexStep in self.steps.keys()) and (indexTransition in self.transitions.keys()):
                self.transitions[indexTransition].add_preceding_step(self.steps[indexStep])
                self.steps[indexStep].add_succeeding_transition(self.transitions[indexTransition])

        for succeedingRelation in code[5]:
            couple = succeedingRelation[1]
            indexTransition = couple[0][1]
            indexStep = couple[1][1]

            if (indexStep in self.steps.keys()) and (indexTransition in self.transitions.keys()):
                self.transitions[indexTransition].add_succeeding_step(self.steps[indexStep])
                self.steps[indexStep].add_preceding_transition(self.transitions[indexTransition])

        for rawStep in code[2]:
            for rawAction in rawStep[1]:
                self.steps[rawStep[0][1]].add_action(self.process_action(rawAction))

        for rawTransition in code[3]:
            if len(rawTransition[1]) == 0:
                rawTransition[1].append(('CT', 1))
            self.transitions[rawTransition[0][1]].set_condition(self.process_expression(rawTransition[1][0]))

    def process_action(self, rawAction):
        action = Action()
        if rawAction[0][0] == 'OU':
            if rawAction[0][1] not in self.outputs.keys():
                self.outputs[rawAction[0][1]] = Output(rawAction[0][1])
            action.set_output(self.outputs[rawAction[0][1]])
            self.outputs[rawAction[0][1]].add_action(action)

        # TODO: improve to include other actions properties

        return action

    def process_expression(self, rawExpression):
        return Expression(self.preprocess_expression(rawExpression))

    def preprocess_expression(self, rawExpression):
        expression = list()
        expression.append(rawExpression[0])
        if rawExpression[0] == 'AND' or rawExpression[0] == 'OR':
            members = list()

            for member in rawExpression[1]:
                members.append(self.preprocess_expression(member))

            expression.append(members)

        elif rawExpression[0] == 'NOT' or rawExpression[0] == 'RE' or rawExpression[0] == 'FE':
            expression.append(self.preprocess_expression(rawExpression[1]))

        elif rawExpression[0] == 'CT':
            expression.append(rawExpression[1])

        elif rawExpression[0] == 'DE' or rawExpression[0] == 'DU':
            subexpression = [rawExpression[1][0]]
            subexpression.append(self.preprocess_expression(rawExpression[1][1]))
            subexpression.append(0)
            expression.append(subexpression)
            # TODO: add other cases

        elif rawExpression[0] == 'IN':
            if rawExpression[1] not in self.inputs.keys():
                self.inputs[rawExpression[1]] = Input(rawExpression[1])

            expression.append(self.inputs[rawExpression[1]])

        elif rawExpression[0] == 'OU':
            if rawExpression[1] not in self.outputs.keys():
                self.outputs[rawExpression[1]] = Output(rawExpression[1])
            expression.append(self.outputs[rawExpression[1]])

        elif rawExpression[0] == 'ST':
            if rawExpression[1] not in self.steps.keys():
                self.steps[rawExpression[1]] = Step(rawExpression[1])
            expression.append(self.steps[rawExpression[1]])

        else:
            print("unknown expression identifier", rawExpression)

        return expression

    def get_outputs(self):
        return self.outputs

    def import_plc_data(self):

        with open('var/inputs.csv', newline='') as csvfile:
            content = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in content:
                if row[0] not in self.inputs.keys():
                    input = Input(row[0], row[1])
                    self.inputs[input.get_name()] = input
                else:
                    self.inputs[row[0]].set_plc_index(row[1])

        with open('var/outputs.csv', newline='') as csvfile:
            content = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in content:
                if row[0] not in self.outputs.keys():
                    output = Output(row[0], row[1])
                    self.outputs[output.get_name()] = output
                else:
                    self.outputs[row[0]].set_plc_index(row[1])

        with open('var/steps.csv', newline='') as csvfile:
            content = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in content:
                if row[0][1:] not in self.steps.keys():
                    step = Step(row[0][1:], plcIndex=row[1])
                    self.steps[step.get_index()] = step
                else:
                    self.steps[row[0][1:]].set_plc_index(row[1])

        with open('var/transitions.csv', newline='') as csvfile:
            content = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in content:
                if row[0][1:] not in self.transitions.keys():
                    transition = Transition(row[0][1:], plcIndex=row[1])
                    self.transitions[transition.get_index()] = transition
                else:
                    self.transitions[row[0][1:]].set_plc_index(row[1])

        with open('var/plcReset.csv', newline='') as csvfile:
            content = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in content:
                if row[0][1:] not in self.transitions.keys():
                    input = Input(row[0], row[1])
                    self.plcReset = input


class Step:
    """Step of a GRAFCET"""

    def __init__(self, index, initial=False, commentary=None, actions=None, plcIndex=None):
        self.index = index
        self.initial = initial
        self.commentary = commentary
        self.actions = actions
        self.plcIndex = plcIndex

        if self.actions is None:
            self.actions = list()

        self.precedingTransitions = list()
        self.succeedingTransitions = list()

    def __str__(self):
        return "Step {}".format(self.index)

    def __repr__(self):
        return str(self)

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

    def set_initial(self, initial):
        self.initial = initial

    def is_initial(self):
        return self.initial

    def set_plc_index(self, plcIndex):
        self.plcIndex = plcIndex

    def get_plc_index(self):
        return self.plcIndex

    def add_action(self, action):
        action.set_step(self)
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

    def remove_preceding_transitions(self):
        self.precedingTransitions.clear()

    def remove_preceding_transition(self, transition):
        self.precedingTransitions.remove(transition)

    def get_preceding_transitions(self):
        return self.precedingTransitions

    def add_succeeding_transitions(self, transitions):
        for transition in transitions:
            self.add_succeeding_transition(transition)

    def add_succeeding_transition(self, transition):
        if transition not in self.succeedingTransitions:
            self.succeedingTransitions.append(transition)
        else:
            warnings.warn("{} already existing as succeeding transition for {}".format(transition, self), UserWarning)

    def remove_succeeding_transitions(self):
        self.succeedingTransitions.clear()

    def remove_succeeding_transition(self, transition):
        self.succeedingTransitions.remove(transition)

    def get_succeeding_transitions(self):
        return self.succeedingTransitions


class Transition:
    """Transition of a GRAFCET"""

    def __init__(self, index, condition=None, plcIndex=None):
        self.index = index
        self.condition = condition
        self.plcIndex = plcIndex

        self.precedingSteps = list()
        self.succeedingSteps = list()

    def __str__(self):
        return "Transition {}".format(self.index)

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

    def set_condition(self, condition):
        self.condition = condition

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

    def remove_preceding_steps(self):
        self.precedingSteps.clear()

    def remove_preceding_step(self, step):
        self.precedingSteps.remove(step)

    def get_preceding_steps(self):
        return self.precedingSteps

    def add_succeeding_steps(self, steps):
        for step in steps:
            self.add_succeeding_step(step)

    def add_succeeding_step(self, step):
        if step not in self.succeedingSteps:
            self.succeedingSteps.append(step)
        else:
            warnings.warn("{} already existing as succeeding step for {}".format(step, self), UserWarning)

    def remove_succeeding_steps(self):
        self.succeedingSteps.clear()

    def remove_succeeding_step(self, step):
        self.succeedingSteps.remove(step)

    def get_succeeding_steps(self):
        return self.succeedingSteps


class Action:

    types = {0: "continuous", 1: "on activation", 2: "on deactivation", 3: "on event"}

    def __init__(self, step=None, typeIndex=0, condition=None, output=None, plcIndex=None):
        self.step = step
        self.type = self.types[typeIndex]
        self.condition = condition
        self.output = output
        self.plcIndex = plcIndex

    def __str__(self):
        return "Action {} of {} in {}".format(self.type, self.type, self.step)

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

    # AND, OR

    def __init__(self, type, expression):
        self.type = type

        self.members = list()

        # TODO: What if expression is already a list of members?
        self.add_members(expression)

    def __str__(self):
        expression = "("
        for member in self.members:
            expression += str(member)
            if self.type is 'OR':
                expression += '+'
            elif self.type is 'AND':
                expression += '.'

        expression[-1] = ")"

        return expression

    def __repr__(self):
        return str(self)

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def add_member(self, member):
        self.members.append(Expression(member))

    def add_members(self, members):
        for member in members:
            self.add_member(member)

    def get_members(self):
        return self.members


class ExpressionUnary:

    # NOT, RE, FE

    def __init__(self, type, expression):
        self.type = type
        self.member = Expression(expression)

    def __str__(self):
        return '({} {})'.format(self.type, self.member)

    def __repr__(self):
        return str(self)

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def add_member(self, member):
        self.member = Expression(member)

    def get_member(self):
        return self.member


class Constant:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value


class Delay:

    def __init__(self, expression):
        self.delay_re = expression[0]
        self.expression = Expression(expression[1])
        self.delay_fe = expression[2]

    def __str__(self):
        return "{}s/{}/{}s".format(self.delay_fe, self.expression, self.delay_re)

    def __repr__(self):
        return str(self)

    def set_expression(self, expression):
        self.expression = expression

    def get_expression(self):
        return self.expression

    def set_delay_re(self, delay_re):
        self.delay_re = delay_re

    def get_delay_re(self):
        return self.delay_re

    def set_delay_fe(self, delay_fe):
        self.delay_fe = delay_fe

    def get_delay_fe(self):
        return self.delay_fe


class Duration:

    def __init__(self, expression):
        self.duration = expression[0]
        self.expression = Expression(expression[1])

    def __str__(self):
        return "{}s/{}".format(self.duration, self.expression)

    def __repr__(self):
        return str(self)

    def set_expression(self, expression):
        self.expression = expression

    def get_expression(self):
        return self.expression

    def set_duration(self, duration):
        self.duration = duration

    def get_duration(self):
        return self.duration


class Input:

    def __init__(self, name, plcIndex=None):
        self.name = name
        self.plcIndex = plcIndex

    def __str__(self):
        return "Input {} of PLC index {}".format(self.name, self.plcIndex)

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
        self.actions = list()

    def __str__(self):
        return "Output {} of PLC index {}".format(self.name, self.plcIndex)

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

    def add_action(self, action):
        self.actions.append(action)

    def get_actions(self):
        return self.actions


class Expression:

    cases = {'AND': partial(ExpressionBinary, 'AND'),
             'OR': partial(ExpressionBinary, 'OR'),
             'NOT': partial(ExpressionUnary, 'NOT'),
             'RE': partial(ExpressionUnary, 'RE'),
             'FE': partial(ExpressionUnary, 'FE'),
             'CT': Constant,
             'DE': Delay,
             'DU': Duration,
             'IN': lambda input: input,
             'OU': lambda output: output,
             'ST': lambda step: step}

    def __init__(self, expression=None):
        if expression is not None:
            self.expression = self.cases[expression[0]](expression[1])
        else:
            self.expression = None

    def __str__(self):
        return "Expression {}".format(self.expression)

    def __repr__(self):
        return str(self)

    def set_expression(self, expression):
        self.expression = self.cases[expression[0]](expression[1])

    def get_expression(self):
        return self.expression
