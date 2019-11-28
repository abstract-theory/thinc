#!/usr/bin/python3

"""

Procedure Outline:
==================

1) A source file is read and split into three objects. The objects
contain code, block comments, and line comments. Each object is in
"line-referenced data format" (see Data Formats).

2) Source code is converted into the "tree-format" (see Data Formats).

3) Transformations of code are performed while it is in the tree-format.

4) Code is converted back into line-referenced data format with the
addition of either indentation syntax or curly braces syntax.

5) Using the line references, code, is recombined with block comments,
and line comments.

6) Block comments are unrolled.

7) Code is beautified

8) Lines are joined into a single string


Data Formats:
=============

Line-referenced data format:
----------------------------
Code
^^^^
    [
        [line_number, code],
        [line_number, code],
        ...
    ]

Block Comments
^^^^^^^^^^^^^^
    [
        [starting_line_number, block_comment],
        [starting_line_number, block_comment],
        ...
    ]

Where "block_comment" is a block comment as an array of lines:

    block_comment = [line, line, line, line, ...]


Line Comments
^^^^^^^^^^^^^
    [
        [line_number, comment],
        [line_number, comment],
        ...
    ]


Tree-formatted source code format:
----------------------------------
    nested_code =
    [
        [line_number, code, nested_code],
        [line_number, code, nested_code],
        ...
    ]

"""

import sys
import re

IND_AMT = 4

def readFile(fn):
    """Read file."""
    with open(fn, 'r') as f:
        lines = f.read()
    return lines

def writeFile(fn, data):
    """Write file."""
    with open(fn, 'w') as f:
        f.write(data)


def indent(code, N=0):
    """Construct code having indentation syntax.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: source code with indentation syntax"""

    out_code = []
    for nL in range(len(code)):
        out_code.append([code[nL][0], " "*(N)*IND_AMT, code[nL][1]])
        out_code += indent(code[nL][2], N+1)
    return out_code


def curlify(code, N=0):
    """Construct code having curly braces syntax.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: source code with curly braces syntax"""

    out_code = []
    for nL in range(len(code)):
        if code[nL][2]:
            out_code.append([code[nL][0], " "*N*IND_AMT, code[nL][1] + " {"])
            out_code += curlify(code[nL][2], N+1)
            out_code.append([None, " "*N*IND_AMT, "}", "", ""])
        else:
            out_code.append([code[nL][0], " "*N*IND_AMT, code[nL][1]])
    return out_code


def nest_indented(code):
    """Convert intended code into nested tree structure.

    args:
        code: Line-referenced data that was produced from indentation-
        style source code.

    returns:
        data: Tree-formatted source code
    """

    re_indent = re.compile('^([\s]*)(.*)')
    line_cont = False
    data = []
    for nL in range(len(code)):
        line_num = code[nL][0]
        line = code[nL][1]

        r = re_indent.search(line)
        white_space = r.group(1)
        char_space = r.group(2)

        nI = len(white_space) // IND_AMT

        # If line is being continued, use the indentation of the
        # previous line. Account for any leading white space.
        if line_cont:
            leading_white_space = white_space[:-nIp*IND_AMT]
            char_space =  leading_white_space + char_space
            nI = nIp

        data_r = data
        for nT in range(nI*2):
            data_r = data_r[-1]

        if line_cont:
            # add to existing line
            data_r[-1][-2] = data_r[-1][-2][:-1] + char_space
        else:
            # append new line
            data_r.append([line_num, char_space, []])

        line_cont = char_space[-1] == "\\"
        # white_space_prev = white_space
        nIp = nI

    return data


