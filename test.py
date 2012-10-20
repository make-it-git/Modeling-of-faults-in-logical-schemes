#!/usr/bin/python
# -*- coding: utf-8 -*-

import main
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
        base_component = main.BaseComponent(2, function_and)
        self.assertRaises(Exception, base_component.out)

    def test_ready(self):
        base_component = main.BaseComponent(2, function_and)
        self.assertFalse(base_component.ready())
        base_component.set_input(0, 0)
        self.assertFalse(base_component.ready())
        base_component.set_input(1, 1)
        self.assertTrue(base_component.ready())

    def test_set_input(self):
        base_component = main.BaseComponent(2, function_and)
        self.assertRaises(ValueError, base_component.set_input, -1, 0)
        self.assertRaises(ValueError, base_component.set_input, 0, 2)

    def test_out(self):
        base_component = main.BaseComponent(2, function_and)
        base_line = main.BaseLine()
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
        base_component = main.BaseComponent(2, function_and)
        base_component.set_input(0, 0)
        base_component.set_input(1, 1)
        self.assertTrue(base_component.ready())
        base_component.clear()
        self.assertFalse(base_component.ready())

class TestBaseLine(unittest.TestCase):

    def test_set_input(self):
       base_line = main.BaseLine()
       self.assertRaises(ValueError, base_line.set_input,-1)
       self.assertRaises(ValueError, base_line.set_input, 2)
       base_line.set_input(1)
       base_line.set_input(0)

    def test_set_output(self):
       base_line = main.BaseLine()
       self.assertRaises(ValueError, base_line.set_output, -1)
       self.assertRaises(ValueError, base_line.set_output, 2)
       base_line.set_output(1)
       base_line.set_output(0)

    def test_clear(self):
       base_line = main.BaseLine()
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
        comp_in1 = main.BaseComponent(1, function_in)
        comp_in2 = main.BaseComponent(1, function_in)
        #and
        comp_and1 = main.BaseComponent(2, function_and)
        #lines
        line_in1_to_and1 = main.BaseLine()
        line_in2_to_and1 = main.BaseLine()
        line_out = main.BaseLine()

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
        c_in1 = main.BaseComponent(1, function_in)
        c_in2 = main.BaseComponent(1, function_in)
        c_in3 = main.BaseComponent(1, function_in)
        c_and = main.BaseComponent(2, function_and)
        c_or = main.BaseComponent(2, function_or)
        #lines (1 and 2 connects to component 'and')
        #3 connects to component 'or'
        #4 links output of 'and' and input of 'or'
        l_in1 = main.BaseLine()
        l_in2 = main.BaseLine()
        l_in3 = main.BaseLine()
        l_in4 = main.BaseLine()
        l_out = main.BaseLine()

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
        function is not a mistake'''
        c_in = main.BaseComponent(1, function_in)
        c_neg1 = main.BaseComponent(1, function_neg)
        c_neg2 = main.BaseComponent(1, function_neg)
        c_or = main.BaseComponent(2, function_or)

        l_in1 = main.BaseLine()
        l_in2 = main.BaseLine()#1 to 2 to neg1
        l_in3 = main.BaseLine()#1 to 3 to neg2
        l_in4 = main.BaseLine()#to 'or'
        l_in5 = main.BaseLine()#to 'or'
        l_out = main.BaseLine()

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
        c = main.BaseComponent(1, function_in)
        neg = main.BaseComponent(1, function_neg)
        l_in = main.BaseLine()
        l_out = main.BaseLine()
        c.attach_output_line(l_in)
        neg.attach_input_line(0, l_in)
        neg.attach_output_line(l_out)
        comps = c.get_output_line().get_components()
        self.assertIs(neg, comps[0])
        line = neg.get_output_line()
        self.assertIs(line, l_out)

if __name__ == '__main__':
    unittest.main()
