# A symbol table data type for the Jack compiler


class SymbolTable(object):

    _CLASS_KIND = ['STATIC', 'FIELD']
    _METHOD_KIND = ['ARG', 'VAR']

    # Indices of each property
    TYPE = 0
    KIND = 1
    INDEX = 2

    def __init__(self):

        # Class level symbol table
        # to record static, field variables
        # in a class.
        self._class_table = dict()
        self._class_indices = dict.fromkeys(self._CLASS_KIND, 0)

        # Method level symbol table
        # to record argument and local variables
        # in a function.
        self._method_table = dict()
        self._method_indices = dict.fromkeys(self._METHOD_KIND, 0)

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

        if kind not in (self._CLASS_KIND + self._METHOD_KIND):
            raise ValueError('Unknown kind of variable!')

        # Determine which sub-table the given variable belongs to.
        is_class = kind in self._CLASS_KIND
        table = self._class_table if is_class else self._method_table
        indices = self._class_indices if is_class else self._method_indices

        # Insert to the sub-table
        table[name] = [t, kind, indices[kind]]
        indices[kind] += 1

        return

    def var_count(self, kind):
        """
        Return the variable count of a given kind.

        :param kind: String. Category of variables desired to count
        :return: int. The count
        """
        if kind not in (self._CLASS_KIND + self._METHOD_KIND):
            raise ValueError('Unknown kind of variable!')

        if kind in self._CLASS_KIND:
            return self._class_indices[kind]
        else:
            return self._method_indices[kind]

    def kind_of(self, name):
        """
        Return the variable's category, given its name.

        :param name: String. Variable's name.
        :return: String. The category.
        """

        info = self.info_of(name)
        return info[self.KIND]

    def type_of(self, name):
        """
        Return the variable's type, given the its name.

        :param name: String. Variable's name.
        :return: String. The type
        """

        info = self.info_of(name)
        return info[self.TYPE]

    def index_of(self, name):
        """
        Returns the running index of the name in its category.

        :param name: String. Variable's name.
        :return: int. The index.
        """

        info = self.info_of(name)
        return info[self.INDEX]

    def info_of(self, name):
        """
        Fetch the whole row indexed by the given name.
        :param name: Given identifier name.
        :return: List. Contains type, kind, index.
        """

        info = self._class_table.get(name)

        if info is None:
            info = self._method_table.get(name)

        return info

    def drop_method_table(self):
        """
        Drop the method level sub-table
        :return:
        """

        self._method_table = dict()

        return


if __name__ == '__main__':
    table_test = SymbolTable()
    table_test.define('a', 'int', 'STATIC')
    print(table_test.index_of('a'), table_test.kind_of('a'), table_test.type_of('a'))
