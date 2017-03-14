import re
import os
import sys


def write_line(a_file, a_line):
    if not os.path.exists(a_file):
        open(a_file, 'w').close()
    with open(a_file, 'a') as out:
        out.write(a_line)

mult_dir = 'results' + os.path.sep + 'mult' + os.path.sep
fail_dir = 'results' + os.path.sep + 'fail' + os.path.sep
four_dir = 'results' + os.path.sep + '404' + os.path.sep
pass_dir = 'results' + os.path.sep + 'passed' + os.path.sep
trace_dir = 'results' + os.path.sep + 'traced' + os.path.sep
dirs = ['results', mult_dir, fail_dir, four_dir, pass_dir, trace_dir]
for path in dirs:
    if not os.path.exists(path):
        os.makedirs(path)

lines = sys.stdin.readlines()
dom_pattern = re.compile('(.*?\.com)(.*?)')
mult_pattern = re.compile('MULT')
four_pattern = re.compile('\(404\)')
fail_pattern = re.compile('FAIL')
pass_pattern = re.compile('PASS')
trace_pattern = re.compile('TRACE')

for line in lines:
    mult = mult_pattern.search(line)
    four = four_pattern.search(line)
    fail = fail_pattern.search(line)
    passed = pass_pattern.search(line)
    traced = trace_pattern.search(line)

    match = dom_pattern.search(line)
    if match:
        domain = match.group(1).replace("http://", '').replace("https://", '')
        file_name = ''
        if mult:
            file_name = mult_dir + domain + '.csv'
            write_line(file_name, line)
        if four:
            file_name = four_dir + domain + '.csv'
            write_line(file_name, line)
        if traced:
            file_name = trace_dir + domain + '.csv'
        if fail:
            file_name = fail_dir + domain + '.csv'
        if passed:
            file_name = pass_dir + domain + '.csv'
        if file_name.strip():
            write_line(file_name, line)
