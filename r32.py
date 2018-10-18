#!/usr/bin/python

# Submit :: Source Code Compiler and Runner :: Version 2.09 :: 20150922

global VERSION
VERSION = '2.32'

global BUILD_DIR
BUILD_DIR = '/ramfs'      # Where should source files be written to.

# Load Primary Libraries
import sys
sys.dont_write_bytecode = True      # Prevents the creation of .pyc files - which appear broken on zee
import os,string,time,uuid,imp,traceback

global DEBUG_START, DEBUG_LAST
DEBUG_START = time.time()
DEBUG_LAST = DEBUG_START

# Load Database Modules
###### USE LOCAL COPY ##### sys.path.append(os.path.abspath('../config'))
import db2

# Load Runner libraries
import runner

# Convert col/data to DICT format
def col_data_to_dict(col, data):
    results = []
    for item in data:
        row = {}
        for i in range(len(col)):
            row[col[i][0]] = item[i]
        results.append(row)
    return results

# Group similiar information
# col is a specific column, data is the results of col_data_to_dict
def group_data(col, data):
    results = {}
    for line in data:
        if not results.has_key(line[col]):
            results[line[col]] = []
        results[line[col]].append(line)
    return results

# Combine two {}, the first has precidence for duplicate keys
def combine_dict(d1, d2):
    results = {}
    for key in d1.keys():
        results[key] = d1[key]
    for key in d2.keys():
        if not results.has_key(key):
            results[key] = d2[key]
    return results

def retrieve_list_of_pending(db2, *UUID):
    query = """
    select year, semester, course, project, id, setid, testid
    from submission s
      LEFT JOIN testSet ts USING(year, semester, course, project)
      LEFT JOIN testCase tc USING(setid)
      LEFT JOIN testResults r USING(id,testid)
    where course = 'SI204' AND """

    query = """
    select year, semester, course, project, id, setid, testid
    from submission s
      LEFT JOIN testSet ts USING(year, semester, course, project)
      LEFT JOIN testCase tc USING(setid)
      LEFT JOIN testResults r USING(id,testid)
    where year=19 AND recent AND """


    if UUID:
        UUID = UUID[0]
        ival = (UUID,)
        query = query + " s.UUID = %s AND "

    query = query + " r.testuuid IS NULL and testid IS NOT NULL ORDER BY setid, testid, id DESC"

    if UUID:
        col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival)
    else:
        col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query)

    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    db2.print_results(col, data)
    #sys.exit()
    return col, data

def retrieve_testcase(db2, testid):
    query = "SELECT ts.setid, tc.testid, tc.tc_language, tc.tc_compile_options, tc.revision as tcrevision, ts.year, ts.semester, ts.course, ts.project, ts.description AS setDesc, ts.filename as setFilename, ts.language, ts.compile_options, tc.rulename, tc.description, tc.points, tc.sourcefile, tc.stdin, tc.source, tc.outvalue, tc.arg, tc.envvar, tc.cond, tc.dfile FROM testCase tc LEFT JOIN testSet ts USING(setid) WHERE testid=%s"
    ival = (testid,)
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival,)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)
    return col, data

# Retrieve all files for a particular testset
def retrieve_files(db2, setid):
    query = "SELECT setid, filename, contents"
    query += "  FROM testFiles"
    query += "  WHERE setid = %s"
    ival = (setid,)
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)
    return data

# Retrieve all files from a particular submission
def retrieve_submission_filenames(db2, id):
    query = "SELECT s.filename, f.filename, f.ext, f.size"
    query += "  FROM submission s, submissionfiles f"
    query += "  WHERE s.id = f.id and s.id = %s"
    ival = (id,)
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)
    return data

# Find testResults without testcases
def retrieve_empty_testresults(db2):
    query = "select DISTINCT r.testid, c.testid from testResults r LEFT JOIN testCase c USING(testid) where c.testid is null"
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)
    return data

def delete_empty_testresults(db2, testid):
    query = "delete from testResults where testid = %s"
    ival = (testid,)
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival)
    #if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
    #    print 'ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)
    return data

