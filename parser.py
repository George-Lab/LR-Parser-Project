# parser.py

from grammar import Grammar, Rule
from exceptions import GrammarError
from collections import deque

class LR1Item:
    """
    Класс для представления элемента LR(1) (Product).
    """
    def __init__(self, left, right, dot, lookahead):
        self.left = left                # Левая часть правила (нетерминал)
        self.right = right              # Правая часть правила (список символов)
        self.dot = dot                  # Позиция точки в правой части правила
        self.lookahead = lookahead      # Символ предсказания (lookahead)

    def __eq__(self, other):
        """
        Определяет равенство двух элементов LR1.
        """
        return (self.left == other.left and
                self.right == other.right and
                self.dot == other.dot and
                self.lookahead == other.lookahead)

    def __hash__(self):
        """
        Позволяет использовать элементы LR1Item в сетах.
        """
        return hash((self.left, tuple(self.right), self.dot, self.lookahead))

    def next_symbol(self):
        """
        Возвращает символ после точки, если он существует.
        """
        if self.dot < len(self.right):
            return self.right[self.dot]
        return None

    def is_complete(self):
        """
        Проверяет, находится ли точка в конце правой части правила.
        """
        return self.dot >= len(self.right)

    def __repr__(self):
        """
        Удобное отображение элемента LR(1).
        """
        right = self.right.copy()
        if self.dot <= len(right):
            right.insert(self.dot, '•')
        return f"{self.left} -> {''.join(right)}, {self.lookahead}"

