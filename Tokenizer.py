# A jack language tokenizer

class Tokenizer(object):
    
    SYMBOLS = ['{', '}', '[', ']', '(', ')', '.', ',', ';', '+', 
               '-', '*', '/', '&', '|', '<', '>', '=', '~']
    KEYWORDS = ['class', 'constructor', 'function', 'method', 'field', 
                'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 
                'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 
                'return']
    
    
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
                if line.startswith('//') or line.startswith('/**'):
                    continue
                potential_tokens = line.split()
                for potential_token in potential_tokens:
                    Tokenizer.tokenize_potential_token(potential_token, output)
            output.write('</tokens>')
                        
                
    @staticmethod
    def tokenize_potential_token(potential_token, output):
        """
        A potential token is a sequence of characters without whitespaes, which may
        be a single token or several tokens combined.
        @param potential_token: String a potential token
        @param output: File Object To which file the tokenized token(s) is goint to be
                                   stored
        """
        if potential_token in Tokenizer.KEYWORDS:
            output.write('    <keyword> ' + potential_token + ' </keyword>\n')
        else:
            token = ''
            for c in potential_token:
                if c in Tokenizer.SYMBOLS:
                    if c == '<':
                        output.write('    <symbol> ' + '&lt' + ' </symbol>\n')
                    elif c == '>':
                        output.write('    <symbol> ' + '&gt' + ' </symbol>\n')
                    else:
                        output.write('    <symbol> ' + c + ' </symbol>\n')
                else:
                    token += c
                
                if token.startswith('\"'):
                    output.write('    <stringConstant> ' + c[1:-1] + ' </stringConstant>')
                elif token != '':
                    output.write('    <identifier> ' + token + ' </identifier>')
        return
                
if __name__ == '__main__':
    import sys
    import os
    file_name = sys.argv[1]
    if os.path.isdir(file_name):
        pass
    if os.path.isfile(file_name):
        Tokenizer.tokenize(file_name)