# find results without testcases
def retrieve_empty_results(db2):
    query = "select distinct s.id, r.id, t.setid, c.testid, s.year, s.semester, s.course, s.project from submission s LEFT JOIN results r USING (id) LEFT JOIN testSet t USING (year, semester, course, project) LEFT JOIN testCase c USING(setid) WHERE r.id is not null and c.testid is null"
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)
    return data

def delete_empty_results(db2, delid):
    query = "delete from results where id = %s"
    ival = (delid,)
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)
    return data

# Insert the results of a compilation
def insert_results(db2, testid, status, compiled, gcc_err, gcc_out, gcc_file, lint):
    query =  "INSERT INTO results (id, status, compiled, gcc_err, gcc_out, gcc_file, lint)"
    query += "  VALUES (%s, %s, %s, %s, %s, %s, %s)"

    try:
        gcc_err = gcc_err.decode('utf-8', 'ignore')
        gcc_out = gcc_out.decode('utf-8', 'ignore')
        lint = lint.decode('utf-8', 'ignore')
    except:
        gcc_err = u' '.join(gcc_err).encode('utf-8', 'ignore')
        gcc_out = u' '.join(gcc_out).encode('utf-8', 'ignore')
        lint = u' '.join(lint).encode('utf-8', 'ignore')

    ival = (testid, status, compiled, gcc_err, gcc_out, gcc_file, lint,)
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'IR-RESULT-ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)

    query =  "INSERT INTO lint (id, status, compiled, gcc_err, gcc_out, gcc_file, lint)"
    query += "  VALUES (%s, %s, %s, %s, %s, %s, %s)"
    ival = (testid, status, compiled, gcc_err, gcc_out, gcc_file, lint,)
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'IR-LINT-ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)

    query =  "UPDATE results SET status=%s, compiled=%s, gcc_err=%s, gcc_out=%s, gcc_file=%s, lint=%s WHERE id=%s"
    ival = (status, compiled, gcc_err, gcc_out, gcc_file, lint, testid,)
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'UR-RESULTS-ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])

    return data

# Insert the results from a particular testcase/submission pair
def insert_test_results(db2, _id, testuuid, testid, testcase, chkfile, points, returnval, stime, stderr, stdout, student_file, _pass, revision):
    if (len(stdout) > 400000):
        stdout = stdout[:400000]
        print 'INSERT - SIZE OVERRIDE - STDOUT'
    if (len(stderr) > 8192):
        stderr = stderr[:8192]
        print 'INSERT - SIZE OVERRIDE - STDERR'

    try:
        stdout = stdout.decode('utf-8', 'ignore')
        stderr = stderr.decode('UTF-8', 'ignore')
    except:
        stdout = u' '.join(stdout).encode('utf-8', 'ignore')
        stderr = u' '.join(stderr).encode('utf-8', 'ignore')

    #stderr = stderr.decode(encoding='UTF-8', errors='ignore')
    query =  "INSERT INTO testResults (id, testuuid, testid, testcase, chkfile, points, returnval, stime, stderr, stdout, student_file, pass, revision)"
    query += "  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    ival = (_id, testuuid, testid, testcase, chkfile, points, returnval, stime, stderr, stdout, student_file, _pass, revision,)
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query, ival)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'INSERT-TR-ERR:'+str([str(lastrowx), str(cerr), str(cwarn), str(len(stdout)), str(len(stderr))])
     #db2.print_results(col, data)
    return data

# Update results table with scores
def update_results_table(db2):
    query = "UPDATE results"
    query += "  LEFT JOIN "
    query += "    (SELECT id, min(testid) as testid, SUM(points) as ppp"
    query += "       FROM testResults"
    query += "       GROUP BY id) AS xx "
    query += "    ON results.id = xx.id "
    query += "  INNER JOIN testCase USING(testid)"
    query += "  INNER JOIN (select setid, min(testid) as testid, sum(points) as availp from testCase group by setid) as zz"
    query += "    USING (setid)"
    query += "  SET results.status = CONCAT('Score: ', trim(TRAILING '.' FROM trim(TRAILING '0' FROM round(xx.ppp,3))), ' / ', trim(TRAILING '.' FROM trim(TRAILING '0' FROM round(zz.availp,3))))"
    #query += "  SET results.status = 'In Progress' "
    query += "  WHERE results.id != 21873 AND (results.status != 'Failed' OR xx.ppp > 0)"
    #print(str(query))
    debug('update_results_table(db2) - Running...')
    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'URT-ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)
    return data

