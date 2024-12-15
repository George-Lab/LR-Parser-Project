from dataclasses import dataclass
from typing import List, Set

@dataclass(frozen=True)
class Rule:
    """
    Класс для представления правила грамматики.
    """
    left: str
    right: str
    
    def __str__(self):
        return f"{self.left} -> {self.right}"

class Grammar:
    """
    Класс для представления контекстно-свободной грамматики.
    """
    def __init__(self):
        self.rules: List[Rule] = []
        self.terminals: Set[str] = set()
        self.non_terminals: Set[str] = set()
        self.start_symbol: str = None
        
    def add_rule(self, left: str, right: str):
        """
        Добавляет правило в грамматику.
        
        :param left: Левая часть правила
        :param right: Правая часть правила
        """
        self.rules.append(Rule(left, right))
        self.non_terminals.add(left)
        for char in right:
            if char.islower():
                self.terminals.add(char)
            else:
                self.non_terminals.add(char)