def parse_raw_code(lines):
    """Separate code, block comments, and line comments.

    args:
        lines: A list of strings where each item is one line of source
            code. Line comments begin with "//" and block comments use
            the "/*" and "*/" syntax.

    returns:
        out_code2: Line-referenced data containing code.
        bcoms: Line-referenced data containing block comments, each
        "rolled up" as an array of lines.
        coms: Line-referenced data containing line comments.
    """

    isBlockComment = False
    isQuotesOpen = False

    out_code = []
    bcoms = []
    coms = []

    for nL in range(len(lines)):
        if not lines[nL].strip():
            continue

        isComment = False

        if not out_code or out_code[-1][1]:
            out_code.append([nL, ""])
        else:
            out_code[-1][0] = nL

        if isBlockComment:
            bcoms[-1][-1].append("")


        cm1 = "\n" # previous character
        for c in lines[nL]:

            if isComment:
                coms[-1][-1] += c
            elif isBlockComment:
                bcoms[-1][-1][-1] += c
            else:
                out_code[-1][-1] += c

            isEscaped = cm1 == "\\"
            if c == "\"" and not (isComment or isBlockComment or isEscaped):
                isQuotesOpen = not isQuotesOpen
            if cm1 == "/" and c == "/" and not (isQuotesOpen or isComment or isBlockComment):
                isComment = True
                out_code[-1][-1] = out_code[-1][-1][:-2]
                coms.append([nL, cm1 + c])
            if cm1 == "/" and c == "*" and not (isQuotesOpen or isComment or isBlockComment):
                isBlockComment = True
                out_code[-1][-1] = out_code[-1][-1][:-2]
                if not bcoms or bcoms[-1][0] != nL:
                    # new block comment
                    bcoms.append([nL, [cm1 + c]])
                else:
                    # multiple block comments on same line
                    bcoms[-1][-1][-1] += cm1+c
            if cm1 == "*" and c == "/" and not (isQuotesOpen or isComment):
                isBlockComment = False

            cm1 = c


    # 1) Remove trailing tabs and white space from code
    # 2) Replace leading tabs with IND_AMT white spaces.
    re_spaces_tabs = re.compile('^([ \t]*)(([^ \t]{1})|([^ \t]{1}.*[^ \t]{1}))([ \t]*)$')
    out_code2 = []
    for nL in range(len(out_code)):
        r = re_spaces_tabs.search(out_code[nL][1])
        if r:
            code_line = r.group(1).replace("\t", " "*IND_AMT) + r.group(2)
            out_code2.append([out_code[nL][0], code_line])

    return out_code2, bcoms, coms


def merge_comments(code, bcoms, coms, ch):
    """Recombine new code with the original block comments and comments."""

    # Line number references will be used as dictionary keys.

    # Iterate over "code". Replace duplicate keys and insert keys
    # wherever they are absent. Be sure that key_{n} < key_{n+1} is
    # always true. In other words, it is paramount that the order of
    # the lines in "code" be preserved.
    code_d = dict()
    key = -1
    for l in code:
        last_key = key
        key = l[0]
        if key == None or key in code_d:
            key = last_key + 1/1024
        code_d[key] = [l[1], l[2]]


    bcom_d = dict()
    for l in bcoms:
        try:
            if ch[l[0]]:
                bcom_d[ch[l[0]]] = l[1]
            else:
                bcom_d[l[0]] = l[1]
        except KeyError:
            bcom_d[l[0]] = l[1]

    com_d = dict()
    for l in coms:
        try:
            if ch[l[0]]:
                com_d[ch[l[0]]] = l[1]
            else:
                com_d[l[0]] = l[1]
        except KeyError:
            com_d[l[0]] = l[1]


    # Iterate over all key values and combine (white space, )code, block
    # comments, and comments.
    all_keys = sorted(set(code_d.keys()) | set(bcom_d.keys()) | set(com_d.keys()))
    out_code = []
    for N in all_keys:
        s = ['', '', '', '']

        # add white space and code
        try:
            s[0] = code_d[N][0]
            s[1] = code_d[N][1]
        except KeyError: pass

        # add block comment
        try:
            s[2] = bcom_d[N]
        except KeyError: pass

        # add line comment
        try:
            s[3] = com_d[N]
        except KeyError: pass

        # if line not blank, append it
        if s != ['', '', '', '']:
            out_code.append(s)

    # Make indentation for line comments the same as the first line
    # of code that comes after it. Note: This can mess up block comments
    # as the white-space within them is already preserved.
    spaces = ""
    for N in reversed(range(len(out_code))):
        if not out_code[N][1]:
            out_code[N][0] = spaces
        else:
            spaces = out_code[N][0]

    return out_code


