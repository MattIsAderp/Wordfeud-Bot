# Scroll down to input your 

from info import BoardMultipliers, LetterValues
import re, copy

with open('words_SOWPODS', 'r') as file:
    AllWords = [line.rstrip('\n') for line in file]

AllWords = [Word.lower() for Word in AllWords]

with open('blacklist_SOWPODS', 'r') as file:            # Only useful if you're using a list of words that isn't used by wordfeud, every word in SOWPODS works in the game, so this really isn't necessary
    Blacklist = [line.rstrip('\n') for line in file]

def worth(x):
    return x[4]


def print2Dlist(l):
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in l]))


def listToString(s):
    str1 = ""
    for c in s:
        str1 += c
    return str1


def possibleWords(l, a):
    WordList = []
    letters = listToString(l).lower()
    for Word in AllWords:
        LettersTemp = letters[:]
        WordTemp = Word[:]
        canMakeWord = True
        for c in WordTemp:
            if c in LettersTemp:
                WordTemp = WordTemp.replace(c, "", 1)
                LettersTemp = LettersTemp.replace(c, "", 1)
            elif "?" in LettersTemp:
                WordTemp = WordTemp.replace(c, "", 1)
                LettersTemp = LettersTemp.replace("?", "", 1)
            else:
                canMakeWord = False
                break

        if canMakeWord:
            WordList.append(Word)
    return WordList


def generateMove(board, r, firstmove):
    moves = []
    columns = []

    for a, row in enumerate(board):
        print(str(round(50/15*a) + 3) + "% done")
        for b, letter in enumerate(row):
            if a == 0:
                columns.append([])
            columns[b].append(letter)
        filteredwords = possibleWords(r + [c for c in row if c not in "."], a)
        for word in filteredwords:
            for b, cell in enumerate(row):
                val = canPlace(word, board, a, b, "row", firstmove)
                if val:
                    moves.append([word, a, b, "row", val])

    for a, column in enumerate(columns):
        print(str(round(50 / 15 * a) + 53) + "% done")
        filteredwords = possibleWords(r + [c for c in column if c not in "."], a)
        for word in filteredwords:
            for b, cell in enumerate(column):
                val = canPlace(word, board, b, a, "col", firstmove)
                if val:
                    moves.append([word, b, a, "col", val])

    moves.sort(key=worth)
    return moves


