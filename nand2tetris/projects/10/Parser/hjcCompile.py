"""
hjcCompile.py -- CompileEngine class for Hack computer Jack compiler
"""

# There are three TODOs in this file.
# I recommend doing them in the following order, which should orient you with the code in a
# way that builds from the simple to the complex:
# 1.  in def _ExpectSymbol(self, symbols):
#     This shows you how to check if tokens are what you
#     think they should be. It is used in almost all methods
#     to test if the terminals are right.
# 2. in def _CompileVarDec(self):
#     This should give you a little of the style of how to resolve a non-terminal
#     In this case it is one of the simplest, the <type> non-terminal
# 3. in def _CompileSubroutineBody(self):
#     This is basically and entire method that resolves an important non-terminal - <subroutineBody>
#     While it seems ambitious, there are a lot of hints in the comments and the way it is done is
#     almost exactly like the way it is done in other methods.

from hjcTokens import *
from hjcTokenizer import *
from hjcOutputFile import *

xml = True  # Enable _WriteXml...() functions

class CompileEngine(object):
    def __init__(self, inputFileName, outputFileName, source=False, debug=False):
        """
        Initializes the compilation of 'inputFileName' to 'outputFileName'.
        If 'source' is True, source code will be included as comments in the
            output.
        If 'debug' is True, ...
        """
        self.inputFileName = inputFileName
        self.outputFile = OutputFile(outputFileName)
        self.tokenizer = Tokenizer(inputFileName, self.outputFile, source)
        self.xmlIndent = 0


    def Close(self):
        """
        Finalize the compilation ans close the output file.
        """
        self.outputFile.Close()


    def CompileClass(self):
        """
        Compiles <class> :=
            'class' <class-name> '{' <class-var-dec>* <subroutine-dec>* '}'

        The tokenizer is expected to be positionsed at the beginning of the
        file.
        """
        # This is the class that is called by hjc.py, based on the files passed to it.

        # Get used to this, a tag is written to correspond to non-terminals with this
        # function. It will also keep track of indentation (study the function).
        self._WriteXmlTag('<class>\n')

        # Advance to the next token, which in this case is the first token,
        # the 'class' keyword.
        self._NextToken()

        # This is a really common construct:
        # See if the take is what you think it should be - in this case
        # the keyword "class". This function will stop the compile if it isn't
        # what you think.
        self._ExpectKeyword(KW_CLASS)
        # OK, got through that. So, it is what we think - let's write it to a file.
        # This functions will create the line of text:
        # <keyword> class </keyword>
        # Observe that there is a difference between _WriteXmlTag and _WriteXml
        self._WriteXml('keyword', 'class')
        # Ready to take on the next thing
        self._NextToken()

        # Look at the grammar. Unless the code is not in the grammar, this has to be
        # an identifier, or the class name.
        # Same strategy as before, test:
        className = self._ExpectIdentifier()
        # OK, it's what we thought, write to the file:
        self._WriteXml('identifier', className)
        # Get the next thing.
        self._NextToken()

        # Now this better be an open curly brace (see grammar)
        self._ExpectSymbol('{')
        self._WriteXml('symbol', '{')
        self._NextToken()

        # Phew, made it past the 'class' <class-name> '{' part. Now let's do the class body:
        # <class-var-dec>* <subroutine-dec>*
        # That's a loop that keeps going indefinitely.
        while True:
            if self.tokenizer.TokenType() != TK_KEYWORD:
                break # Well, if it's not a keyword, something is messed up.
            if self.tokenizer.Keyword() not in (KW_STATIC, KW_FIELD): # It should be a variable declaration.
                break
            self._CompileClassVarDec(); # Alright, someone else wrote the code for this, it must be a <var-dec>
                                        # This is the recursive descent call
        # Same ideas as above, but now it's just for constructors, functions, and methods. This is <subroutine-dec>*
        while True:
            if self.tokenizer.TokenType() != TK_KEYWORD:
                break
            if self.tokenizer.Keyword() not in (KW_CONSTRUCTOR, KW_FUNCTION,
                                              KW_METHOD):
                break
            self._CompileSubroutine(); # This is the recursive descent call

        # The rest is a lot like what happened before, but now writes the terminals that appear at the
        self._ExpectSymbol('}')
        self._WriteXml('symbol', '}')

        self._WriteXmlTag('</class>\n')
        if self.tokenizer.Advance(): # This is really a check to see if the file ends with the end of the class
            self._RaiseError('Junk after end of class definition')

        # If you can follow how this method works, the other are not so bad.

    def _CompileClassVarDec(self):
        """
        Compiles <class-var-dec> :=
            ('static' | 'field') <type> <var-name> (',' <var-name>)* ';'

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<classVarDec>\n')
        storageClass = self._ExpectKeyword((KW_STATIC, KW_FIELD))
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()
        if self.tokenizer.TokenType() == TK_KEYWORD:
            variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
            variableTypeName = None
            self._WriteXml('keyword', self.tokenizer.KeywordStr())
        else:
            variableTypeName = self._ExpectIdentifier()
            variableType = None
            self._WriteXml('identifier', self.tokenizer.Identifier())

        self._NextToken()
        while True:
            variableName = self._ExpectIdentifier()
            self._WriteXml('identifier', self.tokenizer.Identifier())
            self._NextToken()
            if self.tokenizer.TokenType() != TK_SYMBOL or \
                    self.tokenizer.Symbol() != ',':
                break
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</classVarDec>\n')



    def _CompileSubroutine(self):
        """
        Compiles <subroutine-dec> :=
            ('constructor' | 'function' | 'method') ('void' | <type>)
            <subroutine-name> '(' <parameter-list> ')' <subroutine-body>

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after <subroutine-body>.
        """
        self._WriteXmlTag('<subroutineDec>\n')
        subroutineType = self._ExpectKeyword((KW_CONSTRUCTOR, KW_FUNCTION,
                                              KW_METHOD))
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()
        if self.tokenizer.TokenType() == TK_KEYWORD:
            returnType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN,
                                              KW_VOID))
            returnTypeName = None
            self._WriteXml('keyword', self.tokenizer.KeywordStr())
        else:
            returnTypeName = self._ExpectIdentifier()
            returnType = None
            self._WriteXml('identifier', self.tokenizer.Identifier())

        self._NextToken()
        while True:
            subroutineName = self._ExpectIdentifier()
            self._WriteXml('identifier', self.tokenizer.Identifier())
            self._NextToken()
            if self.tokenizer.TokenType() != TK_SYMBOL or \
                    self.tokenizer.Symbol() != ',':
                break
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileParameterList()

        self._ExpectSymbol(')')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileSubroutineBody()
        self._WriteXmlTag('</subroutineDec>\n')


    def _CompileParameterList(self):
        """
        Compiles <parameter-list> :=
            ( <type> <var-name> (',' <type> <var-name>)* )?

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after <subroutine-body>.
        """
        self._WriteXmlTag('<parameterList>\n')

        while True:
            if self.tokenizer.TokenType() == TK_SYMBOL and \
                   self.tokenizer.Symbol() == ')':
                break;

            elif self.tokenizer.TokenType() == TK_KEYWORD:
                variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
                variableTypeName = None
                self._WriteXml('keyword', self.tokenizer.KeywordStr())
            else:
                variableTypeName = self._ExpectIdentifier()
                variableType = None
                self._WriteXml('identifier', self.tokenizer.Identifier())
            self._NextToken();

            variableName = self._ExpectIdentifier();
            self._WriteXml('identifier', self.tokenizer.Identifier())
            self._NextToken();

            if self.tokenizer.TokenType() != TK_SYMBOL or \
                   self.tokenizer.Symbol() != ',':
                break
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._WriteXmlTag('</parameterList>\n')


    def _CompileSubroutineBody(self):
        """
        Compiles <subroutine-body> :=
            '{' <var-dec>* <statements> '}'

        The tokenizer is expected to be positioned before the {
        ENTRY: Tokenizer positioned on the initial '{'.
        EXIT:  Tokenizer positioned after final '}'.
        """

        # TODO: Write this method. It is a matter of looking closely at similar functions and
        # mimicing the way their grammar is enforced with the other methods of this class.
        # Specific hints follow.

        # First, you should write a tag to indicate you are in "subroutineBody".
        self._WriteXmlTag("<subroutineBody>\n")

        # No make sure you've got a open curly brace, write it, and then get the next token.
        self._ExpectSymbol("{")
        self._WriteXml("symbol", self.tokenizer.Symbol())
        self._NextToken()

        # The next portion is zero or more variable declarations. Clearly that's going to be a loop of some
        # sort. You have a method for handling variable declarations, so the loop's body is easy.
        # The question is why it stops. I think it's a matter of seeing if the current token is a TK_KEYWORD
        # and that keywork is a KW_VAR.
        while self.tokenizer.TokenType() == TK_KEYWORD and self.tokenizer.Keyword() == KW_VAR:
            self._CompileVarDec()

        # Following variable declarations, there are statements. Again, look for a method or methods that will
        # compile statements.
        self._CompileStatements()

        # Finally, there is some house keeping to be done as you send the last set of terminals to be written.
        # This is a well worn path and other methods in this class can be consulted for how it is done.
        # Don't forget to advance the token, consistent with the "EXIT" statement above, and close or end the
        # "subroutineBody" tag.
        self._ExpectSymbol("}")
        self._WriteXml("symbol", self.tokenizer.Symbol())
        self._NextToken()
        self._WriteXmlTag("</subroutineBody>\n")


    def _CompileVarDec(self):
        """
        Compiles <var-dec> :=
            'var' <type> <var-name> (',' <var-name>)* ';'

        ENTRY: Tokenizer positioned on the initial 'var'.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<varDec>\n')

        storageClass = self._ExpectKeyword(KW_VAR)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        # TODONE: The following will enforce the <type> portion of the grammar
        # Recall from the grammar that this can be INT|CHAR|BOOLEAN|CLASS NAME
        # CLASS NAME is a valid identifier.
        #
        # This should be structured as an if/else
        # If the token is a keyword, then it has to be int,char, or boolean.
        # else, it must be an identifier.
        # In both cases, begin by calling one of the _Expect functions to test
        # if the token is what you thought it should be.
        # After the call to _Expect, call _WriteXML to create the appropriate tag and contents
        # for each of the two cases.
        # Study _WriteXml for an understanding of what is written and how.

        if self.tokenizer.TokenType() == TK_KEYWORD:
            variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
            variableTypeName = None
            self._WriteXml('keyword', self.tokenizer.KeywordStr())
        else:
            variableTypeName = self._ExpectIdentifier()
            variableType = None
            self._WriteXml('identifier', self.tokenizer.Identifier())

        # Done with <type>. Advance token and consider <var-name>
        self._NextToken()

        while True:
            variableName = self._ExpectIdentifier()
            self._WriteXml('identifier', self.tokenizer.Identifier())
            self._NextToken()

            if self.tokenizer.TokenType() != TK_SYMBOL or \
                    self.tokenizer.Symbol() != ',':
                break
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</varDec>\n')


    def _CompileStatements(self):
        """
        Compiles <statements> := (<let-statement> | <if-statement> |
            <while-statement> | <do-statement> | <return-statement>)*

        The tokenizer is expected to be positioned on the first statement
        ENTRY: Tokenizer positioned on the first statement.
        EXIT:  Tokenizer positioned after final statement.
        """
        self._WriteXmlTag('<statements>\n')

        while self.tokenizer.TokenType() == TK_KEYWORD:
            kw = self._ExpectKeyword((KW_DO, KW_IF, KW_LET, KW_RETURN, KW_WHILE))
            if kw == KW_DO:
                self._CompileDo()
            elif kw == KW_IF:
                self._CompileIf()
            elif kw == KW_LET:
                self._CompileLet()
            elif kw == KW_RETURN:
                self._CompileReturn()
            elif kw == KW_WHILE:
                self._CompileWhile()

        self._WriteXmlTag('</statements>\n')


    def _CompileLet(self):
        """
        Compiles <let-statement> :=
            'let' <var-name> ('[' <expression> ']')? '=' <expression> ';'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<letStatement>\n')

        self._ExpectKeyword(KW_LET)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        variableName = self._ExpectIdentifier()
        self._WriteXml('identifier', self.tokenizer.Identifier())
        self._NextToken()

        variableSubscript = None
        sym = self._ExpectSymbol('[=')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        if sym == '[':
            self._CompileExpression()

            self._ExpectSymbol(']')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

            self._ExpectSymbol('=')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._CompileExpression()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</letStatement>\n')


    def _CompileDo(self):
        """
        Compiles <do-statement> := 'do' <subroutine-call> ';'

        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<doStatement>\n')

        self._ExpectKeyword(KW_DO)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        self._CompileCall()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</doStatement>\n')


    def _CompileCall(self, subroutineName=None):
        """
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first identifier.
            If 'objectName' is supplied, tokenizer is on the '.'
        EXIT:  Tokenizer positioned after final ';'.
        """
        objectName = None
        if subroutineName == None:
            subroutineName = self._ExpectIdentifier()
            self._NextToken()
        self._WriteXml('identifier', subroutineName)

        sym = self._ExpectSymbol('.(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        if sym == '.':
            objectName = subroutineName
            subroutineName = self._ExpectIdentifier()
            self._WriteXml('identifier', self.tokenizer.Identifier())
            self._NextToken()

            sym = self._ExpectSymbol('(')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._CompileExpressionList()

        self._ExpectSymbol(')')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()



    def _CompileReturn(self):
        """
        Compiles <return-statement> :=
            'return' <expression>? ';'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<returnStatement>\n')
        self._ExpectKeyword(KW_RETURN)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        if self.tokenizer.TokenType() != TK_SYMBOL or \
               self.tokenizer.Symbol() != ';':
            self._CompileExpression()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</returnStatement>\n')


    def _CompileIf(self):
        """
        Compiles <if-statement> :=
            'if' '(' <expression> ')' '{' <statements> '}' ( 'else'
            '{' <statements> '}' )?

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<ifStatement>\n')

        self._ExpectKeyword(KW_IF)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileExpression()

        self._ExpectSymbol(')')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._ExpectSymbol('{')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileStatements()

        self._ExpectSymbol('}')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        if self.tokenizer.TokenType() == TK_KEYWORD and \
                self.tokenizer.Keyword() == KW_ELSE:
            self._ExpectKeyword(KW_IF)
            self._WriteXml('keyword', self.tokenizer.KeywordStr())
            self._NextToken()

            self._ExpectSymbol('{')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

            self._CompileStatements()

            self._ExpectSymbol('}')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._WriteXmlTag('</ifStatement>\n')
        pass


    def _CompileWhile(self):
        """
        Compiles <while-statement> :=
            'while' '(' <expression> ')' '{' <statements> '}'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<whileStatement>\n')

        self._ExpectKeyword(KW_WHILE)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileExpression()

        self._ExpectSymbol(')')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._ExpectSymbol('{')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileStatements()

        self._ExpectSymbol('}')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</whileStatement>\n')


    def _CompileExpression(self):
        """
        Compiles <expression> :=
            <term> (op <term)*

        The tokenizer is expected to be positioned on the expression.
        ENTRY: Tokenizer positioned on the expression.
        EXIT:  Tokenizer positioned after the expression.
        """
        self._WriteXmlTag('<expression>\n')

        self._CompileTerm()

        while (self.tokenizer.TokenType() == TK_SYMBOL and \
                self.tokenizer.Symbol() in '+-*/&|<>='):
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

            self._CompileTerm()

        self._WriteXmlTag('</expression>\n')


    def _CompileTerm(self):
        """
        Compiles a <term> :=
            <int-const> | <string-const> | <keyword-const> | <var-name> |
            (<var-name> '[' <expression> ']') | <subroutine-call> |
            ( '(' <expression> ')' ) | (<unary-op> <term>)

        ENTRY: Tokenizer positioned on the term.
        EXIT:  Tokenizer positioned after the term.
        """
        self._WriteXmlTag('<term>\n')

        if self.tokenizer.TokenType() == TK_INT_CONST:
            self._WriteXml('integerConstant', str(self.tokenizer.IntVal()))
            self._NextToken()

        elif self.tokenizer.TokenType() == TK_STRING_CONST:
            self._WriteXml('stringConstant', self.tokenizer.StringVal())
            self._NextToken()

        elif self.tokenizer.TokenType() == TK_KEYWORD and \
                self.tokenizer.Keyword() in (KW_FALSE, KW_NULL, KW_THIS, KW_TRUE):
            self._WriteXml('keyword', self.tokenizer.KeywordStr())
            self._NextToken()

        elif self.tokenizer.TokenType() == TK_SYMBOL and \
                self.tokenizer.Symbol() in '-~':
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

            self._CompileTerm()

        elif self.tokenizer.TokenType() == TK_SYMBOL and \
                self.tokenizer.Symbol() == '(':
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

            self._CompileExpression()

            self._ExpectSymbol(')')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        else:
            variable = self._ExpectIdentifier()
            self._NextToken()

            if self.tokenizer.TokenType() == TK_SYMBOL and \
                    self.tokenizer.Symbol() == '[':
                # identifier[expression]
                self._WriteXml('identifier', variable)
                self._WriteXml('symbol', self.tokenizer.Symbol())
                self._NextToken()

                self._CompileExpression()

                self._ExpectSymbol(']')
                self._WriteXml('symbol', self.tokenizer.Symbol())
                self._NextToken()

            elif self.tokenizer.TokenType() == TK_SYMBOL and \
                    self.tokenizer.Symbol() in '.(':
                # identifier(arglist)
                # identifier.identifier(arglist)
                self._CompileCall(variable)

            else:
                # identifier
                self._WriteXml('identifier', variable)
                # no self._NextToken() -- already there

        self._WriteXmlTag('</term>\n')


    def _CompileExpressionList(self):
        """
        Compiles <expression-list> :=
            (<expression> (',' <expression>)* )?

        ENTRY: Tokenizer positioned on the first expression.
        EXIT:  Tokenizer positioned after the last expression.
        """
        self._WriteXmlTag('<expressionList>\n')

        while True:
            if self.tokenizer.TokenType() == TK_SYMBOL and \
                    self.tokenizer.Symbol() == ')':
                break

            self._CompileExpression()

            if self.tokenizer.TokenType() != TK_SYMBOL or \
                    self.tokenizer.Symbol() != ',':
                break

            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._WriteXmlTag('</expressionList>\n')




    def _WriteXmlTag(self, tag):
        if xml:
            if '/' in tag:
                self.xmlIndent -= 1
            self.outputFile.Write('  ' * self.xmlIndent)
            self.outputFile.Write(tag)
            if '/' not in tag:
                self.xmlIndent += 1


    def _WriteXml(self, tag, value):
        if xml:
            self.outputFile.Write('  ' * self.xmlIndent)
            self.outputFile.WriteXml(tag, value)


    def _ExpectKeyword(self, keywords):
        """
        Parse the next token.  It is expected to be one of 'keywords'.
        'keywords' may be a keywordID or a tuple of keywordIDs.

        Returns the keyword parsed or raises an error.
        """
        if not self.tokenizer.TokenType() == TK_KEYWORD:
            self._RaiseError('Expected '+self._KeywordStr(keywords)+', got '+
                             self.tokenizer.TokenTypeStr())
        if type(keywords) != tuple:
            keywords = (keywords,)
        if self.tokenizer.Keyword() in keywords:
            return self.tokenizer.Keyword()
        self._RaiseError('Expected '+self._KeywordStr(keywords)+', got '+
                         self._KeywordStr(self.tokenizer.Keyword()))


    def _ExpectIdentifier(self):
        """
        Parse the next token.  It is expected to be an identifier.

        Returns the identifier parsed or raises an error.
        """
        if not self.tokenizer.TokenType() == TK_IDENTIFIER:
            self._RaiseError('Expected <identifier>, got '+
                             self.tokenizer.TokenTypeStr())
        return self.tokenizer.Identifier()


    def _ExpectSymbol(self, symbols):
        """
        Parse the next token.  It is expected to be one of 'symbols'.
        'symbols' is a string of one or more legal symbols.

        Returns the symbol parsed or raises an error.
        """
        # TODO: Write code that looks much like code for _ExpectKeyword
        # and _ExpectIdentifier in that it will see if the token is what
        # you expect, in this case a symbol. If it isn't raise an exception.
        # If it is, then return the symbol itself (from self.tokenizer.Symbol()).
        #
        # This will consist of two tests.

        # First, see if the TokenType returned by self.tokenizer.TokenType()
        # is what you expect.

        # Second, test to see if the symbol itself, returned by self.tokenizer.Symbol()
        # is indeed a symbol.
        #
        # To help you, I've included the errors you will need to raise from the first and
        # second tests, respectively.
        if not self.tokenizer.TokenType() == TK_SYMBOL:
            self._RaiseError('Expected '+self._SymbolStr(symbols)+', got '+
                             self.tokenizer.TokenTypeStr())
        if not self.tokenizer.Symbol() in symbols:
            self._RaiseError('Expected '+self._SymbolStr(symbols)+', got '+
                             self._SymbolStr(self.tokenizer.Symbol()))
        return self.tokenizer.Symbol()


    def _RaiseError(self, error):
        message = '%s line %d:\n  %s\n  %s' % (
                  self.inputFileName, self.tokenizer.LineNumber(),
                  self.tokenizer.LineStr(), error)
        raise HjcError(message)


    def _KeywordStr(self, keywords):
        if type(keywords) != tuple:
            return '"' + self.tokenizer.KeywordStr(keywords) + '"'
        ret = ''
        for kw in keywords:
            if len(ret):
                ret += ', '
            ret += '"' + self.tokenizer.KeywordStr(kw) + '"'
        if len(keywords) > 1:
            ret = 'one of (' + ret + ')'
        return ret


    def _SymbolStr(self, symbols):
        if type(symbols) != tuple:
            return '"' + symbols + '"'
        ret = ''
        for symbol in symbols:
            if len(ret):
                ret += ', '
            ret += '"' + symbol + '"'
        if len(symbols) > 1:
            ret = 'one of (' + ret + ')'
        return ret


    def _NextToken(self):
        if not self.tokenizer.Advance():
            self._RaiseError('Premature EOF')
