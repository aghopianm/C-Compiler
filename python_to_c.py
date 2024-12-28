import re

class PythonToCCompiler:
    def __init__(self):
        self.variables = {}

    def tokenize(self, code):
        # Simple regular expression for tokenizing Python code
        token_specification = [
            ('NUMBER', r'\d+'),
            ('ASSIGN', r'='),
            ('NAME', r'[A-Za-z_][A-Za-z0-9_]*'),
            ('PLUS', r'\+'),
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t]+'),
            ('MISMATCH', r'.'),
        ]
        
        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        get_token = re.compile(tok_regex).match
        position = 0
        while position < len(code):
            match = get_token(code, position)
            if match is None:
                raise RuntimeError(f"Unexpected character at position {position}")
            position = match.end()
            type_ = match.lastgroup
            value = match.group()
            if type_ != 'SKIP':
                yield type_, value

    def parse(self, tokens):
        # Simple parser for assignment and addition
        statements = []
        current_token = next(tokens, None)
        result_declared = False  # To avoid multiple declarations of 'result'
        while current_token:
            if current_token[0] == 'NAME':
                var_name = current_token[1]
                current_token = next(tokens, None)
                if current_token and current_token[0] == 'ASSIGN':
                    current_token = next(tokens, None)
                    if current_token and current_token[0] == 'NUMBER':
                        var_value = int(current_token[1])
                        # Declare the variable with type 'int'
                        statements.append(f"int {var_name} = {var_value};")
                        self.variables[var_name] = var_value
            elif current_token[0] == 'PLUS':
                # Handle the addition expression, reference the variables x and y
                if 'x' in self.variables and 'y' in self.variables:
                    if not result_declared:  # Only declare 'result' once
                        statements.append(f"int result = x + y;")
                        result_declared = True
            current_token = next(tokens, None)
        return statements

    def generate_c_code(self, python_code):
        tokens = self.tokenize(python_code)
        statements = self.parse(tokens)
        c_code = "#include <stdio.h>\n\nint main() {\n"
        
        # Add all parsed statements to the main function
        for statement in statements:
            c_code += f"    {statement}\n"
        
        c_code += "    return 0;\n}"
        return c_code

    def compile_file(self, input_file, output_file):
        with open(input_file, 'r') as file:
            python_code = file.read()

        c_code = self.generate_c_code(python_code)

        with open(output_file, 'w') as file:
            file.write(c_code)

        print(f"C code saved to '{output_file}'.")

compiler = PythonToCCompiler()
compiler.compile_file("input.py", "output.c")