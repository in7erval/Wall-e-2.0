import random


def random_choice(text):
    strs = text.lower().split("бот ")
    strs = strs[1].split("или")
    for x in strs:
        if " я " in x:
            x = x.replace(" я ", " ты ")
        elif x.startswith("я"):
            x = x.replace("я", "ты", 1)
        elif " ты " in x:
            x = x.replace(" ты ", " я ")
        elif x.startswith("ты"):
            x = x.replace("ты", "я", 1)
    return "Определённо " + random.choice(strs).strip()
