# The VMWriter for the jack compiler


class VMWriter(object):

    def __init__(self, path):

        self.vm_file = open(path, 'w')

    def write_push(self, segment, index):
        """
        Write the push vm code.

        :param segment: The memory segment to push.
        :param index: The position in the given segment to push
        :return:
        """

        code = 'push {segment} {index}\n'.format(segment=segment, index=index)
        self.vm_file.write(code)

        return

    def write_pop(self, segment, index):
        """
        Write a VM pop code.

        :param segment: Memory segment the value is popped into.
        :param index: Position in the given segment is popped into.
        :return:
        """

        code = 'pop {segment} {index}\n'.format(segment=segment, index=index)
        self.vm_file.write(code)

        return

    def write_arithmetic(self, command):
        """
        Write the VM arithmetical code.
        :return:
        """

        code = '{command}\n'.format(command=command)
        self.vm_file.write(code)

        return

    def write_label(self, label):
        """
        Write a VM label command.

        :param label: String. The label name.
        :return:
        """
        code = '{label}'.format(label=label)
        self.vm_file.write(code)

        return

    def write_goto(self, label):
        """
        Write a VM goto command
        :param lable: String. The label name.
        :return:
        """



    def write_if(self):
        """
        Write a VM if-go command.
        :return:
        """

        pass

    def write_call(self, name, n_args):
        """
        Write a VM function call.

        :param name: Name of the function.
        :param n_args: Number of arguments the functions takes.
        :return:
        """

        pass

    def write_function(self, name, n_locals):
        """
        Write a VM function command.
        :param name: Name of the function.
        :param n_locals: Number of local variables the function has.
        :return:
        """

        pass

    def write_return(self):
        """
        Write a VM return command.
        :return:
        """

        pass

    def close(self):
        """
        Close the output file.
        :return:
        """

        pass
