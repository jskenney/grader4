#!/usr/bin/env python3

#while [ $? -ne 2 ]; do ./client.py ; done
#x = input('foo')

# Submit Server Information
from config import *

# Submit System Grader Version 4.0
# This is the client, and will handle the grading and
# processing of a SINGLE submission to a project.  The
# System will communicate with the server via API calls
# exclusively with no direct database access.

def debugPrint(tf, line):
    if tf:
        try:
            print(line)
        except Exception as e:
            print('--unable-to-print--')
            print(e)

# Load in required Libraries.
import sys
if sys.version_info.major != 3:
    print('This requires Python 3')
    sys.exit(2)
sys.dont_write_bytecode = True
import os, re, platform, time, json, uuid, tempfile, shutil, traceback, argparse
import runner
import check
try:
    import requests
except:
    print("Please install the requests library!")
    print("Use (for python3):")
    print("pip3 install requests")
    sys.exit(2)

# Retrieve information from a REST style API
# Return the results in a python style dictionary
def post_api_json(API_PATH, PAYLOAD={}, TIMEOUT=99):
    PAYLOAD['nosession'] = 1
    results = {}
    if PAYLOAD == {}:
        resp = requests.post(API_PATH, timeout=TIMEOUT)
    else:
        resp = requests.post(API_PATH, data=PAYLOAD, timeout=TIMEOUT)
    if resp.status_code == 200:
        results = json.loads(resp.text)
    return results

# Retrieve a file from a REST style API
# Will download the file to a specified location and filename
def post_api_file(API_PATH, FILENAME='', PAYLOAD={}, TIMEOUT=99):
    PAYLOAD['nosession'] = 1
    if PAYLOAD == {}:
        resp = requests.post(API_PATH, timeout=TIMEOUT, allow_redirects=True)
    else:
        resp = requests.post(API_PATH, data=PAYLOAD, timeout=TIMEOUT, allow_redirects=True)
    if resp.status_code == 200:
        open(FILENAME, 'wb').write(resp.content)
    return True

# Simple debug for printing associative arrays
def dict_to_string_table(d):
    results = ''
    for k, v in d.items():
        k = str(k)
        v = str(v)
        results = results + "{:<15} {:<30}".format(k, v) + '\n'
    return results

##############################################################################
# Will store all debugging information in LINT, which will be updated in the
# Database as a current status report
LINT = ''

##############################################################################
# Retrieve submissions waiting to be processed, if a submissionID (sid)
# was provided as part of the command line, submit that to the system
# for processing.
print('GraderV4')

