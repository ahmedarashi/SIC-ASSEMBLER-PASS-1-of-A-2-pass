import os
from collections import namedtuple

AppStruct = namedtuple('AppStruct', "Value Length Address")
# define OPTAB
OPERATIONTABEL = {  # mnemonic : opcode
"ADD": "18",
    "AND": "40",
    "COMP": "28",
    "DIV": "24",
    "J": "3C",
    "JEQ": "30",
    "JGT": "34",
    "JLT": "38",
    "JSUB": "48",
    "LDA": "00",
    "LDCH": "50",
    "LDL": "08",
    "LDX": "04",
    "MUL": "20",
    "OR": "44",
    "RD": "D8",
    "RSUB": "4C",
    "STA": "0C",
    "STCH": "54",
    "STL": "14",
    "STSW": "E8",
    "STX": "10",
    "SUB": "1C",
    "TD": "E0",
    "TIX": "2C",
    "WD": "DC"
}
# define the directives
DIRECTIVES = ['START', 'END', 'BYTE', 'WORD', 'RESB', 'RESW', 'BASE']

ErrFlag = False
try:
    inputFile = open("input.asm", "r")  # read sic file
except:
    print("The file: " + " does not exist, please check the name correctly.")
    ErrFlag = True
    symtab = open("SymbolTab.txt", "w");
outputFile = open("intermediate.txt", "w")  # create output file
#listFile = open("list.txt", "w")  # write to list file
objectFile = open("ObjectProgram.txt", "w")  # write to object file

while ErrFlag:
    break

Lines = inputFile.readlines()  # read the input file line by line
# define each column as a list
LOCCOUNTER = list()
LABEL = list()
OPCODE = list()
OPERAND = list()
LITERAL = {}  # {key, value}
SYMBOL = {}
ERRORS = []
jump = False
noOfLiterals = 0
index = 0
LOCATION = int("0000", base=16)
progName = Lines[0][0:9].strip()
first_line = Lines[0]
byteLen = 0
isJump = False
isLiteral = False
isIndexed = False
objText = ""
listText = ""
ObjectCodesArray = []
LocctrArray = []

if first_line[11:19].strip() == 'START':
    LOCATION = int(first_line[21:38].strip(), base=16)
    # add first line to intermediateFile
    baseLoc = LOCATION
    LOCCOUNTER.append(hex(baseLoc))
    LABEL.append(first_line[0:9])
    OPCODE.append(first_line[11:19])
    OPERAND.append(first_line[21:38].strip())
else:
    LOCATION = int("0000", base=16)
    baseLoc = LOCATION

start_location = baseLoc

