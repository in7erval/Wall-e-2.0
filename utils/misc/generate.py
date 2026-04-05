"""
Генерация текста по цепям Маркова на основе истории сообщений
"""
import random

BEGIN = "BEGIN"
END = "END"


def _build_chain(messages: list[str]) -> dict[str, list[str]]:
    """Построить цепь Маркова из списка сообщений"""
    chain: dict[str, list[str]] = {BEGIN: [], END: []}

    for text in messages:
        words = text.replace(",", " ").replace("?", " ").replace("!", " ").replace(".", " ").lower().split()
        if not words:
            continue
        chain[BEGIN].append(words[0])
        for i in range(len(words) - 1):
            chain.setdefault(words[i], []).append(words[i + 1])
        chain.setdefault(words[-1], []).append(END)

    return chain


def generate(messages: list[str], length: int = 15, max_attempts: int = 1000) -> str:
    """
    Сгенерировать текст по цепям Маркова.

    Args:
        messages: список текстовых сообщений для обучения
        length: желаемая длина в словах
        max_attempts: максимум попыток генерации
    Returns:
        сгенерированный текст
    """
    chain = _build_chain(messages)

    if not chain[BEGIN]:
        return ""

    for _ in range(max_attempts):
        words = []
        word = random.choice(chain[BEGIN])
        while word != END and len(words) < length * 2:
            words.append(word)
            next_words = chain.get(word, [END])
            word = random.choice(next_words)

        if len(words) >= length:
            return " ".join(words).capitalize()

    # Если не удалось набрать нужную длину — возвращаем лучшее что есть
    words = []
    word = random.choice(chain[BEGIN])
    while word != END:
        words.append(word)
        next_words = chain.get(word, [END])
        word = random.choice(next_words)
        if len(words) > length * 3:
            break

    return " ".join(words).capitalize() if words else ""
