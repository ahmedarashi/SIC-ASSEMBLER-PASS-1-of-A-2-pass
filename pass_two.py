from pass_one import *

intermediateFile = open("intermediate.txt", "r")
contents = intermediateFile.readlines()

objText = "H^" + progName.ljust(6) + "^" + str(hex(start_location))[2:].zfill(6) + "^" + hex(ProgramLength)[2:].zfill(
    6).upper() + "\n"  # +

objectCode = ""
for lineNumber, line in enumerate(contents):
    opcode1 = line[20:32].strip()
    label1 = line[7:19].strip()
    operand1 = line[33:].strip()
    location1 = line[0:4].strip()

    if (isJump and (opcode1 != 'RESW' and opcode1 != 'RESB')):
        # this means that the jump has reached its end
        isJump = False
        ObjectCodesArray.append('JumpEndsAt' + location1)  # (special jump item)
        LocctrArray.append('JumpHere')
    if (opcode1 == ''):
        objectCode = str(LITERAL[operand1][0])
    elif opcode1 in OPERATIONTABEL:
        _Opcode = OPERATIONTABEL[opcode1]

        if (operand1 == ''):
            operandValue = "0000"
        elif (operand1 in SYMBOL):
            operandValue = str(hex(SYMBOL[operand1])[2:])
        elif (operand1 in LITERAL):
            isLiteral = True
            operandValue = LITERAL[operand1][2][2:]
        elif (operand1[len(operand1) - 2:] == ',X'):
            isIndexed = True
            oplen = len(operand1) - 2
            tempOperand = operand1[:oplen]
            if (tempOperand in SYMBOL):
                modifiedOperand = int(hex(SYMBOL[tempOperand]), base=16)
                modifiedOperand += 32768
                operandValue = hex(modifiedOperand)[2:]


        else:  # error invalid operand
            ERRORS.append("ERROR-at Loc " + location1 + ": invalid operand: " + operand1)
        if (isLiteral or isIndexed):
            oop = str(_Opcode)
            objectCode = oop + str(operandValue).upper()
        else:
            objectCode = (_Opcode + operandValue.zfill(4)).upper()

    elif opcode1 == "RESW" or opcode1 == "RESB":
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        isJump = True  # begin or continue the current jump
        continue
    elif (opcode1 == "START"):
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        continue
    elif (opcode1 == "BYTE"):
        if (operand1[0] == 'X'):
            operandValue = operand1[2:len(operand1) - 1]
        elif (operand1[0] == 'C'):
            operandValue = ""
            # Calculate the value between the two parentheses C'---'
            for char in operand1[2:len(operand1) - 1]:
                asc = hex(ord(char))  # ASCII value
                operandValue = operandValue + str(asc[2:])  # to hex
                # print(operand_value)

        else:
            ERRORS.append("ERROR-at Loc " + location1 + ": the BYTE instruction should have either C or X")

        objectCode = operandValue
    elif (opcode1 == "WORD"):
        operandValue = hex(int(operand1))[2:]
        objectCode = operandValue.zfill(6)
    elif (opcode1 == "END"):
        ll1 = location1.upper() + "\t      " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        continue
    elif (opcode1 == "LTORG"):
        ll1 = location1.upper() + "\t      " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        continue
    elif (opcode1 in LITERAL):
        objectCode = str(LITERAL[opcode1][0])
    else:
        # error invalid instruction
        ERRORS.append("ERROR-at Loc " + location1 + ": invalid instruction: " + opcode1)

    ObjectCodesArray.append(objectCode)
    LocctrArray.append(location1)

    if (opcode1 in LITERAL):
        # line = line[:5] + "*" + line[6:] # adds a star at the start of the literal line (as in the textbook)
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(10) + ""
        listText += ll1 + "   " + objectCode.upper() + "\n"
    else:
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(10) + ""
        listText += ll1 + "   " + objectCode.upper() + "\n"

#listFile.write(listText)

while (len(ObjectCodesArray) > 0):
    lineLength = 30
    newLine = "T^" + LocctrArray[0].zfill(6)
    # While there are Object codes remaining
    while (len(ObjectCodesArray) > 0 and len(ObjectCodesArray[0]) / 2 <= lineLength and ObjectCodesArray[0][
                                                                                        0:10] != "JumpEndsAt"):  # Check for Special jumps Items
        lineLength -= len(ObjectCodesArray[0]) / 2
        objCod = "^" + ObjectCodesArray.pop(0)
        LocctrArray.pop(0)
        newLine = newLine + objCod

    # Delete the Special List Item ("JumpEndsAtXXXX"),("Jumphere")
    if (len(ObjectCodesArray) > 0 and ObjectCodesArray[0][0:10] == "JumpEndsAt"):
        ObjectCodesArray.pop(0)
        LocctrArray.pop(0)
    # Jump
    newLine = newLine[0:9].upper() + "" + hex(int(30 - lineLength))[2:].zfill(2).upper() + newLine[8:]
    objText += newLine + "\n"

objText += "E^" + str(hex(start_location))[2:].zfill(6)
objectFile.write(objText)

#listFile.close()
objectFile.close()

if len(ERRORS):
    for error in ERRORS:
        print(error)
    ERRORS.clear()