#!/usr/bin/env python3

# Submit Server Information
API = 'http://mm.cs.usna.edu/api'
KEY = 'test-api-key'

# Submit System Grader Version 2.0
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
print('submission:')
print(submission)

# Claim this submission via the API
LINT = ''
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'retrieving project information', 'lint':LINT})

# Create a Temporary Directory to work with
origdir = os.getcwd()
stordir = tempfile.TemporaryDirectory()
os.chdir(stordir.name)

##############################################################################
# Retrieve project information
project = post_api_json(API+'/project/list', {'apikey':KEY, 'course':submission['course'], 'project':submission['project'], 'lint':LINT})
print('project:')
print(project)

# Retrieve test case information
testcases = post_api_json(API+'/testcase/list', {'apikey':KEY, 'course':submission['course'], 'project':submission['project'], 'lint':LINT})
print('testcases:')
print(testcases)

##############################################################################
# Start Downloading the Submission with TestFiles
print('Downloading Submission')
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'downloading submission', 'lint':LINT})
post_api_file(API+'/submission/pull', '.student.code.tgz', {'apikey':KEY, 'course':submission['course'], 'project':submission['project'], 'sid':submission['sid']})

# Extract the contents of the students submission
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'extracting submission', 'lint':LINT})
#cmd = 'tar xvpf .student.code.tgz'
#stdout, stderr, return_code, etime = runner.run(cmd, '')
#os.remove('.student.code.tgz')

##############################################################################
# Destroy the main temporary Directory
os.chdir(origdir)
stordir.cleanup()

# Remove claim on this submission via the API
post_api_json(API+'/results/status', {'apikey':KEY, 'sid':submission['sid'], 'status':'done'})
