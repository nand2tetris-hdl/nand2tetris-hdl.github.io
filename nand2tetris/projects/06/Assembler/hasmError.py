# Copyright (C) 2011 Mark Armbrust.  Permission granted for educational use.
"""
hasmError.py -- Error handling for Hack Assembler

See "The Elements of Computing Systems", by Noam Nisan and Shimon Schocken
"""

import sys


def Error(message, lineNumber=0, line=''):
    """
    Prints an error message and continues.
    """
    if lineNumber != 0:
        print('Line %d: %s' % (lineNumber, line))
        print('     '+message)
    else:
        print(message)
    print('')
    

def FatalError(message, lineNumber=0, line=''):
    """
    Prints an error message and exits.
    """
    Error(message, lineNumber, line)
    sys.exit(-1)

