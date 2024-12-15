from grammar import Grammar

def read_grammar() -> Grammar:
    """
    Считывает грамматику из стандартного ввода.
    
    :return: Грамматика
    """
    n, t, p = map(int, input().split())
    
    input().split()  # non_terminals (unused)
    input().split()  # terminals (unused)
    
    grammar = Grammar()
    
    for _ in range(p):
        left, right = input().split('->')
        left = left.strip()
        right = right.strip()
        grammar.add_rule(left, right if right else '')
        
    grammar.start_symbol = input().strip()
    return grammar

def read_words() -> list:
    """
    Считывает слова для проверки из стандартного ввода.
    
    :return: Список слов
    """
    m = int(input())
    return [input().strip() for _ in range(m)]