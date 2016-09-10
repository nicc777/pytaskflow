ERR = 0
try:
    from flask import render_template, make_response, redirect
except:
    ERR = 1


def flask_actions(action='RenderTemplate', context=None, template_name='index.html', redirect_url='/', cookies=None):
    if ERR > 0:
        raise Exception("Flask could not be loaded...")
    if not isinstance(cookies, dict):
        cookies = None
    if action == 'RenderTemplate':
        if context is not None:
            response = make_response(render_template(template_name, context=context))
        else:
            response = make_response(render_template(template_name))
    else:
        response = make_response(redirect(redirect_url))
    if cookies is not None:
        for key, value in cookies.items():
            response.set_cookie(key, value)
    return response


# EOF