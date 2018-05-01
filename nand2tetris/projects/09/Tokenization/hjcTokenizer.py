"""
hvmParser.py -- Tokenizer class for Hack Jack compiler
"""

from hjcTokens import *
from hjcError import *

keywords = {
    'boolean' : KW_BOOLEAN,
    'char' : KW_CHAR,
    'class' : KW_CLASS,
    'constructor' : KW_CONSTRUCTOR,
    'do' : KW_DO,
    'else' : KW_ELSE,
    'false' : KW_FALSE,
    'field' : KW_FIELD,
    'function' : KW_FUNCTION,
    'if' : KW_IF,
    'int' : KW_INT,
    'let' : KW_LET,
    'method' : KW_METHOD,
    'null' : KW_NULL,
    'return' : KW_RETURN,
    'static' : KW_STATIC,
    'this' : KW_THIS,
    'true' : KW_TRUE,
    'var' : KW_VAR,
    'void' : KW_VOID,
    'while' : KW_WHILE
    }
symbols = '{}()[].,;+-*/&|<>=~'
numberChars = '0123456789'
numberStart = numberChars
identStart = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
identChars = identStart + numberChars


class Tokenizer(object):
    def __init__(self, sourceName, outputFile=None, source=False):
        """
        Open 'sourceFile' and gets ready to parse it.
        """
        self.file = open(sourceName, 'r');
        self.lineNumber = 0
        self.line = ''
        self.rawline = ''
        self.inComment = False
        self.printSource = source
        self.outputFile = outputFile

    def Advance(self):
        """
        Reads the next command from the input and makes it the current
        command.
        Returns True if a command was found, False at end of file.

        Sets self.line to a line of code by:
            1. stripping return characters, \r
            2. removing comments that follow the line, like <code> // <comment>
            3. Removing multi line comments, like <code> /* <comment> */ <code>
                where the <comment> can span 0 or more lines.
            4. Replace tab characters, \t,  with space
        Once self.line is set, parsing can take place.
        """
        while True:
            if len(self.line) == 0:
                # End by returning false at end of file
                if not self.file:
                    return False
                else:
                    # Get new line
                    self.rawline = self.file.readline()
                    if len(self.rawline) == 0:
                        return False # end if empty

                    self.lineNumber = self.lineNumber + 1
                    self.line = self.rawline
                    # Remove return characters (\n)
                    self.line = self.line.replace('\n', '')
                    # For degugging
                    if (self.printSource):
                        self.outputFile.WriteXml('source',
                                '/// %d: %s' %(self.lineNumber,self.line))

                    # Remove comments that come after code
                    i = self.line.find('//')
                    if i != -1: # -1 means not found
                        self.line = self.line[:i] # [:-1] is whole line

                    if self.inComment:
                        # see if multi line comment ends:
                        i = self.line.find('*/')
                        if i == -1:
                            # still in multiline comment
                            self.line = ''
                        else:
                            # end of multiline comment
                            self.line = self.line[i+2:]
                            self.inComment = False

                    i = self.line.find('/*')
                    while i != -1:
                        j = self.line.find('*/')
                        if j != -1:
                            # inline comment, all appearing in one line as in:
                            # <code> /* <comment> */ <code>

                            self.line = self.line[:i] + ' ' + self.line[j+2:]
                        else:
                            # start of multiline comment
                            self.line = self.line[:i] # <code> /* <comment>
                            self.inComment = True
                            break
                        i = self.line.find('/*')

                    self.line = self.line.replace('\t', ' ').strip()
                    if len(self.line) == 0:
                        continue

           # continue parsing current line
            self._Parse()
            if self.tokenType == None:
                continue
            return True


    def LineNumber(self):
        return self.lineNumber


    def LineStr(self):
        return self.rawline


    def TokenType(self):
        return self.tokenType


    def TokenTypeStr(self):
        if self.tokenType == TK_SYMBOL:
            return '"'+self.symbol+'"'
        if self.tokenType == TK_KEYWORD:
            return '"'+self.keyword+'"'
        return tokenTypes[self.tokenType]


    def Keyword(self):
        return keywords[self.keyword]


    def KeywordStr(self, keywordId=None):
        if (keywordId != None):
            for k in keywords:
                if keywords[k] == keywordId:
                    return k
            raise ValueError
        return self.keyword


    def Symbol(self):
        return self.symbol


    def Identifier(self):
        return self.identifier


    def IntVal(self):
        return self.intVal


    def StringVal(self):
        return self.stringVal


    def _Parse(self):
        # parse the next token
        self.tokenType = None
        self.keyword = None
        self.symbol = None
        self.identifier = None
        self.intVal = None
        self.stringVal = None

        while len(self.line):
            ch = self.line[0] # get the first character in the line
            if ch == ' ':
                # skip spaces
                self.line = self.line[1:]
                continue
            if ch in symbols:
                self.line = self.line[1:]
                self.tokenType = TK_SYMBOL
                self.symbol = ch
                return
            if ch in numberStart:
                self.tokenType = TK_INT_CONST
                self.intVal = self._ParseInt()
                return
            if ch in identStart:
                ident = self._ParseIdent()
                if ident in keywords:
                    self.tokenType = TK_KEYWORD
                    self.keyword = ident
                else:
                    self.tokenType = TK_IDENTIFIER
                    self.identifier = ident
                return
            # ~TODO: Study codes above to develop the steps needed to identify and then parse a string
            # First write a test on ch to see if it is something,
            # if it is what you need, then set the self.tokenType
            # finally, get the value from self_ParseString() and set self.stringVal and return
            if ch == "\"":
                self.tokenType = TK_STRING_CONST
                self.stringVal = self._ParseString()
                return

            raise HjcError('Syntax error on ['+str(self.lineNumber)+','+str(self.rawline.find(ch))+']: illegal character "' + ch + '"')

        self.tokenType = TK_NONE;


    def _ParseInt(self):
        # Parse and return a non-negative integer.
        # ~TODO: Pull the first character off the self.line. If it is a number, then include it as the next digit in the
        # number that is returned. If not, then return ret, the number being parsed.
        ret = 0
        while len(self.line):
            ch = self.line[0]
            if ch in numberChars:
                ret = int(str(ret) + ch)
                self.line = self.line[1:]
            else:
                return ret

    def _ParseIdent(self):
        # Parse and return an identifier or keyword.
        ret = '';
        while len(self.line):
            ch = self.line[0]
            if ch in identChars:
                ret = ret + ch
                self.line = self.line[1:]
            else:
                break
        return ret


    def _ParseString(self):
        # Parse and return a string constant.
        # ~TODO: Complete this function taking the first characters of the line
        # and catenating them to a return string. Know when to stop!
        self.line = self.line[1:]   # skip open quote
        ret = ''
        while len(self.line):
            ch = self.line[0]
            if ch != "\"":
                ret = ret + ch
                self.line = self.line[1:]
            else:
                self.line = self.line[1:]
                return ret
        raise HjcError('Syntax error on ['+str(self.lineNumber)+','+str(self.rawline.find(ch))+']: open string constant')
