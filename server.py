#!/usr/bin/env python3

# Submit Server Information
from config import *

# Load in required Libraries.
import sys
if sys.version_info.major != 3:
    print('This requires Python 3')
    sys.exit(2)
sys.dont_write_bytecode = True
import os, re, platform, time, json, uuid, tempfile, shutil
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

# Import Docker Library, Modify to allow text based dockerfile
import docker
import docker.api.build
docker.api.build.process_dockerfile = lambda dockerfile, path: ('Dockerfile', dockerfile)

# Connect to the local docker instance
client = docker.from_env()

# Track containers
container_list = {}

# How often should we register the docker bases with the system.
docker_interval = 3600
docker_last_call = 0

# Main Loop
while True:

    # Sleep for just a bit
    time.sleep(1.0)

    # Register the available docker bases with the submit system
    if time.time() - docker_interval > docker_last_call:
        docker_last_call = time.time()
        post_api_json(API+'/docker/register', {'apikey':KEY, 'bases':','.join(list(BASE_CONFIG.keys()))})

    # Loop through all possible supported bases for this system
    for BASE in BASE_CONFIG:

        INSTANCES = BASE_CONFIG[BASE]['INSTANCES']
        DOCKER_CPUS = BASE_CONFIG[BASE]['DOCKER_CPUS']
        DOCKER_MEM_LIMIT = BASE_CONFIG[BASE]['DOCKER_MEM_LIMIT']

        ##############################################################################
        # Retrieve submissions waiting to be processed, if a submissionID (sid)
        # was provided as part of the command line, submit that to the system
        # for processing.
        submission_list = post_api_json(API+'/submission/next', {'apikey':KEY, 'base':BASE})

        # Check the docker types of all received submissions
        docker_bases = {}
        for row in submission_list['results']:
            found_base = row['docker']
            if found_base in SUPPORTED_BASES:
                if found_base not in docker_bases:
                    docker_bases[found_base] = [0,0]
                docker_bases[found_base][0] += 1

        # Create an easily pop'd list of the docker bases
        docker_bases_pop = []
        continue_loop = True
        while continue_loop:
            found_one = False
            for key in docker_bases:
                if docker_bases[key][0] != docker_bases[key][1]:
                    docker_bases_pop.append(key)
                    docker_bases[key][1] += 1
                    found_one = True
            if not found_one:
                continue_loop = False
        docker_bases_pop.reverse()

        # Display Results
        submission_print = {}
        for row in submission_list['results']:
            if row['course'] not in submission_print:
                submission_print[row['course']] = {}
            if row['project'] not in submission_print[row['course']]:
                submission_print[row['course']][row['project']] = {}
            if row['user'] not in submission_print[row['course']][row['project']]:
                submission_print[row['course']][row['project']][row['user']] = 0
            submission_print[row['course']][row['project']][row['user']] = submission_print[row['course']][row['project']][row['user']] + 1

        print('\x1b[2J')
        print(time.asctime(time.localtime(time.time())))
        print('Available Submission/Tests to process = '+str(len(submission_list['results']))+' (estimated)')
        for course in submission_print:
            print('  --', course)
            for project in submission_print[course]:
                print('     --', project)
                for user in submission_print[course][project]:
                    print('        --', user, '(', submission_print[course][project][user],')')

        # For some reason this gets confused every now and then...
        try:
            ccl = client.containers.list()
        except:
            ccl = []

        # List and/or kill a container
        if len(ccl) > 0:

            ##############################################################################
            # Determine if we should kill any running docker containers
            running_list = post_api_json(API+'/results/inprogress', {'apikey':KEY})
            running_list_search = {}
            kill_list = []
            if 'results' in running_list:
                for ip in running_list['results']:
                    try:
                        running_list_search[ip['process']] = ip
                        running_list_search[ip['process'][:10]] = ip
                        if ip['status'] == 'kill':
                            kill_list.append(ip['process'])
                            kill_list.append(ip['process'][:10])
                    except:
                        pass

            new_list = {}
            for c in ccl:
                id = c.short_id
                if id not in container_list:
                    container_list[id] = time.time()
                new_list[id] = container_list[id]

                if id in running_list_search:
                    print("           Container:",id,running_list_search[id]['course'],running_list_search[id]['project'],running_list_search[id]['user'],running_list_search[id]['rulename'],int(time.time()-container_list[id]))
                else:
                    print("           Container:",id,int(time.time()-container_list[id]))
                if time.time()-container_list[id] > KILL_AFTER or id in kill_list:
                    try:
                        print("  -Killing Container:",id)
                        c.kill()
                        if id in running_list_search:
                            post_api_json(API+'/results/status', {'apikey':KEY, 'sid':running_list_search[id]['sid'], 'tid':running_list_search[id]['tid'], 'status':'done'})
                            post_api_json(API+'/results/run',    {'apikey':KEY, 'sid':running_list_search[id]['sid'], 'tid':running_list_search[id]['tid'], 'returnval':'7777', 'stime':'7777', 'stdout':'', 'stderr':'', 'sourcefile':'', 'pass':'0'})
                    except:
                        pass
            container_list = new_list

        # Verify that there are results to work with
        if 'results' in submission_list and len(submission_list['results']) > 0 and len(ccl) < INSTANCES:

            # cleanup
            client.images.prune()
            client.containers.prune()

            for build in range(min(INSTANCES-len(ccl), len(docker_bases_pop))):

                # Build a new dockerfile on the fly
                client_base = docker_bases_pop.pop()
                DF = "FROM "+client_base+"""
    MAINTAINER Jeff Kenney
    COPY . /app
    WORKDIR /app
    CMD python3 client.py --base """ + client_base + """
    """

                # Create an image to work with
                img = client.images.build(path=".",dockerfile=DF)
                # Run the image
                con=client.containers.run(img[0], auto_remove=True, cpuset_cpus=DOCKER_CPUS, mem_limit=DOCKER_MEM_LIMIT, remove=True, detach=True, user=666, cap_drop=['all'])
                container_list[con.short_id] = time.time()
                print("  Starting Container: (", client_base,")", con.short_id)

        else:
            time.sleep(DELAYCHECK)

# Wait for system to finish...
while(len(client.containers.list()) > 0):
    time.sleep(0.5)
    print('Waiting for containers to close')

client.images.prune()
