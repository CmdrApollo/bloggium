from dataclasses import dataclass

@dataclass
class Token:
    lexeme: str
    value: str | None = None

    def __repr__(self):
        if self.value:
            return f"[ {self.lexeme} : {self.value} ]"
        return f"[ {self.lexeme} ]"

def tokenize(code: str) -> list[Token]:
    tokens: list[Token] = []

    valid_symbols = {
        "+": "increment",
        "-": "decrement",
        ".": "print",
        ",": "input",
        "!": "number_print",
        ";": "number_input",

        "=": "assign",
        
        "(": "open_forloop",
        ")": "close_forloop",
        "[": "open_whileloop",
        "]": "close_whileloop",
    }

    pos: int = 0

    while pos < len(code):
        char: str = code[pos]

        if char.isspace():
            pos += 1
            continue

        if char == '#':
            while pos < len(code):
                char: str = code[pos]
                if char == "\n":
                    break
                pos += 1
            continue

        next_char: str = code[pos + 1] if pos + 1 < len(code) else ""

        if next_char and char + next_char in valid_symbols:
            tokens.append(Token(valid_symbols[char + next_char]))
            pos += 2
            continue
        elif char in valid_symbols:
            tokens.append(Token(valid_symbols[char]))
            pos += 1
            continue

        if char.isnumeric():
            number: str = ""

            while pos < len(code):
                char = code[pos]

                if not char.isnumeric():
                    break

                number += char

                pos += 1
            
            tokens.append(
                Token(
                    "number",
                    number
                )
            )
            continue

        if char == "'":
            char_literal: str = ""

            pos += 1

            while pos < len(code):
                char = code[pos]

                if char == "'":
                    break

                char_literal += char

                pos += 1

            pos += 1
            
            tokens.append(
                Token(
                    "number",
                    str(ord(char_literal))
                )
            )
            continue

        if char.isalpha():
            identifier: str = ""

            while pos < len(code):
                char = code[pos]

                if not (char.isalnum() or char == "_"):
                    break

                identifier += char

                pos += 1
            
            tokens.append(
                Token(
                    "identifier",
                    identifier
                )
            )
            continue

        pos += 1
    
    return tokens

def run_tokens(tokens: list[Token]) -> None:
    variables: dict[str, float] = {}
    call_stack: list[int] = []
    for_stack: list[tuple[int, int]] = []

    def get_value(token):
        if token.lexeme == "identifier": return variables[token.value]
        if token.lexeme == "number": return int(token.value)
        return None

    pos: int = 0

    while pos < len(tokens):
        tok = tokens[pos]
        
        if tok.lexeme == "identifier":
            if tokens[pos + 1].lexeme == "assign":
                value = get_value(tokens[pos + 2])
                variables[tok.value] = value
                pos += 3
                continue
            elif tokens[pos + 1].lexeme == "input":
                variables[tok.value] = ord(input()[0])
                pos += 2
                continue
            elif tokens[pos + 1].lexeme == "number_input":
                variables[tok.value] = int(input())
                pos += 2
                continue
        elif tok.lexeme == "close_whileloop":
            c = call_stack.pop()
            if get_value(tokens[c]) != 0:
                pos = c + 2
                call_stack.append(c)
            else:
                pos += 1
            continue
        elif tok.lexeme == "close_forloop":
            b = for_stack.pop()
            times, location = b[0] - 1, b[1]
            if times > 0:
                pos = location + 2
                for_stack.append((times, location))
            else:
                pos += 1
            continue
        
        a = get_value(tok)

        if a is None:
            print("A runtime error occured.")
            break

        n = tokens[pos + 1].lexeme

        match n:
            case "increment":
                if tok.lexeme == "identifier":
                    variables[tok.value] += 1
            case "decrement":
                if tok.lexeme == "identifier":
                    variables[tok.value] -= 1
            case "print":
                print(chr(a), end = "")
            case "number_print":
                print(a, end = "")
            case "input":
                if tok.lexeme == "identifier":
                    variables[tok.value] = ord(input()[0])
            case "number_input":
                if tok.lexeme == "identifier":
                    variables[tok.value] = int(input())
            case "open_whileloop":
                call_start = pos
                pos += 1
                brackets = 1
                while brackets and pos < len(tokens):
                    tok = tokens[pos]

                    if tok.lexeme == "open_whileloop":
                        brackets += 1

                    if tok.lexeme == "close_whileloop":
                        brackets -= 1

                    pos += 1

                call_stack.append(call_start)
                pos = call_start
            case "open_forloop":                
                for_start = pos
                pos += 1
                brackets = 1
                while brackets and pos < len(tokens):
                    tok = tokens[pos]

                    if tok.lexeme == "open_forloop":
                        brackets += 1

                    if tok.lexeme == "close_forloop":
                        brackets -= 1

                    pos += 1

                for_stack.append((a, for_start))
                pos = for_start

        pos += 2

if __name__ == "__main__":
    import sys, os

    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]):
            code = open(sys.argv[1]).read()
            run_tokens(tokenize(code))
        else:
            print("couldn't find that file")
    else:
        while True:
            code = input(">>> ")

            if code == 'quit':
                break

            run_tokens(tokenize(code))