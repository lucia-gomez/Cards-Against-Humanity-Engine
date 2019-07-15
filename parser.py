from constants import LIMIT


def pad(s):
    if len(s) < LIMIT:
        return s+(' ' * (LIMIT - len(s)))
    else: return s


def chunk(s):
    i = LIMIT
    while i > 0 and s[i] != ' ':
        i -= 1
    if i == 0:
        return s[:LIMIT-1]+'-', s[LIMIT-1:]
    return s[:i], s[i+1:]


def getCardLinesHelper(s, lines):
    if len(s) <= LIMIT:
        lines.append(pad(s))
        return lines
    else:
        good, rest = chunk(s)
        lines.append(pad(good))
        return getCardLinesHelper(rest, lines)


def getCardLines(s):
    return getCardLinesHelper(s, [])