# Update results table with scores
def update_results_table_maxscore(db2):
    query = "UPDATE results"
    query += "  LEFT JOIN "
    query += "    (SELECT id, min(testid) as testid, MAX(points) as ppp"
    query += "       FROM testResults"
    query += "       GROUP BY id) AS xx "
    query += "    ON results.id = xx.id "
    #query += "  LEFT JOIN testCase USING(testid)"
    #query += "  LEFT JOIN (select setid, min(testid) as testid, sum(points) as availp from testCase group by setid) as zz"
    #query += "    USING (setid)"
    query += "  SET results.maxpoints = xx.ppp"
    #query += "  WHERE results.status != 'Failed' OR xx.ppp > 0"

    debug('update_results_table_maxscore(db2) - Running...')

    col, data, lastrowx, cerr, cwarn = db2.query(db2.db, query)
    if cerr != '' or (cwarn != [] and str(cwarn) != 'None'):
        print 'URTM-ERR:'+str([str(lastrowx), str(cerr), str(cwarn)])
    #db2.print_results(col, data)
    return data


# Retrieve a specific file from a tgz
def extract_submission_file(tgz, filename):
    cmd = 'tar -xOf ./files/' + tgz + ' ' + filename
    stdout, stderr, rc, etime = runner.run(cmd, '')
    return stdout

# Create a directory builddir which is populated by the student source
# and any supporting files necessary.
def build_directory(db2, FILES, testcase, builddir, testfiledir):
    student_source = []
    os.mkdir(builddir, 0750)
    #print '**Building environment in '+builddir
    SFILES = retrieve_submission_filenames(db2, testcase['id'])
    # Version 1 File Layout Support (IN DB)
    # WAS PART 2
    for file in SFILES:
        filename = str(file[1])
        contents = extract_submission_file(file[0], file[1])
        student_source.append(contents)
        if string.find(filename, '/') != -1:
            dirpath = filename.rfind('/')
            dirpath = filename[:dirpath]
            try:
                os.makedirs(builddir+'/'+dirpath, 0755)
            except:
                pass
        try:
            fo = open(builddir+'/'+filename, 'w')
            for line in contents:
                fo.write(line)
            fo.close()
        except:
            pass
    # END Part 2
    # Was PART 1
    for file in FILES:
        filename = str(file[1])
        contents = file[2]
        #print '**Placing test file in directory (' + filename + ')'
        fo = open(builddir+'/'+filename, 'w')
        for line in contents:
            #print str([type(line)])
            if str(type(line)) == "<type 'unicode'>":
                fo.write(line.encode("UTF-8"))
            else:
                fo.write(line)
        fo.close()
    # - END PART 1
    # Version 2 File Layout Support (In filesys)
    # This is a really stupid way of copying files
    # - Recursively copy the contents of testfiledir into builddir
    if os.path.isdir(testfiledir):
        startdir = os.getcwd()
        os.chdir(testfiledir)
        cmd = '/bin/cp -Rp * '+builddir
        os.system(cmd)
        os.chdir(startdir)

    return student_source

# Remove a test directory
# VERY DANGEROUS
def destroy_directory(builddir):
    cmd = '/bin/rm -rf '+builddir
    print(cmd)
    stdout, stderr, rc, etime = runner.run(cmd, '')
    print('done')
    return stdout

