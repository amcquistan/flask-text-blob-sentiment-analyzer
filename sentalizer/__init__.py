# __init__.py

import os

from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for, request, redirect, flash
from textblob import TextBlob

import requests

class PageSentiment:
    def __init__(self, url, header, blob):
        self.url = url
        self.header = header

        self.overall = blob.sentiment 

        self.most_polar_sentence = blob.sentences[0]
        self.least_polar_sentence = blob.sentences[0]
        self.most_objective_sentence = blob.sentences[0]
        self.most_subjective_sentence = blob.sentences[0]

        for sentence in blob.sentences[1:]:
            if self.most_polar_sentence.sentiment.polarity < sentence.sentiment.polarity:
                self.most_polar_sentence = sentence

            if self.least_polar_sentence.sentiment.polarity > sentence.sentiment.polarity:
                self.least_polar_sentence = sentence

            if self.most_objective_sentence.sentiment.subjectivity > sentence.sentiment.subjectivity:
                self.most_objective_sentence = sentence

            if self.most_subjective_sentence.sentiment.subjectivity < sentence.sentiment.subjectivity:
                self.most_subjective_sentence = sentence


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.update(SECRET_KEY='flaskisawesome')

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
            response = requests.get(url)

            if response.status_code != 200:
                raise RuntimeError()

        except:
            # Give error message that this was an invalid url
            flash('Invalid url. Please fix and resubmit.')
            return redirect(url_for('index'))

        # parse results using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        if soup.find('h1'):
            header = soup.find('h1').get_text()
        else:
            header = soup.title.get_text()

        # create TextBlob instance
        blob = TextBlob(soup.get_text())

        # process TextBlob text analytics results
        page_results = PageSentiment(url, header, blob)

        return render_template('results.html', page_results=page_results)

    return app

