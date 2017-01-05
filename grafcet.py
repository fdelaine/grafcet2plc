#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""grafcet.py"""

import warnings


class Grafcet:
    """Represents a GRAFCET"""

    def __init__(self, name=None):
        self.name = name

        self.steps = dict()
        self.transitions = dict()

    def __str__(self):
        return 'Grafcet {}'.format(self.name)

    def __repr__(self):
        return str(self)

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
                self.transitions[indexTransition].add_upstream_step(self.steps[indexStep])

        for couple in code[5]:
            indexTransition = couple[0]
            indexStep = couple[1]

            if (indexStep in self.steps.keys()) and (indexTransition in self.transitions.keys()):
                self.transitions[indexTransition].add_downstream_step(self.steps[indexStep])


class Step:
    """Step of a GRAFCET"""

    def __init__(self, index, initial=False, commentary=None, actions=None, apiIndex=None):
        self.index = index
        self.initial = initial
        self.apiIndex = apiIndex
        self.commentary = commentary
        self.actions = actions

        if self.actions is None:
            self.actions = list()

        self.upstreamTransition = list()
        self.downstreamTransition = list()

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

    def set_api_index(self, apiIndex):
        self.apiIndex = apiIndex

    def get_api_index(self):
        return self.apiIndex

    def add_action(self, action):
        self.actions.append(action)

    def remove_action(self, action):
        self.actions.remove(action)

    def get_actions(self):
        return self.actions


class Transition:
    """Transition of a GRAFCET"""

    def __init__(self, index, condition=None, apiIndex=None):
        self.index = index
        self.apiIndex = apiIndex
        self.condition = condition

        self.upstreamSteps = list()
        self.downstreamSteps = list()

    def __str__(self):
        return 'Y{}'.format(self.index)

    def __repr__(self):
        return str(self)

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

    def set_api_index(self, apiIndex):
        self.apiIndex = apiIndex

    def get_api_index(self):
        return self.apiIndex

    def add_upstream_steps(self, steps):
        for step in steps:
            self.add_upstream_step(step)

    def add_upstream_step(self, step):
        if step not in self.upstreamSteps:
            self.upstreamSteps.append(step)
        else:
            warnings.warn("{} already existing as upstream step for {}".format(step, self), UserWarning)

    def get_upstream_steps(self):
        return self.upstreamSteps

    def remove_upstream_steps(self):
        self.upstreamSteps.clear()

    def remove_upstream_step(self, step):
        self.upstreamSteps.remove(step)

    def add_downstream_steps(self, steps):
        for step in steps:
            self.add_downstream_step(step)

    def add_downstream_step(self, step):
        if step not in self.downstreamSteps:
            self.downstreamSteps.append(step)
        else:
            warnings.warn("{} already existing as downstream step for {}".format(step, self), UserWarning)

    def get_downstream_steps(self):
        return self.downstreamSteps

    def remove_downstream_steps(self):
        self.downstreamSteps.clear()

    def remove_downstream_step(self, step):
        self.downstreamSteps.remove(step)


class Action:

    types = {0: "continuous", 1: "on activation", 2: "on deactivation", 3: "on event"}

    def __init__(self, name, type=types[0], condition=None, output=None, apiIndex=None):
        self.name = name
        self.type = type
        self.condition = condition
        self.output = output
        self.apiIndex = apiIndex

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

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

    def set_api_index(self, apiIndex):
        self.apiIndex = apiIndex

    def get_api_index(self):
        return self.apiIndex


class Expression:
    pass


class ExpressionBinary(Expression):
    pass


class ExpressionUnary(Expression):
    pass


class Constant(Expression):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)


class Delay(Expression):
    pass


class Input(Expression):
    def __init__(self, name, apiIndex=None):
        self.name = name
        self.apiIndex = apiIndex

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_api_index(self, apiIndex):
        self.apiIndex = apiIndex

    def get_api_index(self):
        return self.apiIndex


class Output:

    def __init__(self, name, apiIndex=None):
        self.name = name
        self.apiIndex = apiIndex

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_api_index(self, apiIndex):
        self.apiIndex = apiIndex

    def get_api_index(self):
        return self.apiIndex
