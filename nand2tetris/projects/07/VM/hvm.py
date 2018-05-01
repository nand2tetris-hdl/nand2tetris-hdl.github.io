#!C:\Program Files (x86)\Python36-32\python.exe
"""
hvm.py -- VM Translator, Part I
"""

import sys
import os
from hvmCommands import *
from hvmParser import *
from hvmCodeWriter import *

def Process(sourceFile, codeWriter):
    print('Processing ' + sourceFile)
    parser = Parser(sourceFile)
    codeWriter.SetFileName(sourceFile)
    
    while parser.Advance():
        commandType = parser.CommandType()
        if commandType == C_ARITHMETIC:
            codeWriter.WriteArithmetic(parser.Arg1())
        elif commandType in (C_PUSH, C_POP):
            codeWriter.WritePushPop(commandType, parser.Arg1(), parser.Arg2())
    
def main():
    if len(sys.argv) != 2:
        print('usage: hvm sourceFile.vm')
        print('    sourceFile may be a directory in which case all')
        print('    vm files in the directory will be processed to')
        print('    sourceFile.asm')
        return

    sourceName = sys.argv[1]


    if os.path.isdir(sourceName):
        # process all .vm files in dir
        dirName = sourceName
        print('Processing directory ' + dirName)
        outName = os.path.split(sourceName)[1] + os.path.extsep + 'asm'
        outName = dirName + os.path.sep + outName
        codeWriter = CodeWriter(outName)
        for sourceName in os.listdir(dirName):
            if os.path.splitext(sourceName)[1].lower() == os.path.extsep + 'vm':
                Process(dirName + os.path.sep + sourceName, codeWriter)
    else:
        # process single .vm file
        outName = os.path.splitext(sourceName)[0] + os.path.sep + 'asm'
        codeWriter = CodeWriter(outName)
        Process(sourceName, codeWriter)

    codeWriter.Close()

main()
