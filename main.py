#!/usr/bin/python
# -*- coding: utf-8 -*-

from components import BaseComponent, BaseLine

import itertools
def perform_modeling(input_components, output_line, all_components):
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
    # to return from function
    detectable_failures = [] # input, line.__id and line.get_value()
    # we will iterate over all possible failures
    # for every input first iteration must be run without failures to calculate output
    # because of this first element in all_failures is None
    all_failures = [None]
    all_failures.extend([[line, 0] for line in all_lines])
    all_failures.extend([[line, 1] for line in all_lines])
    for input in input_values:
        current_valid_output_value = None # first iteration sets this variable
        # find all detectable failures for every input
        for failure in all_failures:
            for c in all_components:
                c.clear() # to avoid possible problems from previous iterations
            for l in all_lines:
                l.clear()
            # set failed line for this iteration
            if failure != None:
                line = failure[0]
                value = failure[1]
                line.set_output(value)
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
                        component.out() # from now get_value() on output_lines can be called
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
                        if current_valid_output_value == None: # first iteration for this input (without failures)
                            output_values.append([input, output_line.get_value()])
                            current_valid_output_value = output_line.get_value()
                        else:
                            #if current_valid_output_value != output_line.get_value():
                            # input set, line number, line value, scheme out, scheme out valid for this input set
                            detectable_failures.append([input, str(failure[0]), str(failure[1]), output_line.get_value(), current_valid_output_value])
                        break
                for line in remained_lines:
                    component = line.get_output_component()
                    cur_processing.append(component)
                    component.set_input(line.get_output_component_input_port(), line.get_value())
                cur_processing = list(set(cur_processing)) # remove duplicates
    return [output_values, detectable_failures]

import json
import sys
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
def function_xor(inputs):
    x1 = inputs[0]
    x2 = inputs[1]
    return int(x1 and not(x2) or not(x1) and x2)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " json_file")
        sys.exit(1)
    json_file = open(sys.argv[1])
    json_data = json.loads(json_file.read())
    json_file.close()
    all_inputs = []
    all_lines = []
    output_line = None
    all_components = []

    output_line = BaseLine(json_data["out"])
    lines = []
    for component in json_data["components"]:
        lines.extend(component["in"])
        lines.append(component["out"])
    if "lines" in json_data: # line splits
        for line in json_data["lines"]:
            lines.append(line["line"])
            lines.extend(line["to"])
    lines = sorted(list(set([int(i) for i in lines])))
    for line in lines:
        if str(line) == str(output_line):
            all_lines.append(output_line)
        else:
            all_lines.append(BaseLine(str(line)))
    if "lines" in json_data:
        for line in json_data["lines"]:
            for to_line in line["to"]:
                all_lines[int(line["line"]) - 1].attach_output_line(all_lines[int(to_line) - 1])
    all_inputs = [BaseComponent(1, function_in) for i in range(len(json_data["in"]))]
    i = 0
    for input in json_data["in"]:
        all_inputs[i].attach_output_line(all_lines[int(input) - 1])
        i += 1
    for component in json_data["components"]:
        all_components.append(BaseComponent(len(component["in"]), eval("function_" + component["function"])))
        all_components[-1].attach_output_line(all_lines[int(component["out"]) - 1]) # starts from 1, not from zero
        i = 0
        for input_line in component["in"]:
            all_components[-1].attach_input_line(i, all_lines[int(input_line) - 1])
            i += 1

    output = perform_modeling(all_inputs, output_line, all_components)
    #for valid in output[0]:
    #    print(valid)
    #for failure in output[1]:
        # input set, line number, line value, scheme out, valid scheme out
    #    print(failure)
    table = []
    all_lines = [int(i[1]) for i in output[1]] # conversion to int is required for correct sorting
    all_lines = sorted(set(all_lines))
    all_lines = [str(i) for i in all_lines]
    for v in output[0]:
        # v[0] = input set, v[1] - output value
        failures = [i for i in output[1] if i[0] == v[0]] # for this input set
        lines = []
        i = len(all_lines)
        while i > 0:
            tmp = [] # will contain only 2 elements (one when line is set to 0, second when line is set to 1)
            for failure in failures:
                if failure[1] == all_lines[-i]: # reverse indexing
                    tmp.append([failure[1], failure[2], failure[3], failure[4]])
            i -= 1
            tmp.sort(key = lambda x: x[1]) # sort by line value
            lines.extend(tmp)
        # input set, [line number, value, out, valid out]
        table.append([v[0], lines])
    # now table contains sorted list for pretty output
    out = []
    i = 0
    tmp = []
    for row in table:
        # input sets
        # out.append(row[0][0])
        tmp.append([i, "".join([ str(i) for i in row[0]]) ])
        i += 1
    out.append(tmp)
    tmp = []
    for v in output[0]:
        tmp.append(v[1]) # valid out
    out.append(tmp)
    for row in table:
        tmp = []
        for column in row[1]:
            # column[2] = out, column[3] = valid out
            line_and_value = str(column[0]) + "/" + str(column[1])
            if column[2] == column[3]:
                tmp.append([line_and_value, str(column[2])])
            else:
                tmp.append([line_and_value, "_" + str(column[2])])
        out.append(tmp)

    print("<html>")
    print('<head><meta charset="utf-8"></head>')
    print("<body>")
    print("<table border='2' cellpadding='5'>")
    print("<tr align='center'>")
    print("\t<td>Входные наборы</td>")
    for i in out[0]:
        print("\t<td title='" + str(i[1]) + "'>", end="")
        print(i[0], end="")
        print("</td>")
    print("</tr>")
    print("<tr align='center'>")
    print("\t<td>Выход схемы</td>")
    for i in out[1]: # valid out
        print("\t<td width='20'>", end="")
        print(i , end="")
        print("</td>")
    print("</tr>")
    for row in zip(*out[2:]): # out[0] - input sets, out[1] - valid outs
        print("<tr align='center'>")
        print("\t<td>", end="")
        print(row[0][0], end="")
        print("</td>")
        i = 0 # for indexing input sets
        input_sets = [str(k[1]) for k in out[0]]
        for column in row:
            if column[1].startswith("_"):
                print("\t<td bgcolor='#888888' title='" + input_sets[i] + "'>", end="")
                print(column[1][1:], end="") # without leading "_" which means that it is wrong value
            else:
                print("\t<td title='" + input_sets[i] + "'>", end="")
                print(column[1], end="")
            print("</td>")
            i += 1
        print("</tr>")
    print("</table>")
    print("</body>")
    print("</html>")
