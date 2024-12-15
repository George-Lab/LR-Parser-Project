# grammar.py

class Rule:
    """
    Класс для представления правила грамматики.
    """
    def __init__(self, left, right):
        self.left = left                # Левая часть правила (нетерминал)
        self.right = right              # Правая часть правила (список символов)
    
    def __repr__(self):
        """
        Метод для удобного вывода правила.
        Если правая часть пустая, отображается как 'ε'.
        """
        right = ''.join(self.right) if self.right else 'ε'
        return f"{self.left} -> {right}"

class Grammar:
    """
    Класс для представления контекстно-свободной грамматики.
    """
    def __init__(self, non_terminals, terminals, rules, start_symbol):
        self.non_terminals = set(non_terminals)          # Множество нетерминальных символов
        self.terminals = set(terminals)                  # Множество терминальных символов
        self.rules = rules                                # Список правил типа Rule
        self.start_symbol = start_symbol                  # Стартовый символ грамматики
        self.augmented_start = self.start_symbol + "'"    # Добавленный стартовый символ для расширенной грамматики
        self.non_terminals.add(self.augmented_start)      # Добавляем расширенный нетерминал в множество нетерминалов
        self.rules.insert(0, Rule(self.augmented_start, [self.start_symbol]))  # Добавляем правило S' -> S
        self.first = {}                                   # Словарь для множеств First
        self.follow = {}                                  # Словарь для множеств Follow
        self.compute_first()                              # Вычисляем множества First
        self.compute_follow()                             # Вычисляем множества Follow

    def compute_first(self):
        """
        Вычисление множеств First для всех символов грамматики.
        """
        # Инициализируем множества First для всех символов как пустые множества
        self.first = {symbol: set() for symbol in self.non_terminals.union(self.terminals)}
        
        # Для терминалов множество First содержит сам терминал
        for terminal in self.terminals:
            self.first[terminal].add(terminal)
        
        changed = True  # Флаг для отслеживания изменений в множествах First
        while changed:
            changed = False
            # Проходим по всем правилам грамматики
            for rule in self.rules:
                left, right = rule.left, rule.right
                first_left = self.first[left]  # Текущее множество First для левой части правила
                before_change = len(first_left)  # Сохраняем размер множества до изменений

                if not right:
                    # Если правая часть пуста, добавляем 'ε' в First(left)
                    first_left.add('ε')
                else:
                    # Проходим по символам правой части правила
                    idx = 0
                    while idx < len(right):
                        symbol = right[idx]
                        # Добавляем все символы из First(symbol), кроме 'ε'
                        first_left.update(self.first[symbol] - {'ε'})
                        if 'ε' not in self.first[symbol]:
                            # Если 'ε' нет в First(symbol), прекращаем дальнейший анализ
                            break
                        idx += 1
                    else:
                        # Если все символы справа могут производить 'ε', добавляем 'ε' в First(left)
                        first_left.add('ε')

                # Проверяем, изменилось ли множество First(left)
                if len(first_left) > before_change:
                    changed = True  # Если изменилось, продолжаем итерации

    def compute_follow(self):
        """
        Вычисление множеств Follow для всех нетерминальных символов грамматики.
        """
        # Инициализируем множества Follow как пустые множества для всех нетерминалов
        self.follow = {symbol: set() for symbol in self.non_terminals}
        # Добавляем символ конца строки '$' в Follow расширенного стартового символа
        self.follow[self.augmented_start].add('$')
        
        changed = True  # Флаг для отслеживания изменений в множествах Follow
        while changed:
            changed = False
            # Проходим по всем правилам грамматики
            for rule in self.rules:
                left, right = rule.left, rule.right
                # Проходим по всем символам правой части правила
                for idx, B in enumerate(right):
                    if B in self.non_terminals:
                        follow_B = self.follow[B]  # Текущее множество Follow для символа B
                        before_change = len(follow_B)  # Сохраняем размер множества до изменений

                        if idx + 1 < len(right):
                            # Если после B есть символы
                            beta = right[idx + 1:]
                            # Вычисляем First(beta)
                            first_beta = self.first_sequence(beta)
                            # Добавляем First(beta) без 'ε' в Follow(B)
                            self.follow[B].update(first_beta - {'ε'})
                            if 'ε' in first_beta:
                                # Если First(beta) содержит 'ε', добавляем Follow(left) в Follow(B)
                                self.follow[B].update(self.follow[left])
                        else:
                            # Если B является последним символом в правой части, добавляем Follow(left) в Follow(B)
                            self.follow[B].update(self.follow[left])

                        # Проверяем, изменилось ли множество Follow(B)
                        if len(self.follow[B]) > before_change:
                            changed = True  # Если изменилось, продолжаем итерации

    def first_sequence(self, symbols):
        """
        Вычисляет множество First для последовательности символов.
        :param symbols: Список символов
        :return: Множество символов
        """
        result = set()
        for symbol in symbols:
            # Добавляем все символы из First(symbol), кроме 'ε'
            result.update(self.first[symbol] - {'ε'})
            if 'ε' not in self.first[symbol]:
                # Если 'ε' нет в First(symbol), прекращаем
                break
        else:
            # Если все символы могут производить 'ε', добавляем 'ε'
            result.add('ε')
        return result