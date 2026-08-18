from functools import wraps
import os
from flask import render_template,session
AMK=os.environ.get("AMK")
def md_check(func):
    @wraps(func)
    def wrapper(mode:str="", *args, **kwargs):
        #First mode needs to be checked
        if mode and not getattr(mode, AMK):
            return render_template("receipt.html")
        if not session.get("user_id"):
            return render_template("receipt.html")
        if session.get("role") != "auditor":
            return render_template("receipt.html")
        return func(mode, *args, **kwargs)
    return wrapper