class LR1Parser:
    """
    Класс для реализации LR(1) парсера.
    """
    def __init__(self):
        self.grammar = None                # Объект грамматики
        self.states = []                    # Список множеств состояний (I0, I1, ...)
        self.action_table = []              # Таблица действий (action)
        self.goto_table = []                # Таблица переходов (goto)
        self.transitions = []               # Список переходов между состояниями

    def fit(self, G: Grammar):
        """
        Инициализация парсера на основе грамматики.
        Строит множества состояний и таблицы action и goto.
        :param G: Объект Grammar
        :return: self
        """
        self.grammar = G
        self.build_states()                  # Строим множества состояний LR(1)
        if not self.build_tables():         # Строим таблицы action и goto
            raise GrammarError("Грамматика не является LR(1)")  # Если не удалось построить таблицы без конфликтов
        return self

    def closure(self, items):
        """
        Вычисляет множество замыкания для данного множества элементов LR(1).
        :param items: Набор элементов LR1Item
        :return: Множество замыкания
        """
        closure_set = set(items)             # Инициализируем множество замыкания
        queue = deque(items)                 # Очередь для обработки элементов
        while queue:
            item = queue.popleft()
            next_sym = item.next_symbol()    # Символ после точки
            if next_sym and next_sym in self.grammar.non_terminals:
                # Если символ после точки является нетерминалом, добавляем соответствующие правила
                beta = item.right[item.dot + 1:]  # Остаток правой части после следующего символа
                if beta:
                    first_beta = self.grammar.first_sequence(beta)  # First(beta)
                    if 'ε' in first_beta:
                        # Если beta может производить 'ε', объединяем с символом lookahead
                        lookaheads = (first_beta - {'ε'}) | {item.lookahead}
                    else:
                        lookaheads = first_beta
                else:
                    # Если после символа ничего нет, предсказание такое же, как у текущего элемента
                    lookaheads = {item.lookahead}
                
                # Проходим по всем правилам, где левая часть равна next_sym
                for rule in self.grammar.rules:
                    if rule.left == next_sym:
                        for la in lookaheads:
                            new_item = LR1Item(rule.left, rule.right, 0, la)  # Создаем новый элемент
                            if new_item not in closure_set:
                                closure_set.add(new_item)  # Добавляем в замыкание
                                queue.append(new_item)      # Добавляем в очередь для дальнейшей обработки
        return closure_set

    def goto(self, items, symbol):
        """
        Вычисляет множество переходов по символу.
        :param items: Множество элементов LR1Item
        :param symbol: Символ перехода
        :return: Множество элементов после перехода
        """
        goto_set = set()
        for item in items:
            if item.next_symbol() == symbol:
                # Если текущий элемент может переходить по символу, создаем новый элемент сдвинутой точки
                new_item = LR1Item(item.left, item.right, item.dot + 1, item.lookahead)
                goto_set.add(new_item)
        return self.closure(goto_set) if goto_set else set()

    def build_states(self):
        """
        Строит множества состояний LR(1) и фиксирует переходы между ними.
        """
        # Начальный элемент: S' -> •S, $
        initial_item = LR1Item(self.grammar.augmented_start, [self.grammar.start_symbol], 0, '$')
        I0 = self.closure([initial_item])    # Начальное замыкание
        self.states = [I0]                     # Добавляем начальное состояние
        transitions = []                       # Список переходов (from_state, symbol, to_state)
        queue = deque([I0])                    # Очередь для строительства состояний

        while queue:
            I = queue.popleft()
            for symbol in self.grammar.non_terminals.union(self.grammar.terminals):
                goto_I = self.goto(I, symbol)  # Вычисляем переход по символу
                if goto_I:
                    if goto_I not in self.states:
                        self.states.append(goto_I)      # Добавляем новое состояние
                        queue.append(goto_I)            # Добавляем в очередь для дальнейшего исследования
                    from_state = self.states.index(I)     # Индекс исходного состояния
                    to_state = self.states.index(goto_I)  # Индекс целевого состояния
                    transitions.append((from_state, symbol, to_state))  # Сохраняем переход

        self.transitions = transitions              # Сохраняем все переходы

    def build_tables(self):
        """
        Строит таблицы действий (action) и переходов (goto) для LR(1) парсера.
        :return: True, если таблицы построены без конфликтов, иначе False
        """
        # Инициализируем таблицы как списки словарей для каждого состояния
        self.action_table = [{} for _ in self.states]
        self.goto_table = [{} for _ in self.states]

        # Проходим по всем состояниям и их элементам
        for idx, I in enumerate(self.states):
            for item in I:
                if item.is_complete():
                    # Если элемент завершен, добавляем действие 'reduce' или 'accept'
                    if item.left == self.grammar.augmented_start:
                        # Если правило S' -> S завершено и lookahead '$', то действие 'accept'
                        if item.lookahead == '$':
                            if '$' in self.action_table[idx]:
                                if self.action_table[idx]['$'] != ('accept',):
                                    return False  # Конфликт
                            else:
                                self.action_table[idx]['$'] = ('accept',)
                    else:
                        # Добавляем действие 'reduce' для всех возможных lookahead
                        action = ('reduce', item.left, item.right)
                        if item.lookahead in self.action_table[idx]:
                            existing_action = self.action_table[idx][item.lookahead]
                            if existing_action != action:
                                return False  # Конфликт
                        else:
                            self.action_table[idx][item.lookahead] = action
                else:
                    # Если элемент не завершен, добавляем действие 'shift' для терминалов
                    next_sym = item.next_symbol()
                    if next_sym in self.grammar.terminals:
                        # Вычисляем состояние после сдвига по символу next_sym
                        goto_I = self.goto(I, next_sym)
                        if goto_I:
                            j = self.states.index(goto_I)  # Индекс состояния после перехода
                            action = ('shift', j)
                            if next_sym in self.action_table[idx]:
                                if self.action_table[idx][next_sym] != action:
                                    return False  # Конфликт
                            else:
                                self.action_table[idx][next_sym] = action

        # Построение таблицы GOTO для нетерминалов
        for from_state, symbol, to_state in self.transitions:
            if symbol in self.grammar.non_terminals:
                self.goto_table[from_state][symbol] = to_state

        return True  # Таблицы успешно построены без конфликтов

    def predict(self, word: str) -> bool:
        """
        Проверяет, принадлежит ли слово языку, определенному грамматикой.
        :param word: Строка для проверки
        :return: True, если слово принадлежит языку, иначе False
        """
        word = list(word) + ['$']               # Добавляем символ конца ввода
        stack = [0]                               # Инициализируем стек состоянием 0
        idx = 0                                   # Индекс текущего символа в слове

        while True:
            state = stack[-1]                    # Получаем текущее состояние из вершины стека
            if idx < len(word):
                current_sym = word[idx]          # Текущий символ ввода
            else:
                current_sym = '$'                 # Если выходим за пределы, считаем символ конца
            action = self.action_table[state].get(current_sym)  # Получаем действие из таблицы

            if action is None:
                # Нет действия для текущего состояния и символа, слово не принадлежит языку
                return False

            if action[0] == 'shift':
                # Действие 'shift': переходим в новое состояние и продвигаем символ
                stack.append(action[1])           # Добавляем новое состояние в стек
                idx += 1                           # Переходим к следующему символу
            elif action[0] == 'reduce':
                # Действие 'reduce': сворачиваем по правилу
                left, right = action[1], action[2]  # Получаем правило A -> α
                if right:
                    # Если правая часть правила не пуста, удаляем len(right) состояний из стека
                    for _ in right:
                        if len(stack) > 1:
                            stack.pop()
                        else:
                            # Стек не может быть пустым, некорректная свертка
                            return False
                # После сворачивания, берем новое состояние из вершины стека
                state = stack[-1]
                goto_state = self.goto_table[state].get(left)  # Получаем новое состояние из таблицы GOTO
                if goto_state is None:
                    # Нет перехода по нетерминалу, слово не принадлежит языку
                    return False
                stack.append(goto_state)           # Добавляем новое состояние в стек
            elif action[0] == 'accept':
                # Действие 'accept': слово успешно распознано
                return True
            else:
                # Неизвестное действие, считаем слово не принадлежащим
                return False