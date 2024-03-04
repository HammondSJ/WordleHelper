import string
from pathlib import Path
from collections import Counter
from itertools import chain
import operator

dictionary = "dictionary.txt"
allowedchar = set(string.ascii_letters)

#These are the default settings
maxattempts = 6
maxlength = 5

#Variable settings for word length, allowing use with wordle variants
def settings():
    global maxlength
    print("Do you want to start the solver with default settings?")
    default = input("Y/N >   ")
    if default.upper() == "N":
        print("Input the word length you are solving for")
        maxlength = int(input("(Between 3 and 12) >   "))
        return
    else:
        return
#Need to call settings before anything else gets generated
settings()

#Creates a list of all the words that fits current settings
wordlist = {
    word.lower()
    for word in Path(dictionary).read_text().splitlines()
    if len(word) == maxlength and set(word) < allowedchar
}

#Counts the occurences of each letter in the wordlist
lettercount = Counter(chain.from_iterable(wordlist))

#Calculates the frequency that letters appear in the current wordlist
letterfreq = {
    character: value / lettercount.total()
    for character, value in lettercount.items()
}

#Weighs how common each word is, and then sorts them so they'll show what word is the likeliest
def calcwordcomm(word):
    score = 0.0
    for char in word:
        score += letterfreq[char]
    return score / (maxlength - len(set(word)) + 1)

def sortbywordcomm(words):
    sortby = operator.itemgetter(1)
    return sorted(
        [(word, calcwordcomm(word)) for word in words],
        key=sortby,
        reverse=True,
    )

def displaytable(wordcomm):
    for(word, freq) in wordcomm:
        print(f"{word:<10} | {freq:<5.2}")

#Inputs for both the current word, and the colour coded response from wordle
def inputword():
    while True:
        word = input("Type the word you entered>  ")
        if len(word) == maxlength and word.lower() in wordlist:
            break
    return word.lower()

def inputresponse():
    print("Type the colour coded response from Wordle:")
    print(" G for Green")
    print(" Y for Yellow")
    print(" X for Grey")
    while True:
        response = input("Response from Wordle>  ")
        if len(response) == maxlength and set(response) <= {"G", "Y", "X"}:
            break
        else:
            print(f"Error - {response} is an invalid answer")
    return response

#Creating a list of sets of a size equal to the word length, allowing the program to remove letters in each position
wordvector = [set(string.ascii_lowercase) for _ in range(maxlength)]

def matchvector(word, wordvector):
    assert len(word) == len(wordvector)
    for letter, vletter in zip(word, wordvector):
        if letter not in vletter:
            return False
    return True

def match(wordvector, possiblewords):
    return [word for word in possiblewords if matchvector(word, wordvector)]

#The main bulk of the solver, in charge of calling all the other functions and processing the response
def solve():
    possiblewords = wordlist.copy()
    wordvector = [set(string.ascii_lowercase) for _ in range(maxlength)]
    for attempt in range(1, maxattempts + 1):
        print(f"Attempt {attempt} with {len(possiblewords)} possible words remaining")
        displaytable(sortbywordcomm(possiblewords)[:15])
        word = inputword()
        response = inputresponse()
        for idx, letter in enumerate(response):
            if letter == "G":
                wordvector[idx] = {word[idx]}
            elif letter == "Y":
                try:
                    wordvector[idx].remove(word[idx])
                except KeyError:
                    pass
            elif letter == "X":
                for vector in wordvector:
                    try:
                        vector.remove(word[idx])
                    except KeyError:
                        pass
        possiblewords = match(wordvector, possiblewords)

solve()