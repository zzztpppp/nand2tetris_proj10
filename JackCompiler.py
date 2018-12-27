
from VMwriter import VMWriter

class JackCompiler(object):
    """
    Compile a jack class from token codes.
    """

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
        pass

    def write_parameter_list(self):
        pass

    def write_statements(self):
        pass

    def write_do(self):
        pass

    def write_return(self):
        pass

    def write_while(self):
        pass

    def write_if(self):
        pass

    def write_let(self):
        pass

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