def nest_curly(code):
    """Convert curly-braces code into nested tree structure.

    args:
        code: Line-referenced data that was produced from curly braces-
        style source code.

    returns:
        data: Tree-formatted source code
    """

    def _update_data(num_line, nI, code_buf, data):
        data_r = data
        for nT in range(nI*2): data_r = data_r[-1]
        data_r.append([num_line, code_buf.strip(), []])
        code_buf = ""
        return code_buf

    re_access_modifier_raw = re.compile('^( *)(public|private|protected)( *):$')
    re_switch_raw = re.compile("^( *)(case( .*|'.'|)|default *):$")

    c = "" # This gets overwritten but it triggers better comment formatting
    cm1 = c
    nI = 0 # indentation amount
    code_buf = ""
    data = []
    isParenOpen = False
    isQuotesOpen = False

    for nL in range(len(code)):

        num_line, codeLine = code[nL]

        if not codeLine:
            continue

        isMacro = codeLine[0] == "#"

        if isMacro:
            if code_buf.strip() != "":
                code_buf = _update_data(num_line-1, nI, code_buf, data)
            code_buf = codeLine
            code_buf = _update_data(num_line, nI, code_buf, data)
            continue

        for nC in range(len(codeLine)):

            # The line is being continued. Skip ahead to next line
            if codeLine[nC] == "\\" and nC == len(codeLine)-1:
                continue

            cm1 = c
            c = codeLine[nC]

            # Was previous character escape character? Was it line
            # continuation character?
            isEscaped = (cm1 == "\\") and (nC != 0)

            if c == "\"" and not isEscaped:
                isQuotesOpen = not isQuotesOpen

            # Things to do if quotes are NOT open.
            if not isQuotesOpen:
                # If a double space is found, go to the next character,
                if c == ' ' and cm1 == ' ':
                    continue
                elif c == "(":
                    isParenOpen = True
                elif c == ")":
                    isParenOpen = False
                # If a curly brace is found, change the nesting level,
                elif c in ["{", "}"]:
                    # Either check here for aggregate array
                    # initialization, or handle it in the semi-colon
                    # section.
                        # re.compile("[^{}]{(.*)} *(,.*|) *;$"

                    # The nesting level is going to changed. If there is
                    # any data, append it & clear the buffers.
                    if c == "{":
                        if nC == 0 and num_line:
                            num_line = num_line - 1

                    code_buf = _update_data(num_line, nI, code_buf, data)

                    if c == "{":
                        nI += 1
                    else:
                        nI -= 1

                    continue


            # Now, all characters can be appended
            code_buf += c

            # More things to do if quotes are NOT open.
            # 1) A semi-colon has been found. If there is any data,
            #    append it & clear the buffers.
            # 2) A colon has been found. If it is associated with any of
            #    the keywords "private", "public", "protected", "case",
            #    or "default", append data and clear buffers.
            append_data = False
            if not isQuotesOpen:
                # look for semi-colon not within a loop head
                if (c == ";" and not isParenOpen):
                    append_data = True

                # look for colon, but NOT scope resolution operator
                elif (c == ":" and (re_access_modifier_raw.search(code_buf) or re_switch_raw.search(code_buf))):
                    cp1 = " "
                    try:
                        for nLp1 in range(nL, len(code)):
                            break_outer_loop = False
                            for nCp1 in range(nC+1, len(codeLine)):
                                cp1 = code[nLp1][1][nCp1]
                                if not (nCp1 == len(codeLine)-1 and cp1 != "\\"):
                                    break_outer_loop = True
                                    break
                            if break_outer_loop:
                                break
                    except IndexError:
                        pass

                    if not (cm1 == ":" or cp1 == ":"):
                        append_data = True # colon is not part of operator

            if append_data:
                if nC == 0 and num_line:
                    num_line = num_line - 1
                code_buf = _update_data(num_line, nI, code_buf, data)

    return data


def block_comments_expand(code):
    """Expand multi-line block comments.

    args:
        code: An array of the form:

            [white_space, code, block_comments, line_comments]

    returns:
        out_code: The same as the input, except block comments are
        unrolled:

            [
                [white_space, code, block_comment_line, line_comments],
                ["",          "",   block_comment_line, ""           ],
                ["",          "",   block_comment_line, ""           ],
                ...
            ]
    """

    out_code = []
    for nL in range(len(code)):
        out_code.append([code[nL][0], code[nL][1], "", code[nL][3]])
        if code[nL][2]:
            out_code[-1][2] = code[nL][2][0]
            for nBC in range(1, len(code[nL][2])):
                out_code.append([code[nL][0], "", code[nL][2][nBC], ""])
    return out_code



