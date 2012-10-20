#!/usr/bin/python
# -*- coding: utf-8 -*-

class BaseComponent:

    def __init__(self, number_of_input_ports, function):
        '''function = definition of the function to be performed'''
        if number_of_input_ports <= 0:
            raise ValueError("Number of input ports should be positive integer")
        self.__input_ports = [None for i in range(number_of_input_ports)]
        self.__function = function
        self.__input_lines = [None for i in range(number_of_input_ports)]
        self.__output_line = None

    def set_input(self, i, value):
        if i >= 0 and value in [0, 1]:
            self.__input_ports[i] = value
        else:
            raise ValueError("Illegal arguments. i should be nonnegative integer. value should be 0 or 1")

    def out(self):
        '''Perform function and write result to output port'''
        if self.ready():
            value = self.__function(self.__input_ports)
            if self.__output_line is None:
                raise Exception("Line is not attached")
            else:
                self.__output_line.set_input(value)
                return value
        else:
            raise Exception("Function not ready to be calculated. Not all inputs are set")

    def ready(self):
        for i in self.__input_ports:
            if i == None:
                return False
        return True

    def clear(self):
        self.__input_ports = [None for i in range(len(self.__input_ports))]

    def attach_output_line(self, line):
        '''One output port. One line'''
        self.__output_line = line

    def attach_input_line(self, i, line):
        self.__input_lines[i] = line
        line.add_component(self)

    def get_output_line(self):
        return self.__output_line


class BaseLine:

    def __init__(self):
        self.__input = None
        self.__output = None
        self.__output_lines = []
        self.__components = []

    def set_input(self, value):
        if value in [0, 1]:
            if self.__output is None:#no failures
                self.__input = value
            else:
                self.__input = self.__output
            for line in self.__output_lines: #propagate signal to all lines which are connected to this line(self)
                line.set_input(self.__input)
        else:
            raise ValueError("value should be 0 or 1")

    def set_output(self, value):
        '''If scheme works correctly (without failures)
        then set_output is not called'''
        if value in [0, 1]:
            self.__output = value
        else:
            raise ValueError("value should be 0 or 1")

    def get_value(self):
        if self.__output is not None:#failure
            return self.__output
        else:
            return self.__input

    def clear(self):
        self.__input = None
        self.__output = None

    def attach_output_line(self, line):
        '''should call line.set_input every time something changes in self'''
        self.__output_lines.append(line)

    def add_component(self, component):
        self.__components.append(component)

    def get_components(self):
        return self.__components

if __name__ == '__main__':
    pass
