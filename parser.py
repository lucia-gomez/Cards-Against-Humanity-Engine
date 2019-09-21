from constants import LIMIT


def _pad(s):
    if len(s) < LIMIT:
        return s+(' ' * (LIMIT - len(s)))
    else: return s


def _chunk(s):
    i = LIMIT
    while i > 0 and s[i] != ' ':
        i -= 1
    if i == 0:
        return s[:LIMIT-1]+'-', s[LIMIT-1:]
    return s[:i], s[i+1:]


def _get_card_lines_helper(s, lines):
    if len(s) <= LIMIT:
        lines.append(_pad(s))
        return lines
    else:
        good, rest = _chunk(s)
        lines.append(_pad(good))
        return _get_card_lines_helper(rest, lines)


def get_card_lines(s):
    return _get_card_lines_helper(s, [])