# Provide debugging and itming
def debug(output):
    global DEBUG_LAST
    if DEBUG_START == DEBUG_LAST:
        ff = open('/tmp/runner.rs2','w')
    else:
        ff = open('/tmp/runner.rs2', 'a')
    ntime = time.time()
    dtime = ntime - DEBUG_LAST
    if dtime < 0.0001:
        dtime = 0.0
    print(string.ljust(str(ntime - DEBUG_START)[:8],10) + ' ' + string.ljust(str(dtime)[:8], 10) + ' ' + time.asctime(time.localtime(time.time())) + ' - ' + str(output))
    ff.write(string.ljust(str(ntime - DEBUG_START)[:8],10) + ' ' + string.ljust(str(dtime)[:8], 10) + ' ' + time.asctime(time.localtime(time.time())) + ' - ' + str(output)+'\n')
    ff.close()
    DEBUG_LAST = ntime

###########################################
# Test case checking

# superClean function from the original runner
# modified to accept strings that do not terminate with a \n \r
def superClean(stuff):
    stuff = str(stuff)
    results = []
    try:
        delim = {'\n':1, '\r':1}
        temp = ''
        for i in range(len(stuff)):
            thischar = stuff[i]
            #if delim.has_key(thischar):
            if thischar in delim:
                if temp != '':
                    if string.strip(temp) != '':
                        results.append(string.strip(temp))
                temp = ''
            else:
                temp = temp + thischar
    except:
        results = [str(uuid.uuid4())]
    if temp != '':
        if string.strip(temp) != '':
            results.append(string.strip(temp))
    return results

def superCleanToString(stuff):
    stuff = str(stuff)
    results = []
    newresults = ''
    try:
        delim = {'\n':1, '\r':1}
        temp = ''
        for i in range(len(stuff)):
            thischar = stuff[i]
            #if delim.has_key(thischar):
            if thischar in delim:
                if temp != '':
                    if string.strip(temp) != '':
                        results.append(string.strip(temp))
                        newresults = newresults + str(string.strip(temp))
                temp = ''
            else:
                temp = temp + thischar
    except:
        results = [str(uuid.uuid4())]
    if temp != '':
        if string.strip(temp) != '':
            results.append(string.strip(temp))
            newresults = newresults + str(string.strip(temp))
    return newresults

# assuming array input
def superWhiteSpace(stuff):
    if type(stuff) is str:
        stuff = [stuff]
    results = ''
    for line in stuff:
        line = str(line)
        line = line.replace('\t', ' ')
        line = line.replace('\r', ' ')
        line = line.replace('\n', ' ')
        # while line.find('  ') != -1:
        #     line = line.replace('  ', ' ')
        #     line = line.strip()
        while line.find(' ') != -1:
            line = line.replace(' ', '')
            line = line.strip()
        if line != '':
            results = results + line
    return results

# Check the results and see if the test was successful
def check_test(stdin, source, sourcefile, cond, outvalue, created_file, created_exists, student_source, stdout, stderr, returnval, stime, infinite):
    # set default check variables
    chk_student = stdout
    chk_testcase = outvalue

    # change inputs
    if source == 'Return Code':
        chk_student = returnval
    elif source == 'Infinite Loop':
        chk_student = infinite
    elif source == 'Student source code':
        chk_student = student_source
    elif source == 'Created File':
        chk_student = created_file

    # check to see if this is the simple "compiles" case
    if cond == 'compiles':
        return True

    if cond == 'manual review as html':
        return True

    # check for equality
    if cond == 'is exactly':
        chk1 = (chk_student == chk_testcase)
        if chk1:
            return True
        try:
            chk2 = (string.strip(chk_student) == string.strip(chk_testcase))
            if chk2:
                return True
        except:
            pass
        if superClean(chk_student) == superClean(chk_testcase):
            return True
        return False

    #JK-whitespace#
    #superWhiteSpace(stuff)

    # check for equality
    if cond == 'whitespace':
        chk1 = (chk_student == chk_testcase)
        if chk1:
            return True
        try:
            chk2 = (string.strip(chk_student) == string.strip(chk_testcase))
            if chk2:
                return True
        except:
            pass
        if superClean(chk_student) == superClean(chk_testcase):
            return True
        if superWhiteSpace(chk_student) == superWhiteSpace(chk_testcase):
            return True
        return False

    # check via the various conditions
    if cond == 'has':
        results = string.find(str(chk_student), chk_testcase)
        if results != -1:
            return True
        results = string.find(superCleanToString(chk_student), superCleanToString(chk_testcase))
        return results != -1
    if cond == 'does not have':
        results = string.find(str(chk_student), chk_testcase)
        return results == -1
    if cond == 'exists':
        if source == 'Student source code':
            return chk_student != []
        if source == 'Created File':
            return created_exists
        if source == 'Output':
            return chk_student != []

    # truth checking
    if cond == 'is true':
        isvalid = (str(chk_student) == '1' or chk_student == True)
        return isvalid
    if cond == 'is false':
        isvalid = (str(chk_student) == '1' or chk_student == True)
        return not isvalid

    # numeric <, <=, >, >=
    if str(type(chk_student)) == "<type 'str'>":
        chk_student = eval(chk_student)
    if str(type(chk_testcase)) == "<type 'str'>":
        chk_testcase = eval(chk_testcase)

    if cond == 'greater than':
        return chk_student > chk_testcase
    if cond == 'less than':
        return chk_student < chk_testcase
    if cond == 'greater or equal':
        return chk_student >= chk_testcase
    if cond == 'less or equal':
        return chk_student <= chk_testcase

    return -1   # Return (did not run any checks)

