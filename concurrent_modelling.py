#!/usr/bin/python
# -*- coding: utf-8 -*-

import itertools
from components import BaseComponent, BaseLine

class ConcurrentComponent(BaseComponent):

    def __init__(self, number_of_input_ports, function, id = ""):
        BaseComponent.__init__(self, number_of_input_ports, function, id)
        self.__failures = None

    def clear(self):
        BaseComponent.clear(self)
        self.__failures = None

    def add_failures(self, failures, input_set):
        #print(input_set)
        #print(str(self))
        if self.__failures:
            self.__failures.append(failures)
        else:
            self.__failures = []
            self.__failures.append(failures)
        #print(len(self.__failures))

    def get_failures(self, input_set = None):
        if input_set:
            return self.__failures[input_set]
        else:
            if self.__failures:
                return self.__failures[-1]
            else:
                return []

class ConcurrentLine(BaseLine):

    def set_input(self, value):
        BaseLine.set_input(self, value)
        if self._output_component:
            self._output_component.set_input(self._output_component_input_port, value)
            if self._output_component.ready():
                self._output_component.out()


def perform_modelling(input_components, output_line, all_components):
    # it creates all possible combinations of 0,1 of length(input_components)
    # if len(input_components) = 2, then input_values = [(0, 0), (0, 1), (1, 0), (1, 1)]
    input_values = [i for i in itertools.product([0, 1], repeat = len(input_components))]
    output_values = [] # input set, output value
    #find all lines in scheme
    all_lines = []
    for component in all_components:
        for line in component.get_input_lines(): # many input lines
            all_lines.append(line)
        all_lines.append(component.get_output_line()) # but only one output lines
    for component in input_components:
        all_lines.append(component.get_output_line())
    all_lines = list(set(all_lines))
    for input in input_values:
        for c in all_components:
            c.clear() # to avoid possible problems from previous iterations
        for l in all_lines:
            l.clear()
        cur_processing = input_components[:] # copy list
        i = 0
        for component in cur_processing: # set input of scheme
            component.set_input(0, input[i])
            component.out()
            i += 1
        while len(cur_processing) > 0: # for every iteration
            # lines where value can be calculated now
            lines = [component.get_output_line() for component in cur_processing if component.ready()]
            components_to_remove = []
            i = 0
            for component in cur_processing:
                if component.ready():
                    components_to_remove.append(i)

                    valid_out = component.out() # from now get_value() on output_lines can be called
                    if component not in input_components: # they are dummy components
                        transportable_failures = []
                        for in_line in component.get_input_lines(): # check all possible failures if they can be transported through this component
                            valid_line_value = in_line.get_value()
                            # comp_port = in_line.get_output_component_input_port()
                            in_line.set_input(0 if valid_line_value else 1)
                            # component.set_input(comp_port, in_line.get_value())
                            if component.out() != valid_out: # transportable failure
                                transportable_failures.append( [in_line, in_line.get_value()] )
                            in_line.set_input(valid_line_value)
                            # component.set_input(comp_port, in_line.get_value())
                            # component.out()
                        # always add output line's failure
                        transportable_failures.append( [component.get_output_line(), 0 if valid_out else 1] )
                        # print(str(input) + str(component) + str([str(i[0]) + "/" + str(i[1]) for i in transportable_failures]))
                        # now we have all possible failures ONLY for this component
                        # we must check if some transportable failures from previous components can be transported
                        # first of all we check NOT splitted input lines
                        # component - element being checked
                        # in_component - input component, attached to "component", possibly via 2 lines (if line is splitted)
                        for in_line in component.get_input_lines():
                            in_component = in_line.get_input_component()
                            if in_component and in_component not in input_components: # not splitted line and not dummy input component
                                failures = in_component.get_failures()
                                for failure in failures:
                                    # failure[0] - line, failure[1] - value
                                    valid_line_value = failure[0].get_value()
                                    failure[0].set_input(failure[1])
                                    # all components outs are ready
                                    # see ConcurrentLine.set_input and ConcurrentLine.out(BaseLine.out) definitions
                                    if component.out() != valid_out:
                                        transportable_failures.append( [failure[0], failure[1]] )
                                    failure[0].set_input(valid_line_value)
                            elif in_line.get_input_line(): # splitted line
                                in_component = in_line.get_input_line().get_input_component()
                                if in_component not in input_components:
                                    failures = in_component.get_failures()
                                    for failure in failures:
                                        valid_line_value = failure[0].get_value()
                                        failure[0].set_input(failure[1])
                                        if component.out() != valid_out:
                                            transportable_failures.append( [failure[0], failure[1]] )
                                            # check if next line is necessary
                                            component.set_input( in_line.get_output_component_input_port(), in_line.get_value() )
                                        failure[0].set_input(valid_line_value)
                                else:
                                    valid_line_value = in_component.get_output_line().get_value()
                                    in_component.get_output_line().set_input(0 if valid_line_value else 1)
                                    if component.out() != valid_out:
                                        transportable_failures.append( [in_component.get_output_line(), 0 if valid_line_value else 1] )
                                    in_component.get_output_line().set_input(valid_line_value)


                        #print(str(input) + str(component) + "|" +  str(len(transportable_failures)))
                        component.add_failures(transportable_failures, input)
                        print(str(input) + str(component) + str(sorted([str(i[0]) + "/" + str(i[1]) for i in transportable_failures])))
                    # remove these 2 lines
                    #if component.get_failures() and str(component == "17-18-19"):
                    #   print([ [input, str(component), str(i[0]), i[1]] for i in component.get_failures()])

                i += 1
            i = 0
            for k in components_to_remove:
                cur_processing.pop(k - i)
                i += 1

            remained_lines = [] # if the line is splitted
            for line in lines:
                component = line.get_output_component() # to which component this line is attached as input
                if component is None: # this line is connected to other lines
                    remained_lines.extend(line.get_output_lines())
                else:
                    cur_processing.append(component) # for every input line component will be added
                    # because of this we remove duplicates from cur_processing by using set()
                    # we can call line.get_value() because lines[] contain only lines with ready to use values (not None)
                    component.set_input(line.get_output_component_input_port(), line.get_value())
            if len(remained_lines) == 0: # it can be output line
                if len(lines) == 1 and lines[0] is output_line:
                    # if current_valid_output_value == None: # first iteration for this input (without failures)
                    output_values.append([input, output_line.get_value()])
                    # current_valid_output_value = output_line.get_value()
                    # else:
                    #    #if current_valid_output_value != output_line.get_value():
                    #    # input set, line number, line value, scheme out, scheme out valid for this input set
                    #    detectable_failures.append([input, str(failure[0]), str(failure[1]), output_line.get_value(), current_valid_output_value])
                    # break
            for line in remained_lines:
                component = line.get_output_component()
                cur_processing.append(component)
                component.set_input(line.get_output_component_input_port(), line.get_value())
            cur_processing = list(set(cur_processing)) # remove duplicates
    print([i[1] for i in output_values] == [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1])
    return [output_values, all_components]
