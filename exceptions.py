# exceptions.py

class GrammarError(Exception):
    """
    Исключение для ошибок, связанных с грамматикой.
    """
    pass

class ParsingError(Exception):
    """
    Исключение для ошибок во время парсинга.
    """
    pass