###########################################
# Test Runner
def run_testcase(db2, FILES, BUILD_DIR, testcase):
    try:
        testfilelocation = './test_files/' + str(testcase['year']) + '/' + str(testcase['semester']) + '/' + str(testcase['course']) + '/' + str(testcase['project'])
        testuuid = str(uuid.uuid4())
        print('building directory')
        builddir = BUILD_DIR+'/'+testuuid
        print('done copy')
        testid = testcase['id']
        COMPILE_OPTIONS = testcase['compile_options']
        if testcase['tc_compile_options'] != None:
            COMPILE_OPTIONS = testcase['tc_compile_options']

        # Build the temporary working environment
        print '    Building environment in '+builddir
        student_source = build_directory(db2, FILES, testcase, builddir, testfilelocation)
        print '    Initiating Compilers'

        # Determine which language module to use
        lang = testcase['language']
        if testcase['tc_language'] != None:
            lang = testcase['tc_language']
        mylang = imp.load_source('happy','./modules/'+lang+'.py')
        print '      Using '+mylang.language+' Version '+mylang.version

        # Move to the build directory
        os.chdir(builddir)

        # Compile the software
        gcc_out, gcc_err, rc, etime, gcc_file, compiled, compiled_filename, lint = mylang.compile(builddir, testuuid, testcase, FILES, COMPILE_OPTIONS)

        # Fixing Odd issue with bad characters in gcc_err (r32)
        gcc_err = gcc_err.decode(encoding='UTF-8', errors='ignore')
        if (len(gcc_err) > 8192):
            gcc_err = gcc_err[:8192]

        db_status = 'Failed'
        if compiled:
            db_status = 'Compiled'

        # Add the compilation results to the database
        insert_results(db2, testid, db_status, compiled, gcc_err, gcc_out, gcc_file, lint)

        # If it successfully compiled, run tests.
        if compiled:
            # Run the specific test
            print '    Running specific test case, conditions:'
            print '      - set          : '+str(testcase['year'])+ ' '+str(testcase['semester'])+ ' '+str(testcase['course'])+ ' '+str(testcase['project'])+ ' '
            print '      - id           : '+str(testcase['id'])
            print '      - testuuid     : '+testuuid
            print '      - testid       : '+str(testcase['testid'])
            print '      - testcase     : '+testcase['rulename']
            print '      - student_file : '+gcc_file
            print '      - revision     : '+str(testcase['tcrevision'])
            print '      - source       : '+str(testcase['source'])
            print '      - sourcefile   : '+str(testcase['sourcefile'])
            print '      - cond         : '+str(testcase['cond'])
            print '      - outvalue     : LEN:'+str(len(testcase['outvalue'].encode('UTF-8')))
            print '      - points       : '+str(testcase['points'])
            print '      - arg          : '+str(testcase['arg'])
            print '      - envvar       : '+str(testcase['envvar'])
            print '      - dfile        : '+str(testcase['dfile'])
            print '      - stdin        : LEN:'+str(len(str(testcase['stdin'])))

            # Flush the buffer so that results can be seen
            sys.stdout.flush()

            # Run testcase against particular language subsystem module
            if testcase['cond'] == 'compiles':
                # if it is just checking for compiled - then it has already succeeded
                stdout, stderr, returnval, stime, infinite = ("","",7777,0.01,0)
            else:
                print '      Running code now, standby...'
                try:
                    stdout, stderr, returnval, stime, infinite = mylang.run_testcase(builddir, gcc_file, compiled_filename, str(testcase['stdin']), testcase['arg'], testcase['envvar'])
                except:
                    time.sleep(0.3)
                    stdout, stderr, returnval, stime, infinite = mylang.run_testcase(builddir, gcc_file, compiled_filename, str(testcase['stdin']), testcase['arg'], testcase['envvar'])

            # Display the results of the test
            print '      * returnval    : '+str(returnval)
            print '      * stime        : '+str(stime)
            print '      * infinite     : '+str(infinite)
            print '      * stderr       : LEN:'+str(len(str(stderr)))
            print '      * stdout       : LEN:'+str(len(str(stdout)))

            # If looking for a createdfile
            source = testcase['source']
            sourcefile = testcase['sourcefile']
            created_file = ''
            created_exists = 0
            if source == 'Created File' and sourcefile != '' and sourcefile != None:
                try:
                    created_file = open(builddir+'/'+sourcefile).readlines()
                    created_exists = 1
                    created_file = "".join(created_file)
                except:
                    created_file = ''

            print '      * Created File : LEN:'+str(len(str(created_file)))+' Lines'

            # Validate Test Case
            print '      Validating output against testcase parameters.'
            passfail = check_test(testcase['stdin'].encode('UTF-8'), str(testcase['source']), str(testcase['sourcefile']), str(testcase['cond']), testcase['outvalue'].encode('UTF-8'), created_file, created_exists, student_source, stdout, stderr, returnval, stime, infinite)

            # Calculate points and process pass / fail results
            db_points = 0
            db_chkfile = created_file
            if passfail:
                db_pass = 'pass'
                try:
                    if testcase['points'] >= 0:
                        db_points = testcase['points']
                except:
                    pass
            else:
                db_pass = 'fail'

            # Show the results of the pass/fail and points determination
            print '      > points       : '+str(db_points)
            print '      > pass         : '+db_pass

            # Add the test result to the database
            insert_test_results(db2, testcase['id'], testuuid, testcase['testid'], testcase['rulename'], db_chkfile, db_points, returnval, stime, stderr, stdout, gcc_file, db_pass, testcase['tcrevision'])

        else:
            # Their Submission did not compile, mark as failure.
            db_pass = 'fail'
            db_points = 0
            db_chkfile = ''
            db_returnval = 8888
            db_stime = 0
            db_stderr = gcc_err
            db_stdout = 'Compile Failed'
            print '      Compile FAILED'

            # Add the test result to the database
            insert_test_results(db2, testcase['id'], testuuid, testcase['testid'], testcase['rulename'], db_chkfile, db_points, db_returnval, db_stime, db_stderr, db_stdout, gcc_file, db_pass, testcase['tcrevision'])

        # Delete the environment
        print '    Destroying environment'
        destroy_directory(builddir)

        # Flush the buffer so that results can be seen
        sys.stdout.flush()
    except Exception as e:
        #Capture and Display all errors
        print "*********************************************************"
        print "CRITICAL ERROR WITHIN SUBMISSION RUNNER - TEST CASE ABORT"
        print ''
        print "TEST: "
        for key in testcase.keys():
            print '  ',string.ljust(key,11) + ' = ' + str([testcase[key]])[1:-1]
        print ''
        print "ERROR: " + str(e)
        traceback.print_exc()
        print "*********************************************************"
        sys.stdout.flush()
        print '    Destroying environment'
        destroy_directory(builddir)