def add_colon(code):
    """Adds colons to functions, classes, structs, typdefs, and enums.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code.
    """

    re_access_modifier = re.compile('^(public|private|protected)( *):$')
    re_switch = re.compile("^(case( .*|'.'|)|default *):$")

    out_code = []
    for nL in range(len(code)):
        branch = code[nL][:]
        if branch[2]:
            if branch[1]:
                if not (re_access_modifier.search(branch[1]) or re_switch.search(branch[1])):
                    branch[1] += ":"
            else:
                branch[0] = None
                branch[1] += ":"
        branch = [*branch[:2], add_colon(branch[2])]
        out_code.append(branch)
    return out_code



def rem_special_indent(code):
    """Removes indention for special for blocks marked by "public",
    "private", "protected", "case ", "default",

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code."""


    re_access_modifier = re.compile("^(public|private|protected)( *):$")
    re_switch = re.compile("^(case( .*|'.'|)|default *):$")

    def _pattern_match(s):
        isMatch = False
        if re_access_modifier.search(s) or re_switch.search(s):
            isMatch = True
        return isMatch

    out_code = []
    for nL in range(len(code)):
        if code[nL][2] and _pattern_match(code[nL][1]):
            out_code.append([*code[nL][:2], []])
            out_code += rem_special_indent(code[nL][2])
        else:
            out_code.append([*code[nL][:2], rem_special_indent(code[nL][2])])
    return out_code


def add_special_indent(code):
    """Adds indention for special for blocks marked by "public",
    "private", "protected", "case ", "default",

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code."""


    re_access_modifier = re.compile("^(public|private|protected)( *):$")
    re_switch = re.compile("^(case( .*|'.'|)|default *):$")

    def _pattern_match(s):
        isMatch = False
        if re_access_modifier.search(s) or re_switch.search(s):
            isMatch = True
        return isMatch

    isIndented = False
    out_code = []
    for nL in range(len(code)):
        isKeyWord = _pattern_match(code[nL][1])
        if isKeyWord:
            out_code.append([*code[nL][:2], add_special_indent(code[nL][2])])
            isIndented = True
        elif isIndented:
            out_code[-1][-1].append([*code[nL][:2], add_special_indent(code[nL][2])])
        else:
            out_code.append([*code[nL][:2], add_special_indent(code[nL][2])])

    return out_code


def add_semicolon(code):
    """Adds semi-colons to the end of code lines, classes, structs,
    typedefs, enums, and function declarations.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code.
    """
    def _is_aggregate_array(v):
        b = False

        if v[2]:
            pass
        elif v[1]:
            is_d_quote_open = False
            is_s_quote_open = False
            c = ""
            for n in range(len(v[1])):
                cm1 = c
                c = v[1][n]
                is_escaped = cm1 == "\\"
        return b

    re_array_init = re.compile('^([a-zA-Z0-9_] *)$')
    re_array_init = re.compile('^([a-zA-Z0-9_] *)$')
    re_macro = re.compile('^#.*$')
    re_enum = re.compile('^enum( .*|,.*|)$') # enum do not end with a ";"

    out_code = []
    for nL in range(len(code)):
        branch = code[nL][:]
        if branch[2]:
            if not re_enum.search(branch[1]):
                branch = [*branch[:2], add_semicolon(branch[2])]
        elif branch[1]:
            if not re_macro.search(branch[1]):
                branch[1] += ";"

        out_code.append(branch)
    return out_code


def rem_colon(code):
    """Removes colons from functions, classes, structs, typdefs, and enums.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code.
    """

    re_access_modifier = re.compile('^(public|private|protected)( *):$')
    re_switch = re.compile("^(case( .*|'.'|)|default *):$")

    out_code = []
    for nL in range(len(code)):
        branch = code[nL][:]
        # if branch[1] and branch[2]:
        if branch[1]:
            if not (re_access_modifier.search(branch[1]) or re_switch.search(branch[1]) or branch[1][0] == "#"):
                if branch[1][-1] == ":":
                    branch[1] = branch[1][:-1]
                    # Add empty code line if there is no code in between braces
                    if not branch[2]:
                        branch[2] = [[None, "", []]]
        branch = [*branch[:2], rem_colon(branch[2])]
        out_code.append(branch)
    return out_code