for lineIndex, line in enumerate(Lines):
    tempLocCtr = baseLoc
    if lineIndex == 0: continue

    if line.strip()[0] != '.':
        _LABEL = line[0:9].strip()
        _OPCODE = line[11:19].strip()
        _OPERAND = line[21:38].strip()

        if _LABEL != '':
            if _LABEL in SYMBOL:
                ERRORS.append('ERROR-Line:' + str(lineIndex) + ' : duplicate symbol')
                ErrFlag = True
            elif (_LABEL != ''):
                # insert {LABEL,baseLoc} into SYMTAB
                SYMBOL[_LABEL] = baseLoc

        # search OPTAB for opcode
        if (_OPCODE in OPERATIONTABEL):
            baseLoc = baseLoc + 3
        elif (_OPCODE == 'WORD'):
            baseLoc += 3
        elif (_OPCODE == 'RESW') and (_OPERAND != ''):
            baseLoc += 3 * int(_OPERAND)
        elif (_OPCODE == 'RESB') and (_OPERAND != ''):
            baseLoc += int(_OPERAND)
        elif (_OPCODE == 'BYTE'):
            if (_OPERAND[0] == 'C'):
                # -3 ==> to ignore the three characters ==> (C'')
                byteLen = len(_OPERAND) - 3
                baseLoc += byteLen
            elif _OPERAND[0] == 'X':
                byteLen = (int((len(_OPERAND) - 3) / 2))  # it will increase one byte to the baseLoc
                baseLoc += byteLen
                # LTORG && END Processing
        elif (_OPCODE == 'LTORG' or _OPCODE == 'END'):
            LABEL.append(_LABEL)
            OPCODE.append(_OPCODE)
            OPERAND.append(_OPERAND)

            LOCCOUNTER.append(hex(baseLoc))
            displacement = 0
            totalDisplacement = 0
            for _literal in LITERAL:

                if (LITERAL[_literal].Address == '0000'):
                    LITERAL[_literal] = AppStruct(LITERAL[_literal].Value, LITERAL[_literal].Length,
                                                  hex(tempLocCtr + displacement))

                    LABEL.append("")
                    OPCODE.append("")
                    OPERAND.append(_literal)
                    LOCCOUNTER.append(str(hex(tempLocCtr + displacement)))
                    displacement += int(LITERAL[_literal].Length)
                    totalDisplacement += displacement
                    baseLoc += displacement
        else:
            ERRORS.append('ERROR at line ' + str(lineIndex) + ': invalid operation code : ' + _OPCODE)
            errorFlag = True

        if (_OPERAND != ''):
            # =C'-----' literal
            if (_OPERAND[0:2] == '=C'):

                name = _OPERAND
                value = ''
                for char in _OPERAND[3:len(_OPERAND) - 1]:
                    asc = hex(ord(char))  # ASCII value
                    value = value + str(asc[2:])
                # -4 is to ignore the four characters ==> (=C'')
                length = len(_OPERAND) - 4
                newLiteral = AppStruct(value, length, '0000')
                LITERAL[name] = newLiteral



            elif (_OPERAND[0:2] == '=X'):

                name = _OPERAND
                value = _OPERAND[3:len(_OPERAND) - 1]
                length = 1
                newLiteral = AppStruct(value, length, '0000')
                LITERAL[name] = newLiteral
                # LOCCTR += length

                # write line to intermediate readFile, remove comment

        if (_OPCODE != 'LTORG' and _OPCODE != 'END'):  # END,LTORG lines have been written above
            LOCCOUNTER.append(hex(tempLocCtr))
            LABEL.append(_LABEL)
            OPCODE.append(_OPCODE)
            OPERAND.append(_OPERAND)

ProgramLength = baseLoc - start_location - 1 + 1
print("\nProgram Name: " + str(progName) + "\n" + "Program Length: " + str(hex(ProgramLength)[2:]).upper() + " H\n")
print('\n\n         SYMTAB')
print('_________________________\n|  LABEL   |  LOCATION  |\n|-----------------------|')
for lineNumber, Label in enumerate(SYMBOL):
    print("|  " + Label.ljust(7) + " |   " + str(hex(SYMBOL[Label])).upper()[2:] + ' H   |')
print('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n\n')

listLength = len(LOCCOUNTER)
for item in range(listLength):
    ll = str(LOCCOUNTER[item].upper()[2:]) + "   " + str(LABEL[item].ljust(10)) + "   " + str(
        OPCODE[item].ljust(10)) + "   " + str(OPERAND[item].ljust(10)) + "\n"
    outputFile.write(str(ll))

    # في قسم طباعة العناوين في ملف symbolTab.txt
with open("symbolTab.txt", "w") as symtab:
    symtab.write("\n\n         SYMTAB\n")
    symtab.write("_________\n|  LABEL   |  LOCATION  |\n|-----------------------|\n")

    mainAddresses = {}  # لتخزين العناوين الرئيسية لكل Label

    for lineNumber, Label in enumerate(SYMBOL):
        symtab.write("|  " + Label.ljust(7) + " |   " + str(hex(SYMBOL[Label])).upper()[2:] + ' H   |\n')

        # احتفظ بالعنوان الرئيسي لل Label الحالي
        mainAddresses[Label] = SYMBOL[Label]



    # قم بطباعة العناوين الرئيسية في النص النهائي
    print("\nMain Addresses:")
    for Label, address in mainAddresses.items():
        print(f"{Label} {hex(address)[2:].upper()}")

outputFile.close()
