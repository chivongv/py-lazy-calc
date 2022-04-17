#!/usr/bin/python3

import sys
from enum import Enum

m_inputs = {}
m_mapped_values = {}
m_visited = set()

class InputLoopError(Exception):
    """Raised when the inputs created a loop"""
    pass

class Commands(Enum):
    QUIT = "quit"
    PRINT = "print"
    CLEAR = "clear"
    RESET = "reset"

    def to_string():
        return "print quit clear reset"

class Operations(Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"

    def to_string():
        return "add subtract multiply"

def print_usage():
    print('Input usage: <register> <operation> <value>' +
    '\nOperations: ' + Operations.to_string() +
    '\nValid commands: ' + Commands.to_string() + '\n')

def is_numeric(k):
    try:
        a = int(k)
        return True
    except ValueError:
        # if k is not a value, check if k is not in m_inputs then add [] to m_inputs[k]
        if(not k in m_inputs):
            m_inputs[k] = []

        return False

def is_valid_operator(op):
    for i in Operations:
        if(op == i.value):
            return True

    return False

def print_invalid_command(command):
    print('Command \'' + command + '\' is not valid. Please enter a valid command. Commands: ' + Commands.to_string())

def mapped_to_input(reg, val):
    return [reg, 'add', val]

def clear_inputs():
    m_inputs.clear()

def reset_all():
    m_inputs.clear()
    m_mapped_values.clear()

def debug():
    print(m_inputs)
    print(m_mapped_values)

def evaluate(reg):
    if(is_numeric(reg)):
        return int(reg)

    # returns value if reg already been evaluated
    if(m_mapped_values.get(reg)):
        return m_mapped_values.get(reg)

    if (reg in m_visited):
        raise InputLoopError("Cycle detected. Please check the inputs.")
    
    result = 0
    m_visited.add(reg)
    # get only the inputs for the current reg
    reg_inputs = m_inputs[reg]

    for i in reg_inputs:
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

    m_mapped_values[reg] = result
    m_inputs[reg] = [] # clear the inputs for reg since we already evaluated reg
    return result

def process_iine(line):
    op = line.lower().split(" ")
    current_reg = op[0]
    op_length = len(op)

    if(op_length == 3):
        operator = op[1].lower()

        if(is_numeric(current_reg)):
            print("Register '" + current_reg + "' is not valid. Please enter a alphanumeric register name.")
            # we can not have numeric register name due to e.g. 2 add 1, A add 2 -> should 2 be evaluated here as reg or number?
            return

        if(is_valid_operator(operator)):
            if(current_reg in m_inputs):
                # get inputs for the current reg, append current line and put it in m_inputs
                reg_inputs = m_inputs.get(current_reg)
                reg_inputs.append(op)
                m_inputs[current_reg] = reg_inputs
            else:
                m_inputs[current_reg] = [op]
            
        else:
            print('Operator \'' + operator + '\' is not supported yet. Please enter one of these operators: ' + Operations.to_string())

    elif(op_length == 2):
        current_command = op[0]
        current_reg = op[1]

        if(current_command.lower() == Commands.PRINT.value):
            if(current_reg in m_inputs):
                try:
                    # make use of evaluated regs
                    if(current_reg in m_mapped_values and len(m_inputs[current_reg]) > 0):
                        input = mapped_to_input(current_reg, m_mapped_values[current_reg])
                        m_inputs[current_reg].insert(0, input) # add mapped to beginning of m_inputs
                        m_mapped_values.pop(current_reg, None) # remove reg from m_mapped_values

                    m_visited.clear()
                    print(evaluate(current_reg))

                except InputLoopError:
                    print("Cycle detected. Please check the inputs.")

                except Exception as e:
                    print("Something went wrong during evaluation. " + e)
            else:
                print("This register name '" + current_reg + "' does not exists.")
        else:
            print_invalid_command(current_command)

    elif (current_reg == "debug"):
        print("Debugging...")
        debug()

    elif (current_reg == "clear"):
        clear_inputs()
        print("All inputs has been cleared.")

    elif (current_reg == "reset"):
        reset_all()
        print("All values has been reseted.")

    elif (current_reg == "print"):
        print("Please add a register name along with print e.g. print <register>")

    else:
        print_invalid_command(line)

def main():
    print('Welcome to simple calc with lazy evaluation')
    print_usage()

    # Reading files
    if (len(sys.argv) >= 2):
        for i in range(1, len(sys.argv)):
            try:
                file = open(sys.argv[i], 'r')
                print("Reading from file \'" + sys.argv[i] + "\'")

                for line in file:
                    if(line.lower().strip() == Commands.QUIT.value):
                        break
                    process_iine(line.strip())

                file.close()
                print('')
                m_inputs.clear()
                m_mapped_values.clear()

            except FileNotFoundError:
                print('File \'' + sys.argv[i] + '\' can not be found.\n')

            except Exception as e:
                print("Something went wrong during reading files. " + e)

    # Read line by line from user
    else:
        line = input('Please enter your command: ')

        while(not line.lower() == Commands.QUIT.value):
            process_iine(line)
            line = input('Please enter your command: ')
            
if __name__ == "__main__":
    main()