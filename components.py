#!/usr/bin/python
# -*- coding: utf-8 -*-

class BaseComponent:

    def __init__(self, number_of_input_ports, function, id = ""):
        '''function = definition of the function to be performed'''
        if number_of_input_ports <= 0:
            raise ValueError("Number of input ports should be positive integer")
        self.__input_ports = [None for i in range(number_of_input_ports)]
        self.__input_lines = [None for i in range(number_of_input_ports)]
        self.__output_line = None
        self.__function = function
        self.__id = id

    def set_input(self, i, value):
        if i >= 0 and value in [0, 1]:
            self.__input_ports[i] = value
        else:
            raise ValueError("Illegal arguments. i should be nonnegative integer. value should be 0 or 1")

    def out(self):
        '''Perform function and write result to output line'''
        if self.ready():
            value = self.__function(self.__input_ports)
            if self.__output_line is None:
                raise Exception("Line is not attached") #must call attach_output_line
            else:
                self.__output_line.set_input(value) #write result of function to output line
                return value
        else:
            # always call ready() method before calling out()
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
        line.set_input_component(self)

    def attach_input_line(self, i, line):
        self.__input_lines[i] = line
        line.set_output_component(self, i) #add this component(self) to line object

    def get_output_line(self):
        return self.__output_line

    def get_input_lines(self):
        return self.__input_lines

    def __str__(self):
        return(self.__id)


class BaseLine:

    def __init__(self, id = ""):
        self.__input = None # input value
        self.__output = None # output value (in case of failure)
        self.__output_lines = []
        self.__output_component = None
        self.__output_component_input_port = None
        self.__id = id
        self.__input_component = None # if input component is attached this var is not None
        self.__input_line = None # otherwise __inout_component is None and __input_line is set to valid value

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
        '''must call line.set_input every time something is changed in self'''
        self.__output_lines.append(line)
        line.set_input_line(self)

    def set_output_component(self, component, port): #only one component can be attached to this line
        self.__output_component = component    #to attach many components line should be splitted
        self.__output_component_input_port = port

    def get_output_component(self):
        return self.__output_component

    def get_output_component_input_port(self):
        return self.__output_component_input_port

    def get_output_lines(self):
        return self.__output_lines

    def set_input_component(self, component):
        self.__input_component = component

    def get_input_component(self):
        return self.__input_component

    def set_input_line(self, line):
        self.__input_line = line

    def get_input_line(self):
        return self.__input_line

    def __str__(self):
        return(self.__id)