def rem_semicolon(code):
    """Removes semi-colons from the ends of code lines, classes, structs,
    typedefs, enums, and function declarations.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code.
    """


    out_code = []
    for nL in range(len(code)):
        branch = code[nL][:]
        if branch[1]:
            if branch[1][-1] == ";" and not branch[2]:
                branch[1] = branch[1][:-1]
        branch = [*branch[:2], rem_semicolon(branch[2])]
        out_code.append(branch)
    return out_code



def to_indented_aliases(code):
    """Restructure code for classes, structs, typdefs, and enums.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code.
        mv: A dictionary of line numbers that have been combines. Format
        is { original_line_number: new_line_number, ... }
    """

    re_class_curly = re.compile('^(class|struct|typedef|enum|union)( [^;]*|)$')

    def _f(_branch0, _branch1):
        """Analyze node for aliases. If found,restructure alias."""
        if re_class_curly.search(_branch0[1]):
            child_parrents = _branch0[1].split(":")
            if len(child_parrents) == 2:
                parrents = ": " + child_parrents[1].strip()
            else:
                parrents = ""
            child = child_parrents[0]
            if _branch1[1][:-1]:
                aliases = ", " + _branch1[1][:-1]
            else:
                aliases = ""

            _new_code = [_branch0[0], child + aliases + parrents, _branch0[2]]
            _skipNext = True
        else:
            _new_code = _branch0
            _skipNext = False
        return [_new_code, _skipNext]


    out_code = []
    skipNext = False
    mv = dict()
    for nL in range(len(code)):
        if skipNext:
            skipNext = False
        else:
            try:
                new_code, skipNext = _f(code[nL][:], code[nL+1][:])
                if skipNext:
                    mv[code[nL+1][0]] = code[nL][0]
            except IndexError:
                new_code = code[nL][:]
            nested_code, nested_mv = to_indented_aliases(new_code[2])
            out_code.append([*new_code[:2], nested_code])
            mv = {**mv, **nested_mv}

    return out_code, mv


def to_indented_do_while(code):
    """Restructure code for do-while loops.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code.
        mv: A dictionary of line numbers that have been combines. Format
        is { original_line_number: new_line_number, ... }
    """

    re_while = re.compile('^(while *\(.+\))(;)$')

    def _f(_branch0, _branch1):
        """Analyze node for aliases. If found, restructure alias."""
        r = re_while.search(_branch1[1])
        if _branch0[1] == "do" and r:
            _new_code = [_branch0[0], _branch0[1] + " " + r.group(1), _branch0[2]]
            _skipNext = True
        else:
            _new_code = _branch0
            _skipNext = False
        return [_new_code, _skipNext]

    out_code = []
    skipNext = False
    mv = dict()
    for nL in range(len(code)):
        if skipNext:
            skipNext = False
        else:
            try:
                new_code, skipNext = _f(code[nL][:], code[nL+1][:])
                if skipNext:
                    mv[code[nL+1][0]] = code[nL][0]
            except IndexError:
                new_code = code[nL][:]
            nested_code, nested_mv = to_indented_do_while(new_code[2])
            out_code.append([*new_code[:2], nested_code])
            mv = {**mv, **nested_mv}

    return out_code, mv



def to_curly_aliases(code):
    """Restructure code for classes, structs, enums, and typdefs.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code
        mv: A dictionary of line numbers that have been split. Format
        is { original_line_number: None, ... }
    """

    re_class_indented = re.compile('^(class|struct|typedef|enum|union)( [^;]*|,[^;]*|)$')

    def _f(_branch0):
        """Analyze node for aliases. If found,restructure alias."""
        child_parrents, inner_code, aliases = [_branch0[1], _branch0[2], ""]

        # if regex is true, change above values
        if re_class_indented.search(_branch0[1]):
            child_aliases_parrents = _branch0[1].split(":")
            child_aliases = child_aliases_parrents[0].split(", ")

            child_parrents = child_aliases[0]
            if len(child_aliases_parrents) == 2:
                child_parrents += (": " + child_aliases_parrents[1].strip())

            aliases = ";"
            if len(child_aliases) >= 2:
                aliases = ", ".join(map(str.strip, child_aliases[1:])) + ";"

        return [child_parrents, inner_code, aliases]

    mv = dict()
    out_code = []
    for nL in range(len(code)):
        res = _f(code[nL][:])
        nested_code, ch = to_curly_aliases(res[1])
        out_code.append([code[nL][0], res[0], nested_code])
        mv = {**mv, **ch}
        if res[2]: # A benign "if" statement to cut down on some of the noise.
            # out_code.append([None, res[2], []])
            mv[code[nL][0]] = None
            out_code.append([code[nL][0], res[2], []])

    return out_code, mv


