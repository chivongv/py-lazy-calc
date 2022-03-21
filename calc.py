#!/usr/bin/python

import sys
from enum import Enum

mInputs = {}
mMappedValues = {}
mVisited = set()

class LoopException(Exception):
    """Raised when the inputs created a loop"""
    pass

class Commands(Enum):
    QUIT = "quit"
    PRINT = "print"
    CLEAR = "clear"
    RESET = "reset"

    def toString():
        return "print quit clear reset"

class Operations(Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"

    def toString():
        return "add subtract multiply"

def printUsage():
    print('Input usage: <register> <operation> <value>' +
    '\nOperations: ' + Operations.toString() +
    '\nCommands: ' + Commands.toString() + '\n')

def isNumeric(k):
    try:
        a = int(k)
        return True
    except ValueError:
        # if k is not a value, check if k is not in mInputs then add [] to mInputs[k]
        if(not k in mInputs):
            mInputs[k] = []
        return False

def isValidOperator(op):
    for i in Operations:
        if(op == i.value):
            return True
    return False

def printInvalidCommand(line):
    print('Command \'' + line + '\' is not valid. Please enter a valid command. Commands: ' + Commands.toString())

def mappedToInput(reg, val):
    return [reg, 'add', val]

def clearInputs():
    mInputs.clear()

def resetAll():
    mInputs.clear()
    mMappedValues.clear()

def debug():
    print(mInputs)
    print(mMappedValues)

def evaluate(reg):
    if(isNumeric(reg)):
        return int(reg)

    # returns value if reg already been evaluated
    if(mMappedValues.get(reg)):
        return mMappedValues.get(reg)

    if (reg in mVisited):
        # Here we can either 1. log out error and exit script or 2. throw error and catch it higher up. I choose option 2
        raise LoopException("Cycle detected. Please check the inputs.")
    
    result = 0
    mVisited.add(reg)
    # get only the inputs for the current reg
    regInputs = mInputs[reg]

    for i in regInputs:
        operator = i[1].lower()

        # skip if mReg is not same as reg
        if(i[0] != reg):
            continue
        
        if(operator == Operations.ADD.value):
            result += evaluate(i[2])

        elif(operator == Operations.SUBTRACT.value):
            result -= evaluate(i[2])
            
        elif(operator == Operations.MULTIPLY.value):
            result *= evaluate(i[2])

    mMappedValues[reg] = result
    mInputs[reg] = [] # clear the inputs for reg since we already evaluated reg
    return result

def processLine(line):
    op = line.lower().split(" ")
    currentReg = op[0]
    opLength = len(op)

    if(opLength == 3):
        operator = op[1].lower()

        if(isNumeric(currentReg)):
            print("Register '" + currentReg + "' is not valid. Please enter a alphanumeric register name.")
            return

        if(isValidOperator(operator)):
            if(currentReg in mInputs):
                # get inputs for the current reg, append current line and put it in mInputs
                regInputs = mInputs.get(currentReg)
                regInputs.append(op)
                mInputs[currentReg] = regInputs
            else:
                mInputs[currentReg] = [op]
            
        else:
            print('Operator \'' + operator + '\' is not supported yet. Please enter one of these operators: ' + Operations.toString())

    elif(opLength == 2):
        currentCommand = op[0]
        currentReg = op[1]
        if(currentCommand.lower() == Commands.PRINT.value):
            if(currentReg in mInputs):
                try:
                    # make use of evaluated regs
                    if(currentReg in mMappedValues and len(mInputs[currentReg]) > 0):
                        input = mappedToInput(currentReg, mMappedValues[currentReg])
                        mInputs[currentReg].insert(0, input) # add mapped to beginning of mInputs
                        mMappedValues.pop(currentReg, None) # remove reg from mMappedValues
                    mVisited.clear()
                    print(evaluate(currentReg))
                except LoopException:
                    print("Cycle detected. Please check the inputs.")
            else:
                print("This register name '" + currentReg + "' does not exists.")

    elif (currentReg == "debug"):
        debug()

    elif (currentReg == "clear"):
        clearInputs()

    elif (currentReg == "reset"):
        resetAll()

    else:
        printInvalidCommand(line)

def main():
    print('Welcome to simple calc with lazy evaluation')
    printUsage()

    # Reading files
    if (len(sys.argv) >= 2):
        for i in range(1, len(sys.argv)):
            try:
                file = open(sys.argv[i], 'r')
                print("Reading from file \'" + sys.argv[i] + "\'")
                for line in file:
                    if(line.lower().strip() == Commands.QUIT.value):
                        break
                    processLine(line.strip())
                file.close()
                print('')
                mInputs.clear()
                mMappedValues.clear()
            except FileNotFoundError:
                print('File \'' + sys.argv[i] + '\' can not be found.\n')

    # Read line by line from user
    else:
        line = input('Please enter your command: ')
        while(not line.lower().__contains__(Commands.QUIT.value)):
            processLine(line)
            line = input('Please enter your command: ')
            

if __name__ == "__main__":
    main()