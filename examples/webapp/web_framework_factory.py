"""
Here is where web framework specific stuff happens
"""
import warnings
import inspect
from pytaskflow.taskflow_engine import EntryPoint, LoggingHandler


def flask_entry_point_creator(request_obj, response_obj, other_objs={}):
    try:
        _flask = __import__('flask', globals(), locals(), ['request'], 0)
        if not (inspect.ismodule(_flask) and _flask.__name__ == 'flask'):
            warnings.warn("It doesn't appear that flask is installed, so this function will not be able to construct an EntryPoint")
        else:
            entry_point = EntryPoint(
                request_path=request_obj.path,
                request_method=request_obj.method,
                query_string=request_obj.args,
                post_data=request_obj.form,
                cookies=request_obj.cookies,
                default_template='home',
                log_handler=LoggingHandler(),
                framework_request_obj=request_obj,
                framework_response_obj=response_obj,
                additional_framework_objects=other_objs
            )
            return entry_point
    except:
        warnings.warn("It appears flask is not installed. Your app will now probably break...")
    return EntryPoint()


# ./end of file
