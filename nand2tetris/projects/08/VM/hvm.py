#!C:\Program Files (x86)\Python36-32\python.exe
"""
hvm.py -- VM Translator, Part II
"""

import sys
import os
from hvmCommands import *
from hvmParser import *
from hvmCodeWriter import *

def Process(sourceFile, codeWriter):
    global sysinit, debug
    print('Processing ' + sourceFile)
    if debug:
        parser = Parser(sourceFile, codeWriter)
    else:
        parser = Parser(sourceFile)
    codeWriter.SetFileName(sourceFile)

    while parser.Advance():
        commandType = parser.CommandType()
        if commandType == C_ARITHMETIC:
            codeWriter.WriteArithmetic(parser.Arg1())
        elif commandType in (C_PUSH, C_POP):
            codeWriter.WritePushPop(commandType, parser.Arg1(), parser.Arg2())
        elif commandType == C_LABEL:
            codeWriter.WriteLabel(parser.Arg1())
        elif commandType == C_GOTO:
            codeWriter.WriteGoto(parser.Arg1())
        elif commandType == C_IF:
            codeWriter.WriteIf(parser.Arg1())
        elif commandType == C_FUNCTION:
            codeWriter.WriteFunction(parser.Arg1(), parser.Arg2())
        elif commandType == C_RETURN:
            codeWriter.WriteReturn()
        elif commandType == C_CALL:
            codeWriter.WriteCall(parser.Arg1(), parser.Arg2())


def Usage():
    print('usage: hvm [options] sourceFile.vm')
    print('    sourceFile may be a directory in which case all vm files in')
    print('    the directory will be processed to sourceFile.asm')
    print()
    print('    -d option writes VM commands as comments in .asm file.')
    print('    -n option does not write Sys.init call in the bootstrap.')
    sys.exit(-1)


def main():
    global sysinit, debug
    sysinit = True
    debug = True
    while True:
        if len(sys.argv) >= 2:
            if sys.argv[1] == '-n':
                sysinit = False
                del (sys.argv[1])
                continue
            if sys.argv[1] == '-d':
                debug = True
                del (sys.argv[1])
                continue
        break

    if len(sys.argv) != 2:
        Usage()

    sourceName = sys.argv[1]
    if os.path.isdir(sourceName):
        dirName = sourceName
    else:
        dirName = os.path.split(sourceName)[0]
    outName = os.path.split(sourceName)[1]
    outName = os.path.splitext(outName)[0] + os.path.extsep + 'asm'
    if len(dirName) > 0:
        outName = dirName + os.path.sep + outName
    codeWriter = CodeWriter(outName)
    codeWriter.Debug(debug)
    codeWriter.WriteInit(sysinit)

    if os.path.isdir(sourceName):
        # process all .vm files in dir
        dirName = sourceName
        print('Processing directory ' + dirName)
        for sourceName in os.listdir(dirName):
            if os.path.splitext(sourceName)[1].lower() == os.path.extsep + 'vm':
                Process(dirName + os.path.sep + sourceName, codeWriter)
    else:
        # process single .vm file
        Process(sourceName, codeWriter)

    codeWriter.Close()



main()
