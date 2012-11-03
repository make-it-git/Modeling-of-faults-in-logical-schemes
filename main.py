#!/usr/bin/python
# -*- coding: utf-8 -*-

from components import BaseComponent, BaseLine
from parallel_modelling import perform_modelling
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

    output = perform_modelling(all_inputs, output_line, all_components)
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
