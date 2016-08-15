from pytaskflow.taskflow_engine import *


class VisitCounterFunction(Function):
    def __init__(self):
        super(VisitCounterFunction, self).__init__()

    def result(self, entry_point=EntryPoint(), previous_result=None):
        counter_value = 0
        result_obj = {}
        proceed = True
        if isinstance(previous_result, Result):
            if previous_result.is_error is False:
                if isinstance(previous_result.result_obj, dict):
                    result_obj = previous_result.result_obj
                    if 'CounterValue' in result_obj:
                        if isinstance(result_obj['CounterValue'], int):
                            counter_value = previous_result.result_obj['CounterValue'] + 1
            else:
                proceed = False
        result_obj['CounterValue'] = counter_value
        result_obj['Proceed'] = proceed
        result = Result(result_obj)
        return result