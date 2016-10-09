from pytaskflow.taskflow_engine import Result, Function


class ErrorMessageFunction(Function):
    def __init__(self):
        super(ErrorMessageFunction, self).__init__()

    def execute(self, input_result=Result(result_obj={})):
        if input_result.is_error:
            if input_result.err_msg is not None:
                print('ERROR: {}'.format(input_result.err_msg))
            else:
                print('ERROR: An error was set, but the error message was not provided')
        else:
            print('WARNING: The ErrorMessageFunction was called but the input_result contained no error information')
        self.result = Result(result_obj={}, stop=True)


# EOF