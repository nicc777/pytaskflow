from pytaskflow.taskflow_engine import *

ENTRY_POINT_TEMPLATE_MAP = {
    '/': 'index.html',
}

DEFAULT_TEMPLATE = 'index.html'


class ServeTemplateFunction(Function):
    def __init__(self):
        super(ServeTemplateFunction, self).__init__()

    def result(self, entry_point=EntryPoint(), previous_result=None):
        result_obj = {}
        template_name = DEFAULT_TEMPLATE
        if isinstance(previous_result, Result):
            if isinstance(previous_result.result_obj, dict):
                result_obj = previous_result.result_obj
        if entry_point.request_path in ENTRY_POINT_TEMPLATE_MAP:
            template_name = ENTRY_POINT_TEMPLATE_MAP[entry_point.request_path]
        result_obj['Proceed'] = False
        result_obj['TemplateName'] = template_name
        result_obj['Action'] = 'ServeTemplate'
        result = Result(result_obj)
        return result


# ./end of file