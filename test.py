#!/usr/bin/python
# -*- coding: utf-8 -*-

from components import BaseComponent, BaseLine
from parallel_modelling import perform_modelling

import unittest
def function_and(inputs):
    return inputs[0] and inputs[1]
def function_or(inputs):
    return inputs[0] or inputs[1]
def function_neg(inputs):
    i = inputs[0]
    if i == 1:
        return 0
    if i == 0:
        return 1
def function_in(inputs):
    return inputs[0]

class TestBaseComponent(unittest.TestCase):

    def test_exception(self):
        base_component = BaseComponent(2, function_and)
        self.assertRaises(Exception, base_component.out)

    def test_ready(self):
        base_component = BaseComponent(2, function_and)
        self.assertFalse(base_component.ready())
        base_component.set_input(0, 0)
        self.assertFalse(base_component.ready())
        base_component.set_input(1, 1)
        self.assertTrue(base_component.ready())

    def test_set_input(self):
        base_component = BaseComponent(2, function_and)
        self.assertRaises(ValueError, base_component.set_input, -1, 0)
        self.assertRaises(ValueError, base_component.set_input, 0, 2)

    def test_out(self):
        base_component = BaseComponent(2, function_and)
        base_line = BaseLine()
        base_component.attach_output_line(base_line)
        base_component.set_input(0, 0)
        base_component.set_input(1, 0)
        self.assertEqual(0, base_component.out())
        base_component.set_input(0, 0)
        base_component.set_input(1, 1)
        self.assertEqual(0, base_component.out())
        base_component.set_input(0, 1)
        base_component.set_input(1, 0)
        self.assertEqual(0, base_component.out())
        base_component.set_input(0, 1)
        base_component.set_input(1, 1)
        self.assertEqual(1, base_component.out())

    def test_clear(self):
        base_component = BaseComponent(2, function_and)
        base_component.set_input(0, 0)
        base_component.set_input(1, 1)
        self.assertTrue(base_component.ready())
        base_component.clear()
        self.assertFalse(base_component.ready())

class TestBaseLine(unittest.TestCase):

    def test_set_input(self):
       base_line = BaseLine()
       self.assertRaises(ValueError, base_line.set_input,-1)
       self.assertRaises(ValueError, base_line.set_input, 2)
       base_line.set_input(1)
       base_line.set_input(0)

    def test_set_output(self):
       base_line = BaseLine()
       self.assertRaises(ValueError, base_line.set_output, -1)
       self.assertRaises(ValueError, base_line.set_output, 2)
       base_line.set_output(1)
       base_line.set_output(0)

    def test_clear(self):
       base_line = BaseLine()
       self.assertIsNone(base_line.get_value())
       base_line.set_input(1)
       self.assertEqual(1, base_line.get_value())
       base_line.clear()
       self.assertIsNone(base_line.get_value())
       base_line.set_output(1)
       self.assertEqual(1, base_line.get_value())

class TestBaseConnection(unittest.TestCase):

    def test_base_connection(self):
        #inputs
        comp_in1 = BaseComponent(1, function_in)
        comp_in2 = BaseComponent(1, function_in)
        #and
        comp_and1 = BaseComponent(2, function_and)
        #lines
        line_in1_to_and1 = BaseLine()
        line_in2_to_and1 = BaseLine()
        line_out = BaseLine()

        comp_in1.attach_output_line(line_in1_to_and1)
        comp_in2.attach_output_line(line_in2_to_and1)
        comp_and1.attach_input_line(0, line_in1_to_and1)
        comp_and1.attach_input_line(1, line_in1_to_and1)
        comp_and1.attach_output_line(line_out)

        comp_in1.set_input(0, 0)
        comp_in1.out()
        comp_in2.set_input(0, 0)
        comp_in2.out()
        comp_and1.set_input(0, line_in1_to_and1.get_value())
        comp_and1.set_input(1, line_in2_to_and1.get_value())
        comp_and1.out()
        self.assertEqual(0, line_out.get_value())

        comp_in1.set_input(0, 1)
        comp_in1.out()
        comp_in2.set_input(0, 1)
        comp_in2.out()
        comp_and1.set_input(0, line_in1_to_and1.get_value())
        comp_and1.set_input(1, line_in2_to_and1.get_value())
        comp_and1.out()
        self.assertEqual(1, line_out.get_value())

    def test_2components(self):
        '''3 inputs, 1 output
        in1 and in2 or in3'''
        #components
        c_in1 = BaseComponent(1, function_in)
        c_in2 = BaseComponent(1, function_in)
        c_in3 = BaseComponent(1, function_in)
        c_and = BaseComponent(2, function_and)
        c_or = BaseComponent(2, function_or)
        #lines (1 and 2 connects to component 'and')
        #3 connects to component 'or'
        #4 links output of 'and' and input of 'or'
        l_in1 = BaseLine()
        l_in2 = BaseLine()
        l_in3 = BaseLine()
        l_in4 = BaseLine()
        l_out = BaseLine()

        c_in1.attach_output_line(l_in1)
        c_in2.attach_output_line(l_in2)
        c_and.attach_input_line(0, l_in1)
        c_and.attach_input_line(1, l_in2)
        c_and.attach_output_line(l_in4)

        c_in3.attach_output_line(l_in3)
        c_or.attach_input_line(0, l_in4)
        c_or.attach_input_line(1, l_in3)
        c_or.attach_output_line(l_out)

        c_in2.set_input(0, 1)
        c_in1.set_input(0, 1)
        c_in3.set_input(0, 0)
        c_in1.out()
        c_in2.out()
        c_in3.out()
        c_and.set_input(0, l_in1.get_value())
        c_and.set_input(1, l_in2.get_value())
        c_and.out()
        c_or.set_input(0, l_in4.get_value())
        c_or.set_input(1, l_in3.get_value())
        c_or.out()
        self.assertEqual(1, l_out.get_value())

    def test_split_lines(self):
        '''not(in1) or not(in1)
        function is not a mistake. it tests line's splitting'''
        c_in = BaseComponent(1, function_in)
        c_neg1 = BaseComponent(1, function_neg)
        c_neg2 = BaseComponent(1, function_neg)
        c_or = BaseComponent(2, function_or)

        l_in1 = BaseLine()
        l_in2 = BaseLine()#1 to 2 to neg1
        l_in3 = BaseLine()#1 to 3 to neg2
        l_in4 = BaseLine()#to 'or'
        l_in5 = BaseLine()#to 'or'
        l_out = BaseLine()

        c_in.attach_output_line(l_in1)
        l_in1.attach_output_line(l_in2)
        l_in1.attach_output_line(l_in3)
        c_neg1.attach_input_line(0, l_in2)
        c_neg2.attach_input_line(0, l_in3)

        c_neg1.attach_output_line(l_in4)
        c_neg2.attach_output_line(l_in5)
        c_or.attach_input_line(0, l_in4)
        c_or.attach_input_line(1, l_in5)

        c_or.attach_output_line(l_out)

        c_in.set_input(0, 0)
        c_in.out()
        c_neg1.set_input(0, l_in2.get_value())
        c_neg2.set_input(0, l_in3.get_value())
        c_neg1.out()
        c_neg2.out()
        c_or.set_input(0, l_in4.get_value())
        c_or.set_input(1, l_in5.get_value())
        c_or.out()
        self.assertEqual(1, l_out.get_value())

    def test_get_lines_and_components(self):
        c = BaseComponent(1, function_in)
        neg = BaseComponent(1, function_neg)
        l_in = BaseLine()
        l_out = BaseLine()
        c.attach_output_line(l_in)
        neg.attach_input_line(0, l_in)
        neg.attach_output_line(l_out)
        comp = c.get_output_line().get_output_component()
        self.assertIs(neg, comp)
        line = neg.get_output_line()
        self.assertIs(line, l_out)

