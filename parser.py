from __future__ import print_function
from __future__ import division

import glob, os
import re
import sys
import getopt
import progressbar
from time import sleep
from db_helper import Database

FILE_DIR = "/home/harry/workspace/Controller/Output/"

rx_dict = {
    'instruction': re.compile(r'instruction: (?P<instruction>.{11})'),
    'trap': re.compile(r'instruction: .{13}(?P<trap>.{4})')
}


def _parse_line(line):
    keys = []
    matches = []
    for key, rx in rx_dict.items():
        match = rx.search(line)
        if match:
            keys.append(key)
            matches.append(match)

    return keys, matches


def parse_file(filepath):
    total_lines = sum((1 for i in open(filepath, 'rb')))
    bar = progressbar.ProgressBar(maxval=total_lines,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    with open(filepath, 'r') as file_object:
        with Database() as db:
            count = 0
            line = file_object.readline()
            while line:
                keys, matches = _parse_line(line)

                if keys.__contains__('instruction') and not keys.__contains__('trap'):
                    instruction = matches[keys.index('instruction')].group('instruction')
                    trap = 'v'
                    db.save_instruction(instruction, trap, filepath, count)
                elif keys.__contains__('instruction') and keys.__contains__('trap'):
                    instruction = matches[keys.index('instruction')].group('instruction')
                    trap = matches[keys.index('trap')].group('trap')
                    db.save_instruction(instruction, trap, filepath, count)

                count = count + 1
                bar.update(count)
                line = file_object.readline()

            bar.finish()


def reset_db():
    with Database() as db:
        db.reset()


if __name__ == '__main__':
    os.chdir(FILE_DIR)
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "r", ["reset"])
    except getopt.GetoptError:
        print('Usage: parser.py -r(optional)')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-r", "--reset"):
            reset_db()

    for filename in glob.glob("*.txt"):
        print("Parsing file '{0}'".format(filename))
        parse_file(filename)
        print("File '{0}' parsed!\n".format(filename))
