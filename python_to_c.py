import re

class PythonToCCompiler:
    def __init__(self):
        self.variables = {}

    def tokenize(self, code):
        token_specification = [
            ('NUMBER', r'\d+(\.\d+)?'),
            ('ASSIGN', r'='),
            ('NAME', r'[A-Za-z_][A-Za-z0-9_]*'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULTIPLY', r'\*'),
            ('DIVIDE', r'/'),
            ('LT', r'<'),
            ('GT', r'>'),
            ('EQ', r'=='),
            ('WHILE', r'while'),
            ('FOR', r'for'),
            ('IF', r'if'),
            ('IN', r'in'),
            ('COLON', r':'),
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t]+'),
            ('COMMENT', r'#.*'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('COMMA', r','),
            ('MISMATCH', r'.'),
        ]

        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        get_token = re.compile(tok_regex).match
        position = 0
        tokens = []
        
        while position < len(code):
            match = get_token(code, position)
            if match is None:
                raise RuntimeError(f"Unexpected character at position {position}")
            position = match.end()
            type_ = match.lastgroup
            value = match.group()
            if type_ not in ['COMMENT', 'SKIP']:
                tokens.append((type_, value))
                
        return iter(tokens)

    def parse(self, tokens):
        statements = []
        current_token = next(tokens, None)

        while current_token:
            if current_token[0] == 'NAME':
                if current_token[1] == 'while':  # Handle while loop
                    current_token = next(tokens, None)
                    condition = []
                    while current_token and current_token[0] != 'COLON':
                        condition.append(current_token[1])
                        current_token = next(tokens, None)
                    
                    statements.append(f"while ({' '.join(condition)}) {{")
                    
                    current_token = next(tokens, None)  # Skip colon
                    if current_token and current_token[0] == 'NEWLINE':
                        current_token = next(tokens, None)
                    
                    if current_token and current_token[0] == 'NAME':
                        var_name = current_token[1]
                        current_token = next(tokens, None)
                        if current_token and current_token[0] == 'ASSIGN':
                            current_token = next(tokens, None)
                            if current_token and current_token[0] == 'NAME':
                                first_op = current_token[1]
                                current_token = next(tokens, None)
                                if current_token and current_token[0] == 'PLUS':
                                    current_token = next(tokens, None)
                                    if current_token and current_token[0] == 'NUMBER':
                                        increment = current_token[1]
                                        statements.append(f"    {var_name} = {first_op} + {increment};")
                    
                    statements.append("}")

                elif current_token[1] == 'if':  # Handle if statements
                    current_token = next(tokens, None)
                    condition = []
                    while current_token and current_token[0] != 'COLON':
                        condition.append(current_token[1])
                        current_token = next(tokens, None)
                    
                    statements.append(f"if ({' '.join(condition)}) {{")
                    
                    current_token = next(tokens, None)  # Skip colon
                    if current_token and current_token[0] == 'NEWLINE':
                        current_token = next(tokens, None)
                    
                    if current_token and current_token[0] == 'NAME':
                        if current_token[1] == 'print':
                            current_token = next(tokens, None)  # Skip print
                            if current_token and current_token[0] == 'LPAREN':
                                current_token = next(tokens, None)  # Skip left paren
                                if current_token:
                                    var_name = current_token[1]
                                    format_spec = '%f' if var_name in self.variables and self.variables[var_name][0] == 'float' else '%d'
                                    statements.append(f'    printf("{format_spec}\\n", {var_name});')
                        else:
                            var_name = current_token[1]
                            current_token = next(tokens, None)
                            if current_token and current_token[0] == 'ASSIGN':
                                current_token = next(tokens, None)
                                if current_token and current_token[0] == 'NUMBER':
                                    var_value = current_token[1]
                                    statements.append(f"    {var_name} = {var_value};")
                    
                    statements.append("}")

                elif current_token[1] == 'for':  # Handle for loop
                    current_token = next(tokens, None)
                    if current_token and current_token[0] == 'NAME':
                        loop_var = current_token[1]
                        
                        while current_token and (current_token[0] != 'NUMBER'):
                            current_token = next(tokens, None)
                        
                        start = current_token[1]
                        current_token = next(tokens, None)
                        current_token = next(tokens, None)
                        end = current_token[1]
                        
                        statements.append(f"for (int {loop_var} = {start}; {loop_var} < {end}; {loop_var}++) {{")
                        
                        while current_token and (current_token[0] != 'NAME' or current_token[1] != 'print'):
                            current_token = next(tokens, None)
                        
                        if current_token and current_token[1] == 'print':
                            current_token = next(tokens, None)
                            if current_token and current_token[0] == 'LPAREN':
                                current_token = next(tokens, None)
                                if current_token and current_token[0] == 'NAME':
                                    var_to_print = current_token[1]
                                    statements.append(f'    printf("%d\\n", {var_to_print});')
                        
                        statements.append("}")

                else:  # Handle variable assignment, including expressions like 'a * z'
                    var_name = current_token[1]
                    current_token = next(tokens, None)
                    
                    if current_token and current_token[0] == 'ASSIGN':
                        current_token = next(tokens, None)
                        expression_parts = []
                        
                        while current_token and current_token[0] not in ['NEWLINE', 'ASSIGN', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE']:
                            expression_parts.append(current_token[1])
                            current_token = next(tokens, None)
                        
                        if current_token and current_token[0] in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE']:
                            operator = current_token[1]
                            current_token = next(tokens, None)
                            expression_parts.append(operator)
                            while current_token and current_token[0] not in ['NEWLINE', 'ASSIGN']:
                                expression_parts.append(current_token[1])
                                current_token = next(tokens, None)

                        # Generate the assignment for expressions
                        expr_str = ' '.join(expression_parts)
                        if '*' in expr_str or '/' in expr_str:
                            var_type = 'float'
                        else:
                            var_type = 'int'

                        statements.append(f"{var_type} {var_name} = {expr_str};")
                        self.variables[var_name] = (var_type, expr_str)

            current_token = next(tokens, None)

        return statements

    def generate_c_code(self, python_code):
        tokens = self.tokenize(python_code)
        statements = self.parse(tokens)
        c_code = "#include <stdio.h>\n\nint main() {\n"
        
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