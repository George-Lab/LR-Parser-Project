# main.py

from grammar import Grammar, Rule
from parser import LR1Parser
from exceptions import GrammarError
import sys
import re

def read_input():
    """
    Читает входные данные из стандартного ввода и преобразует их в объект Grammar и список слов.
    :return: Tuple (Grammar, List[str])
    """
    lines = sys.stdin.read().splitlines()
    idx = 0

    # Проверяем наличие первой строки с числами N, T, P
    if idx >= len(lines):
        raise GrammarError('Недостаточно входных данных')
    N, T, P = map(int, lines[idx].split())
    idx += 1

    # Чтение нетерминалов
    if idx >= len(lines):
        raise GrammarError('Недостаточно данных для нетерминалов')
    non_terminals = list(lines[idx].strip())  # Предполагаем, что нетерминалы идут без пробелов
    idx += 1

    # Чтение терминалов
    if idx >= len(lines):
        raise GrammarError('Недостаточно данных для терминалов')
    terminals = list(lines[idx].strip())       # Предполагаем, что терминалы идут без пробелов
    idx += 1

    # Чтение правил
    rules = []
    for _ in range(P):
        if idx >= len(lines):
            raise GrammarError('Недостаточно правил в грамматике')
        line = lines[idx].strip()
        idx += 1
        # Разбор правила с помощью регулярного выражения
        match = re.match(r'(\w+)->(.*)', line)
        if match:
            left = match.group(1)                # Левая часть правила
            right = match.group(2).strip()       # Правая часть правила
            if right == '':
                right_symbols = []                # Пустая правая часть представляет ε
            else:
                right_symbols = list(right)       # Разбиваем правую часть на символы
            rules.append(Rule(left, right_symbols))  # Добавляем правило в список
        else:
            raise GrammarError('Некорректный формат правила')

    # Чтение стартового символа
    if idx >= len(lines):
        raise GrammarError('Недостаточно данных для стартового символа')
    start_symbol = lines[idx].strip()
    idx += 1

    # Чтение количества слов
    if idx >= len(lines):
        raise GrammarError('Недостаточно данных для количества слов')
    m = int(lines[idx])
    idx += 1

    # Чтение слов
    words = []
    for _ in range(m):
        if idx >= len(lines):
            raise GrammarError('Недостаточно данных для слов')
        words.append(lines[idx].strip())       # Добавляем слово в список
        idx += 1

    # Создаем объект Grammar
    return Grammar(non_terminals, terminals, rules, start_symbol), words

def main():
    """
    Основная функция программы.
    Читает входные данные, строит парсер и проверяет принадлежность слов языку.
    """
    try:
        grammar, words = read_input()        # Читаем грамматику и слова
        parser = LR1Parser()                 # Создаем объект парсера
        parser.fit(grammar)                  # Инициализируем парсер грамматикой

        for word in words:
            result = parser.predict(word)     # Проверяем слово
            print("Yes" if result else "No") # Выводим результат
    except GrammarError as e:
        # Если возникла ошибка грамматики, выводим "No" для всех слов
        for _ in range(len(words)):
            print("No")
    except Exception as e:
        # Для любых других ошибок также выводим "No"
        for _ in range(len(words)):
            print("No")

if __name__ == "__main__":
    main()