from dataclasses import dataclass
from grammar import Rule

@dataclass(frozen=True)
class LR0Item:
    """
    Класс для представления LR(0) элемента.
    """
    rule: Rule
    dot_position: int
    
    def __str__(self):
        right = self.rule.right
        pos = self.dot_position
        return f"{self.rule.left} -> {right[:pos]}•{right[pos:]}"
    
    def next_symbol(self) -> str:
        """
        Возвращает следующий символ после точки.
        
        :return: Следующий символ или None, если точка в конце
        """
        if self.dot_position >= len(self.rule.right):
            return None
        return self.rule.right[self.dot_position]
    
    def advance(self) -> 'LR0Item':
        """
        Возвращает новый элемент с точкой, сдвинутой на одну позицию вправо.
        
        :return: Новый LR0Item с продвинутой точкой
        """
        return LR0Item(self.rule, self.dot_position + 1)