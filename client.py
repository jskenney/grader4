#!/usr/bin/env python3

# Submit Server Information
API = 'http://mm.cs.usna.edu/api'
KEY = 'test-api-key'

# Submit System Grader Version 3.0
# This is the client, and will handle the grading and
# processing of a SINGLE submission to a project.  The
# System will communicate with the server via API calls
# exclusively with no direct database access.

# Load in required Libraries.
import sys
if sys.version_info.major == 2:
    print('This requires Python 3')
    sys.exit()
sys.dont_write_bytecode = True
import os, re, platform, time, json, uuid, tempfile, shutil
import runner
import check
try:
    import requests
except:
    print("Please install the requests library!")
    print("Use (for python3):")
    print("  pip3 install requests")
    sys.exit()

# Retrieve information from a REST style API
# Return the results in a python style dictionary
def post_api_json(API_PATH, PAYLOAD={}, TIMEOUT=99):
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
post = {'apikey':KEY}
if len(sys.argv) > 1:
    post['sid'] = sys.argv[-1]
submission_list = post_api_json(API+'/submission/next', post)

# Verify that there are results to work with
if 'results' not in submission_list or len(submission_list['results']) < 1:
    print('Nothing to process, ending')
    sys.exit()

# Work with a specific submission
submission = submission_list['results'][0]
print('SUBMISSION:')
print(dict_to_string_table(submission))

LINT += 'SUBMISSION:\n' + dict_to_string_table(submission) + '\n'

# Claim this submission via the API
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'retrieving project information', 'lint':LINT})

# Create a Temporary Directory to work with
origdir = os.getcwd()
stordir = tempfile.TemporaryDirectory()
os.chdir(stordir.name)

##############################################################################
# Retrieve project information
project = post_api_json(API+'/project/list', {'apikey':KEY, 'course':submission['course'], 'project':submission['project'], 'lint':LINT})
project = project['results'][0]
LINT += 'PROJECT:\n' + dict_to_string_table(project) + '\n'

print('PROJECT:')
print(dict_to_string_table(project))

# Retrieve test case information
testcases = post_api_json(API+'/testcase/list', {'apikey':KEY, 'course':submission['course'], 'project':submission['project'], 'lint':LINT})
testcase = []
for test in testcases['results']:
    if test['tid'] == submission['tid']:
        testcase = test
if testcase == []:
    print('testcase failure - testcase missing...')
    post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'system failure - testcase removed?', 'lint':LINT})
    sys.exit()

LINT += 'TESTCASE:\n' + dict_to_string_table(testcase)+ '\n'
print('TESTCASE:')
print(dict_to_string_table(testcase))

##############################################################################
# Start Downloading the Submission with TestFiles
print('Downloading Submission')
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'downloading submission', 'lint':LINT})
post_api_file(API+'/submission/pull', '.student.code.tgz', {'apikey':KEY, 'course':submission['course'], 'project':submission['project'], 'sid':submission['sid']})

##############################################################################
# Build Local Test Environment
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'extracting submission files', 'lint':LINT})
cmd = 'tar -xvpf .student.code.tgz'
stdout, stderr, return_code, etime = runner.run(cmd, '')
os.remove('.student.code.tgz')
LINT += 'extraction:\n' + str(stdout) + '\nERROR:' + str(stderr) + '\n'
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'extracting submission files - complete', 'lint':LINT})

##############################################################################
# Makefile Lint Step
if testcase['analysis_target'] != '':
    print('Beginning ANLYSIS step')
    post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'init analysis', 'lint':LINT})
    cmd = 'make '+testcase['analysis_target']
    stdout, stderr, return_code, etime = runner.run(cmd, '')
    post_api_json(API+'/results/analysis', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'returnval':return_code, 'stime':etime, 'stdout':stdout, 'stderr':stderr})

##############################################################################
# Makefile Compile Step
compiled = True
if testcase['compile_target'] != '':
    print('Beginning COMPILE step')
    post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'init compile', 'lint':LINT})
    cmd = 'make '+testcase['compile_target']
    stdout, stderr, return_code, etime = runner.run(cmd, '')
    if return_code != 0:
        compiled = False
    post_api_json(API+'/results/compile', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'returnval':return_code, 'stime':etime, 'stdout':stdout, 'stderr':stderr})

##############################################################################
# Makefile Run Step
final = False
if compiled:
    stdout, stderr, return_code, etime = b'', b'', 8888, -1.0
    if testcase['run_target'] != '':
        print('Beginning RUN step')
        post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'init run', 'lint':LINT})
        cmd = 'make '+testcase['run_target']
        stdout, stderr, return_code, etime = runner.run(cmd, '')
        print('------------STDOUT-----------')
        print(stdout)
        print('')
        print('------------STDERR-----------')
        print(stderr)
        print('')

    ##############################################################################
    # Analysis of Results and return values to database for test run.
    final = check.test(testcase['stdin'], testcase['source'], testcase['sourcefile'], testcase['cond'], testcase['outvalue'], stdout, stderr, return_code, etime, return_code == 9999)
else:
    print('*-*-COMPILE-FAIL-ABORT-RUN*-*')

##############################################################################
# Store results
sourcefile = ''
if testcase['cond'] == 'Student source code' or testcase['cond'] == 'Created File':
    sourcefile = testcase['sourcefile']
if final:
    print('-------------PASS------------')
else:
    print('*-*-*-*-*-*-*FAIL*-*-*-*-*-*-')
if final:
    final = '1'
else:
    final = '0'
post_api_json(API+'/results/run', {'apikey':KEY, 'sid':submission['sid'], 'tid':submission['tid'], 'returnval':return_code, 'stime':etime, 'stdout':stdout, 'stderr':stderr, 'sourcefile':sourcefile, 'pass':final})

##############################################################################
# Destroy the main temporary Directory
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'destroying local test environment', 'lint':LINT})
os.chdir(origdir)
stordir.cleanup()

# Remove claim on this submission via the API
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'done'})
