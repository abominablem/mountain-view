# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 23:45:24 2021

@author: marcu
"""

import re
from mh_logging import log


def fields_from_formula(formula, mode, trace = None):
    log.log_trace(__name__, "fields_from_formula", trace)
    """
    Given a formula, tries to extract a list of all formulas used in
    it. Default character sets deal with Alteryx formulas
    
    Works through the formula, looking for character signifying either the
    beginning of a string (quote_chars) or the beginning of a field name
    (field_chars). Once found, it will match all the way to the end of that
    string or field name, remove it from the formula, and add it to the
    list of fields if it is a field name.
    """
    
    fields = []
    if mode == "Alteryx":
        quote_chars = ['"', "'"] #chars used to denote string limits
        field_chars = ["["] #chars used to denote field name limits
        field_char_map = {"[": "]"} #ending char for a field start char
    elif mode == "SQL":
        quote_chars = ["'"]
        field_chars = ["[", '"']
        field_char_map = {"[": "]", '"': '"'}
    else:
        raise ValueError("Invalid formula character set entered. "
                         "Enter one of Alteryx/SQL")
        
    def get_index(string, char, start=0):
        try:
            return string.index(char, start)
        except ValueError:
            return None
        
    def first_char(string, chars):
        out = (None, "")
        for c in chars:
            i = get_index(string, c)
            if i is None: 
                continue
            else:
                if out[0] is None or i < out[0]:
                    out = (i, c)
        return out
    
    # while not re.search(".*(\[[^\[\]]+?\]).*", formula) is None:
    def has_field(formula):
        regex_special_chars = "[](){}*+?|^$.\\"
        for c in field_chars:
            ce = field_char_map[c]
            if c in regex_special_chars: c = "\\" + c
            if ce in regex_special_chars: ce = "\\" + ce
            regex = ".*(%s[^%s%s]+?%s).*" % (c, c, ce, ce)
            if not re.search(regex, formula) is None:
                return True
        return False

    while has_field(formula):
        #remove strings from the formula
        str_start, char = first_char(formula, field_chars + quote_chars)
        
        #Get the corresponding end character of the field name
        if char in field_chars:
            str_end = get_index(formula, field_char_map[char], str_start + 1)
            fields.append(formula[str_start+1:str_end])
        else:
            str_end = get_index(formula, char, str_start + 1)
        
        formula = formula[:str_start] + formula[str_end + 1:]
    return list(set(fields))

if __name__ == "__main__":
    print(fields_from_formula("[date of birth] > CAST('2021-04-05' AS "
                              "datetime) AND \"anvil\" = 'falling'", 
                              mode = "Alteryx"))
