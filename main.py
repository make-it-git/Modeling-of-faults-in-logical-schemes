#!/usr/bin/python
# -*- coding: utf-8 -*-

class BaseComponent:

    def __init__(self, number_of_input_ports, function, id = ""):
        '''function = definition of the function to be performed'''
        if number_of_input_ports <= 0:
            raise ValueError("Number of input ports should be positive integer")
        self.__input_ports = [None for i in range(number_of_input_ports)]
        self.__function = function
        self.__input_lines = [None for i in range(number_of_input_ports)]
        self.__output_line = None
        self.__id = id

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

    def attach_input_line(self, i, line):
        self.__input_lines[i] = line
        line.add_component(self, i) #add this component(self) to line object

    def get_output_line(self):
        return self.__output_line

    def __str__(self):
        return(self.__id)


class BaseLine:

    def __init__(self, id = ""):
        self.__input = None
        self.__output = None
        self.__output_lines = []
        self.__component = None
        self.__component_input_port = None
        self.__id = id

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

    def add_component(self, component, port): #only one component can be attached to this line
        self.__component = component    #to attach many components line should be splitted
        self.__component_input_port = port

    def get_component(self):
        return self.__component

    def get_component_port(self):
        return self.__component_input_port

    def get_output_lines(self):
        return self.__output_lines

    def __str__(self):
        return(self.__id)

import itertools
def perform_modeling(inputs, output_line, all_components):
    # it creates all possible combinations of 0,1 of length(inputs)
    # if len(inputs) = 2, then input_values = [(0, 0), (0, 1), (1, 0), (1, 1)]
    input_values = [i for i in itertools.product([0, 1], repeat = len(inputs))]
    output_values = [] # to return from function
    for input in input_values:
        for c in all_components:
            c.clear() # to avoid possible problems from previous iterations
        cur_processing = inputs[:] # copy list
        i = 0
        for component in cur_processing: # set input of scheme
            component.set_input(0, input[i])
            component.out()
            i += 1
        while len(cur_processing) > 0: # for every iteration
            lines = [component.get_output_line() for component in cur_processing if component.ready()]
            components_to_remove = []
            i = 0
            for component in cur_processing:
                if component.ready():
                    components_to_remove.append(i)
                    component.out() # from now get_value() on output_lines can be called
                i += 1
            i = 0
            for k in components_to_remove:
                cur_processing.pop(k - i)
                i += 1

            remained_lines = [] #splitted line
            for line in lines:
                component = line.get_component()
                if component is None: #this line is connected to other lines
                    remained_lines = line.get_output_lines()
                else:
                    cur_processing.append(component) # for every input line component will be added
                    #because of this we remove duplicates from cur_processing by using set()
                    component.set_input(line.get_component_port(), line.get_value())
            if len(remained_lines) == 0: #it can be output line
                if len(lines) == 1 and lines[0] is output_line:
                    #print(input, end=' ')
                    #print(output_line.get_value())
                    output_values.append(output_line.get_value())
                    break
            for line in remained_lines:
                component = line.get_component()
                cur_processing.append(component)
                component.set_input(line.get_component_port(), line.get_value())
            cur_processing = list(set(cur_processing)) # remove duplicates
    return output_values

if __name__ == '__main__':
    pass
