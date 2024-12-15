import pytest
from grammar import Grammar, Rule
from lr0_parser import LR0Parser
from lr0_items import LR0Item

class TestLR0Parser:
    def test_empty_string(self):
        grammar = Grammar()
        grammar.add_rule('S', '')
        grammar.start_symbol = 'S'
        
        parser = LR0Parser()
        parser.fit(grammar)
        
        assert parser.predict('') == True
        assert parser.predict('a') == False

    def test_simple_concatenation(self):
        grammar = Grammar()
        grammar.add_rule('S', 'ab')
        grammar.start_symbol = 'S'
        
        parser = LR0Parser()
        parser.fit(grammar)
        
        assert parser.predict('ab') == True
        assert parser.predict('a') == False
        assert parser.predict('b') == False
        assert parser.predict('ba') == False

    def test_left_recursion(self):
        grammar = Grammar()
        grammar.add_rule('S', 'Sa')
        grammar.add_rule('S', 'a')
        grammar.start_symbol = 'S'
        
        parser = LR0Parser()
        parser.fit(grammar)
        
        assert parser.predict('a') == True
        assert parser.predict('aa') == True
        assert parser.predict('aaa') == True
        assert parser.predict('b') == False

    def test_right_recursion(self):
        grammar = Grammar()
        grammar.add_rule('S', 'aS')
        grammar.add_rule('S', 'a')
        grammar.start_symbol = 'S'
        
        parser = LR0Parser()
        parser.fit(grammar)
        
        assert parser.predict('a') == True
        assert parser.predict('aa') == True
        assert parser.predict('aaa') == True
        assert parser.predict('b') == False

    def test_invalid_grammar(self):
        grammar = Grammar()
        grammar.add_rule('S', 'aS')
        # Missing start symbol
        
        parser = LR0Parser()
        with pytest.raises(Exception):
            parser.fit(grammar)

    def test_grammar_construction(self):
        grammar = Grammar()
        grammar.add_rule('S', 'aB')
        grammar.add_rule('B', 'b')
        grammar.start_symbol = 'S'
        
        assert len(grammar.terminals) == 2
        assert len(grammar.non_terminals) == 2
        assert 'a' in grammar.terminals
        assert 'b' in grammar.terminals
        assert 'S' in grammar.non_terminals
        assert 'B' in grammar.non_terminals

    def test_lr0_item_operations(self):
        rule = Rule('S', 'abc')
        item = LR0Item(rule, 1)
        
        assert str(item) == "S -> a•bc"
        assert item.next_symbol() == 'b'
        
        next_item = item.advance()
        assert next_item.dot_position == 2
        assert str(next_item) == "S -> ab•c"

    def test_multiple_rules_same_nonterminal(self):
        grammar = Grammar()
        grammar.add_rule('S', 'aS')
        grammar.add_rule('S', 'bS')
        grammar.add_rule('S', '')
        grammar.start_symbol = 'S'
        
        parser = LR0Parser()
        parser.fit(grammar)
        
        assert parser.predict('') == True
        assert parser.predict('a') == True
        assert parser.predict('b') == True
        assert parser.predict('ab') == True
        assert parser.predict('ba') == True
        assert parser.predict('aab') == True
        assert parser.predict('c') == False