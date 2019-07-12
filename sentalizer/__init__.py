# __init__.py

import os

from flask import Flask, render_template, url_for, request, redirect

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')


    @app.route('/results', methods=('POST',))
    def results():
        url = request.form.get('url')

        try:
            # fetch page associated with url using requests

            
        except:
            # Give error message that this was an invalid url
            pass

        # parse results using BeautifulSoup

        # create TextBlob instance

        # process TextBlob text analytics results

        return render_template('results.html', page_results={})

    return app