###########################################################################################
# Build BUILD_DIR if not exists
try:
    os.makedirs(BUILD_DIR, 0755)
except:
    pass

###########################################################################################
# Perform test cleaning
empty_testresults = retrieve_empty_testresults(db2)
for deletable in empty_testresults:
    print 'Deleting empty testResults -> ' + str([deletable])
    delete_empty_testresults(db2, deletable[0])

empty_results = retrieve_empty_results(db2)
for deletable in empty_results:
    print 'Deleting empty results -> ' + str([deletable])
    delete_empty_results(db2, deletable[0])

###########################################################################################
# Determine what languages this system is capable of compiling against
#languages = {}
#for lang in os.listdir('../languages'):
#    if string.find(lang, '.py') != -1:
#        if string.splitfields(lang, '.py')[1] == '':
#            try:
#                mylang = imp.load_source('happy','../languages/'+lang)
#                newlang = string.splitfields(lang, '.py')[0]
#                languages[newlang] = [lang, mylang.title, mylang.version, mylang.language, mylang.extensions, mylang.options]
#            except:
#                languages[lang] = []
#                del(languages[lang])
#                print 'INVALID LANGUAGE FILE: '+str(lang)

###########################################################################################
# Run the Program!
_curdir = os.getcwd()
print 'Submit Runner Version '+str(VERSION)+ ' '+ time.asctime(time.localtime(time.time()))
debug('Submit Runner Version '+str(VERSION)+ ' Online...')