def to_curly_do_while(code):
    """Restructure code for do-while loops.

    args:
        code: Tree-formatted source code.

    returns:
        out_code: Tree-formatted source code
        mv: A dictionary of line numbers that have been split. Format
        is { original_line_number: None, ... }
    """

    re_do_while = re.compile('^(do) (while *\(.+\))$')

    def _f(_branch0):
        """Analyze node for aliases. If found,restructure alias."""
        top, inner_code, bottom = [_branch0[1], _branch0[2], ""]
        r = re_do_while.search(_branch0[1])
        # if regex is true, change above values
        if r:
            top = r.group(1)
            bottom = r.group(2) + ";"
        return [top, inner_code, bottom]

    mv = dict()
    out_code = []
    for nL in range(len(code)):
        res = _f(code[nL][:])
        nested_code, ch = to_curly_do_while(res[1])
        out_code.append([code[nL][0], res[0], nested_code])
        mv = {**mv, **ch}
        if res[2]: # A benign "if" statement to cut down on some of the noise.
            mv[code[nL][0]] = None
            out_code.append([code[nL][0], res[2], []])

    return out_code, mv



def cosmetic_lines(code0):
    """Add or remove new lines to certain places in the source code.
    This operation is purely cosmetic.

    args:
        code0: source code as an array of lines.

    return:
        out_code: source code as an array of lines."""

    # strip any extra spaces from input
    code1 = []
    for n in range(len(code0)):
        if sum(map(bool, map(str.strip, code0[n]))):
            code1.append(code0[n])


    # drag aliases back behind closing curly bracket
    code = []
    alias = re.compile("^([a-zA-Z_]{1}[a-zA-Z0-9_]* *(,[a-zA-Z0-9_ ,]+|);|;)")
    for n in range(len(code1)):
        if alias.search(code1[n][1]) and prev_char == "}":
            code[-1][1] += " "*(len(code1[n][1]) > 1) + code1[n][1]
            code[-1][2] += code1[n][2]
            code[-1][3] += code1[n][3]
        else:
            code.append(code1[n])
        prev_char = (" " + code1[n][1])[-1]


    insert_line = [False]*len(code)

    # Create annotation for all lines.
    label = [None] * len(code)
    depth = [None] * len(code)

    for n in range(len(code)):
        depth[n] = len(code[n][0])
        if code[n][1]:
            if code[n][1][0] == "#":
                label[n] = "macro"
            elif code[n][1][0] == "}":
                label[n] = "close_brace"
            else:
                label[n] = "code"
        elif code[n][2] or code[n][3]:
            label[n] = "comment"

    # Iterate over code while looking two line ahead.
    for n in range(len(code)):
        i0 = depth[n]
        l0 = label[n]
        try:
            i1 = depth[n+1]
            l1 = label[n+1]
        except IndexError:
            l1 = None
            i1 = None
        try:
            i2 = depth[n+2]
            l2 = label[n+2]
        except IndexError:
            l2 = None
            i2 = None

        # Only add spaces when the next item is not indented.
        if i1 == 0:
            # Add space for certain changes in content type.
            if     (l0 == "code" and l1 == "comment") \
                or (l0 == "close_brace" and l1 == "comment") \
                or (l0 == "close_brace" and l1 == "code") \
                or (l0 == "macro" and l1 == "comment") \
                or (l0 == "macro" and l1 == "code") \
                or (l0 == "comment" and l1 == "macro") \
                or (l0 == "comment" and l1 == "code") \
                or (l0 == "code" and l1 == "macro"):
                    insert_line[n] = True
            # Examine consecutive code blocks
            elif (l0 == "code" or l0 == "close_brace") and l1 == "code":
                # Add space if indention will decrease.
                if i0 > i1:
                    insert_line[n] = True
                # Add space if next code section is a block of code. For
                # example a function, class, loop, or ect.
                elif i2 != None and i2 > i1:
                    insert_line[n] = True

        # Add blank at very end. C/C++ compilers often like this.
        if i1 == None and i2 == None:
            insert_line[n] = True

    # insert new lines
    out_code = []
    for n in range(len(code)):
        out_code.append(code[n])
        if insert_line[n]:
            out_code.append(["","","",""])


    return out_code


