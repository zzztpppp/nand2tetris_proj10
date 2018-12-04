# A symbol table data type for the Jack compiler


class SymbolTable(object):

    def __init__(self):

        # Class level symbol table
        # to record static, field variables
        # in a class.
        self._class_table = dict()

        # Method level symbol table
        # to record argument and local variables
        # in a function.
        self._method_table = dict()

    def define(self, name, t, kind):
        """
        Defines a new identifier and inserts it
        into the symbol table and assigns running
        index to it

        :param name: String. Name of the identifier.
        :param t: String. Type of the identifier.
        :param kind: String. Category of the variable.
        :return:
        """

        pass

    def var_count(self, kind):
        """
        Return the variable count of a given kind.

        :param kind: String. Category of variables desired to count
        :return: int. The count
        """

        pass

    def kind_of(self, name):
        """
        Return the variable's category, given the variable's name.

        :param name: String. Variable's name.
        :return: String. The category.
        """

        pass

    def type_of(self, name):
        """
        Return the variable's type, given the variable's name.

        :param name: String. Variable's name.
        :return: String. The type
        """

        pass

    def index_of(self, name):
        """
        Returns the running index of the name in its category.

        :param name: String. Variable's name.
        :return: int. The index.
        """

        pass