def canPlace(word, board, pos1, pos2, direction, firstmove):
    blanks = []
    if word in Blacklist:
        return False
    if direction == "col":
        if pos1 + len(word) - 1 > 14:
            return False
        for i, c in enumerate(word):
            if board[pos1 + i][pos2] == ".":
                pass
            elif board[pos1 + i][pos2] == c:
                pass
            elif board[pos1 + i][pos2] == c.upper():
                pass
            else:
                return False
        if pos1 > 0:
            if board[pos1-1][pos2] != ".":
                return False
        if not pos1 + len(word) > 14:
            if board[pos1 + len(word)][pos2] != ".":
                return False

        isNextToWord = False

        if firstmove:
            for i, c in enumerate(word):
                if pos1 + i == 7 and pos2 == 7:
                    isNextToWord = True

        extra1 = 0
        extra2 = 0
        if pos2 < 14:
            extra1 = 1
        if pos2 > 0:
            extra2 = 1

        for pos in range(pos1, pos1 + len(word) - 1):
            extra3 = 0
            extra4 = 0
            if pos > 0:
                extra3 = 1
            if pos < 14:
                extra4 = 1

            if board[pos][pos2+extra1] != ".":
                if extra1 != 0:
                    isNextToWord = True
            if board[pos][pos2-extra2] != ".":
                if extra2 != 0:
                    isNextToWord = True
            if board[pos+extra4][pos2] != ".":
                if extra4 != 0:
                    isNextToWord = True
            if board[pos-extra3][pos2] != ".":
                if extra3 != 0:
                    isNextToWord = True
            if board[pos][pos2] != ".":
                isNextToWord = True

        if not isNextToWord:
            return False

        value = 0
        temprack = listToString(rack[:])
        tempword = listToString(word[:])
        layedletters = []
        lengthrack = len(temprack)
        wordmult = 1
        for i, c in enumerate(word):
            if c in temprack or board[pos1 + i][pos2].lower() == c:
                if board[pos1 + i][pos2].isupper():
                    charvalue = 0
                else:
                    charvalue = LetterValues[c]
                tempword = tempword.replace(c, "", 1)
                if not board[pos1 + i][pos2] == c and not board[pos1 + i][pos2] == c.upper():
                    temprack = temprack.replace(c, "", 1)
                    layedletters.append([pos1 + i, pos2])
                    if BoardMultipliers[pos1 + i][pos2] == "tl":
                        value += charvalue * 3
                    elif BoardMultipliers[pos1 + i][pos2] == "dl":
                        value += charvalue * 2
                    elif BoardMultipliers[pos1 + i][pos2] == "tw":
                        wordmult *= 3
                        value += charvalue
                    elif BoardMultipliers[pos1 + i][pos2] == "dw":
                        wordmult *= 2
                        value += charvalue
                    else:
                        value += charvalue
                elif not board[pos1 + i][pos2] == c.upper():
                    value += charvalue
            elif "?" in temprack:
                tempword = tempword.replace(c, "", 1)
                temprack = temprack.replace("?", "", 1)
                blanks.append([pos1 + i, pos2])
                layedletters.append([pos1 + i, pos2])

                if not board[pos1 + i][pos2] == c and not board[pos1 + i][pos2] == c.upper():
                    temprack = temprack.replace(c, "", 1)
                    layedletters.append([pos1 + i, pos2])
                    if BoardMultipliers[pos1 + i][pos2] == "tw":
                        wordmult *= 3
                        value += charvalue
                    elif BoardMultipliers[pos1 + i][pos2] == "dw":
                        wordmult *= 2
                        value += charvalue
            else:
                return False

        if len(temprack) == lengthrack:
            return False

        value *= wordmult

        ConnectedWords = connectedWords(board, pos1, pos2, word, direction, blanks)

        for w in ConnectedWords:
            if w[0].lower() not in AllWords or w[0].lower() in Blacklist or len(w[0]) < 2:
                return False

        for connectedword in ConnectedWords:
            WordAlreadyExist = True
            for i, c in enumerate(connectedword[0]):
                if board[connectedword[1]][connectedword[2] + i] != c:
                    WordAlreadyExist = False

            if not WordAlreadyExist:
                value += connectedword[3]

        if len(temprack) == 0:
            value += 40

        return value
    else:

        if pos2 + len(word) - 1 > 14:
            return False
        for i, c in enumerate(word):
            if board[pos1][pos2 + i] == ".":
                pass
            elif board[pos1][pos2 + i] == c:
                pass
            elif board[pos1][pos2 + i] == c.upper():
                pass
            else:
                return False
        if pos2 > 0:
            if board[pos1][pos2 - 1] != ".":
                return False
        if not pos2 + len(word) > 14:
            if board[pos1][pos2 + len(word)] != ".":
                return False

        isNextToWord = False

        if firstmove:
            for i, c in enumerate(word):
                if pos1 == 7 and pos2 + i == 7:
                    isNextToWord = True

        extra1 = 0
        extra2 = 0
        if pos1 < 14:
            extra1 = 1
        if pos1 > 0:
            extra2 = 1

        for pos in range(pos2, pos2 + len(word) - 1):
            extra3 = 0
            extra4 = 0
            if pos > 0:
                extra3 = 1
            if pos < 14:
                extra4 = 1
            if pos > 0:
                extra3 = 1
            if board[pos1][pos+extra4] != ".":
                isNextToWord = True
            if board[pos1][pos-extra3] != ".":
                if extra3 != 0:
                    isNextToWord = True
            if board[pos1+extra1][pos] != ".":
                if extra1 != 0:
                    isNextToWord = True
            if board[pos1-extra2][pos] != ".":
                if extra2 != 0:
                    isNextToWord = True
            if board[pos1][pos] != ".":
                isNextToWord = True

        if not isNextToWord:
            return False

        value = 0
        LocForMult1 = []
        LocForMult2 = []
        temprack = listToString(rack[:])
        tempword = listToString(word[:])
        layedletters = []
        lengthrack = len(temprack)
        wordmult = 1
        for i, c in enumerate(tempword):
            if c in temprack or board[pos1][pos2 + i] == c or board[pos1][pos2 + i] == c.upper():
                if board[pos1][pos2 + i].isupper():
                    charvalue = 0
                else:
                    charvalue = LetterValues[c]
                tempword = tempword.replace(c, "", 1)
                if not board[pos1][pos2 + i] == c and not board[pos1][pos2 + i] == c.upper():
                    temprack = temprack.replace(c, "", 1)
                    layedletters.append([pos1, pos2 + i])
                    LocForMult1.append(pos1)
                    LocForMult2.append(pos2 + i)
                    if BoardMultipliers[pos1][pos2 + i] == "tl":
                        value += charvalue * 3
                    elif BoardMultipliers[pos1][pos2 + i] == "dl":
                        value += charvalue * 2
                    elif BoardMultipliers[pos1][pos2 + i] == "tw":
                        wordmult *= 3
                        value += charvalue
                    elif BoardMultipliers[pos1][pos2 + i] == "dw":
                        wordmult *= 2
                        value += charvalue
                    else:
                        value += charvalue
                elif not board[pos1][pos2 + i] == c.upper():
                    value += charvalue
            elif "?" in temprack:
                tempword = tempword.replace(c, "", 1)
                temprack = temprack.replace("?", "", 1)
                blanks.append([pos1, pos2 + i])
                layedletters.append([pos1, pos2 + i])

                if not board[pos1][pos2 + i] == c and not board[pos1][pos2 + i] == c.upper():
                    temprack = temprack.replace(c, "", 1)
                    layedletters.append([pos1, pos2 + i])
                    LocForMult1.append(pos1)
                    LocForMult2.append(pos2 + i)
                    if BoardMultipliers[pos1][pos2 + i] == "tw":
                        wordmult *= 3
                    elif BoardMultipliers[pos1][pos2 + i] == "dw":
                        wordmult *= 2
            else:
                return False

        if len(temprack) == lengthrack:
            return False

        value *= wordmult

        ConnectedWords = connectedWords(board, pos1, pos2, word, direction, blanks)

        for w in ConnectedWords:
            if w[0].lower() not in AllWords or len(w[0]) < 2 or w[0].lower() in Blacklist:
                return False

        for connectedword in ConnectedWords:
            WordAlreadyExist = True
            cwval = 0
            mult = 1
            for i, c in enumerate(connectedword[0]):

                if board[connectedword[1] + i][connectedword[2]] != c:
                    WordAlreadyExist = False

            if not WordAlreadyExist:
                value += connectedword[3]

        if len(temprack) == 0:
            value += 40

        return value


