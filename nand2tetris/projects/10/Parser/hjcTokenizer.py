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
        """
        while True:
            if len(self.line) == 0:
                # Read next line
                if not self.file:
                    return False
                else:
                    self.rawline = self.file.readline()
                    if len(self.rawline) == 0:
                        return False
                    self.lineNumber = self.lineNumber + 1
                    self.rawline = self.rawline.replace('\n', '')
                    if (self.printSource):
                        self.outputFile.WriteXml('source',
                                '/// %d: %s' %(self.lineNumber,self.rawline))
                    self.line = self.rawline
                    i = self.line.find('//')
                    if i != -1:
                        self.line = self.line[:i]

                    if self.inComment:
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
                            # inline comment
                            self.line = self.line[:i] + ' ' + self.line[j+2:]
                        else:
                            # start of multiline comment
                            self.line = self.line[:i]
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
            ch = self.line[0]
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
            if ch == '"':
                self.tokenType = TK_STRING_CONST
                self.stringVal = self._ParseString()
                return;
            raise HjcError('Syntax error in line '+str(self.lineNumber)+': illegal character "' + ch + '"')

        self.tokenType = TK_NONE;


    def _ParseInt(self):
        # Parse and return a non-negative integer.
        ret = 0;
        while len(self.line):
            ch = self.line[0]
            if ch in numberChars:
                ret = ret*10 + int(ch)
                if ret > 32767:
                    raise HjcError('Syntax error in line '+str(self.lineNumber)+': numeric constant > 32767')
                self.line = self.line[1:]
            else:
                break
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
        # Parse and return a string constatnt.
        ret = ''
        self.line = self.line[1:]   # skip open quote
        while len(self.line):
            ch = self.line[0]
            if ch == '"':
                self.line = self.line[1:]
                return ret
            else:
                ret = ret + ch
                self.line = self.line[1:]

        raise HjcError('Syntax error in line '+str(self.lineNumber)+': open string constant')



