#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from functions import *

def print_usage(prog_name):
    print("Usage: " + prog_name + " [parallel|concurrent] json_file html_file")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print_usage(sys.argv[0])
        sys.exit(1)
    if sys.argv[1] == "parallel":
        from parallel_modelling import perform_modelling
        from components import BaseComponent, BaseLine
    elif sys.argv[1] == "concurrent":
        from concurrent_modelling import perform_modelling
        from concurrent_modelling import ConcurrentComponent as BaseComponent, ConcurrentLine as BaseLine
    else:
        print_usage(sys.argv[0])
        sys.exit(1)
    html_file_name = sys.argv[3]

    [all_inputs, output_line, all_components] = generate_scheme_from_json(sys.argv[2], BaseLine, BaseComponent)

    output = perform_modelling(all_inputs, output_line, all_components)
    if sys.argv[1] == "parallel":
        make_html_output_parallel(output, html_file_name)
    elif sys.argv[1] == "concurrent":
        make_html_output_concurrent(output, html_file_name, len(all_inputs))
