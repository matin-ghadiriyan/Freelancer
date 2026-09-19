from extentions import app
from rate_limit_function import rate_limit
from flask import abort



@app.before_request
def before_request():
    if not rate_limit():
        abort(429)

