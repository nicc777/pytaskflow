from pytaskflow.taskflow_engine import Result, Function, Task
import random


class ErrorMessageFunction(Function):
    def __init__(self):
        super(ErrorMessageFunction, self).__init__()

    def execute(self, input_result=Result(result_obj={}), globals_dict={}):
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

    def execute(self, input_result=Result(result_obj={}), globals_dict={}):
        """
        Optional input parameters (result_obj dict):
            'Numbers': list of integers
        :param input_result: Result with the input parameters
        :param globals_dict: dict
        :return: nothing - sets self.result
        """
        numbers = []
        success_task = None
        if 'Numbers' in input_result.result_obj:
            numbers = input_result.result_obj['Numbers']
        if len(numbers) < 10:
            numbers.append(random.randrange(100))
            if 'GenerateRandomNumberAndAddToListTask' in globals_dict:
                success_task = globals_dict['GenerateRandomNumberAndAddToListTask']
        self.result = Result(result_obj={'Numbers': numbers}, override_success_task=success_task)


class CalcSumOfListOfNumbers(Function):
    def __init__(self):
        super(CalcSumOfListOfNumbers, self).__init__()

    def execute(self, input_result=Result(result_obj={}), globals_dict={}):
        total = 0
        if 'Numbers' in input_result.result_obj:
            nums = input_result.result_obj['Numbers']
            for num in nums:
                if isinstance(num, int):
                    total += num
        self.result = Result(result_obj={'Total': total, 'Stop': True})


class DumpResultObj(Function):
    def __init__(self):
        super(DumpResultObj, self).__init__()

    def execute(self, input_result=Result(result_obj={}), globals_dict={}):
        if isinstance(input_result.result_obj, dict):
            for k,v in input_result.result_obj.items():
                print('DUMP: {}={}'.format(k, v))
        print('--- DUMP DONE ---')
        stop = False
        if 'Stop' in input_result.result_obj:
            if isinstance(input_result.result_obj['Stop'], bool):
                stop = input_result.result_obj['Stop']
                del input_result.result_obj['Stop']
        self.result = Result(result_obj=input_result.result_obj, stop=stop)


# EOF