class TestBasicModeling(unittest.TestCase):

    def setUp(self):
        self.c = BaseComponent
        self.l = BaseLine

    def test_base_modeling(self):
        comp = self.c
        line = self.l

        c_in1 = comp(1, function_in, "in1")
        c_in2 = comp(1, function_in, "in2")
        c_and = comp(2, function_and, "and")

        l_1 = line("l1")
        l_2 = line("l2")
        l_out = line("lout")

        c_in1.attach_output_line(l_1)
        c_in2.attach_output_line(l_2)
        c_and.attach_input_line(0, l_1)
        c_and.attach_input_line(1, l_2)
        c_and.attach_output_line(l_out)

        components = [c_and]
        output = perform_modelling([c_in1, c_in2], l_out, components)
        self.assertEqual([ i[1] for i in output[0]], [0, 0, 0, 1])
        #for failure in output[1]:
        #    print(failure)

    def test_more_components(self):
        '''
        not(x1) and x2 or x3
        '''
        comp = self.c
        line = self.l
        in1 = comp(1, function_in, "in1")
        in2 = comp(1, function_in, "in2")
        in3 = comp(1, function_in, "in3")
        c_neg = comp(1, function_neg, "neg")
        c_and = comp(2, function_and, "and")
        c_or = comp(2, function_or, "or")
        l1 = line("l1")
        l2 = line("l2")
        l3 = line("l3")
        l4 = line("l4")
        l5 = line("l5")
        l6 = line("l6") #out

        in1.attach_output_line(l1)
        in2.attach_output_line(l2)
        in3.attach_output_line(l3)

        c_neg.attach_input_line(0, l1)
        c_neg.attach_output_line(l4)

        c_and.attach_input_line(0, l4)
        c_and.attach_input_line(1, l2)
        c_and.attach_output_line(l5)

        c_or.attach_input_line(0, l5)
        c_or.attach_input_line(1, l3)
        c_or.attach_output_line(l6)

        components = [c_neg, c_and, c_or]
        output = perform_modelling([in1, in2, in3], l6, components)
        self.assertEqual([ i[1] for i in output[0]], [0, 1, 1, 1, 0, 1, 0, 1])
        #for failure in output[1]:
        #    print(failure)

    def test_line_split(self):
        '''
        not(x1) or x1 and x2
        '''
        comp = self.c
        line = self.l
        input = [comp(1, function_in) for i in range(2)]
        lines = [line(str(i)) for i in range(7)]
        c_neg = comp(1, function_neg)
        c_and = comp(2, function_and)
        c_or = comp(2, function_or)

        input[0].attach_output_line(lines[0])
        input[1].attach_output_line(lines[1])

        lines[0].attach_output_line(lines[2])
        lines[0].attach_output_line(lines[3])

        c_neg.attach_input_line(0, lines[2])
        c_neg.attach_output_line(lines[4])

        c_and.attach_input_line(0, lines[3])
        c_and.attach_input_line(1, lines[1])
        c_and.attach_output_line(lines[5])

        c_or.attach_input_line(0, lines[4])
        c_or.attach_input_line(1, lines[5])
        c_or.attach_output_line(lines[6])

        components = [c_neg, c_and, c_or]
        output = perform_modelling(input, lines[6], components)
        self.assertEqual([ i[1] for i in output[0]], [1, 1, 0, 1])
        #for failure in output[1]:
        #    print(failure)


if __name__ == '__main__':
    unittest.main()