def connectedWords(board, pos1, pos2, wordtocheck, direction, blanks):
    tempboard = copy.deepcopy(board)
    columns = []
    ConnectedWords = []
    if direction == "row":
        for i, pos in enumerate(range(pos2, pos2 + len(wordtocheck))):
            if tempboard[pos1][pos] == ".":
                if [pos1, pos] in blanks:
                    tempboard[pos1][pos] = wordtocheck[i].upper()
                else:
                    tempboard[pos1][pos] = wordtocheck[i]

        for a, row in enumerate(tempboard):
            for b, letter in enumerate(row):
                if a == 0:
                    columns.append([])
                if [a, b] in blanks:
                    columns[b].append(letter.upper())
                else:
                    columns[b].append(letter)

        # print2Dlist(tempboard)
        extra1 = 0
        extra2 = 0
        if pos2 > 0:
            extra1 = 1
        if not pos2 + len(wordtocheck) + 1 > 14:
            extra2 = 1
        for pos in range(pos2 - extra1, pos2 + len(wordtocheck) + extra2):
            column = listToString(columns[pos])
            wordsincolumn = [s for s in column.split(".") if s not in "."]
            for word in wordsincolumn:
                a = re.search(r"\b(" + word + r")\b", column)
                if a:
                    if a.start() <= pos1 <= a.end() and len(word) > 1:
                        val = 0
                        mult = 1
                        for i, c in enumerate(word):
                            if c.isupper():
                                pass
                            else:
                                carpos1 = a.start() + i
                                if carpos1 == pos1:
                                    if BoardMultipliers[pos1][pos] == "tw":
                                        mult *= 3
                                        val += LetterValues[c]
                                    elif BoardMultipliers[pos1][pos] == "dw":
                                        mult *= 2
                                        val += LetterValues[c]
                                    elif BoardMultipliers[pos1][pos] == "tl":
                                        val += LetterValues[c] * 3
                                    elif BoardMultipliers[pos1][pos] == "dl":
                                        val += LetterValues[c] * 2
                                    else:
                                        val += LetterValues[c]
                                else:
                                    val += LetterValues[c]

                        val *= mult
                        ConnectedWords.append([word, a.start(), pos, val])

        return ConnectedWords

    else:
        for i, pos in enumerate(range(pos1, pos1 + len(wordtocheck))):
            if tempboard[pos][pos2] == ".":
                if [pos, pos2] in blanks:
                    tempboard[pos][pos2] = wordtocheck[i].upper()
                else:
                    tempboard[pos][pos2] = wordtocheck[i]

        for a, row in enumerate(tempboard):
            for b, letter in enumerate(row):
                if a == 0:
                    columns.append([])
                if [a, b] in blanks:
                    columns[b].append(letter.upper())
                else:
                    columns[b].append(letter)

        extra1 = 0
        extra2 = 0
        if pos1 > 0:
            extra1 = 1
        if not pos1 + len(wordtocheck) + 1 > 14:
            extra2 = 1
        for pos in range(pos1 - extra1, pos1 + len(wordtocheck) + extra2):
            row = listToString(tempboard[pos])
            wordsinrow = [s for s in row.split(".") if s not in "."]
            for word in wordsinrow:
                a = re.search(r"\b(" + word + r")\b", row)
                if a:
                    if a.start() <= pos2 <= a.end() and len(word) > 1:
                        val = 0
                        mult = 1
                        for i, c in enumerate(word):
                            if c.isupper():
                                pass
                            else:
                                carpos2 = a.start() + i
                                if carpos2 == pos2:
                                    if BoardMultipliers[pos][pos2] == "tw":
                                        mult *= 3
                                        val += LetterValues[c]
                                    elif BoardMultipliers[pos][pos2] == "dw":
                                        mult *= 2
                                        val += LetterValues[c]
                                    elif BoardMultipliers[pos][pos2] == "tl":
                                        val += LetterValues[c] * 3
                                    elif BoardMultipliers[pos][pos2] == "dl":
                                        val += LetterValues[c] * 2
                                    else:
                                        val += LetterValues[c]
                                else:
                                    val += LetterValues[c]

                        val *= mult
                        ConnectedWords.append([word, pos, a.start(), val])
        return ConnectedWords



#English international

Board =        [[".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],  # Current state of the board, replace
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],  # "." with the letter on that position,
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],  # if the letter is a blank letter (gives 0 points),
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],  # put it as a capital letter instead, so that the
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],  # program knows to not count it towards the total points.
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."]]


rack = ["o", "a", "n", "i", "u", "y", "n"]  #Put all of your letters, here, if you have a blank letter put it as "?"
moves = generateMove(Board, rack, True)   #arg1: Name of board, arg2: name of rack, arg3: True if you're playing the first move of the game, False for the rest of the game
moves.reverse()
print("Generated " + str(len(moves)) + " possible moves.")
print2Dlist(moves[:10])
