import click
import os
from os.path import join, dirname
from flask import Flask, render_template
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from dotenv import load_dotenv, find_dotenv
from flask_wtf import Form
from flask_pagedown import PageDown
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
from flask_analytics import Analytics


# Tell our app where to get its environment variables from
dotenv_path = join(dirname(__file__), '.env')
try:
    load_dotenv(dotenv_path)
except IOError:
    find_dotenv()

# Declare a few necessary environment variables
DEBUG = os.environ.get('DEBUG')
ADDRESS = os.environ.get('ADDRESS')
PORT = os.environ.get('PORT')
FLATPAGES_AUTO_RELOAD = os.environ.get('FLATPAGES_AUTO_RELOAD')
FLATPAGES_EXTENSION = os.environ.get('FLATPAGES_EXTENSION')
FLATPAGES_ROOT = os.environ.get('FLATPAGES_ROOT')
POST_DIR = os.environ.get('POST_DIR')

if FLATPAGES_AUTO_RELOAD or FLATPAGES_EXTENSION or FLATPAGES_ROOT or POST_DIR is None:
    raise Exception('A Flatpages environment variable was not set!')

app = Flask(__name__)
flatpages = FlatPages(app)
freezer = Freezer(app)
pagedown = PageDown(app)
app.secret_key = os.environ.get('APP_KEY')
app.config.from_object(__name__)

# Simple check for Google Analytics
if os.environ.get('USE_ANALYTICS') is not None and not False:
    Analytics(app)
    app.config['ANALYTICS']['GOOGLE_CLASSIC_ANALYTICS']['ENABLED'] = True
    if os.environ.get('GOOGLE_ANALYTICS_ACCOUNT') is None:
        print "Google Analytics enabled but account not set, no data will be sent to Google."
    else:
        app.config['ANALYTICS']['GOOGLE_CLASSIC_ANALYTICS']['ACCOUNT'] = os.environ.get('GOOGLE_ANALYTICS_ACCOUNT')


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/projects')
def projects():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('index.html')


@app.route('/posts/')
def post_history():
    my_post = [p for p in flatpages if p.path.startswith(POST_DIR)]
    my_post.sort(key=lambda item: item['date'], reverse=False)
    return render_template('posts.html', posts=my_post)


@app.route('/posts/<name>/')
def post(name):
    path = '{}/{}'.format(POST_DIR, name)
    post = flatpages.get_or_404(path)
    return render_template('post.html', post=post)


@click.command()
@click.option('--build', '/-b', help='Compile markdown into static pages')
def main(build):
    if os.environ.get('ADDRESS') and os.environ.get('PORT') is not None:
        host = '{}:{}'.format(ADDRESS, PORT)
    elif os.environ.get('ADDRESS') is None:
        print "ADDRESS Environment Variable not set, defaulting to localhost."
        host = '127.0.0.1:{}'.format(PORT)
    elif os.environ.get('PORT') is None:
        print "PORT Environment Variable not set, defaulting to 5000."
    else:
        print "ADDRESS and PORT Environment Variables not set, defaulting to localhost:5000."
        host = '127.0.0.1:5000'

    if build:
        freezer.freeze()
        print "Static pages built!"
    else:
        app.run(host=host, debug=DEBUG)

if __name__ == '__main__':
    main()
