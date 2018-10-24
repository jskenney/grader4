#!/usr/bin/python

# db2 version 2.01
#  Version 2.01 - UTF-8 Support

# Configuration settings for database connection!
dbuser = 'submit'
dbpass = 's!0b3tER'
dbhost = '10.1.83.45'
dbname = 'submit'

# Load Primary Libraries
import sys
sys.dont_write_bytecode = True      # Prevents the creation of .pyc files - which appear broken on zee
import string

# Establish network connection
try:
    import mysql.connector as dblink
    from mysql.connector.errors import Error
    db = dblink.connect(user=dbuser, password=dbpass, host=dbhost, database=dbname, charset='utf8', collation='utf8_general_ci', use_unicode=True)
    try:
        db.autocommit(True)         # Different version of connector handle
    except:                         # the autocommit portion differently
        db.autocommit = True
    mode = "connector"
except:
    import MySQLdb as dblink
    db = dblink.connect(dbhost, dbuser, dbpass, dbname)
    try:
        db.autocommit(True)
    except:
        db.autocommit = True
    mode = "mysqldb"

# Let there be UTF-8
if mode == "mysqldb":
    db.query("set character_set_client='utf8'")
    db.query("set character_set_results='utf8'")
    db.query("set collation_connection='utf8_general_ci'")

# Debug Query - Provide loud errors
def query_debug(db, sql, *prepare):
    if prepare:
        col, data, lastrowx, cerr, cwarn = query(db, sql, prepare[0])
    else:
        col, data, lastrowx, cerr, cwarn = query(db, sql)
    if cerr != '' or cwarn != None:
        print('---------------------------------------------------------------')
        print('SQL ERROR FOR THE FOLLOWING SQL STATEMENT')
        print(sql)
        if cerr != '':
            print("ERROR:",cerr)
        if cwarn != None:
            print("WARNING:", cwarn)
        print('---------------------------------------------------------------')
    return col, data, lastrowx, cerr, cwarn

# Query the database
def query(db, sql, *prepare):
    db.get_warnings = True
    cursor = db.cursor()
    error = ""

    try:
        if prepare:
            cursor.execute(sql, prepare[0])
        else:
            cursor.execute(sql)
        #db.commit()        # Necessary if not autocommit
    except dblink.Error as e:
        error = str(e)      # DB will prevent issue
        #db.rollback()      # Necessary if not autocommit.

    try:
        warning = cursor.fetchwarnings()
    except:
        warning = cursor.messages

    lastrow = cursor.lastrowid
    columns = cursor.description

    try:                    # Check for no results due to an error in SQL
        data = cursor.fetchall()
    except:
        data = []
        columns = []

    cursor.close()

    return columns, data, lastrow, error, warning

def row_to_dict(columns, data):
    results = {}
    for column in columns:
        column = column[0]
        results[column] = ''
    for line in data:
        for i in range(len(columns)):
            item = line[i]
            results[columns[i][0]] = str(item)
    return results

def rows_to_dict(columns, data):
    results = []
    for line in data:
        this_line = {}
        for i in range(len(columns)):
            item = line[i]
            this_line[columns[i][0]] = str(item)
        results.append(this_line)
    return results

def get_value(columns, data, column, *default):
    results = ''
    if default:
        results = default
    if len(data) == 0:
        return results
    for row in data:
        for i in range(len(row)):
            if columns[i][0] == column:
                if str(row[i]) != '':
                    return str(row[i])
    return results

def clean_columns(columns):
    results = []
    for col in columns:
        results.append(col[0])
    return results

def trim(columns, data, chkcolumns):
    results = []
    for row in data:
        toprint = []
        for col in chkcolumns:
            for i in range(len(columns)):
                if col == columns[i][0]:
                    toprint.append(row[i])
        results.append(toprint)
    return chkcolumns, results

def print_header_dash(column_names, column_size):
    results = '+'
    for i in range(len(column_names)):
        col = column_names[i]
        size= column_size[col]
        for ii in range(size+2):
            results = results + '-'
        results = results + '+'
    results = results[:-1] + '+'
    print(results)

def print_row(column_names, column_size, row):
    results = ''
    for i in range(len(column_names)):
        col = column_names[i]
        size= column_size[col]
        #results = results + '| ' + string.ljust(string.strip(str(row[i])), size) + ' '
        results = results + '| ' + str(row[i]).strip().ljust(size) + ' '
    results = results + '|'
    print(results)

def print_results(columns, data, *html):
    if columns != [] and data != []:
        column_names = []
        column_size = {}
        if html:
            print ('<pre>')
        for col in columns:
            col = col[0]
            column_names.append(col)
            column_size[col] = len(col)
        for row in data:
            for i in range(len(columns)):
                col = column_names[i]
                if len(str(row[i])) > column_size[col]:
                    column_size[col] = len(str(row[i]))
        print_header_dash(column_names, column_size)
        print_row(column_names, column_size, column_names)
        print_header_dash(column_names, column_size)
        for row in data:
            print_row(column_names, column_size, row)
        print_header_dash(column_names, column_size)
        if html:
            print ('</pre>')

def print_results_bycols(columns, data, chkcolumns, *html):
    if columns != [] and data != []:
        column_names = []
        column_size = {}
        if html:
            print ('<pre>')
        for col in columns:
            col = col[0]
            column_names.append(col)
            column_size[col] = len(col)
        for row in data:
            for i in range(len(columns)):
                col = column_names[i]
                if len(string.strip(str(row[i]))) > column_size[col]:
                    column_size[col] = len(str(row[i]))
        print_header_dash(chkcolumns, column_size)
        print_row(chkcolumns, column_size, chkcolumns)
        print_header_dash(chkcolumns, column_size)
        for row in data:
            toprint = []
            for col in chkcolumns:
                for i in range(len(columns)):
                    if col == columns[i][0]:
                        toprint.append(row[i])
            print_row(chkcolumns, column_size, toprint)
        print_header_dash(chkcolumns, column_size)
        if html:
            print ('</pre>')

#col, data, lastrow, error, warnings = query(db, "select * from session")
