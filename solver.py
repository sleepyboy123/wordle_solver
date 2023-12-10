from collections import Counter
import numpy as np
import os
import re
import requests

# Initialise an array of all 5 letter words
if not os.path.exists("word_list.txt"):
    response = requests.get("https://meaningpedia.com/5-letter-words?show=all")
    pattern = re.compile(r'<span itemprop="name">(\w+)</span>')
    word_list = np.array(pattern.findall(response.text))
    np.savetxt('word_list.txt', word_list, fmt='%s')
else:
    word_list = np.loadtxt('word_list.txt', dtype=str)

# Initialise Variables for all guesses
word = ["", "", "", "", ""]
wrong_position = {}
unused_letters = set()

# Function to check if a worst is valid based on current information
def check_word(possible_word):
    # Perform a letter by letter check
    for a in range(len(possible_word)):
        # Possible word contains unused_letter
        if possible_word[a] in unused_letters:
            return False
        # Possible word does not contain letter in right position
        if word[a] and possible_word[a] != word[a]:
            return False
    # Perform a check on wrong positions
    for letter, wrong_pos in wrong_position.items():
        if letter not in possible_word:
            return False
        for pos in wrong_pos:
            if possible_word[pos] == letter:
                return False
    return True

# Best First Guess is CRANE
# Best Second Guess is PLUTO

while "" in word:
    guess = input("Please input your guess: ").upper()
    # Output will be given in this format
    # ? represents grey characters.
    # ?O represents orange letters
    # T represents green letters
    # Example input ? ? ?O ? T
    output = input("What does the output look like: ").upper().split(" ")

    for i in range(len(guess)):
        # Handle unused characters
        if output[i] == "?" and guess[i] not in wrong_position and guess[i] not in word:
             unused_letters.add(guess[i])

        # Handle correct characters in correct position
        if output[i] == guess[i]:
            word[i] = guess[i]

        # Handle correct characters in wrong position
        if output[i] == "?" + guess[i]:
            if guess[i] in wrong_position:
                wrong_position[guess[i]].append(i)
            else:
                wrong_position[guess[i]] = [i]

    # Fetch possible answers for next guess
    possible_next_guess = []

    for possible_word in word_list:
        upper_possible_word = possible_word.upper()
        if check_word(upper_possible_word):
            possible_next_guess.append(upper_possible_word)

    # Reduce the total word list based on what we have filtered
    word_list = possible_next_guess

    # Find the most common letters and use that to calculate a weightage
    most_common_letters = Counter(c for w in possible_next_guess for c in w if c.isalpha())
    weighted_possible_next_guess = []
    for possible in possible_next_guess:
        score = 0
        for l in possible:
            score += most_common_letters[l]
        possible_object = {"word": possible, "score": score}
        weighted_possible_next_guess.append(possible_object)

    weighted_possible_next_guess = sorted(weighted_possible_next_guess, key=lambda x: x["score"], reverse=True)

    print(weighted_possible_next_guess)
    print(len(weighted_possible_next_guess))
    print("most_common_letters", most_common_letters)
    print("unused_letters ", unused_letters)
    print("word", word)
    print("wrong_position", wrong_position)
    print("\n")
