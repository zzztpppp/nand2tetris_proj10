# This is the jack language compilation engine

class CompilationEngine(object):
    
    SUBROUTINE_TYPE = ['function', 'method', 'constructor']
    CLASS_VAR_TYPE = ['static', 'field']
    VAR_TYPE = ['int', 'char', 'boolean']
    PRIMITIVE_RETURN_TYPE = ['int', 'char', 'boolean', 'void']
    STATEMENTS_TYPES = ['let', 'do', 'while', 'if', 'return']
    
    def __init__(self, input_tokens):
        """
        :param input_tokens: A list of strings, each of which stands for a token
                            generated by a tokenizer
        """
        self.token_list = input_tokens
        self.num_tokens_left = len(input_tokens)
        self.current_token = 0
        self.compilation_result = []
    
    def compile_class(self):
        """
        Compile a whole class. This method will be invoked
        when a 'class' keyword is seen by the engine.
        """
     
        if self._get_the_token() != 'class':
            raise ValueError('Missing keyword <class>')
            
        self.compilation_result.append('<class>')
        
        # Compile class head.
        self._eat('class')
        if self._get_the_token_type() != 'identifier':
            raise ValueError('An identifier must be followed by a class declaration')
        self.eat(self._get_the_token())
        self._eat('{')

        # Compile the class body recursively
        while self.num_tokens_left > 0:
            the_token = self._get_the_token()
            if the_token in self.CLASS_VAR_TYPE:
                self.compile_class_var_dec()

            elif the_token in self.SUBROUTINE_TYPE:
                self.compile_subroutine_dec()

        return self.compilation_result

    def compile_class_var_dec(self):
        """
        Compile a static or field variable declaration
        """
        # Compile the head of class variable declaration.
        self.compilation_result.append('<classVarDec>')
        self._eat(self._get_the_token())
        if self._get_the_token_type() == 'identifier' or self._get_the_token() in VAR_TYPE:
            self._eat(self._get_the_token())
        else:
            raise ValueError('Variable type should be specified')
        
        # Compile the variable(s) declared.
        while self._get_the_token() != ';':
            if self._get_the_token_type() == 'identifier':
                self._eat(self._get_the_token)
            else:
                raise ValueError('Illegal variable name!')
            
            if self._get_the_token() == ',':
                self._eat(',')
            elif self._get_the_token() != ';':
                raise ValueError('Variable names must seperated by comma')
        self._eat(';')
        
        self.compilation_result.append('</classVarDec>')
        
        return
        
    def compile_subroutine_dec(self):
        """
        Compile a method/function/constructor declaration in a class.
        """
        self.compilation_result.append('<subroutineDec>')
        self._eat(self._get_the_token())
        
        # Then token after the subroutine signiture should be
        # the return type of the subroutine
        if self._get_the_token_type() in PRIMITIVE_RETURN_TYPE or self._get_the_token_type == 'identifier':
            self._eat(self._get_the_token())
        
        else:
             raise ValueError('Illegal return type!')
        
        if self._get_the_token_type() == 'identifier':
            self._eat(self._get_the_token())
        else:
            raise ValueError('Illegal function name!')
        
        # Compile the subroutine's parameters
        # and the paranthesis.
        self._eat('(')
        self.compile_parameter_list()
        self._eat(')')
        
        # Compile the subroutine's body
        # and the wrapping curly brackets.
        self.compile_subroutine_body()
        self.compilation_result.append('</subroutineDec>')
        
        
        
        return
        
    def compile_subroutine_body(self):
        """
        Compile a subroutine's body.
        A subroutine body each consists of a sequence of variable declaration or a sequence
        of statements
        """
        self.compilation_result.append('<subroutineBody>')
        self._eat('{')
        
        while self._get_the_token() == 'var':
            self.compile_var_dec()
        
        if self._get_the_token() not in STATEMENTS_TYPES:
            raise ValueError('There is no statement in this subroutine!')
        self.compile_statments()
        
        self._eat('}')
        self.compilation_result.append('/subroutineBody')
        
        return
    
    
    def compile_parameter_list(self):
        """
        Comile a (list of) parameters.
        """
        self.compilation_result.append('<parameterList>')
        
        # Compile 0 or more comma seperated parameters
        while self.current_token != ')':
            if self._get_the_token_type() in VAR_TYPE or self._get_the_token_type() == 'identifier':
                self.eat(self._get_the_token())
            else:
                raise ValueError('Illegal parameter type.')
            
            
            if self._get_the_token_type() == 'identifier':
                self._eat(self._get_the_token())
            else:
                raise ValueError('Illegal parameter name!')
            
            if self._get_the_token() == ',':
                self._eat(',')
            elif self._get_the_token() != ')':
                raise ValueError('Parameters must be seperated by comma!')
        
        self.compilation_result.append('</parameterList>')
        
        return
    
    def compile_var_dec(self):
        """
        Compile the variable declaration in a method/function.
        """
        self._eat('var')
        
        if self._get_the_token_type() in VAR_TYPE or self._get_the_token_type() == 'identifier':
            self._eat(self._get_the_token())
        else:
            raise ValueError('Illegal variable type!')
        
        if self._get_the_token_type() != 'identifier':
            raise ValueError('Illegal variable name!')
        else:
            self._eat(self._get_the_token())
        
        self._eat(';')
        
        return
        
    def compile_statements(self):
        """
        Compile a sequence of statements, not including the enclosing curly brackets.
        """
        returned = False
        while self._get_the_token() in STATEMENTS_TYPES:
            the_token = self._get_the_token()
            if the_token == 'do':
                self.compile_do()
            if the_token == 'let':
                self.compile_let()
            if the_token == 'while':
                self.compile_while()
            if the_token == 'if':
                self.compile_if()
            if the_token == 'return':
                returned = True
                self.compile_return()
                
        if not returned:
            raise ValueError('No return statement!')
            
        return
        
    def compile_do(self):
        """
        Compiles a do statement.
        """
        self._eat('do')
        
        self._eat(self._get_the_token())
        self._eat('(')
        self.compile_expression_list()
        self._eat(')')
        self._eat(';')
        
        return
        
    def compile_let(self):
        """
        Compile a let statement.
        """
        self._eat('let')
        self._eat()
        
    def compile_while(self):
        """
        Compile a while statement.
        """
        pass
    
    def compile_return(self):
        """
        Compile a return statement.
        """
        pass
    
    def compile_if(self):
        """
        Compile a if statement.
        """
        pass
        
    def compile_expression(self):
        """
        Compile an expression.
        """
        pass
        
    def compile_term(self):
        """
        Compile a term.
        """
        pass
        
    def compile_expression_list(self):
        """
        Compile a list of expressions.
        """
        pass
        
    def _eat(self, token):
        """
        :param token: String
                      The token to advance over.
        Ouput the given token and advance the token list.
        """
        pass
    
    def _get_token_type(self):
        """
        Return the current the token
        :return: String
                 The current token.
        """

        pass
    
    def _get_the_token(self):
        pass