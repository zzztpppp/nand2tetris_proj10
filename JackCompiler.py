
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

    def __init__(self, parsed_codes, class_name):

        self.parsed_codes = parsed_codes
        self.progress = 0
        self.class_name = class_name
        self.writer = VMWriter(class_name + '.vm')

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
        while self._get_the_tag() != self.STATEMETNS_START:
            self._advance()

        self.write_statements()

        return

    def write_parameter_list(self):
        pass

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
        pass

    def write_if(self):
        pass

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
        while self._get_the_tag != self._EXPRESSION_END:
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
            num_args = self.write_expression()
            self.writer.write_call(func_name, num_args)

        # A method call





    def write_expression_list(self):
        pass

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
        tag = re.match(self.TAG_FINDER, current_line).strip('<>')
        if tag.split()[0] in self.VARIABLES:
            return 'variable'

        return tag

    def _parse_var_tag(self):

        current_line = self.parsed_codes[self.progress]
        tag = re.match(self.TAG_FINDER, current_line).strip('<>').split()

        return tag


