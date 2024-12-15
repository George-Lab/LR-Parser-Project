from input_handler import read_grammar, read_words
from lr0_parser import LR0Parser

def main():
    """
    Основная функция для запуска парсера.
    """
    try:
        grammar = read_grammar()
        words = read_words()
        
        parser = LR0Parser()
        parser.fit(grammar)
        
        for word in words:
            print("Yes" if parser.predict(word) else "No")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()