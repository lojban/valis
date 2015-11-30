
from flask.ext.assets import Environment, Bundle

from ..context import app

assets = Environment(app)

def configure():
    _configure_css_assets()
    _configure_js_assets()

def _configure_js_assets():
    js = Bundle(Bundle('jquery.js',
                       'jquery-ui.js'),
                Bundle('underscore.js',
                       'backbone.js',
                       'backbone.marionette.js',
                       'handlebars-v3.0.3.js'),
                Bundle('URI.js'),
                Bundle('katex.js'),
                Bundle('valis-application.js',
                       'valis-utilities.js',
                       'valis-bangu.js',
                       'valis-tex.js',
                       'valis-templates.js',
                       'valis-models.js',
                       'valis-views.js',
                       'valis-dispatch.js',
                       'valis-router.js'),
                output='gen/scripts.js')
    assets.register('scripts', js)

def _configure_css_assets():
    css = Bundle('jquery-ui.css',
                 'katex.css',
                 'valis.css',
                 output='gen/styles.css')
    assets.register('styles', css)

