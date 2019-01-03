
from VMwriter import VMWriter
from SymbolTable import SymbolTable


class JackCompiler(object):
    """
    Compile a jack class from token codes.
    """

    VARIABLES = [SymbolTable._CLASS_KIND, SymbolTable._METHOD_KIND]

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
        func_name = self.class_name + '.' + func_name

        # Get the number of arguments
        num_args = 0
        while True:
            if self._get_the_tag() == self.SYMBOL:
                num_args += 1
                self._advance()
            elif self._get_the_tag() == self.PARAM_LIST:
                break

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
        pass

    def write_do(self):
        pass

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

        return


    def write_expression(self):
        pass

    def write_term(self):
        pass

    def write_expression_list(self):
        pass

    def _advance(self):
        pass

    def _get_the_token(self):
        pass

    def _get_the_tag(self):
        pass

    def _parse_variable_tag(self):

        pass

    def _strip_var(self):
        pass


