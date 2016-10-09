from pytaskflow.taskflow_engine import Result, Function
import random


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


class GenerateRandomNumberAndAddToList(Function):
    def __init__(self):
        super(GenerateRandomNumberAndAddToList, self).__init__()

    def execute(self, input_result=Result(result_obj={})):
        numbers = []
        stop = False
        if 'Numbers' in input_result.result_obj:
            numbers = input_result.result_obj['Numbers']
        if len(numbers) < 10:
            numbers.append(random.randrange(100))
        if len(numbers) >= 10:
            stop = True
        self.result = Result(result_obj={'Numbers': numbers}, stop=stop)


class CalcSomeOfListOfNumbers(Function):
    def __init__(self):
        super(CalcSomeOfListOfNumbers, self).__init__()

    def execute(self, input_result=Result(result_obj={})):
        total = 0
        if 'Numbers' in input_result.result_obj:
            nums = input_result.result_obj['Numbers']
            for num in nums:
                if isinstance(num, int):
                    total += num
        self.result = Result(result_obj={'Total': total})


class DumpResultObj(Function):
    def __init__(self):
        super(DumpResultObj, self).__init__()

    def execute(self, input_result=Result(result_obj={})):
        if isinstance(input_result.result_obj, dict):
            for k,v in input_result.result_obj:
                print('DUMP: {}={}'.format(k, v))
        print('--- DUMP DONE ---')


# EOF