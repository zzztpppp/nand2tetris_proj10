# A jack language tokenizer


class Tokenizer(object):
    
    SYMBOLS = ['{', '}', '[', ']', '(', ')', '.', ',', ';', '+', 
               '-', '*', '/', '&', '|', '<', '>', '=', '~']
    KEYWORDS = ['class', 'constructor', 'function', 'method', 'field', 
                'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 
                'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 
                'return']
    INTEGERS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']


    @staticmethod
    def tokenize(file_name):
        """
        Tokenize a single file.
        @param: file_name: file to be tokenized.
        """
        with open(file_name, 'r') as f:
            code_flow = f.readlines()
        
        # Start tokenizing the code line by line.
        with open(file_name[0:file_name.find('.')] + '.xml', 'w') as output:
            output.write('<tokens>\n')
            for line in code_flow:
                # Ommit annotations
                line = line.strip()
                if line.startswith('//') or line.startswith('/**') or line.startswith('*'):
                    continue
                # Ommit inline annotations
                an_pos = line.find('//')
                if an_pos > 0:
                    line = line[:an_pos]
                
                Tokenizer.tokenize_line(line.strip(), output)
            output.write('</tokens>')

    @staticmethod
    def tokenize_line(line, output):
        """
        Tokenize a line of code
        @param line: String, a line of code.
        @param output: File object, into which 
                       tokenized codes are written.
        """
        current_token = ''
        string_mod = False
        constant_mod = False
        for c in line:
            if string_mod:
                if c == '\"':
                    string_mod = False
                    output.write('    <stringConstant> ' + current_token[1:] + ' </stringConstant>\n')
                    current_token = ''
                else:
                    current_token += c
            
            elif constant_mod:
                if c in Tokenizer.INTEGERS:
                    current_token += c
                else:
                    constant_mod = False
                    output.write('    <integerConstant> ' + current_token + ' </integerConstant>\n')
                    current_token = ''
                    if c in Tokenizer.SYMBOLS:
                        output.write('    <symbol> ' + c + ' </symbol>\n')
                    else:
                        continue
                    
            elif c in Tokenizer.SYMBOLS:
                if current_token != '':
                    if current_token in Tokenizer.KEYWORDS:
                        output.write('    <keyword> ' + current_token + ' </keyword>\n')
                    else:
                        output.write('    <identifier> ' + current_token + ' </identifier>\n')
                    current_token = ''
                if c == '>':
                    output.write('    <symbol> ' + '&gt;' + ' </symbol>\n')
                elif c == '<':
                    output.write('    <symbol> ' + '&lt;' + ' </symbol>\n')
                elif c == '&':
                    output.write('    <symbol> ' + '&amp;' + ' </symbol>\n')
                else:
                    output.write('    <symbol> ' + c + ' </symbol>\n')
                current_token = ''
            elif c == ' ':
                if current_token in Tokenizer.KEYWORDS:
                    output.write('    <keyword> ' + current_token + ' </keyword>\n')
                elif current_token != '':
                    output.write('    <identifier> ' + current_token + ' </identifier>\n')
                
                current_token = ''
            elif c == '\"':
                  string_mod = True
                  current_token += c
                  
            elif c in Tokenizer.INTEGERS and current_token == '':
                constant_mod = True
                current_token += c
            
            else:
                current_token += c


def tokenize(file_name):
    import os
    if os.path.isdir(file_name):
        for file in os.listdir(file_name):
            path = os.path.join(file_name, file)
            tokenize(path)
    if os.path.isfile(file_name) and file_name.endswith('.jack'):
        Tokenizer.tokenize(file_name)


if __name__ == '__main__':
    import sys
    file_name = sys.argv[1]
    tokenize(file_name)
    
    
    
    
    
    
    