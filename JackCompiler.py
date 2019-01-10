import re

from VMwriter import VMWriter
from SymbolTable import SymbolTable


class JackCompiler(object):
    """
    Compile a jack class from token codes.
    """
    UNARY_OP = ['-', '~']
    OPS = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
    VARIABLES = [SymbolTable._CLASS_KIND, SymbolTable._METHOD_KIND]
    OPS_MAP = {'+': 'add', '-': 'sub', '&amp': 'and', '|': 'or', '&lt': 'lt', '&gt': 'gt', '=': 'eq'}
    CONSTANTS = ['integerConstant', 'stringConstant', 'keywordConstant']
    TAG_FINDER = re.compile('<.*?>')
    IDENTIFIER = 'identifier'
    STATEMENTS_START = '<statements>'
    PARAM_LIST_END = '</parameterList>'
    DO_START = '<doStatement>'
    IF_START = '<ifStatement>'
    LET_START = '<letStatement>'
    RETURN_START = '<returnStatement>'
    RETURN_END = '</returnStatement>'
    WHILE_START = '<whileStatement>'
    EXPRESSION_START = '<expression>'
    EXPRESSION_END = '</expression>'
    EXPRESSION_LIST_END = '</expressionList>'
    TERM_START = '<term>'

    def __init__(self, parsed_codes, class_name):

        self.parsed_codes = parsed_codes
        self.progress = 0
        self.class_name = class_name
        self.writer = VMWriter(class_name + '.vm')
        self.labels = 0

    def write_class(self):
        pass

    def write_subroutine_dec(self):
        for _ in range(3):
            self._advance()

        # Get the function name
        func_name = self._get_the_token()
        func_name = '.'.join([func_name, self.class_name])

        # Get the number of arguments, by counting the
        # number of commas appeared in the parameters
        num_args = 0
        while True:
            if self._get_the_tag() == self.SYMBOL:
                num_args += 1
                self._advance()
            elif self._get_the_tag() == self.PARAM_LIST_END:
                break
        num_args += 1
        self.writer.write_function(func_name, num_args)

        return

    def write_subroutine_body(self):
        """
        Write the VM code of a subroutine
        body.
        :return:
        """

        # Ignore the variable declaration.
        while self._get_the_tag() != self.STATEMENTS_START:
            self._advance()

        self.write_statements()

        return

    def write_parameter_list(self):
        """
        Count and return the number of
        parameters a function takes

        :return: Int number of arguments.
        """

        n_args = 0
        while self._get_the_tag() != self.PARAM_LIST_END:
            if self._get_the_token() == ',':
                n_args += 1

        return n_args + 1


    def write_statements(self):
        # Advance over the statements wrapper.
        self._advance()

        # Write the 5 types of statements
        while self._get_the_tag() in self.STATEMENTS_START:

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

        return

    def write_do(self):
        # Advance over the do statement wrapper
        while self._get_the_tag() != self.DO_START:
            self._advance()

        func_name = self._get_the_token()
        func_name = '.'.join([func_name, self.class_name])

    def write_return(self):
        """
        Genearate and write the
        return statement.

        :return:
        """

        value_returned = False
        while self._get_the_tag() != self.RETURN_END:
            self._advance()
            if self._get_the_tag() == self.EXPRESSION_START:
                self.write_expression()
                value_returned = True

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

        self._advance()
        self._eat('while')
        self._eat('(')
        self.write_expression()
        self._eat(')')
        self.writer.write_arithmetic('not')
        self.writer.write_if(label_2)

        self.write_statements()
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
        self._advance()
        self._eat('if')
        self._eat('(')
        self.write_expression()
        self._eat(')')

        self.writer.write_arithmetic('not')
        self.writer.write_if(label_1)
        self._eat('{')
        self.write_statements()
        self._eat('}')





    def write_let(self):
        """
        Generate VM code for let statement.
        :return:

        """

        # Advance over head.
        while self._get_the_tag() != self.IDENTIFIER or self._get_the_tag() != self.VARIABLES:
            self._advance()

        tag = self._strip_var()
        var_type = tag[0]
        index = tag[2]
        self._advance()

        array_assignment = False
        while self._get_the_token() != '=':
            self._advance()
            if self._get_the_token() == '[':
                array_assignment = True
                self._advance()
                self.write_expression()

        # Write the vm code for assignee
        self.write_expression()

        # Assign values to the assigner
        # TODO: Convert var_type to segment.
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
        self._advance()

        return

    def write_expression(self):
        """
        Write the VM code of an expression.
        :return:
        """

        # Advance over the expression header.
        self._advance()

        # Compile the expression element by element(term or op)
        # the op is written if and if only if 2 terms are written.
        terms_written = 0
        the_op = None
        while self._get_the_tag != self.EXPRESSION_END:
            if self._get_the_token() in self.OPS:
                the_op = self._get_the_token()
            elif self._get_the_tag()  == self.TERM_START:
                self.write_term()
                terms_written += 1

            if terms_written == 2:
                if the_op in self.OPS_MAP.keys():
                    self.writer.write_arithmetic(self.OPS_MAP[the_op])
                elif the_op == '*':
                    self.writer.write_call('Math.multiply', 2)
                elif the_op == '/':
                    self.writer.write_call('Math.divide', 2)

                terms_written = 1

        self._advance()

    def write_term(self):
        self._advance()
        if self._get_the_tag() in self.CONSTANTS:
            self.writer.write_push('constant', self._get_the_token())

        # A static function call.
        elif self._get_the_tag() == self.IDENTIFIER:
            class_name = self._get_the_token()
            self._eat(class_name)
            self._eat('.')
            func_name = self._get_the_token()
            func_name = '.'.join([class_name, func_name])

            self._eat('(')
            num_args = self.write_expression_list()
            self.writer.write_call(func_name, num_args)

        # A variable operation
        elif self._get_the_tag() == 'variable':
            var_name = self._get_the_token()
            var_tag = self._parse_var_tag()
            segment = var_tag[0]
            index = var_tag[2]
            self._eat(var_name)

            # A method call
            if self._get_the_token() == '.':
                self._eat('.')
                method_name = self._get_the_token()
                method_name = '.'.join([var_tag[1], method_name])

                # Push the object's pointer
                self.writer.write_push(segment, index)

                self._eat('(')
                self._eat(')')
                nargs = self.write_expression_list()
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

        return


    def write_expression_list(self):
        """
        Write the vm code of an expression list with a function call.
        :return:
        """

        n_args = 0
        while self._get_the_tag() != self.EXPRESSION_LIST_END:
            if self._get_the_tag() == self.EXPRESSION_START:
                n_args += 1
                self.write_expression()
            else:
                self._advance()

        return

    def _advance(self):
        """
        Advance over pure tags

        :return:
        """

        if self._get_the_token() != '':
            raise ValueError('Cannot advance over tokens!')

        if len(self.parsed_codes) <= self.progress:
            raise IndexError('No tag to advance over anymore!')

        self.progress += 1

        return

    def _eat(self, token):
        """
        Advance over a given token.
        Raise ValueError if the current code does not match\
        the given token.

        :return:
        """

        print(self._get_the_token())
        if self._get_the_token() != token:
            raise ValueError('No {0} to eat'.format(token))

        if len(self.parsed_codes) <= self.progress:
            raise IndexError('No codes to compile anymore')

        self.progress += 1

        return

    def _get_the_token(self):
        current_line = self.parsed_codes[self.progress]
        return re.sub(self.TAG_FINDER, '', current_line)

    def _get_the_tag(self):

        current_line = self.parsed_codes[self.progress]
        tag = re.match(self.TAG_FINDER, current_line).group(0).strip('<>')
        if tag.split()[0] in self.VARIABLES:
            return 'variable'

        return tag

    def _parse_var_tag(self):

        current_line = self.parsed_codes[self.progress]
        tag = re.match(self.TAG_FINDER, current_line).group(0).strip('<>').split()

        return tag

    def _get_label(self):

        self.labels += 1

        return str(self.labels)
