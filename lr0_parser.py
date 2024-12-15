from typing import Dict, Set, Tuple, Optional
from grammar import Grammar, Rule
from lr0_items import LR0Item

class LR0Parser:
    """
    Класс для реализации LR(0) парсера.
    """
    def __init__(self):
        self.grammar = None
        self.automaton = []
        self.goto = {}
        self.action_table = {}
        
    def fit(self, grammar: Grammar) -> 'LR0Parser':
        """
        Инициализирует парсер с заданной грамматикой.
        
        :param grammar: Грамматика для парсинга
        :return: Сам парсер
        """
        self.grammar = grammar
        self.augmented_start = 'S\''
        self._build_automaton()
        self._build_parsing_table()
        return self
        
    def _closure(self, items: Set[LR0Item]) -> Set[LR0Item]:
        """
        Вычисляет замыкание множества LR(0) элементов.
        
        :param items: Множество LR(0) элементов
        :return: Замыкание множества LR(0) элементов
        """
        result = items.copy()
        while True:
            size = len(result)
            new_items = set()
            
            for item in result:
                next_sym = item.next_symbol()
                if next_sym and next_sym in self.grammar.non_terminals:
                    for rule in self.grammar.rules:
                        if rule.left == next_sym:
                            new_items.add(LR0Item(rule, 0))
                            
            result.update(new_items)
            if len(result) == size:
                break
                
        return result

    def _goto(self, items: Set[LR0Item], symbol: str) -> Set[LR0Item]:
        """
        Вычисляет переход для множества LR(0) элементов по символу.
        
        :param items: Множество LR(0) элементов
        :param symbol: Символ для перехода
        :return: Множество LR(0) элементов после перехода
        """
        next_items = set()
        for item in items:
            if item.next_symbol() == symbol:
                next_items.add(item.advance())
        return self._closure(next_items) if next_items else set()
    
    def _build_automaton(self):
        """
        Строит автомат LR(0) для заданной грамматики.
        """
        augmented_rule = Rule(self.augmented_start, self.grammar.start_symbol)
        start_item = LR0Item(augmented_rule, 0)
        initial_state = self._closure({start_item})
        
        self.automaton = [initial_state]
        self.goto = {}
        
        symbols = self.grammar.terminals | self.grammar.non_terminals
        
        i = 0
        while i < len(self.automaton):
            state = self.automaton[i]
            for symbol in symbols:
                next_state = self._goto(state, symbol)
                if next_state:
                    state_idx = next((idx for idx, s in enumerate(self.automaton) if s == next_state), None)
                    if state_idx is None:
                        self.automaton.append(next_state)
                        state_idx = len(self.automaton) - 1
                    self.goto[(i, symbol)] = state_idx
            i += 1

    def _build_parsing_table(self):
        """
        Строит таблицу парсинга для LR(0) автомата.
        """
        self.action_table = {}
        
        # Сначала добавляем действия reduce (низкий приоритет)
        for state_idx, state in enumerate(self.automaton):
            for item in state:
                if item.dot_position == len(item.rule.right):
                    if item.rule.left == self.augmented_start:
                        self.action_table[(state_idx, '$')] = ('accept', None)
                    else:
                        for terminal in self.grammar.terminals | {'$'}:
                            if (state_idx, terminal) not in self.action_table:
                                self.action_table[(state_idx, terminal)] = ('reduce', item.rule)
        
        # Затем добавляем действия shift (высокий приоритет)
        for (state_idx, symbol), next_state in self.goto.items():
            if symbol in self.grammar.terminals:
                self.action_table[(state_idx, symbol)] = ('shift', next_state)

    def predict(self, word: str) -> bool:
        """
        Проверяет принадлежность слова языку, порождаемому грамматикой.
        
        :param word: Слово для проверки
        :return: True, если слово принадлежит языку, иначе False
        """
        word = word + '$'
        stack = [(0, [])]
        cursor = 0
        
        while cursor <= len(word):
            state = stack[-1][0]
            current_symbol = word[cursor] if cursor < len(word) else '$'
            
            if (state, current_symbol) not in self.action_table:
                return False
            
            action, value = self.action_table[(state, current_symbol)]
            
            if action == 'shift':
                stack.append((value, [current_symbol]))
                cursor += 1
            elif action == 'reduce':
                if value.right:
                    stack = stack[:-len(value.right)]
                
                current_state = stack[-1][0]
                if (current_state, value.left) not in self.goto:
                    return False
                    
                next_state = self.goto[(current_state, value.left)]
                stack.append((next_state, [value.left]))
            elif action == 'accept':
                return cursor == len(word) - 1
            else:
                return False
        
        return False