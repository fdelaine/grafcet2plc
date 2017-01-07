#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""parserGrafcet.py"""

from lib import sp   # Parser SP développé par C. Delord (http://www.cdsoft.fr/sp)


def parser_cadepa():

    grafcetName = sp.R('\w+')
    stepName = sp.R(r'X\d+')
    transitionName = sp.R(r'Y\d+')
    constant = sp.R(r'0|1') / (lambda lettre: ('Cte', lettre == '1'))
    input = sp.R(r'[a-zA-Z]\w*')
    output = sp.R(r'[a-zA-Z]\w*')
    time = sp.R(r'\d+\s[a-zA-Z]')
    commentary = sp.R(r'"([a-zA-Z0-9_]|\s)*"')


    blanks = sp.R(r'\s+')
    sc = sp.K(';')
    bs = sp.K('\\')
    co = sp.K(',')

    with sp.Separator(blanks | sc | bs | co):

        grafcet = sp.Rule()
        initialSteps = sp.Rule()
        step = sp.Rule()
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
        step |= stepName & action[:1] & commentary[:1]
        action |= '[' & output[1:] & ']'
        transition |= transitionName & condition[:1]
        condition |= '[' & (sum | product | atom) & ']'
        expression |= sum | product | atom
        sum |= (product | atom)[2::'+']
        product |= atom[2::'.']
        atom |= variable | constant | negation | delay | risingEdge | fallingEdge | ('(' & expression & ')')
        variable |= input
        negation |= '/' & atom
        delay |= 'T/' & stepName & '/' & time & '/'
        risingEdge |= '>' & (variable | negation | delay | ('(' & expression & ')'))
        fallingEdge |= '<' & (variable | negation | delay | ('(' & expression & ')'))
        precedingRelation |= stepName & '>' & transitionName
        succedingRelation |= transitionName & '>' & stepName

    return grafcet
