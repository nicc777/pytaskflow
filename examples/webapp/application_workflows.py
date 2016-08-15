from .application_tasks import sample_application_task_collection
from pytaskflow.taskflow_engine import EntryPoint, WorkFlow, Result
import warnings, types


def flask_sample_app_workflow(entry_point):
    template_name = 'base.html'
    counter_value = 0
    action = 'ServeTemplate'
    redirect_url = '/'
    if isinstance(entry_point, EntryPoint):
        app_workflow = WorkFlow("GetSessionFunction", sample_application_task_collection(), entry_point=entry_point)
        result = app_workflow.result
        if isinstance(result, Result):
            result_obj = result.result_obj
            if 'Action' in result_obj:
                if result_obj['Action'] == 'Redirect':
                    if 'RedirectURL' in result_obj:
                        redirect_url = result_obj['RedirectURL']
            if 'TemplateName' in result_obj:
                template_name = result_obj['TemplateName']
            if 'CounterValue' in result_obj:
                counter_value = result_obj['CounterValue']
        else:
            warnings.warn("result was expected to be Result() but is %s" % type(result))
    entry_point.log_handler.log(level='debug', message="type(entry_point.framework_response_obj)=%s" % type(entry_point.framework_response_obj))
    # if str(type(entry_point.framework_response_obj)) == "<class 'function'>":
    if isinstance(entry_point.framework_response_obj, types.FunctionType):
        entry_point.log_handler.log(level='debug', message="   function name: %s" % entry_point.framework_response_obj.__name__)
    response = entry_point.framework_response_obj(template_name, visits=counter_value)
    return response

# ./end of file
