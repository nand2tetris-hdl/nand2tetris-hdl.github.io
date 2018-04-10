#!C:\Program Files (x86)\Python36-32\python.exe

# Copyright (C) 2011 Mark Armbrust.  Permission granted for educational use.
"""
hasm.py -- Hack computer assembler

See "The Elements of Computing Systems", by Noam Nisan and Shimon Schocken
"""
import os
import sys

from hasmCode import *
from hasmError import *
from hasmParser import *
from hasmSymbols import *


def Pass1(sourceFile):
    global symbolTable, address
    parser = Parser(sourceFile)

    while parser.Advance():
        commandType = parser.CommandType()
        if commandType == NO_COMMAND:
            pass
        elif commandType in (A_COMMAND, C_COMMAND):
            address += 1
        elif commandType == L_COMMAND:
            symbol = parser.Symbol()
            if symbolTable.Contains(symbol):
                Error('Multiple definitions for symbol ' + symbol,
                      parser.LineNo(), parser.Line())
            elif not symbolTable.AddEntry(symbol, address):
                Error('Invalid symbol name ' + symbol,
                      parser.LineNo(), parser.Line())


def Pass2(sourceFile):
    global outFile
    global symbolTable, address, ramAddress
    parser = Parser(sourceFile)
    coder = Code()

    while parser.HasMoreCommands():
        parser.Advance()
        commandType = parser.CommandType()

        if commandType == NO_COMMAND:
            pass

        elif commandType == A_COMMAND:
            symbol = parser.Symbol()
            try:
                value = int(symbol)
            except:
                if symbolTable.Contains(symbol):
                    value = symbolTable.GetAddress(symbol)
                elif symbolTable.AddEntry(symbol, ramAddress):
                    value = ramAddress
                    ramAddress += 1
                else:
                    Error('Invalid symbol name ' + symbol,
                          parser.LineNo(), parser.Line())
                    value = 0x7FFF
            code = code & 0x7FFF
            outFile.write(Int2Bin(code) + '\n')

        elif commandType == C_COMMAND:
            dest = coder.Dest(parser.Dest())
            if dest == None:
               Error('unknown destination field: ' + parser.Dest(),
                     parser.LineNo(), parser.Line())
               dest='???'
            comp = coder.Comp(parser.Comp())
            if comp == None:
                print (parser.Comp())
                Error('unknown computation field: ' + parser.Comp(),
                    parser.LineNo(), parser.Line())
                comp='???????'
            jump = coder.Jump(parser.Jump())
            if jump == None:
               Error('unknown jump field: ' + parser.Jump(),
                     parser.LineNo(), parser.Line())
               jump='???'
            bin = ('111' + comp + dest + jump)
            outFile.write(bin+'\n')
            address += 1

        elif commandType == L_COMMAND:
            pass
            
        


def Int2Bin(i):
    bin = ''
    while i:
        if i & 1:
            bin = '1' + bin
        else:
            bin = '0' + bin
        i //= 2
    bin = '0' * 16 + bin
    return bin[-16:]


def Usage():
    print('usage: hasm sourceFile')
    sys.exit(-1)


def Main():
    global address, ramAddress, symbolTable, outFile
    try:
        if len(sys.argv) != 2:
            Usage()

        sourceName = sys.argv[1]
        outName = os.path.splitext(sourceName)[0] + os.path.extsep + 'hack'
        try:
            outFile = open(outName, 'w')
        except:
            FatalError('Could not open output file "' + outName + '"')

        symbolTable = Symbols()
        address = 0
        Pass1(sourceName)

        address = 0
        ramAddress = 16
        Pass2(sourceName)

        print('Code size = %5d (0x%04X)' % (address, address))
        print('Data size = %5d (0x%04X)' % (ramAddress, ramAddress))

    except SystemExit as e:
        sys.exit(e)


if __name__ == '__main__':
    Main()
