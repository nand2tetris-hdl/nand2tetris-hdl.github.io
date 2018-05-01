"""
hvmCodeWriter.py -- Code Writer class for Hack VM translator
"""

import os
from hvmCommands import *

debug = False

class CodeWriter(object):

    def __init__(self, outputName):
        """
        Open 'outputName' and gets ready to write it.
        """
        self.file = open(outputName, 'w')
        self.SetFileName(outputName)

        self.labelNumber = 0
        self.returnLabel = None
        self.callLabel = None
        self.cmpLabels = {}
        self.needHalt = False


    def Debug(self, value):
        """
        Set debug mode.
        Debug mode writes usefull comments in the output stream.
        """
        global debug
        debug = value


    def Close(self):
        """
        Write a jmp $ and close the output file.
        """
        if self.needHalt:
            if debug:
                self.file.write('    // <halt>\n')
            label = self._UniqueLabel()
            self._WriteCode('@%s, (%s), 0;JMP' % (label, label))
        self.file.close()


    def SetFileName(self, fileName):
        """
        Sets the current file name to 'fileName'.
        Restarts the local label counter.

        Strips the path and extension.  The resulting name must be a
        legal Hack Assembler identifier.
        """
        if (debug):
            self.file.write('    // File: %s\n' % (fileName))
        self.fileName = os.path.basename(fileName)
        self.fileName = os.path.splitext(self.fileName)[0]
        self.functionName = None


    def Write(self, line):
        """
        Raw write for debug comments.
        """
        self.file.write(line + '\n')


    def WriteInit(self, sysinit = True):
        """
        Write the VM initialization code:
            Set the SP to 256.
            Initialize system pointers to -1.
            Call Sys.Init()
            Halt loop
        Passing sysinit = False oly sets the SP.  This allows the simpler
        VM test scripts to run correctly.
        """
        if (debug):
            self.file.write('    // Initialization code\n')
        self.needHalt = not sysinit
        self._WriteCode('@256, D=A, @SP, M=D')
        if sysinit:
            self._WriteCode('A=A+1, M=-1, A=A+1, M=-1, A=A+1, M=-1, A=A+1, M=-1')
            self.WriteCall('Sys.init', 0)
            halt = self._UniqueLabel()
            self._WriteCode('@%s, (%s), 0;JMP' % (halt, halt))


    def WritePushPop(self, commandType, segment, index):
        """
        Write Hack code for 'commandType' (C_PUSH or C_POP).
        'segment' (string) is the segment name.
        'index' (int) is the offset in the segment.
        """
        if commandType == C_PUSH:
            if (debug):
                self.file.write('    // push %s %d\n' % (segment, int(index)))
            if segment == T_CONSTANT:
                self._WritePushValue(index)
            elif segment == T_STATIC:
                self._WritePushMem(self._StaticLabel(index))
            elif segment == T_POINTER:
                self._WritePushMem(3 + int(index))
            elif segment == T_TEMP:
                self._WritePushMem(5 + int(index))
            else:
                self._WriteGetPtrAD(segment, index)
                self._WriteCode('D=M')
                self._WritePushD()

        elif commandType == C_POP:
            if (debug):
                self.file.write('    // pop %s %d\n' % (segment, int(index)))
            if segment == T_STATIC:
                self._WritePopMem(self._StaticLabel(index))
            elif segment == T_POINTER:
                self._WritePopMem(3 + int(index))
            elif segment == T_TEMP:
                self._WritePopMem(5 + int(index))
            else:
                self._WriteGetPtrAD(segment, index)
                self._WriteCode('@R15, M=D')
                self._WritePopD()
                self._WriteCode('@R15, A=M, M=D')
        else:
            raise ValueError('Bad push/pop command (%s)' % commandType)


    def WriteArithmetic(self, command):
        """
        Write Hack code for stack arithmetic 'command' (str).
        """
        if (debug):
            self.file.write('    // %s\n' % command)
        if command == T_ADD:
            self._WriteStackMath2('+')
        elif command == T_SUB:
            self._WriteStackMath2('-')
        elif command == T_AND:
            self._WriteStackMath2('&')
        elif command == T_OR:
            self._WriteStackMath2('|')
        elif command == T_NEG:
            self._WriteStackMath1('-')
        elif command == T_NOT:
            self._WriteStackMath1('!')
        elif command == T_EQ:
            self._WriteCompare('JEQ')
        elif command == T_GT:
            self._WriteCompare('JGT')
        elif command == T_LT:
            self._WriteCompare('JLT')
        else:
            raise ValueError('Bad arithmetic command: ' + command)


    def _WriteStackMath2(self, operator):
        """
        Write code for binary stack operation.
        """
        self._WriteCode('@SP, AM=M-1, D=M, A=A-1, M=M%sD' % operator)


    def _WriteStackMath1(self, operator):
        """
        Write code for unary stack operation.
        """
        self._WriteCode('@SP, A=M-1, M=%sM' % operator)


    def _WriteCompare(self, jmp):
        """
        Write code for arithmetic compare command.  'jmp' identifies
        the TRUE condition.
        """
        if jmp in self.cmpLabels:
            target = self.cmpLabels[jmp]
            retAddr = self._UniqueLabel()
            self._WriteMoveValue(retAddr, 'R13')
            self._WriteCode('@%s, 0;JMP, (%s)' % (target, retAddr))
        else:
            # Since this writes a subroutine we need to set the return
            # address even though we are going to enter it directly.
            retAddr = self._UniqueLabel()
            self._WriteMoveValue(retAddr, 'R13')
            self._WriteCompareCommon(jmp)
            self._WriteCode('(%s)' % retAddr)


    def _WriteCompareCommon(self, jmp):
        """
        Write the compare subroutine for 'jmp' comparison.
        """
        if debug:
            self.file.write('    // %s compare common code\n' % (jmp))
        writeTail = False;
        if not 'tail1' in self.cmpLabels:
            self.cmpLabels['tail1'] = self._UniqueLabel()
            self.cmpLabels['tail2'] = self._UniqueLabel()
            writeTail = True

        label0 = self._UniqueLabel()
        self.cmpLabels[jmp] = label0
        label1 = self.cmpLabels['tail1']
        label2 = self.cmpLabels['tail2']
        self._WriteCode('(%s)' % label0)
        self._WriteCode('@SP, A=M-1, D=M, A=A-1, D=M-D')
        self._WriteCode('@%s, D;%s' % (label1, jmp))
        self._WriteCode('@%s, D=0;JMP' % (label2))

        if writeTail:
            if debug:
                self.file.write('    // compare common tail code\n')
            self._WriteCode('(%s), D=-1, (%s)' % (label1, label2))
            self._WriteCode('@SP, AM=M-1, A=A-1, M=D')
            self._WriteCode('@R13, A=M, 0;JMP')


    def WriteLabel(self, label):
        """
        Write Hack code for 'label' VM command.
        """
        if (debug):
            self.file.write('    // label %s\n' % (label))
        self._WriteCode('(%s)' % self._LocalLabel(label))


    def WriteGoto(self, label):
        """
        Write Hack code for 'goto' VM command.
        """
        if (debug):
            self.file.write('    // goto %s\n' % (label))
        self._WriteCode('@%s, 0;JMP' % self._LocalLabel(label))


    def WriteIf(self, label):
        """
        Write Hack code for 'if-goto' VM command.
        """
        if (debug):
            self.file.write('    // if-goto %s\n' % (label))
        target = self._LocalLabel(label)

        #TODO: Write the code to complete the if-goto assuming that:
        # 1. the variable 'target' contains the location to jump to, and
        # 2. the top of the stack contains a value that if non-zero will cause a jump


    def WriteFunction(self, functionName, numLocals):
        """
        Write Hack code for 'function' VM command.
        """
        self.functionName = functionName
        if (debug):
            self.file.write('    // function %s %s\n' % (functionName, numLocals))

        numLocals = int(numLocals)

        #TODO: Write code to complete the function command in the VM language
        # the main tasks are:
        # 1. Create a label for the function name
        # 2. Initialize numLocals, local variables to 0 and place them on the stack
        #    initially, the SP is at the position of the first local.This can be
        #    done with a loop, or just writting the correct ML the correct number of times.
        #    for loops, try loop = self._UniqueLabel() to get a label for the ML.


    def WriteReturn(self):
        """
        Write Hack code for 'return' VM command.
        """
        # Jump to common 'return' code.
        # If this is is the first 'return', generate the common code.
        if (debug):
            self.file.write('    // return\n')

        if self.returnLabel != None:
            self._WriteCode('@%s, 0;JMP' % self.returnLabel)
        else:
            self._WriteReturnCommon()


    def _WriteReturnCommon(self):
        """
        IP  = Instruction Pointer
        RIP = Return Instruction Pointer
        RVAL= Return value
        Write ReturnCommon():
            Save RIP -- it gets clobbered by RVAL if call had no args
            Move RVAL to corect place on stack
            Discard working stack and locals
            Pop saved state
            Set SP to immediately after RVAL
            Jump to RIP
        """
        if debug:
            self.file.write('    // return common code\n')

        self.returnLabel = self._UniqueLabel()
        self._WriteCode('(%s)' % self.returnLabel)

        # TODO: Write the code below to handle the return, as specified in the book and notes.
        # In addition to self._WriteCode, you will find it useful to use the helper
        # functions self._WriteMoveMem and , self._WritePopMem
        # Study the helper functions and be prepared to report on how they work.
        self._WriteCode('@LCL, D=M, @5, A=D-A, D=M') # return IP
         self._WriteCode('@R14, M=D')                #   -> R14
         self._WritePopD()                           # return value
         self._WriteCode('@ARG, A=M, M=D')           #   -> ARG[0]
         self._WriteCode('D=A+1, @R15, M=D')         # ARG+1 -> R15
         self._WriteMoveMem('LCL', 'SP')             # discard locals
         self._WritePopMem('THAT')                   # restore state
         self._WritePopMem('THIS')
         self._WritePopMem('ARG')
         self._WritePopMem('LCL')
         self._WriteMoveMem('R15', 'SP')             # final SP
         self._WriteCode('@R14, A=M, 0;JMP')         # return to caller

    def WriteCall(self, functionName, numArgs):
        """
        Write Hack code for 'call' VM command.

        IP = Instruction pointer
        """
        # Save parameters into temp registers and jump to common 'call' code.
        # If this is is the first 'call', generate the common code.
        if (debug):
            self.file.write('    // call %s %s\n' % (functionName, numArgs))

        retAddr = self._UniqueLabel()
        self._WriteMoveValue(functionName, 'R15')   # target IP -> R15
        self._WriteMoveValue(numArgs, 'R14')        # numArgs -> R14
        self._WriteCode('@%s, D=A' % retAddr)       # return IP -> D

        if self.callLabel != None:                  # call function
            self._WriteCode('@%s, 0;JMP' % self.callLabel)
        else:
            self._WriteCallCommon()

        self._WriteCode('(%s)' % retAddr)           # return label


    def _WriteCallCommon(self):
        """
        Write CallCommon(R15=target, R14=numArgs, D=retIP)
        """
        if debug:
            self.file.write('    // call common code\n')
        self.callLabel = self._UniqueLabel()
        self._WriteCode('(%s)' % self.callLabel)

        # TODO: Write the code below to handle the call, as specified in the book and notes.
        # Minus the code in the method WriteCall above
        # In addition to self._WriteCode, you may find the helper
        # function self._WritePushMem useful.
        # In addition to storing the 'frame', you'll need to set LCL and ARG
        # as well as execute the jump to function address.
        self._WritePushD()                          # push return IP
         self._WritePushMem('LCL')                   # save state
         self._WritePushMem('ARG')
         self._WritePushMem('THIS')
         self._WritePushMem('THAT')
         self._WriteCode('@SP, D=M, @LCL, M=D')      # set new LCL
         self._WriteCode('@R14, D=D-M, @5, D=D-A, @ARG, M=D') # set new ARG
         self._WriteCode('@R15, A=M, 0;JMP')         # jump to function

    def _UniqueLabel(self):
        """
        Make a globally unique label.
        The label will be _sn where sn is an incrementing number.
        """
        self.labelNumber += 1
        return '_' + str(self.labelNumber)


    def _LocalLabel(self, name):
        """
        Make a function/module unique name for the label.
        If no function has been entered, the name will be
        FileName$$name. Otherwise it will be FunctionName$name.
        """
        if self.functionName != None:
            return self.functionName + '$' + name
        else:
            return self.fileName + '$$' + name


    def _StaticLabel(self, index):
        """
        Make a name for static variable 'index'.
        The name will be FileName.index
        """
        return self.fileName + '.' + str(index)


    def _WriteCode(self, code):
        """
        Write the comma separated commands in 'code'.
        """
        code = code.replace(',', '\n').replace(' ', '')
        self.file.write(code + '\n')


    def _WritePushD(self):
        """
        Write code to push D onto the stack.
        """
        self._WriteCode('@SP, AM=M+1, A=A-1, M=D')


    def _WritePushMem(self, label):
        """
        Write code to push contents of a memory location onto the stack.
        'label' my be an identifier or an absolute address.
        """
        self._WriteCode('@%s, D=M' %label)
        self._WritePushD()


    def _WritePushValue(self, value):
        """
        Write code to push an immediate value onto the stack.
        'value' may be an identifier, in which case its address is pushed.
        """
        if str(value) == '0':
            self._WriteCode('@SP, AM=M+1, A=A-1, M=0')
        elif str(value) == '1':
            self._WriteCode('@SP, AM=M+1, A=A-1, M=1')
        else:
            self._WriteCode('@%s, D=A' %value)
            self._WritePushD()


    def _WritePopD(self):
        """
        Write code to pop the stack into D.
        """
        self._WriteCode('@SP, AM=M-1, D=M')


    def _WritePopMem(self, label):
        """
        Write code to pop the stack into a memory location.
        'label' my be an identifier or an absolute address.
        """
        self._WritePopD()
        self._WriteCode('@%s, M=D' % label)


    def _WriteMoveMem(self, src, dest):
        """
        Write code to move the contents of 'src' memory location into
        'dest' memory location.  'src' and 'dest' my be identifiers
        or absolute addresses.
        """
        self._WriteCode('@%s, D=M, @%s, M=D' % (src, dest))


    def _WriteMoveValue(self, value, dest):
        """
        Write code to move an immediate value into 'dest' memory
        location.  'dest' my be an identifier or an absolute address.
        """
        if str(value) == '0':
            self._WriteCode('@%s, M=0' % dest)
        elif str(value) == '1':
            self._WriteCode('@%s, M=1' % dest)
        else:
            self._WriteCode('@%s, D=A, @%s, M=D' % (value, dest))


    def _WriteGetPtrAD(self, segment, index):
        """
        Write code to get pointer to segment[index] into A and D.
        """
        if segment == T_CONSTANT:
            raise ValueError('constant segment is virtual')
        elif segment == T_STATIC:
            raise ValueError('static segment is not indexed')
        elif segment == T_POINTER:
            raise ValueError('pointer segment is not dynamic')
        elif segment == T_TEMP:
            raise ValueError('temp segment is not dynamic')

        if segment == T_ARGUMENT:
            pointer = 'ARG'
        elif segment == T_LOCAL:
            pointer = 'LCL'
        elif segment == T_THIS:
            pointer = 'THIS'
        elif segment == T_THAT:
            pointer = 'THAT'
        else:
            raise ValueError('unknown segment name: %s' % segment)

        if (int(index) == 0):
            self._WriteCode('@%s, AD=M' % pointer)
        elif (int(index) == 1):
            self._WriteCode('@%s, AD=M+1' % pointer)
        else:
            self._WriteCode('@%s, D=M, @%d, AD=D+A' % (pointer, int(index)))
