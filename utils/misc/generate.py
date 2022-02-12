import random

BEGIN = "BEGIN"
END = "END"
LENGTH = 50


async def print_dict_file(dictionary):
    f = open("dictionary.txt", "w")
    for x in dictionary:
        f.write(x + " " + str(dictionary[x]) + "\n")
    f.close()


async def generate(history: list, length):
    strings = list()
    for row in history:
        strings.append(row.replace('\n', ' ').lower())
    strs = set()
    for x in strings:
        strs.add(x.replace("\n", " ").lower())
    strings = list()
    for x in strs:
        strings.append(x.replace(",", " ").replace("?", " ").replace("!", " ").replace(".", " ").split())
    dictionary = {BEGIN: set(), END: set()}
    for i in range(len(strings)):
        x = strings[i]
        for j in range(len(x)):
            if x[j] not in dictionary.keys():
                dictionary[x[j]] = set()
    for x in strings:
        if len(x) > 0:
            dictionary[BEGIN].add(x[0])
    for x in strings:
        if len(x) > 1:
            for i in range(len(x) - 1):
                if x[i] not in dictionary.keys():
                    dictionary[x[i]] = set()
                dictionary[x[i]].add(x[i + 1])
        if len(x) > 0:
            dictionary[x[len(x) - 1]].add(END)
    generated = ""
    await print_dict_file(dictionary)
    count = 0
    while len(generated.split(" ")) < length and count < 1000000:
        generated = (await find(dictionary)).strip().capitalize()
        count += 1
    return generated


async def find(dictionary, generated=""):
    words = list(dictionary.get(BEGIN))
    while True:
        word = random.choice(words)
        if word == END:
            break
        generated += (word + " ")
        words = list(dictionary.get(word))
    return generated
