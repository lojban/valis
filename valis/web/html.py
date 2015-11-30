
from flask import render_template, redirect, url_for, request

from ..context import app

def configure():

    @app.route('/', methods=['GET'])
    def root():
        return redirect(url_for("home", **request.args))

    @app.route('/ui', defaults={'path': ''}, methods=['GET'])
    @app.route('/ui/<path:path>', methods=['GET'])
    def home(path):
        return render_template('app.html')

