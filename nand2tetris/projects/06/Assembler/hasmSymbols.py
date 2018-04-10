# Copyright (C) 2011 Mark Armbrust.  Permission granted for educational use.
"""
hasmSymbols.py -- Symbol table for Hack computer assembler

See "The Elements of Computing Systems", by Noam Nisan and Shimon Schocken
"""

from hasmError import *


class Symbols(object):
    # Valid characters for symbol names.
    initialChars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMONPQRSTUVWXYZ_.$:'
    continueChars = initialChars + '0123456789'

    def __init__(self):
        """
        Constructor Symbols()
        Initializes the symbol table with built-in symbols.
        """
        self.symbolDict = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'R0': 0,
            'R1': 1,
            'R2': 2,
            'R3': 3,
            'R4': 4,
            'R5': 5,
            'R6': 6,
            'R7': 7,
            'R8': 8,
            'R9': 9,
            'R10': 10,
            'R11': 11,
            'R12': 12,
            'R13': 13,
            'R14': 14,
            'R15': 15,
            'SCREEN': 0x4000,
            'KBD': 0x6000
            }

    def Contains(self, symbol):
        """
        Returns True if 'symbol' is in the symbol table.
        """
        return symbol in self.symbolDict

    def GetAddress(self, symbol):
        """
        Return 'symbol's address.
        Raises exception if symbol not found.
        use the symbolDict
        """
        return self.symbolDict[symbol]
        
    def AddEntry(self, symbol, value):
        """
        Add 'symbol' to the symbol table.

        Returns True if the symbol was added.
        Returns False if the symbol name is illegal.

        Existing entries will be silently overwritten.
        """
        if self._ValidName(symbol):
            self.symbolDict[symbol] = value
            return True
        else:
            return False


    def _ValidName(self, symbol):
        '''
        Returns True if 'symbol' is a valid symbol name.
        '''
        if len(symbol) == 0:
            return False
        valid = self.initialChars
        for c in symbol:
            if not c in valid:
                return False
            valid = self.continueChars
        return True