# Did we try to get a specific UUID or file from the command line?
if len(sys.argv) > 1:
    UUID = sys.argv[1]
    if string.find(str(UUID), '_') != -1:
        UUID = string.splitfields(UUID, '_')[-5]
    debug('Checking for input with specific UUID='+str(UUID))
    # Retrieve unprocessed submissions by testcase
    columns, data = retrieve_list_of_pending(db2, UUID)
else:
    # Retrieve unprocessed submissions by testcase
    columns, data = retrieve_list_of_pending(db2)

# Convert DB results to a traditional python {}
PROC_ID = {}
PENDING = col_data_to_dict(columns, data)
PENDING = group_data('setid', PENDING)
debug('PENDING = retrieve_list_of_pending(db2) - Complete...')

# Process specific information for a specific project (testset setid)
for setid in PENDING.keys():
    # PENDING[setid][0] = {'project': u'proj02', 'course': u'IC210', 'semester': u'FALL', 'testid': 237, 'year': u'16', 'setid': 155, 'id': 6019}
    # Retrieve any Files that are part of this testSet
    print 'Getting Files'
    FILES = retrieve_files(db2, setid)
    #debug('FILES = retrieve_files(db2, setid)')
    print 'Processing ' + str(PENDING[setid][0]['year']) + ' ' + str(PENDING[setid][0]['semester']) + ' ' + str(PENDING[setid][0]['course']) + ' ' + str(PENDING[setid][0]['project'])
    print '  Test Package has '+ str(len(FILES)) + ' associated files.'
    #for fileinfo in FILES:
    #    print '    ' + string.ljust(str(fileinfo[1]),30) + ' ' + str(len(fileinfo[2]))
    TESTS = group_data('testid', PENDING[setid])
    print '  Loaded ' + str(len(TESTS.keys())) + ' pending tests to process.'
    for testid in TESTS.keys():
        #print str([TESTS[testid]])
        print 'Getting testcases'
        columns, data = retrieve_testcase(db2, testid)
        print 'Converting testcases'
        testcase = col_data_to_dict(columns, data)[0]
        for submission in TESTS[testid]:
            print 'os.chdir()'
            os.chdir(_curdir)
            PROC_ID[submission['id']] = 1
            print 'run_testcase()'
            run_testcase(db2, FILES, BUILD_DIR, combine_dict(testcase, submission))

# Update results based off of test cases ran.
if PENDING != {}:
        debug('Package Processing Complete...')
        ###########################################
        update_results_table(db2)
        update_results_table_maxscore(db2)
        debug('update_results_table(db2) - Complete...')

debug("Processed "+str(PROC_ID.keys()))
