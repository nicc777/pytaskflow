from .application_tasks import sample_application_task_collection
from pytaskflow.taskflow_engine import EntryPoint, WorkFlow, Result
import warnings


def flask_sample_app_workflow(entry_point):
    template_name = 'home'
    counter_value = 0
    if isinstance(entry_point, EntryPoint):
        app_workflow = WorkFlow("GetSessionFunction", sample_application_task_collection(), entry_point=entry_point)
        result = app_workflow.result
        if isinstance(result, Result):
            result_obj = result.result_obj
            if 'TemplateName' in result_obj:
                template_name = result_obj['TemplateName']
            if 'CounterValue' in result_obj:
                counter_value = result_obj['CounterValue']
        else:
            warnings.warn("result was expected to be Result() but is %s" % type(result))
    return (template_name, counter_value)

# ./end of file