def isCurly(code):
    """Determine if code is the standard C/C++ syntax. C/C++
    syntax MUST have semi-colons at the end of lines. Indented syntax
    should not, although it likely has colons at the end of lines.

    args:
        code: Code in line-referenced format.

    returns:
        isC: True, if code is C/C++ syntax, or False if code is indented
        syntax. This option can be forced if code is misidentified."""

    # An upper limit on the number of lines to analyze.
    max_lines = min(50000, len(code))
    count_semicolons = 0
    count_colons = 0
    count_code_lines = 0
    isC = False
    for nL in range(max_lines):
        code_line = code[nL][1]
        if code_line:
            count_code_lines += 1
            if code_line[-1] == ";":
                count_semicolons += 1
            elif code_line[-1] == ":":
                count_colons += 1
    if count_semicolons > count_colons:
        isC = True
    return isC


def code_join(code):
    middle_code2 = [None]*len(code)
    for n in range(len(code)):
        middle_code2[n] =    code[n][0] \
                + code[n][1] \
                + " "*bool(code[n][1])*(bool(code[n][2]) or bool(code[n][3])) \
                + code[n][2] \
                + " "*bool(code[n][2])*bool(code[n][3]) \
                + code[n][3]
    return '\n'.join(middle_code2)


def convert(raw_code, make_indented=None):

    code, bcoms, coms = parse_raw_code(raw_code.splitlines())

    if make_indented == None:
        make_indented = isCurly(code)

    if make_indented:
        c2 = nest_curly(code)
        c3, mv1 = to_indented_aliases(c2)
        c4, mv2 = to_indented_do_while(c3)
        c5 = add_special_indent(c4)
        c6 = rem_semicolon(c5)
        c7 = add_colon(c6)
        c8 = indent(c7)
        mv = {**mv1, **mv2}
    else:
        c2 = nest_indented(code)
        c3 = rem_colon(c2)
        c4 = add_semicolon(c3)
        c5 = rem_special_indent(c4)
        c6, mv2 = to_curly_do_while(c5)
        c7, mv1 = to_curly_aliases(c6)
        c8 = curlify(c7)

    mv = {**mv1, **mv2}
    c9 = merge_comments(c8, bcoms, coms, mv)
    c10 = block_comments_expand(c9)
    c11 = cosmetic_lines(c10)
    out_code = code_join(c11)

    return out_code


def main(argv):
    """A compiler to convert C/C++ back and forth between the
    traditional syntax and another indentation-based Pythonic syntax.

    Usage:
        python3 thinc.py -i InputFileName -o OutputFileName

        python3 thinc.py -i Inpute.c -o Output.ic
        python3 thinc.py -i Inpute.ic -o Output.c -c
        python3 thinc.py -i Inpute.c
        cat Inpute.ic | python3 thinc.py

    args:
        -i: The input filename. Default is stdin.
        -o: The output filename. Default is stdout.
        -c: Force conversion to curly bracket syntax (C/C++ syntax).
        -p: Force conversion to indented syntax (Pythonic syntax).
    """

    make_indented = None
    fn_in = None
    fn_out = None

    for n in range(len(argv)):
        try:
            if argv[n] == "-c":
                make_indented = False
            elif argv[n] == "-p":
                make_indented = True
            elif argv[n] == "-i":
                fn_in = argv[n+1]
            elif argv[n] == "-o":
                fn_out = argv[n+1]
        except IndexError:
            pass

    if fn_in:
        code_in = readFile(fn_in)
    else:
        code_in = sys.stdin.read()

    new_lines = convert(code_in, make_indented)

    if fn_out:
        writeFile(fn_out, new_lines)
    else:
        sys.stdout.write(new_lines)


if __name__ == "__main__":
    main(sys.argv)
