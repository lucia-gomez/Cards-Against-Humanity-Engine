from typing import List
from state import WhiteCard, BlackCard
import csv

def loadWhiteCards(filename: str) -> List[WhiteCard]:
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        cards = [WhiteCard(False, ''.join(row)) for row in reader if row != []]
    file.close()
    return cards

def loadBlackCards(filename: str) -> List[BlackCard]:
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        cards = [BlackCard(row[0], int(row[1])) for row in reader if row != []]
    file.close()
    return cards
