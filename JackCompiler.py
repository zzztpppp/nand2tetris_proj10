import re

from VMwriter import VMWriter
from SymbolTable import SymbolTable
from Tokenizer import Tokenizer
from CompilationEngine import CompilationEngine

def compile_file(file):
    """
    Compile a given file or a whole directory.
    :param : string
                 A file name or directory name.
    :return:
    """
    import os
    if os.path.isdir(file):
        for name in os.listdir(file):
            file_path = os.path.join(file, name)
            compile_file(file_path)
    else:
        _compile_file(file)

    return


def _compile_file(file_path):
    """
    Compile a single file
    :param file_path: string
    :return:
    """
    if not file_path.endswith('.xml'):
        return

    with open(file_path) as f:
        tokens = f.readlines()
        # Ignore the '<tokens>' signature
        compiler = JackCompiler(tokens, file_path[:-4], 10)
        compiler.write_class()

    return


class JackCompiler(object):
    """
    Compile a jack class from token codes.
    """
    UNARY_OP = ['-', '~']
    OPS = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
    VARIABLES = [SymbolTable._CLASS_KIND, SymbolTable._METHOD_KIND]
    VAR_MAP = {'static': 'static', 'field': 'this', 'ARG': 'argument', 'VAR': 'local'}
    OPS_MAP = {'+': 'add', '-': 'sub', '&amp;': 'and', '|': 'or', '&lt;': 'lt', '&gt;': 'gt', '=': 'eq'}
    U_OPS_MAP = {'-': 'neg', '~': 'not'}
    CONSTANTS = ['<integerConstant>', '<stringConstant>', '<keyword>']
    KEY_WORD_CONST_MAP = {'true': -1, 'false': 0 , 'null': 0}
    INSTANCE_FUNCS = ['constructor', 'method']
    STATIC_FUNCS = ['function']
    TAG_FINDER = re.compile('<.*?>')
    CLASS_VAR_DEC_START = '<classVarDec>'
    IDENTIFIER = '<identifier>'
    FUNC_START = '<subroutineDec>'
    STATEMENTS_START = '<statements>'
    STATEMENTS_END = '</statements>'

    PARAM_LIST_END = '</parameterList>'
    PARAM_LIST_START = '<parameterList>'

    DO_START = '<doStatement>'
    DO_END = '</doStatement>'

    IF_START = '<ifStatement>'
    IF_END = '</ifStatement>'

    LET_START = '<letStatement>'
    LET_END = '</letStatement>'

    RETURN_START = '<returnStatement>'
    RETURN_END = '</returnStatement>'

    WHILE_START = '<whileStatement>'
    WHILE_END = '</whileStatement>'

    EXPRESSION_START = '<expression>'
    EXPRESSION_END = '</expression>'

    EXPRESSION_LIST_START = '<expressionList>'
    EXPRESSION_LIST_END = '</expressionList>'

    TERM_START = '<term>'
    TERM_END = '</term>'

    CLASS_START = '<class>'
    CLASS_END = '</class>'

    FUNC_DEC_START = '<subroutineDec>'
    FUNC_DEC_END = '</subroutineDec>'

    FUNC_BODY_START = '<subroutineBody>'
    FUNC_BODY_END = '</subroutineBody>'

    VAR_START = '<varDec>'
    VAR_END = '</varDec>'

    ALL_STATEMENTS = [DO_START, LET_START, RETURN_START, WHILE_START, IF_START]

    def __init__(self, parsed_codes, class_name, size):

        self.parsed_codes = parsed_codes
        self.progress = 0
        self.class_name = class_name
        self.writer = VMWriter(class_name + '.vm')
        self.labels = 0
        self.size = size
        self.function_table = {}

    def write_class(self):
        """
        Write the VM code of a class

        :return:
        """

        self._advance(self.CLASS_START)
        self._eat('class')
        self._eat(self.class_name)
        self._eat('{')

        while self._get_the_tag() != self.FUNC_START:
            self._advance_hard()
        while self._get_the_tag() == self.FUNC_START:
            self.write_subroutine_dec()

        self._eat('}')
        self._advance_hard()

        return

    def write_subroutine_dec(self):
        """
        Write the VM code for a
        subroutine.

        :return:
        """

        # Get the functions name and type
        self._advance(self.FUNC_DEC_START)
        subroutine_type = self._get_the_token()
        self._eat(subroutine_type)
        return_type = self._get_the_token()
        self._eat(return_type)
        func_name = self._get_the_token()
        self._eat(func_name)

        # Store into a dictionary
        # for the convenience of in-class call.
        self.function_table[func_name] = subroutine_type

        # func_name = '.'.join([self.class_name, func_name])

        # Deal with parameter list, get the number of
        # parameters the function possesses.
        self._eat('(')
        n_args = self.write_parameter_list()
        self._eat(')')

        # Deal with the function body
        self.write_subroutine_body(func_name)

        # Subroutine end.
        self._advance(self.FUNC_DEC_END)

        return

    def write_local_var_dec(self):
        """
        Deal with the local variable
        declaration.

        :return: The number of local variables
                 a function possesses.
        """
        num_variables = 0
        while True:
            if self._get_the_tag() == self.VAR_START:
                num_variables += self._local_var_count()
            else:
                break

        return num_variables

    def _local_var_count(self):

        n_var = 1
        if self._get_the_tag() != self.VAR_START:
            raise ValueError('A variable declaration needed here')
        while self._get_the_tag() != self.VAR_END:
            if self._get_the_token() == ',':
                self._eat(',')
                n_var += 1
            else:
                self._advance_hard()

        self._advance(self.VAR_END)

        return n_var

    def write_subroutine_body(self, func_name):
        """
        Write the subroutine body.

        :return:
        """

        if self._get_the_tag() != '<subroutineBody>':
            raise ValueError('No subroutine body to process!')
        self._advance(self.FUNC_BODY_START)
        self._eat('{')

        # Deal with the function local variable and name space.
        # Allocate the memory and align to the base address.
        subroutine_type = self.function_table[func_name]
        n_vars = self.write_local_var_dec()
        func_name = '.'.join([self.class_name, func_name])
        self.writer.write_function(func_name, n_vars)

        # VM code needed for object manipulation.
        if subroutine_type == 'constructor':
            self.writer.write_push('constant', self.size)
            self.writer.write_call('Memory.alloc', 1)
            self.writer.write_pop('pointer', 0)
        if subroutine_type == 'method':
            self.writer.write_push('argument', 0)
            self.writer.write_pop('pointer', 0)

        self.write_statements()

        self._eat('}')
        self._advance(self.FUNC_BODY_END)

        return

    def write_parameter_list(self):
        """
        Count and return the number of
        parameters a function takes

        :return: Int number of arguments.
        """

        self._advance(self.PARAM_LIST_START)
        n_commas = 0
        has_args = False

        # If commas are detected, number of arguments of
        # the given function must be num commas + 1
        while self._get_the_tag() != self.PARAM_LIST_END:
            if self._get_the_token() == ',':
                self._eat(',')
                n_commas += 1
            else:
                has_args = True
                self._advance_hard()
        self._advance(self.PARAM_LIST_END)

        # No commas detected and no arguments.
        if n_commas == 0 and not has_args:
            return 0

        return n_commas + 1

    def write_statements(self):
        # Advance over the statements wrapper.
        self._advance(self.STATEMENTS_START)

        # Write the 5 types of statements
        while self._get_the_tag() in self.ALL_STATEMENTS:
            the_tag = self._get_the_tag()
            if the_tag == self.DO_START:
                self.write_do()
            if the_tag == self.IF_START:
                self.write_if()
            if the_tag == self.LET_START:
                self.write_let()
            if the_tag == self.RETURN_START:
                self.write_return()
            if the_tag == self.WHILE_START:
                self.write_while()
        self._advance(self.STATEMENTS_END)
        return

    def write_do(self):
        """
        Write a do statement
        :return:
        """
        # Advance over the do statement wrapper

        self._advance(self.DO_START)
        self._eat('do')

        is_method = True
        the_name = self._get_the_token()
        if self._get_the_tag() == self.IDENTIFIER:
            self._eat(the_name)
            if self._get_the_token() == '.':
                is_method = False
                self._eat('.')
                func_name = self._get_the_token()
                self._eat(func_name)
                func_name = '.'.join([the_name, func_name])
            else:
                self.writer.write_push('pointer', 0)
                func_name = '.'.join([self.class_name, the_name])
        else:
            var_tag = self._parse_var_tag()
            self._eat(the_name)
            var_type = var_tag[1]
            self.writer.write_push(self.VAR_MAP[var_tag[0]], var_tag[2])
            self._eat('.')
            the_name = self._get_the_token()
            func_name = '.'.join([var_type, the_name])
            self._eat(the_name)

        self._eat('(')
        n_args = self.write_expression_list()
        if is_method:
            n_args += 1
        self._eat(')')
        self.writer.write_call(func_name, n_args)

        # Drop the return value.
        self.writer.write_pop('temp', 1)
        self._eat(';')
        self._advance(self.DO_END)
        return

    def write_return(self):
        """
        Generate and write the
        return statement.

        :return:
        """

        value_returned = False
        self._advance(self.RETURN_START)
        self._eat('return')
        if self._get_the_tag() == self.EXPRESSION_START:
            value_returned = True
            self.write_expression()
        self._eat(';')
        self._advance(self.RETURN_END)

        if not value_returned:
            self.writer.write_push('constant', 1)

        self.writer.write_return()

        return

    def write_while(self):
        """
        Write the VM code for while statements
        :return:
        """

        # Put the label
        label_1 = '_'.join([self.class_name, self._get_label()])
        label_2 = '_'.join([self.class_name, self._get_label()])

        self.writer.write_label(label_1)

        self._advance(self.WHILE_START)
        self._eat('while')
        self._eat('(')
        self.write_expression()
        self._eat(')')
        self.writer.write_arithmetic('not')
        self.writer.write_if(label_2)

        self._eat('{')
        self.write_statements()
        self._eat('}')
        self._advance(self.WHILE_END)
        self.writer.write_goto(label_1)
        self.writer.write_label(label_2)

        return

    def write_if(self):
        """
        Write the VM code for the if clause

        :return:
        """

        # Generate labels needed in this if clause
        label_1 = '_'.join([self.class_name, self._get_label()])
        label_2 = '_'.join([self.class_name, self._get_label()])

        # Advance over the if head.
        self._advance(self.IF_START)
        self._eat('if')
        self._eat('(')
        self.write_expression()
        self._eat(')')

        self.writer.write_arithmetic('not')
        self.writer.write_if(label_1)
        self._eat('{')
        self.write_statements()
        self._eat('}')
        self.writer.write_goto(label_2)

        self.writer.write_label(label_1)
        if self._get_the_token() == 'else':
            self._eat('else')
            self._eat('{')
            self.write_statements()
            self._eat('}')
        self.writer.write_label(label_2)

        self._advance(self.IF_END)
        return

    def write_let(self):
        """
        Generate VM code for let statement.
        :return:

        """

        # Advance over head.
        self._advance(self.LET_START)
        self._eat('let')

        tag = self._parse_var_tag()
        var_type = self.VAR_MAP[tag[0]]
        index = tag[2]
        self._eat(self._get_the_token())

        array_assignment = False
        if self._get_the_token() == '[':
            array_assignment = True
            self._eat('[')
            self.write_expression()
            self._eat(']')

        self._eat('=')

        # Write the vm code for assignee
        self.write_expression()

        # Assign values to the assigner
        if array_assignment:
            self.writer.write_pop('temp', 0)
            self.writer.write_push(var_type, index)
            self.writer.write_arithmetic('add')
            self.writer.write_pop('pointer', 1)
            self.writer.write_push('temp', 0)
            self.writer.write_pop('that', 0)
        else:
            self.writer.write_pop(var_type, index)

        # Advance over the tail.
        self._eat(';')
        self._advance(self.LET_END)

        return

    def write_expression(self):
        """
        Write the VM code of an expression.
        :return:
        """

        # Advance over the expression header.
        self._advance(self.EXPRESSION_START)

        # Compile the expression element by element(term or op)
        # the op is written if and if only if 2 terms are written.
        terms_written = 0
        the_op = None
        while self._get_the_tag() != self.EXPRESSION_END:
            if self._get_the_token() in self.OPS:
                the_op = self._get_the_token()
                self._eat(the_op)
            elif self._get_the_tag() == self.TERM_START:
                self.write_term()
                terms_written += 1

            if terms_written == 2:
                print(the_op)
                if the_op in self.OPS_MAP.keys():
                    self.writer.write_arithmetic(self.OPS_MAP[the_op])
                elif the_op == '*':
                    self.writer.write_call('Math.multiply', 2)
                elif the_op == '/':
                    self.writer.write_call('Math.divide', 2)

                terms_written = 1

        self._advance(self.EXPRESSION_END)

        return

    def write_term(self):
        self._advance(self.TERM_START)
        the_tag = self._get_the_tag()
        if the_tag in self.CONSTANTS:
            the_token = self._get_the_token()
            if the_token == 'this':
                self.writer.write_push('pointer', 0)
            elif the_token == 'that':
                self.writer.write_push('pointer', 1)
            elif the_tag == '<stringConstant>':
                string_length = len(the_token)
                self.writer.write_push('constant', string_length)
                self.writer.write_call('String.new', 1)

                # Construct the string in a loop.
                # For sake of convenience, copy
                # the new initialized string as many
                # times as we need to construct it.
                self.writer.write_pop('temp', 1)
                for _ in range(string_length + 1):
                    self.writer.write_push('temp', 1)
                for i in range(string_length):
                    char = ord(the_token[i])
                    self.writer.write_push('constant', char)
                    self.writer.write_call('String.appendChar', 2)
                    self.writer.write_pop('temp', 1)
            elif the_tag == '<keyword>':
                if the_token == 'true':
                    self.writer.write_push('constant', 1)
                    self.writer.write_arithmetic('neg')
                else:
                    self.writer.write_push('constant', 0)

            else:
                if the_token[0] in self.U_OPS_MAP.keys():
                    self.writer.write_push('constant', the_token[1:])
                    self.writer.write_arithmetic(the_token[0])
                else:
                    self.writer.write_push('constant', the_token)
            self._eat(the_token)

        # A static function call.
        elif the_tag == self.IDENTIFIER:
            class_name = self._get_the_token()
            self._eat(class_name)
            self._eat('.')
            func_name = self._get_the_token()
            self._eat(func_name)
            func_name = '.'.join([class_name, func_name])

            self._eat('(')
            num_args = self.write_expression_list()
            self._eat(')')
            self.writer.write_call(func_name, num_args)

        elif self._get_the_token() == '(':
            self._eat('(')
            self.write_expression()
            self._eat(')')

        # An unary op
        elif self._get_the_token() in self.UNARY_OP:
            unary_op = self._get_the_token()
            self._eat(unary_op)
            self.write_term()
            self.writer.write_arithmetic(self.U_OPS_MAP[unary_op])

        # An object operation
        else:
            var_name = self._get_the_token()
            var_tag = self._parse_var_tag()
            segment = self.VAR_MAP[var_tag[0]]
            index = var_tag[2]
            self._eat(var_name)

            # A method call
            if self._get_the_token() == '.':
                self._eat('.')
                method_name = self._get_the_token()
                self._eat(method_name)
                method_name = '.'.join([var_tag[1], method_name])

                # Push the object's pointer
                self.writer.write_push(segment, index)

                self._eat('(')
                nargs = self.write_expression_list() + 1
                self._eat(')')
                self.writer.write_call(method_name, nargs)

            # An array addressing
            elif self._get_the_token() == '[':
                self._eat('[')
                self.write_expression()
                self._eat(']')

                self.writer.write_push(segment, index)
                self.writer.write_arithmetic('add')
                self.writer.write_pop('pointer', 1)
                self.writer.write_push('that', 0)

            # Just a variable
            else:
                self.writer.write_push(segment, index)

        self._advance(self.TERM_END)

        return

    def write_expression_list(self):
        """
        Write the vm code of an expression list with a function call.
        :return:
        """

        self._advance(self.EXPRESSION_LIST_START)
        n_args = 0
        while self._get_the_tag() != self.EXPRESSION_LIST_END:
            # print(self._get_the_tag() + 'Fuck')
            if self._get_the_tag() == self.EXPRESSION_START:
                n_args += 1
                self.write_expression()
            else:
                self._advance_hard()
        self._advance(self.EXPRESSION_LIST_END)
        return n_args

    def _advance(self, tag):
        """
        Advance over pure tags

        :return:
        """

        if self._get_the_token() != '':
            raise ValueError('Cannot advance over tokens!')

        if len(self.parsed_codes) <= self.progress:
            raise IndexError('No tag to advance over anymore!')

        if self._get_the_tag() != tag:
            raise ValueError('No such tag {tag} to advance over'.format(tag=tag))

        print(self._get_the_tag())
        self.progress += 1

        return

    def _advance_hard(self):
        """
        Force the compilation engine to advance a line of code.
        This method can't do advancing over a pure tag.
        :return:
        """
        print(self.parsed_codes[self.progress])

        # if self._get_the_token() == '':
        #     raise ValueError('Hard advancing cannot advance over a pure tag ', self._get_the_tag())
        if self._get_the_tag() == self.EXPRESSION_LIST_END:
            raise ValueError('Fuck! How dare you advance this???????????????????????????????????')
        if len(self.parsed_codes) <= self.progress:
            raise IndexError('No codes to compile anymore')

        self.progress += 1

        return

    def _eat(self, token):
        """
        Advance over a given token.
        Raise ValueError if the current code does not match\
        the given token.

        :return:
        """

        if token == '&lt':
            raise ValueError('The sneaky bastard is here')

        if self._get_the_token() != token:
            raise ValueError('No {0} to eat, current token is {1}'.format(token, self._get_the_token()))

        print(self._get_the_token())
        if len(self.parsed_codes) <= self.progress:
            raise IndexError('No codes to compile anymore')

        self.progress += 1

        return

    def _get_the_token(self):
        current_line = self.parsed_codes[self.progress].strip()
        return re.sub(self.TAG_FINDER, '', current_line).strip()

    def _get_the_tag(self):

        current_line = self.parsed_codes[self.progress].strip()
        tag = re.match(self.TAG_FINDER, current_line).group(0)
        if tag.split()[0] in self.VARIABLES:
            return 'variable'

        return tag

    def _parse_var_tag(self):

        current_line = self.parsed_codes[self.progress].strip()
        tag = re.match(self.TAG_FINDER, current_line).group(0).strip('<>').split()

        return tag

    def _get_label(self):

        self.labels += 1

        return str(self.labels)


def compile(file):
    """
    Compile a given file or a whole directory.
    :param : string
                 A file name or directory name.
    :return:
    """
    import os
    if os.path.isdir(file):
        for name in os.listdir(file):
            file_path = os.path.join(file, name)
            compile(file_path)
    else:
        _compile(file)

    return

def _compile(file_path):
    if not file_path.endswith('.jack'):
        return


    # Tokenize the code
    import os
    print('Processing file', os.path.basename(file_path), '=============================================')

    Tokenizer.tokenize(file_path)
    token_path = file_path.replace('jack', 'xml')
    with open(token_path) as f:
        tokens = f.readlines()

    # Syntax analysis
    compiler = CompilationEngine(tokens[1:-1])
    result = compiler.get_result()

    # Compile to VM code
    print('Processing file', os.path.basename(token_path))
    num_fields = compiler.symbol_table.var_count('field')
    compiler = JackCompiler(result, os.path.basename(token_path)[:-4], num_fields)
    compiler.write_class()

    return


if __name__ == '__main__':
    import sys
    file_name = sys.argv[1]
    compile(file_name)