# Copyright (C) 2011 Mark Armbrust.  Permission granted for educational use.
"""
hasmParser.py -- Parser class for Hack computer assembler

See "The Elements of Computing Systems", by Noam Nisan and Shimon Schocken

This parser is slightly different than the parser design in
the book.

Because it is very difficult for HasMoreCommands() to deal with
trailing blank lines and comment only lines, CommandType() returns
NO_COMMAND for any lines that contains no command.

Use LineNo() to retrieve the current input line number and Line()
to retrieve the text.  These can be used to add context to error
messages.
"""

from hasmError import *


NO_COMMAND = 0
A_COMMAND = 1
C_COMMAND = 2
L_COMMAND = 3


class Parser(object):

    def __init__(self, source):
        """
        Costructor Parser(source)
        Open 'source' and get ready to parse it.
        'source' may be a file name or a string list
        """
        try:
            self.file = open(source, 'r');
        except:
            FatalError('Could not open source file "'+ source +'"')

        self.lineNumber = 0
        self.rawline = ''
        self.line = ''


    def HasMoreCommands(self):
        """
        Returns True if there are more commands to process, False at end of file.
        """
        return self.file is not None

    def Advance(self):
        """
        Reads the next command from the input and makes it the current
        command.  Should be called only if HasMoreCommands() is True.
        Initially there is no current command.
        """
        self.rawline = self.file.readline()
        if len(self.rawline) == 0:
            self.file.close()
            self.file = None
            self.commandType = NO_COMMAND
            return
        self.rawline = self.rawline.rstrip()
        self.lineNumber += 1
        self.line = self.rawline

        i = self.line.find('//')
        if i != -1:
            self.line = self.line[:i]

        self.line = self.line.strip()
        self.line = self.line.replace('\t', ' ')
        self._Parse()
        return True

    def CommandType(self):
        """
        Returns the type of the current command:
        A_COMMAND for @Xxx where Xxx is either a symbol or a decimal number
        C_COMMAND for dest=comp;jump (not anything else)
        L_COMMAND (actually, pseudocommand) for (Xxx) where Xxx is a symbol
        NO_COMMAND a blank line or comment
        """
        return self.commandType

    def Symbol(self):
        """
        Returns the symbol or decimal Xxx of the current command @Xxx or (Xxx).
        Should be called only when commandType() is A_COMMAND or L_COMMAND.
        """
        return self.symbol

    def Dest(self):
        """
        Returns the dest mnemonic in the current C-command (8 possibilities).
        Should be called only when commandType() is C_COMMAND.
        dest is optional; returns empty string if not present.
        """
        return self.dest

    def Comp(self):
        """
        Returns the comp mnemonic in the current C-command (28 possibilities).
        Should be called only when commandType() is C_COMMAND.
        """
        return self.comp

    def Jump(self):
        """
        Returns the jump mnemonic in the current C-command (8 possibilities).
        Should be called only when commandType() is C_COMMAND.
        jump is optional; returns empty string if not present.
        """
        return self.jump

    def Line(self):
        """
        Returns the input line that has been parsed.
        May be used to implement list file output.
        """
        return self.rawline

    def LineNo(self):
        """
        Returns the line number for the line that has been parsed.
        May be used to implement list file output.
        """
        return self.lineNumber

    def _Parse(self):
        self.commandType = None
        self.symbol = None
        self.dest = None
        self.comp = None
        self.jump = None
        self.keywordId = None
        self._ParseCommandType()
        if self.commandType == A_COMMAND:
            self._ParseSymbol()
        elif self.commandType == L_COMMAND:
            self._ParseSymbol()
        elif self.commandType == C_COMMAND:
            self._ParseDest()
            self._ParseComp()
            self._ParseJump()

    def _ParseCommandType(self):
        if len(self.line) == 0:
            self.commandType = NO_COMMAND

        elif self.line[0] == '@':
            self.commandType = A_COMMAND
        elif self.line[0] == '(':
            self.commandType = L_COMMAND
        else:
            self.commandType = C_COMMAND

    def _ParseSymbol(self):
        if self.CommandType() == L_COMMAND:
            if self.line[-1] == ')':
                self.line = self.line[:-1]
        self.symbol = self.line[1:].strip()

    def _ParseDest(self):
        i = self.line.find('=')
        if i == -1:
            self.dest = ''
        else:
            self.dest = self.line[:i].replace(' ', '')

    def _ParseComp(self):
        if (self.commandType == C_COMMAND):
                i = self.line.find('=')
                if i == -1:
                    if self.line.find(';') == -1:
                        self.comp = None
                    else:
                        self.comp = self.line.strip()[0]
                else:
                    self.comp = self.line[i+1:]
                

    def _ParseJump(self):
        i = self.line.find(';')
        if i == -1:
            self.jump = ''
        else:
            self.jump = self.line[i+1:].strip()
