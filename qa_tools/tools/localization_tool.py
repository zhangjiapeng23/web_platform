#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/3/29

import re


# Change all value to natural number.
def localization_value2number(inputfile, output):
    i = 0
    with open(inputfile, 'r+', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if '#' in line:
                newfile = open(output, 'a', encoding='utf-8')
                newfile.writelines(str(line))
                newfile.close()
            elif '=' in line:
                newline = re.sub('(?<==).+?(?=$)', str(i), line)
                i += 1
                newfile = open(output, 'a', encoding='utf-8')
                newfile.writelines(str(newline))
                newfile.close()

