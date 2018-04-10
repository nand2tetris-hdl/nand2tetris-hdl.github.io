"""
hvmCodeWriter.py -- Code Writer class for Hack VM translator
"""

import os
from hvmCommands import *

debug = True

class CodeWriter(object):

    def __init__(self, outputName):
        """
        Open 'outputName' and gets ready to write it.
        """
        self.file = open(outputName, 'w')
        self.fileName = self.SetFileName(outputName)

        # used to generate unique labels
        self.labelNumber = 0


    def Close(self):
        """
        Write a jmp $ and close the output file.
        """
        label = self._UniqueLabel()
        self._WriteCode('(%s), @%s, 0;JMP' % (label, label))
        self.file.close()


    def SetFileName(self, fileName):
        """
        Sets the current file name to 'fileName'.
        Restarts the local label counter.

        Strips the path and extension.  The resulting name must be a
        legal Hack Assembler identifier.
        """
        self.fileName = os.path.basename(fileName)
        self.fileName = os.path.splitext(self.fileName)[0]


    def _UniqueLabel(self):
        self.labelNumber += 1
        return '_' + str(self.labelNumber)


    def _Static(self, n):
        return self.fileName + '.' + str(n)


    def _WriteCode(self, code):
        code = code.replace(',', '\n').replace(' ', '')
        self.file.write(code + '\n')


    def WriteArithmetic(self, command):
        """
        Write Hack code for 'command' (str).
        """
        # TODO: write the assembly code for the various arithmetic commands
        # HINT: for several of these, use self._WritePopD() for popping to the D register. I suggest implementing self._WritePopD first.
        # use self._WriteCode() for writing the assembly language commands to file

        if (debug): # debug mode writes comments to the hack file
            self.file.write('    // %s\n' % command)
        if command == T_ADD:
            # TODO: implement VM addition. i.e., pop the stack to register D, add this with the new value at the bottom of the stack,
            # and replace the bottom of the stack with this value
            
            pass
        elif command == T_SUB:
            # TODO: implement VM subtraction. This is similar to VM addition
            pass
        elif command == T_AND:
            # TODO: implement VM add. This is similar to VM addition
            pass
        elif command == T_OR:
            # TODO: implement VM or. This is similar to VM addition
            pass
        elif command == T_NEG:
            # TODO: implement VM negation. i.e., calculate the negation of the value at pointed to by the stack pointer (SP),
            # and store this at the current SP location
            pass
        elif command == T_NOT:
            # TODO: implement VM bit-wise not. This is similar to VM negation.
            pass
        elif command == T_EQ:
            self._WriteCompare('JEQ')
        elif command == T_GT:
            self._WriteCompare('JGT')
        elif command == T_LT:
            self._WriteCompare('JLT')
        else:
            print command
            raise(ValueError, 'Bad arithmetic command')


    def _WritePushD(self):
        # TODO: write the assemby code commands for pushing the D register value onto the stackself.
        self._WriteCode('') # <- TODO: write Assembly code here


    def _WritePopD(self):
        # TODO: write the assemby code commands for popping the stack onto the D register.
        self._WriteCode('') # <- TODO: write Assembly code here


    def _WriteCompare(self, jmp):
        label1 = self._UniqueLabel();
        label2 = self._UniqueLabel();
        self._WriteCode('@SP, A=M-1, A=A-1, D=M, A=A+1, D=D-M')
        self._WriteCode('@%s, D;%s' % (label1, jmp))
        self._WriteCode('@%s, D=0;JMP' % (label2))
        self._WriteCode('(%s), D=-1, (%s)' % (label1, label2))
        self._WriteCode('@SP, AM=M-1, A=A-1, M=D')


    def WritePushPop(self, commandType, segment, index):
        """
        Write Hack code for 'commandType' (C_PUSH or C_POP).
        'segment' (string) is the segment name.
        'index' (int) is the offset in the segment.
        """
        # TODO: write assembly code for some of the VM push and pop commands
        # HINT: use self._WritePushD to push the value in the D register onto the Stack. Use self._WritePopD to pop the Stack onto the D register
        if commandType == C_PUSH:
            if (debug): # debug mode writes comments to the hack file
                self.file.write('    // push %s %d\n' % (segment, int(index)))
            if segment == T_CONSTANT:
                # TODO: push the value 'index' on the stack
                # NOTE: here 'index' is used as a constant, not an actual index
                # See following lines for examples of how to place a variable into a string using Python.
                pass
            elif segment == T_STATIC:
                self._WriteCode('@%s.%d, D=M' % (self.fileName, int(index)))
                self._WritePushD()
            elif segment == T_POINTER:
                self._WriteCode('@%d, D=M' % (3 + int(index)))
                self._WritePushD()
            elif segment == T_TEMP:
                # TODO: push the value of the TEMP segment at index 'index' onto the stack
                # NOTE: the TEMP segment begins at RAM address 5
                pass
            else:
                self._WriteGetPtrD(segment, index) # gets the memory address for the given pointer and index and loads this memory address into register D
                # TODO: get the value at the memory address now in register D, and push this value onto the Stack

        elif commandType == C_POP:
            if (debug): # debug mode writes comments to the hack file
                self.file.write('    // pop %s %d\n' % (segment, int(index)))
            if segment == T_STATIC:
                self._WritePopD()
                self._WriteCode('@%s.%d, M=D' % (self.fileName, int(index)))
            elif segment == T_POINTER:
                self._WritePopD()
                self._WriteCode('@%d, M=D' % (3 + int(index)))
            elif segment == T_TEMP:
                # TODO: pop the value on the stack into the memory location in the TEMP segment at index 'index'
                # NOTE: the TEMP segment begins at RAM address 5
                pass
            else:
                self._WriteGetPtrD(segment, index)# gets the memory address for the given pointer and index and loads this memory address into register D
                # TODO: register D is now a memory address. Pop the value from the Stack into this memory address.
        else:
            raise(ValueError, 'Bad push/pop command')


    def _WriteGetPtrD(self, segment, index):
        if segment == T_CONSTANT:
            raise(ValueError, 'constant segment is virtual')
        elif segment == T_STATIC:
            raise(ValueError, 'static segment is not indexed')
        elif segment == T_POINTER:
            raise(ValueError, 'pointer segment is not dynamic')
        elif segment == T_TEMP:
            raise(ValueError, 'temp segment is not dynamic')

        if segment == T_ARGUMENT:
            pointer = 'ARG'
        elif segment == T_LOCAL:
            pointer = 'LCL'
        elif segment == T_THIS:
            pointer = 'THIS'
        elif segment == T_THAT:
            pointer = 'THAT'
        else:
            raise(ValueError, 'unknown segment name')

        self._WriteCode('@%s, D=M, @%d, D=D+A' % (pointer, int(index)))
