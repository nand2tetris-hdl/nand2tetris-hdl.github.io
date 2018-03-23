# Copyright (C) 2011 Mark Armbrust.  Permission granted for educational use.
"""
hasmCode.py -- Code class for Hack computer assembler

See "The Elements of Computing Systems", by Noam Nisan and Shimon Schocken
"""

class Code(object):

    _compDict = {
            '0': '101010',
            '1': '111111',
            '-1': '111010',
            'D': '001100',
            'A': '110000',
            '!D': '001101',
            '!A': '110001',
            '-D': '001111',
            '-A': '110011',
            'D+1': '011111',
            'A+1': '110111',
            'D-1': '001110',
            'A-1': '110010',
            'D+A': '000010',
            'D-A': '010011',
            'A-D': '000111',
            'D&A': '000000',
            'D|A': '010101',
            'M': '110000',
            '!M': '110001',
            '-M': '110011',
            'M+1': '110111',
            'M-1': '110010',
            'D+M': '000010',
            'D-M': '010011',
            'M-D': '000111',
            'D&M': '000000',
            'D|M': '010101'
        }
    _jumpDict = {
            'null': '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }

    def __init__(self):
        """
        Constructor Code()
        """
        pass

    def Dest(self, mnemonic):
        """
        Returns the binary code of the dest mnemonic. (3 bits)
        Returns None if the mnemonic cannot be decoded.
        """
        code = ''
        if 'A' in mnemonic:
            code += '1'
        else:
            code += '0'
        
        if 'D' in mnemonic:
            code += '1'
        else:
            code += '0'

        if 'M' in mnemonic:
            code += '1'
        else:
            code += '0'
        
        if (len(mnemonic) > 0 and code == '000') or len(mnemonic) > 3:
            return None #if mnemonic is of wrong format, return None
        return code

    def Comp(self, mnemonic):
        """
        Returns the binary code of the comp mnemonic. (7 bits)
        Returns None if the mnemonic cannot be decoded.
        """
        compBinary = None
        if mnemonic in self._compDict:
            compBinary = self._compDict[mnemonic]
            if 'M' in mnemonic:
                compBinary = '1' + compBinary
            else:
                compBinary = '0' + compBinary
        return compBinary

    def Jump(self, mnemonic):
        """
        Returns the binary code of the jump mnemonic. (3 bits)
        Returns None if the mnemonic cannot be decoded
        """
        if len(mnemonic) > 3:
            return None
        if mnemonic in self._jumpDict:
            return self._jumpDict[mnemonic]
        else:
            return self._jumpDict['null']
