#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""parserGrafcet.py"""

from lib import sp   # Parser SP développé par C. Delord (http://www.cdsoft.fr/sp)


def parser_cadepa():

    def delay_conversion(duration, timeBase):
        timeBases = {'s': 1, 'd': 0.1, 'c': 0.01, 'z': 10}

        return float(duration*timeBases[timeBase])

    grafcetName = sp.R('\w+')
    stepName = sp.R(r'X\d+') / (lambda name: ('ST', name[1:]))
    transitionName = sp.R(r'Y\d+') / (lambda name: ('TR', name[1:]))
    constant = sp.R(r'0|1') / (lambda value: ('CT', int(value)))
    input = sp.R(r'[a-zA-WZ]\w*') / (lambda name: ('IN', name))
    output = sp.R(r'[a-zA-WZ]\w*') / (lambda name: ('OU', name))
    time = sp.R(r'\d+\s[a-zA-Z]') / (lambda inputTime: delay_conversion(float(inputTime[:-2]), inputTime[-1]))
    commentaryText = sp.R(r'[^"]*')

    blanks = sp.R(r'\s+')
    sc = sp.K(';')
    bs = sp.K('\\')
    co = sp.K(',')
    ic = sp.K('"')

    with sp.Separator(blanks | sc | bs | co):

        grafcet = sp.Rule()
        initialSteps = sp.Rule()
        step = sp.Rule()
        commentary = sp.Rule()
        actions = sp.Rule()
        action = sp.Rule()
        transition = sp.Rule()
        condition = sp.Rule()
        expression = sp.Rule()
        sum = sp.Rule()
        product = sp.Rule()
        atom = sp.Rule()
        variable = sp.Rule()
        negation = sp.Rule()
        delay = sp.Rule()
        risingEdge = sp.Rule()
        fallingEdge = sp.Rule()
        precedingRelation = sp.Rule()
        succedingRelation = sp.Rule()

        grafcet |= '%' & grafcetName & initialSteps & step[:] & transition[:] & precedingRelation[:] & \
                   succedingRelation[:]
        initialSteps |= '(' & stepName[1:] & ')'
        step |= stepName & actions[:1] & commentary[:1]
        commentary |= ic & commentaryText & ic
        actions |= '[' & action[:] & ']'
        action |= output
        transition |= transitionName & condition[:1]
        condition |= '[' & (sum | product | atom) & ']'
        expression |= sum | product | atom
        sum |= (product | atom)[2::'+'] / (lambda members: ('OR', members))
        product |= atom[2::'.'] / (lambda members: ('AND', members))
        atom |= variable | constant | negation | delay | risingEdge | fallingEdge | ('(' & expression & ')')
        variable |= input | stepName
        negation |= '/' & atom / (lambda member: ('NOT', member))  # TODO: Negation can't be true for delay, or constant => improve
        delay |= ('T/' & atom & '/' & time & '/') / (lambda member: ('DE', member))
        risingEdge |= '>' & (variable | negation | delay | ('(' & expression & ')')) / (lambda member: ('RE', member))
        fallingEdge |= '<' & (variable | negation | delay | ('(' & expression & ')')) / (lambda member: ('FE', member))
        precedingRelation |= (stepName & '>' & transitionName) / (lambda couple: ('PR', couple))
        succedingRelation |= (transitionName & '>' & stepName) / (lambda couple: ('SR', couple))

    return grafcet