try:

    # Define Required Command Line Arguments
    parser = argparse.ArgumentParser(description="Autograde an available job.")
    parser.add_argument('--course', dest='course', metavar='COURSE', default='%', nargs=1, help='select a specific course')
    parser.add_argument('--project', dest='project', metavar='PROJECT', default='%', nargs=1, help='select a specific project')
    parser.add_argument('--base', dest='base', metavar='DOCKERBASE', default='%', nargs=1, help='select default docker image')
    parser.add_argument('--user', dest='user', metavar='USER', default='%', nargs=1, help='select a user to process')
    parser.add_argument('--rulename', dest='rulename', metavar='RULENAME', default='%', nargs=1, help='select a specific testcase to run')
    parser.add_argument('--debug', dest='debug', metavar='DEBUGVALUE', default='%', nargs='?', help='set a specific delay to allow file system debugging')
    args = parser.parse_args()

    # Select docker base image
    if args.base != '%':
        BASE = args.base[0]
    else:
        BASE = BASE_DEFAULT

    # Change debugging level
    if args.debug != '%':
        DEBUG = True
        try:
            args.debug = int(args.debug)
        except:
            args.debug = '%'

    # Retrieve a specific project/user/test to process, override already completed if specificed manually
    if args.course != '%' and args.project != '%' and args.user != '%' and args.rulename != '%':
        submission_list = post_api_json(API+'/submission/verify', {'apikey':KEY, 'base':BASE, 'course': args.course, 'project': args.project, 'user':args.user, 'rulename':args.rulename})
    else:
        submission_list = post_api_json(API+'/submission/claim', {'apikey':KEY, 'base':BASE})

    # Verify that there are results to work with
    if 'results' not in submission_list or len(submission_list['results']) < 1:
        print('GraderV4 - Nothing to Process - Exiting.')
        sys.exit(2)

    # Connect to the local docker server
    DOCKER = platform.node()

    # Status
    print('GraderV4 - Processing next submission - '+DOCKER)

    # Work with a specific submission
    submission = submission_list['results']
    debugPrint(DEBUG, 'SUBMISSION:')
    debugPrint(DEBUG, dict_to_string_table(submission))

    LINT += 'SUBMISSION:\n' + dict_to_string_table(submission) + '\n'

    # Claim this submission via the API
    post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'setup', 'process':DOCKER, 'lint':LINT})

    # Create a Temporary Directory to work with
    origdir = os.getcwd()
    stordir = tempfile.TemporaryDirectory()
    os.chdir(stordir.name)

    ##############################################################################
    # Retrieve project information
    project = post_api_json(API+'/project/list', {'apikey':KEY, 'course':submission['course'], 'project':submission['project'], 'process':DOCKER, 'lint':LINT})
    project = project['results'][0]
    LINT += 'PROJECT:\n' + dict_to_string_table(project) + '\n'

    debugPrint(DEBUG, 'PROJECT:')
    debugPrint(DEBUG, dict_to_string_table(project))

    # Retrieve test case information
    testcases = post_api_json(API+'/testcase/list', {'apikey':KEY, 'course':submission['course'], 'project':submission['project'], 'process':DOCKER, 'lint':LINT})
    testcase = []
    for test in testcases['results']:
        if test['tid'] == submission['tid']:
            testcase = test
    if testcase == []:
        debugPrint(DEBUG, 'testcase failure - testcase missing...')
        post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'system failure - testcase removed?', 'process':DOCKER, 'lint':LINT})
        sys.exit()

    LINT += 'TESTCASE:\n' + dict_to_string_table(testcase)+ '\n'
    debugPrint(DEBUG, 'TESTCASE:')
    debugPrint(DEBUG, dict_to_string_table(testcase))

    ##############################################################################
    # Start Downloading the Submission with TestFiles
    debugPrint(DEBUG, 'Downloading Submission')
    post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'downloading', 'process':DOCKER, 'lint':LINT})
    post_api_file(API+'/submission/pull', '.student.code.tgz', {'apikey':KEY, 'course':submission['course'], 'project':submission['project'], 'sid':submission['sid']})

    ##############################################################################
    # Build Local Test Environment
    debugPrint(DEBUG, 'Extracting Submission')
    post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'extracting', 'process':DOCKER, 'lint':LINT})
    cmd = 'tar -xvpf .student.code.tgz'
    stdout, stderr, return_code, etime = runner.run(cmd, '')
    os.remove('.student.code.tgz')
    LINT += 'extraction:\n' + stdout + '\nERROR:' + stderr + '\nextraction-complete.\n'

    debugPrint(DEBUG, 'File Listing:')
    for item in os.listdir('.'):
        debugPrint(DEBUG, "  {:<7} {:<30}".format('file:', item))
    debugPrint(DEBUG, '')

    ##############################################################################
    # Setup available environmental variables
    _envvar = {'gradercourse':   submission['course'],
               'graderproject':  submission['project'],
               'graderuser':     submission['user'],
               'graderrulename': testcase['rulename'],
               'graderpid':      str(submission['pid']),
               'gradersid':      str(submission['sid']),
               'gradertid':      str(submission['tid'])
              }

    ##############################################################################
    # Makefile Compile Step
    compiled = True
    print('Working with: http://submit.usna.edu/site/receipt.php?submission='+submission['UUID'])
    if testcase['compile_target'] != '':
        post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'compiling', 'process':DOCKER, 'lint':LINT})
        if testcase['makefile'] != None and testcase['makefile'] != '':
            cmd = 'make -f ' + testcase['makefile'] + ' ' + testcase['compile_target']
        else:
            cmd = 'make ' + testcase['compile_target']
        stdout, stderr, return_code, etime = runner.run(cmd, '', testcase['infinite'], _envvar=_envvar)
        if len(stdout) > MAX_SIZE:
            stdout = stdout[:MAX_SIZE]
        if len(stderr) > MAX_SIZE:
            stderr = stderr[:MAX_SIZE]
        debugPrint(DEBUG, '-COMPILE-----------STDOUT-----------')
        debugPrint(DEBUG, stdout)
        debugPrint(DEBUG, '')
        debugPrint(DEBUG, '-COMPILE-----------STDERR-----------')
        debugPrint(DEBUG, stderr)
        debugPrint(DEBUG, '')
        if return_code != 0:
            compiled = False
        post_api_json(API+'/results/compile', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'returnval':return_code, 'stime':etime, 'stdout':stdout, 'stderr':stderr})

    ##############################################################################
    # Makefile Lint Step
    if testcase['analysis_target'] != '':
        post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'analysis', 'process':DOCKER, 'lint':LINT})
        if testcase['makefile'] != None and testcase['makefile'] != '':
            cmd = 'make -f ' + testcase['makefile'] + ' ' + testcase['analysis_target']
        else:
            cmd = 'make ' + testcase['analysis_target']
        print('Beginning ANALYSIS step ['+submission['course']+'] ['+str(submission['pid'])+' '+submission['project']+'] ['+str(submission['sid'])+' '+submission['user']+'] ['+str(submission['tid'])+' '+testcase['rulename']+'] ['+str(testcase['infinite'])+'] ['+cmd+']')
        stdout, stderr, return_code, etime = runner.run(cmd, '', testcase['infinite'], _envvar=_envvar)
        if len(stdout) > MAX_SIZE:
            stdout = stdout[:MAX_SIZE]
        if len(stderr) > MAX_SIZE:
            stderr = stderr[:MAX_SIZE]
        debugPrint(DEBUG, '-ANALYSIS-----------STDOUT-----------')
        debugPrint(DEBUG, stdout)
        debugPrint(DEBUG, '')
        debugPrint(DEBUG, '-ANALYSIS-----------STDERR-----------')
        debugPrint(DEBUG, stderr)
        debugPrint(DEBUG, '')
        post_api_json(API+'/results/analysis', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'returnval':return_code, 'stime':etime, 'stdout':stdout, 'stderr':stderr})

    ##############################################################################
    # Makefile Run Step
    final = False
    diffval = ''
    stdout, stderr, return_code, etime = u'', u'', 9000, -1.0
    if compiled:
        stdout, stderr, return_code, etime = u'', u'', 8888, -1.0
        if testcase['run_target'] != '':
            post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'running', 'process':DOCKER, 'lint':LINT})
            if testcase['makefile'] != None and testcase['makefile'] != '':
                cmd = 'make -f ' + testcase['makefile'] + ' ' + testcase['run_target']
            else:
                cmd = 'make ' + testcase['run_target']
            print( 'Beginning RUN step      ['+submission['course']+'] ['+str(submission['pid'])+' '+submission['project']+'] ['+str(submission['sid'])+' '+submission['user']+'] ['+str(submission['tid'])+' '+testcase['rulename']+'] ['+str(testcase['infinite'])+'] ['+cmd+']')
            stdout, stderr, return_code, etime = runner.run(cmd, testcase['stdin'], testcase['infinite'], _envvar=_envvar)
            if len(stdout) > MAX_SIZE:
                stdout = stdout[:MAX_SIZE]
            if len(stderr) > MAX_SIZE:
                stderr = stderr[:MAX_SIZE]
            debugPrint(DEBUG, '-RUN-----------STDOUT-----------')
            debugPrint(DEBUG, stdout)
            debugPrint(DEBUG, '')
            debugPrint(DEBUG, '-RUN-----------STDERR-----------')
            debugPrint(DEBUG, stderr)
            debugPrint(DEBUG, '')

        ##############################################################################
        # Analysis of Results and return values to database for test run.
        final, diffval = check.test(testcase['stdin'], testcase['source'], testcase['sourcefile'], testcase['cond'], testcase['outvalue'], stdout, stderr, return_code, etime, return_code == 9999, DEBUG_SHOW_TESTCASE)

    else:
        print('*-*-COMPILE-FAIL-ABORT-RUN-*-*')

    ##############################################################################
    # Store results
    sourcefile = ''
    if testcase['cond'] == 'Student source code' or testcase['cond'] == 'Created File':
        sourcefile = testcase['sourcefile']
    if final:
        print('---PASS------PASS------PASS---')
        final = '1'
    else:
        print('*-*-*-*-*-*-*FAIL*-*-*-*-*-*-*')
        final = '0'

    data = post_api_json(API+'/results/run', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'returnval':return_code, 'stime':etime, 'stdout':stdout, 'stderr':stderr, 'sourcefile':sourcefile, 'pass':final, 'diff':diffval})

    ##############################################################################
    # DEBUG - Final Debugging Opportunity
    if DEBUG and args.debug != '%':
        debugPrint(DEBUG, 'STORAGE:')
        debugPrint(DEBUG, stordir.name)
        debugPrint(DEBUG, '')
        post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'debug '+stordir.name, 'process':DOCKER, 'lint':LINT})
        time.sleep(args.debug)

    ##############################################################################
    # Destroy the main temporary Directory
    post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'destroy', 'process':DOCKER, 'lint':LINT})
    os.chdir(origdir)
    stordir.cleanup()

    # Remove claim on this submission via the API
    post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'done'})

    print('')

except Exception as ex:
    LINT = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
    if LINT.find('Read timed out. (read timeout=99)') == -1:
        post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'crash', 'lint':LINT})
    else:
        post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'status':'done'})
