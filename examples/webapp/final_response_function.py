from pytaskflow.taskflow_engine import *


class FinalResponseFunction(Function):
    def __init__(self):
        super(FinalResponseFunction, self).__init__()

    def result(self, entry_point=EntryPoint(), previous_result=None):
        return_result = {
            'ReturnResult': "Default TEXT response... Something may have gone wrong...",
        }
        if isinstance(previous_result, Result):
            cookies = {}
            redirect_url = '/'
            template_name = 'base.html'
            action = 'ServeTemplate'
            context = None
            if 'Action' in previous_result.result_obj:
                if previous_result.result_obj['Action'] == 'Redirect':
                    if 'RedirectURL' in previous_result.result_obj:
                        redirect_url = previous_result.result_obj['RedirectURL']
            if 'TemplateName' in previous_result.result_obj:
                template_name = previous_result.result_obj['TemplateName']
                action = 'ServeTemplate'
            if 'Cookies' in previous_result.result_obj:
                if isinstance(previous_result.result_obj['Cookies'], dict):
                    cookies = previous_result.result_obj['Cookies']
            if 'Context' in previous_result.result_obj:
                context = previous_result.result_obj['Context']
        else:
            warnings.warn("result was expected to be Result() but is %s" % type(result))
        return return_result