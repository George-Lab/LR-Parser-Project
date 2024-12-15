# tests/test_parser.py

import unittest
from grammar import Grammar, Rule
from parser import LR1Parser
from exceptions import GrammarError

class TestLR1Parser(unittest.TestCase):
    def test_simple_expression(self):
        """
        Тест для простой арифметической грамматики.
        Грамматика:
            S -> E
            E -> E + T | T
            T -> T * F | F
            F -> ( E ) | I
        Терминалы: '+', '*', '(', ')', 'I'
        """
        rules = [
            Rule('S', ['E']),
            Rule('E', ['E', '+', 'T']),
            Rule('E', ['T']),
            Rule('T', ['T', '*', 'F']),
            Rule('T', ['F']),
            Rule('F', ['(', 'E', ')']),
            Rule('F', ['I'])  # 'I' представляет идентификатор
        ]
        non_terminals = ['S', 'E', 'T', 'F']
        terminals = ['+', '*', '(', ')', 'I']
        grammar = Grammar(non_terminals, terminals, rules, 'S')
        parser = LR1Parser()
        parser.fit(grammar)

        # Тестируем принадлежность слов языку
        self.assertTrue(parser.predict('I+I*I'))
        self.assertTrue(parser.predict('(I+I)*I'))
        self.assertFalse(parser.predict('I+*I'))
        self.assertFalse(parser.predict('I+I*'))
        self.assertFalse(parser.predict('(I+I*I'))

    def test_epsilon_production(self):
        """
        Тест грамматики с ε-продукциями.
        Грамматика:
            S -> A
            A -> aA | ε
        Терминалы: 'a'
        """
        rules = [
            Rule('S', ['A']),
            Rule('A', ['a', 'A']),
            Rule('A', [])  # Представляет A -> ε
        ]
        non_terminals = ['S', 'A']
        terminals = ['a']
        grammar = Grammar(non_terminals, terminals, rules, 'S')
        parser = LR1Parser()
        parser.fit(grammar)

        # Тестируем принадлежность слов языку
        self.assertTrue(parser.predict(''))
        self.assertTrue(parser.predict('a'))
        self.assertTrue(parser.predict('aaaaa'))
        self.assertFalse(parser.predict('b'))
        self.assertFalse(parser.predict('aaab'))

    def test_left_recursion(self):
        """
        Тест грамматики с левой рекурсией.
        Грамматика:
            S -> S a | b
        """
        rules = [
            Rule('S', ['S', 'a']),
            Rule('S', ['b'])
        ]
        non_terminals = ['S']
        terminals = ['a', 'b']
        grammar = Grammar(non_terminals, terminals, rules, 'S')
        parser = LR1Parser()
        
        with self.assertRaises(GrammarError):
            parser.fit(grammar)  # Эта грамматика может не быть LR(1)

    def test_non_lr1_grammar(self):
        """
        Тест грамматики, которая не является LR(1).
        Грамматика:
            S -> A a | A b
            A -> c | d
        Терминалы: 'a', 'b', 'c', 'd'
        """
        rules = [
            Rule('S', ['A', 'a']),
            Rule('S', ['A', 'b']),
            Rule('A', ['c']),
            Rule('A', ['d'])
        ]
        non_terminals = ['S', 'A']
        terminals = ['a', 'b', 'c', 'd']
        grammar = Grammar(non_terminals, terminals, rules, 'S')
        parser = LR1Parser()
        parser.fit(grammar)

        # Тестируем принадлежность слов языку
        self.assertTrue(parser.predict('ca'))
        self.assertTrue(parser.predict('cb'))
        self.assertTrue(parser.predict('da'))
        self.assertTrue(parser.predict('db'))
        self.assertFalse(parser.predict('c'))
        self.assertFalse(parser.predict('d'))
        self.assertFalse(parser.predict('caa'))
        self.assertFalse(parser.predict('dab'))

    def test_multiple_rules(self):
        """
        Тест грамматики с несколькими производствами для нетерминала.
        Грамматика:
            S -> A B | B C
            A -> a | ε
            B -> b
            C -> c | ε
        Терминалы: 'a', 'b', 'c'
        """
        rules = [
            Rule('S', ['A', 'B']),
            Rule('S', ['B', 'C']),
            Rule('A', ['a']),
            Rule('A', []),
            Rule('B', ['b']),
            Rule('C', ['c']),
            Rule('C', [])
        ]
        non_terminals = ['S', 'A', 'B', 'C']
        terminals = ['a', 'b', 'c']
        grammar = Grammar(non_terminals, terminals, rules, 'S')
        parser = LR1Parser()
        parser.fit(grammar)

        # Тестируем принадлежность слов языку
        self.assertTrue(parser.predict('ab'))
        self.assertTrue(parser.predict('bc'))
        self.assertTrue(parser.predict('aab'))
        self.assertTrue(parser.predict('b'))
        self.assertTrue(parser.predict('abc'))
        self.assertTrue(parser.predict('a'))
        self.assertTrue(parser.predict(''))
        self.assertFalse(parser.predict('ac'))
        self.assertFalse(parser.predict('aabc'))
        self.assertFalse(parser.predict('abb'))

    def test_complex_grammar(self):
        """
        Тест более сложной грамматики.
        Грамматика:
            S -> C C
            C -> c C | d
        Терминалы: 'c', 'd'
        """
        rules = [
            Rule('S', ['C', 'C']),
            Rule('C', ['c', 'C']),
            Rule('C', ['d'])
        ]
        non_terminals = ['S', 'C']
        terminals = ['c', 'd']
        grammar = Grammar(non_terminals, terminals, rules, 'S')
        parser = LR1Parser()
        parser.fit(grammar)

        # Тестируем принадлежность слов языку
        self.assertTrue(parser.predict('cd'))
        self.assertTrue(parser.predict('ccd'))
        self.assertTrue(parser.predict('cccd'))
        self.assertTrue(parser.predict('dd'))
        self.assertFalse(parser.predict('c'))
        self.assertFalse(parser.predict('d'))
        self.assertFalse(parser.predict('cdc'))
        self.assertFalse(parser.predict('ccc'))

if __name__ == '__main__':
    unittest.main()