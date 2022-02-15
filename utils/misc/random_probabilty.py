import random


def random_probability(text):
    if "насколько" in text:
        strs = text.split("насколько", 2)
    elif "на сколько" in text:
        strs = text.lower().split("на сколько", 2)
    else:
        return
    if len(strs) > 1:
        prob = random.randint(0, 101)  # не баг а фича
        return f"Я думаю, что на {str(prob)}%"
