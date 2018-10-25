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
def test(stdin, source, sourcefile, cond, outvalue, stdout, stderr, returnval, stime, infinite, debug=True):

    # set default check variables
    chk_student = stdout
    chk_testcase = outvalue
    created_exists = True

    # change inputs based on the ___source___
    if source == 'Return Code':
        chk_student = returnval
    elif source == 'Infinite Loop':
        chk_student = infinite
    elif source == 'Student source code' or source == 'Created File':
        try:
            chk_student = b''.join(open(sourcefile,'rb').readlines())
        except:
            created_exists = False
    elif source == 'Run time':
        chk_student = str(stime)

    # Check for NoneType
    if chk_student is None:
        chk_student = b''
    if chk_testcase is None:
        chk_testcase = b''

    # Convert everything to bytes
    if not isinstance(chk_student, bytes):
        chk_student = bytes(chk_student, 'utf-8')
    if not isinstance(chk_testcase, bytes):
        chk_testcase = bytes(chk_testcase, 'utf-8')

    # Print debugging information if requested
    if debug:
        print ('*********** Test Case Conditions *************')
        print ('This test case checks to see if the ['+source+'] ['+cond+']')
        print ('Expected: '+str(chk_testcase))
        print ('Received: '+str(chk_student))
        print ('**********************************************')
        
    # check to see if this is the simple "compiles" case
    if cond == 'compiles':
        return True

    # if condition is 'whitespace' which ignores whitespace,
    # delete whitespace and then do the comparision as 'is exactly'
    if cond == 'whitespace':
        cond = 'is exactly'
        chk_student = chk_student.replace(b'\n', b'').replace(b'\t', b'').replace(b' ', b'')
        chk_testcase = chk_testcase.replace(b'\n', b'').replace(b'\t', b'').replace(b' ', b'')

    # check for equality
    if cond == 'is exactly':
        return chk_student.strip().replace(b'\r', b'') == chk_testcase.strip().replace(b'\r', b'')

    # check via the various conditions
    if cond == 'has':
        return chk_student.find(chk_testcase) != -1
    if cond == 'does not have':
        return chk_student.find(chk_testcase) == -1

    # Verify that results existed
    if cond == 'exists':
        if source == 'Student source code' or source == 'Created File':
            return created_exists
        if source == 'Output':
            return chk_student != b''

    # truth checking
    if cond == 'is true':
        return chk_student == b'1' or chk_student == True
    if cond == 'is false':
        return not chk_student == b'1' or chk_student == True

    # numeric <, <=, >, >=
    try:
        chk_student = float(chk_student)
        chk_testcase = float(chk_testcase)
    except:
        return False

    if cond == 'greater than':
        return chk_student > chk_testcase
    if cond == 'less than':
        return chk_student < chk_testcase
    if cond == 'greater or equal':
        return chk_student >= chk_testcase
    if cond == 'less or equal':
        return chk_student <= chk_testcase

    return False
