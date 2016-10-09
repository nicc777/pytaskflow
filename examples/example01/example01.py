from examples.example01.workflow_factory import get_workflow, get_error_task
from examples.example01.functions import DumpResultObj, CalcSumOfListOfNumbers
from pytaskflow.taskflow_engine import Result, Task

if __name__ == '__main__':
    t3 = Task(task_name='Task 3: Dump All Variables')
    t3.register_function(function=DumpResultObj(), success_task=None, err_task=None)
    t2 = Task(task_name='Task 2: Calculate Sum Total of a List of Numbers')
    t2.register_function(function=CalcSumOfListOfNumbers(), success_task=t3, err_task=get_error_task())
    workflow = get_workflow()
    result = workflow.run_workflow(input_result=Result(result_obj={'SuccessTask': t2}))
    for k, v in result.result_obj.items():
        print('RESULT: {}={}'.format(k, v))

# EOF