
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
        pass

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


    def write_term(self):
        pass

    def write_expression_list(self):
        pass

    def _advance(self):
        """
        Return current code and move forward.
        :return:
        """

        pass

