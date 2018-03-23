"""
hvmParser.py -- Parser class for Hack VM translator
"""

from hvmCommands import *

class Parser(object):
    def __init__(self, sourceName):
        """
        Open 'sourceFile' and gets ready to parse it.
        """
        self.file = open(sourceName, 'r');
        self.lineNumber = 0
        self.line = ''
        self.rawline = ''

    def Advance(self):
        """
        Reads the next command from the input and makes it the current
        command.
        Returns True if a command was found, False at end of file.
        """
        while True:
            if self.file:
                self.rawline = self.file.readline()
                if len(self.rawline) == 0:
                    return False
                self.rawline = self.rawline.replace('\n', '')
                self.line = self.rawline
                i = self.line.find('//')
                if i != -1:
                    self.line = self.line[:i]
                self.line = self.line.replace('\t', ' ').strip()
                if len(self.line) == 0:
                    continue
                self._Parse()
                return True
            else:
                return False

    def _Parse(self):
        # command [arg1 [arg2]]
        self.commandType = None
        self.arg1 = None
        self.arg2 = None
        self.comp = None
        self.jump = None
        self._ParseCommandType()
        if self.commandType not in (C_ARITHMETIC, C_RETURN):
            self._ParseArg1()
            if self.commandType in (C_PUSH, C_POP, C_FUNCTION, C_CALL):
                self._ParseArg2()
                
        
    def _ParseCommandType(self):
        # command is first run of non-whitespace
        self.line = self.line.lstrip()
        i = self.line.find(' ')
        if i != -1:
            command = self.line[:i]
            self.line = self.line[i:]
        else:
            command = self.line
            self.line = ''
        if len(command) == 0:
            return
        
        if command in T_ARITHMETIC:
            self.commandType = C_ARITHMETIC
            self.arg1 = command
        elif command == T_PUSH:
            self.commandType = C_PUSH
        elif command == T_POP:
            self.commandType = C_POP
        elif command == T_LABEL:
            self.commandType = C_LABEL
        elif command == T_GOTO:
            self.commandType = C_GOTO
        elif command == T_IF:
            self.commandType = C_IF
        elif command == T_FUNCTION:
            self.commandType = C_FUNCTION
        elif command == T_RETURN:
            self.commandType = C_RETURN
        elif command == T_CALL:
            self.commandType = C_CALL

    def CommandType(self):
        """
        Returns the type of the current command:
            C_ARITHMETIC = 1
            C_PUSH = 2
            C_POP = 3
            C_LABEL = 4
            C_GOTO = 5
            C_IF = 6
            C_FUNCTION = 7
            C_RETURN = 8
            C_CALL = 9
        """
        return self.commandType

    def _ParseArg(self):
        # arg is next run of non-whitespace
        self.line = self.line.lstrip()
        i = self.line.find(' ')
        if i != -1:
            arg = self.line[:i]
            self.line = self.line[i:]
        else:
            arg = self.line
            self.line = ''
        if len(arg) == 0:
            return None
        else:
            return arg
        
    def _ParseArg1(self):
        self.arg1 = self._ParseArg()

    def _ParseArg2(self):
        self.arg2 = self._ParseArg()

    def Arg1(self):
        """
        Returns the command's first argument.
        """
        return self.arg1

    def Arg2(self):
        """
        Returns the command's second argument.
        """
        return self.arg2

