#!/usr/bin/python
# -*- coding: utf-8 -*-

import main
import unittest
def function_and(inputs):
    return inputs[0] and inputs[1]

class TestBaseComponent(unittest.TestCase):

    def setUp(self):
        self.inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]

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



if __name__ == '__main__':
    unittest.main()
