#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Borrowed Respectably from the Wifite Project :) 

import sys, logging, re

logging.basicConfig(filename='rootsec.latest.log',
                            filemode='w',
                            format='%(asctime)s : %(message)s',
			    datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

class Color(object):
    ''' Helper object for easily printing colored text to the terminal. '''

    # Basic console colors
    colors = {
        'W' : '\033[0m',  # white (normal)
        'R' : '\033[31m', # red
        'G' : '\033[32m', # green
        'O' : '\033[33m', # orange
        'B' : '\033[34m', # blue
        'P' : '\033[35m', # purple
        'C' : '\033[36m', # cyan
        'GR': '\033[37m', # gray
        'D' : '\033[2m',   # dims current color. {W} resets.
	'LR': '\033[91m'
    }

    # Helper string replacements
    replacements = {
        '{+}': ' {D}{G}[{W}{G}+{D}{G}]{W}',
        '{!}': ' {O}[{R}!{O}]{W}',
        '{?}': ' {B}[{C}?{B}]{W}',
	'{-}': ' {LR}[{D}-{W}{LR}]'
    }

    last_sameline_length = 0

    @staticmethod
    def writenolog(text):
        '''
        Prints text using colored format on same line.
        Example:
            Color.p('{R}This text is red. {W} This text is white')
        '''
        sys.stdout.write(Color.s(text))
        sys.stdout.flush()
        if '\r' in text:
            text = text[text.rfind('\r')+1:]
            Color.last_sameline_length = len(text)
        else:
            Color.last_sameline_length += len(text)

    @staticmethod
    def println(text):
        '''
        Prints text using colored format on same line.
        Example:
            Color.p('{R}This text is red. {W} This text is white')
        '''
        Color.log(text)
        sys.stdout.write(Color.s(text))
        sys.stdout.flush()
        if '\r' in text:
            text = text[text.rfind('\r')+1:]
            Color.last_sameline_length = len(text)
        else:
            Color.last_sameline_length += len(text)

    @staticmethod
    def printlnnolog(text):
        '''
        Prints text using colored format on same line.
        Example:
            Color.p('{R}This text is red. {W} This text is white')
        '''
        sys.stdout.write(Color.s(text))
        sys.stdout.flush()
        if '\r' in text:
            text = text[text.rfind('\r')+1:]
            Color.last_sameline_length = len(text)
        else:
            Color.last_sameline_length += len(text)

    @staticmethod
    def write(text):
        '''Prints text using colored format with trailing new line.'''
        forlog = Color.strip(text)
        logging.info(forlog)
        Color.println('%s\n' % text)
        Color.last_sameline_length = 0

    @staticmethod
    def pe(text):
        '''Prints text using colored format with leading and trailing new line to STDERR.'''
        sys.stderr.write(Color.s('%s\n' % text))
        Color.last_sameline_length = 0

    @staticmethod
    def s(text):
        ''' Returns colored string '''
        output = text
        for (key,value) in Color.replacements.items():
            output = output.replace(key, value)
        for (key,value) in Color.colors.items():
            output = output.replace('{%s}' % key, value)
        return output

    @staticmethod
    def strip(text):
        return re.sub(r'({[A-Z]})', '', text)

    @staticmethod
    def clear_line():
        spaces = ' ' * Color.last_sameline_length
        sys.stdout.write('\r%s\r' % spaces)
        sys.stdout.flush()
        Color.last_sameline_length = 0

    @staticmethod
    def clear_entire_line():
        import os
        (rows, columns) = os.popen('stty size', 'r').read().split()
        Color.println('\r' + (' ' * int(columns)) + '\r')

    @staticmethod
    def pexception(exception):
        '''Prints an exception. Includes stack trace if necessary.'''
        Color.write('\n{!} {R}Error: {O}%s' % str(exception))

        # Don't dump trace for the "no targets found" case.
        if 'No targets found' in str(exception):
            return

        from ..config import Configuration
        if Configuration.verbose > 0 or Configuration.print_stack_traces:
            Color.println('\n{!} {O}Full stack trace below')
            from traceback import format_exc
            Color.write('\n{!}    ')
            err = format_exc().strip()
            err = err.replace('\n', '\n{!} {C}   ')
            err = err.replace('  File', '{W}File')
            err = err.replace('  Exception: ', '{R}Exception: {O}')
            Color.println(err)

    @staticmethod
    def writetoline(text):
        Color.clear_entire_line()
        Color.println(text)

    def log(text):
        logging.info(text)
if __name__ == '__main__':
    Color.write('{R}Testing{G}One{C}Two{P}Three{W}Done')
    Color.write('{C}Testing{P}String{W}')
    Color.write('{+} Good line')
    Color.write('{!} Danger')

