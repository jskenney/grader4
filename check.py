#!/usr/bin/env python3

# Submit System Grader Version 3.0
# This library will handle checking the resutls of a testcase

# Load Primary Libraries
import sys
sys.dont_write_bytecode = True

# Possible options for:
#  source: 'Return Code', 'Infinite Loop', 'Student source code', 'Created File', 'Run time'
#  cond: 'compiles', 'is exactly', 'whitespace', 'has', 'does not have', 'exists', 'is true', 'is false'
#        'greater than', 'less than', 'greater or equal', 'less or equal'
# Check the results and see if the test was successful
# Returns pass/fail and the value it was tested against.
def test(stdin, source, sourcefile, cond, outvalue, stdout, stderr, returnval, stime, infinite, debug=True):

    # set default check variables
    chk_student = stdout
    chk_testcase = outvalue

    # Assume that a file was created
    created_exists = True

    # change inputs based on the ___source___
    if source == 'Return Code':
        chk_student = returnval
    elif source == 'Infinite Loop':
        chk_student = infinite
    elif source == 'Student source code' or source == 'Created File':
        try:
            chk_student = u''.join(open(sourcefile,'r').readlines())
        except:
            created_exists = False
    elif source == 'Run time':
        chk_student = str(stime)

    # Check for NoneType
    if chk_student is None:
        chk_student = u''
    if chk_testcase is None:
        chk_testcase = u''

    # Create diff results
    diff_student = chk_student

    # check to see if this is the simple "compiles" case
    if cond == 'compiles' or cond == 'manual review as html':
        return True, diff_student

    # if condition is 'whitespace' which ignores whitespace,
    # delete whitespace and then do the comparision as 'is exactly'
    if cond == 'whitespace':
        cond = 'is exactly'
        if isinstance(chk_student, bool) or isinstance(chk_student, int) or isinstance(chk_student, float):
            chk_student = str(chk_student)
        chk_student = chk_student.replace(u'\n', u'').replace(u'\t', u'').replace(u' ', u'')
        chk_testcase = chk_testcase.replace(u'\n', u'').replace(u'\t', u'').replace(u' ', u'')

    # check for equality
    if cond == 'is exactly':
        if isinstance(chk_student, bool) or isinstance(chk_student, int) or isinstance(chk_student, float):
            chk_student = str(chk_student)
        return chk_student.strip().replace(u'\r', u'') == chk_testcase.strip().replace(u'\r', u''), diff_student

    # check via the various conditions
    if cond == 'has':
        return chk_student.find(chk_testcase) != -1, diff_student
    if cond == 'does not have':
        return chk_student.find(chk_testcase) == -1, diff_student

    # Verify that results existed
    if cond == 'exists':
        if source == 'Student source code' or source == 'Created File':
            return created_exists, diff_student
        if source == 'Output':
            return chk_student != u'', diff_student

    # truth checking
    if cond == 'is true':
        return chk_student == u'1' or chk_student == True, diff_student
    if cond == 'is false':
        return not chk_student == u'1' or chk_student == True, diff_student

    # numeric <, <=, >, >=
    try:
        chk_student = float(chk_student)
        chk_testcase = float(chk_testcase)
    except:
        return False, diff_student

    if cond == 'greater than':
        return chk_student > chk_testcase, diff_student
    if cond == 'less than':
        return chk_student < chk_testcase, diff_student
    if cond == 'greater or equal':
        return chk_student >= chk_testcase, diff_student
    if cond == 'less or equal':
        return chk_student <= chk_testcase, diff_student

    return False, diff_student
