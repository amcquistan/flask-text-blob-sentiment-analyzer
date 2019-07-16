# Building a Text Analytics App in Python with Flask, Requests, BeautifulSoup, and TextBlob

### Introduction

This article introduces how to build a Python and Flask based web application for performing text analytics on internet resources such as blog pages. To perform text analytics I will utilizing Requests for fetching web pages, BeautifulSoup for parsing html and extracting the viewable text and, apply the TextBlob package to calculate a few sentiment scores.

### Basic Usage of TextBlob

[TextBlob](https://textblob.readthedocs.io/en/dev/index.html) is a wrapper around the [Natural Language Toolkit (NLTK)](http://www.nltk.org/) library with the purpose of abstracting its complexities.

Using TextBlob is as simple as instantiating the TextBlob main class while passing it the text data you would like to analyze. 

```
(venv) $ python
Python 3.6.5 (default, Apr 25 2018, 14:23:58) 
[GCC 4.2.1 Compatible Apple LLVM 9.1.0 (clang-902.0.39.1)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from textblob import TextBlob
>>> blob = TextBlob(''''I really enjoy programming in Python. It is a very approachable
... language with a plethora of valuable, high quality, libraries in
... both the standard library and as third party package from the
... community''')
```

The base TextBlob object has a namedtuple field called sentiment which itself has two fields, polarity and subjectivity. Both fields are numeric measures of sentiment with polarity falling between -1 indicating linguistically negative speech up to +1 being interpretted as positive speech with neurality at zero. The subjectivity field ranges between 0 representing objective semantics up to 1 being thought of subjective or opinionated.  The sentalizer demo app will report these values for the overal sentiment of the page.

For the example above here is the overall sentiment.

```
>>> blob.sentiment
Sentiment(polarity=0.15200000000000002, subjectivity=0.26799999999999996)
```

TextBlob also breaks down the sentiment to finer levels of granularity like sentences and even individual words. In fact, the TextBlob class has a list field named sentences containing a collection of Sentence objects. Sentence objects are quite similar to the TextBlob class itself only representing sentences instead of the entire document. Like TextBlob, Sentence objects have a sentiment namedtuple field along with a collection of Word objects named words. The sentalizer app will evaluate the collection of Sentence objects to find the most and least polar as well the most objective and most subjective sentences.

Here are the sentiment values for the prior example.

```
>>> for sentence in blob.sentences:
...     print(sentence)
...     print(sentence.sentiment)
...     print()
... 
'I really enjoy programming in Python.
Sentiment(polarity=0.4, subjectivity=0.5)

It is a very approachable
language with a plethora of valuable, high quality, libraries in
both the standard library and as third party package from the
community
Sentiment(polarity=0.09, subjectivity=0.20999999999999996)
```

There is a whole lot more functionality packed into the TextBlob package which I encourage the reader to discover in the excellent TextBlob documentation and further experiment with but, I will only be demonstrating usage of sentiment at the document and sentence level. 

### Local Dev Setup

First off I create a Python 3 virtual environment, activate it, then install the required libraries.

##### Virtual Environment

```
mkdir flask-text-blob-sentiment-analyzer
python3 -m venv venv
```

##### Activate Virtual Environemnt (Windows)

```
venv\Scripts\activate.bat
```

##### Activate Virtual Environment (Mac / Linux)

```
source venv/bin/activate
```

##### Install Python Packages

```
(venv) pip install Flask textblob beautifulsoup4 requests
```

##### Fetch the Text Blob (NLTK) Corpora Files

The NLTK corpora files are used to guide the evaulation of text data. This installs the corpus data files in a directory named nltk_data in the user's home directory.

```
python -m textblob.download_corpora
```

### Building the Flask Sentalizer App

With the necessary Python libraries and supporting data file installed I begin building the application starting with creating an application package named sentalizer then open it in my favorite text editor / IDE, Visual Studio Code.

```
(venv) mkdir sentalizer
```

I add a __init__.py module turning the directory into a package. In the __init__.py module I create an application factory function for making an instance of the Flask application as shown in the offical [Flask documentation](https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/).

```
# __init__.py

import os

from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    try:
        os.makedirs(app.instance_path)
    except OSError as e:
        print(e)

    @app.route('/')
    def index():
        return "Howdy"
    
    return app
```

First things first I want to test the setup by running the flask dev server and making sure I can reach it from the browser before getting too much further down the road.

##### Running the Dev Server (Windows)

```
(venv) export FLASK_APP=sentalizer
(venv) export FLASK_ENV=development
(venv) flask run
 * Serving Flask app "sentalizer" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 325-549-505
```

##### Running the Dev Server (Mac / Linux)

```
(venv) set FLASK_APP=flaskr
(venv) set FLASK_ENV=development
(venv) flask run
 * Serving Flask app "sentalizer" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 325-549-505
```

Pointing my browser to http://127.0.0.1:5000/ shows the following.

*** howdy.png ***

Obviously that isn't too exciting so I will move on. Next I add a couple of new directories inside the sentializer package. One dirctory is named templates and is for the Jinja HTML templates. The other directory is named static and contains a CSS framework named [Bulma](https://bulma.io/) to take away that blah plain HTML look. Below is the tree ouput so you see what I'm working with.

```
(venv)  tree .
.
├── __init__.py
├── __pycache__
│   └── __init__.cpython-36.pyc
├── static
│   └── bulma-0.7.5
│       ├── CHANGELOG.md
│       ├── LICENSE
│       ├── README.md
│       ├── bulma.sass
│       ├── css
│       │   ├── bulma.css
│       │   ├── bulma.css.map
│       │   └── bulma.min.css
│        ... omitting bulma source for brevity
└── templates
    ├── base.html
    ├── index.html
    └── results.html
```
 
I start by building out the base.html template which is a master layout for the other two pages. This base.html template sources the bulma css and creates a navbar with a logo link that directs to the index route. Additionally, there are two Jinja code block sections defined by using the {% block %} syntax. These blocks are for injecting heading and main content into by the index.html and results.html templates that will extend base.html. 

```
<!-- base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Sentializer</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='bulma-0.7.5/css/bulma.min.css') }}">
</head>
<body>
  <nav class="navbar is-light" role="navigation" aria-label="main navigation">
    <div class="container">
        <div class="navbar-brand">
          <a href="/" class="navbar-item">Sentalizer</a>
        </div>
    </div>
  </nav>
  
  <section class="hero is-light is-fullheight-with-navbar">
    <div class="hero-head">
      <div class="container">
          {% block heading %}{% endblock %}
        
        <!-- user message can go in the section -->
        
      </div>
    </div>

    <div class="hero-body">
      <div class="container">
    
        {% block main %}{% endblock %}
    
      </div>
    </div>

  </section>

</body>
</html>
```

Note the use of the url_for(...) template filter for building references URI paths of resources for the templates. This template filter function is availble to the context of all templates. Here I am using it to reference the bulma css file. Another noteworthy piece is what surrounds the url_for function, the 

```
{{ }} 
```

interpolation curly brackets are used to evaluate Python code and output its content in their place.  There is another type of interpolation construct that uses curly brackets,

```
{% %}
```

which are used with program control language elements.


Next I scaffold out the index.html template starting by extending the base.html template accomplished with the extends template context helper followed by the name of the base.html file in quotes. Then I provide an implementation for the heading and main blocks. Right now the heading contains a paragraph element and the main block contains a placeholder comment where I will later add a form along with an input field for collecting webpage urls along with a submit button.

```
<!-- index.html -->
{% extends 'base.html' %}

{% block heading %}
<p class="title has-text-centered">
  Enter a webpage url for Sentiment Analysis
</p>
{% endblock %}

{% block main %}

  <!-- place form code here for submitting the url -->

{% endblock %}

```
I do something similar for the results.html template which will eventually show a series of tiles, each one containing a calculated sentiment value for the text analytics output of the submitted url's page.

```
<!-- results.html -->
{% extends 'base.html' %}

{% block heading %}
<p class="title has-text-centered">
  Sentiment Result
</p>
{% endblock %}

{% block main %}

  <!-- place sentiment result tiles below -->
  
{% endblock %}
```

Thats a good start on the templates so, I'll move on to getting the Flask application to serve up the index.html and results.html template. Back over in the __init__.py module I add a few common imports from the Flask package I'll be working with. The import I want to focus on right now is the render_template function. I use this to load the index.html template which gets processed and returned as html. All of this is then returned to be served by the Flask app when the / url is requested. Below is the updated __init__.py module.


```
# __init__.py

import os

from flask import Flask, render_template, url_for, request, redirect, flash

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
```

Upon saving the __init__.py module the Flask dev server should reload itself if the dev server is still running, otherwise it needs started again. Reloading the browser pointing to http://127.0.0.1:5000/ now shows the following.

*** index-scaffolding.png ***

At this point I can make a new route and view function for serving up the results.html template.  To do this I define a new function named results(...) below the @app.route('/results') decorator and, similarly use render_template to return the results.html template.  However, there is one change needed within the decorator to direct it to only accept the POST request method as shown below.

```
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
            pass
            
        except:
            # Give error message that this was an invalid url
            pass

        # parse results using BeautifulSoup

        # create TextBlob instance

        # process TextBlob text analytics results

        return render_template('results.html', page_results={})

        return render_template('results.html', page_results={})

    return app
```

The newly introduced results() view function expects a form field named url which can be retrieved by the form dict field on the global request object I imported from the flask package previously. I have also added comments to describe the program flow necessary to perform the text analytics followed by the use of the render_template function again but, a new keyword argument named page_results is used which, for the moment, is just an empty dictionary.

Now that I have a /results route to POST a url to I can add a form to index.html. Notice in the below form element I've again used url_for(...) method but this time I've supplied an argument of 'results' which is the name of the view_function for the route I want to POST the form data to.

```
<!-- index.html -->
{% extends 'base.html' %}

{% block heading %}
<p class="title has-text-centered">
  Enter a webpage url for Sentiment Analysis
</p>
{% endblock %}

{% block main %}

  <!-- place form code here for submitting the url -->
  <div class="columns">
    <div class="column is-offset-2 is-8">
      <form action="{{ url_for('results') }}" method="POST">
        <div class="field has-addons">
          <div class="control is-expanded">
            <input type="text" name="url" class="input" placeholder="http://example.com">
          </div>
          <div class="control">
            <button class="button is-primary">Submit</button>
          </div>
        </div>
      </form>
    </div>
  </div>

{% endblock %}
```

*** index-with-form.png ***

The app is capable of accepting a url representing a page to perform sentiment analysis on so, I can now implement the text analytics functionality. As already alluded to in the results(...) view function comments, the page first needs fetched using the POSTed url. To accomplish this I import the requests library and call the requests.get(...) method with the url.  This is a HTTP request being made with an unvalidated url that may or may not point to a real web resource so, an exception being raised is a real posibility. If an exception is raised an error message will be shown to the user. 

To show error messages I will use Flask's message flashing functionality via the flash method that was imported from Flask package earlier. Additionally, I need to give the application a secret key because message flashing utilizes the session which requires a secret key to be set in the app instance's config dict as shown below.

```
app = Flask(__name__, instance_relative_config=True)
    
app.config.update(SECRET_KEY='flaskisawesome')
```

Now if an exception is raised due to a web page not being successfully returned the flash(...) method is called and the user is redirected to the index.html page.

```
try:
    # fetch page associated with url using requests
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError()

except:
    # Give error message that this was an invalid url
    flash('Invalid url. Please fix and resubmit.')
    return redirect(url_for('index'))
```

Some work is still neeeded to see the flashed message in the UI. Over in the base.html, below the comment for messages, I add a {% with ... %} template block for invoking the get_flashed_messages template function (available to all templates) and assign the returned collection to a messages variable. The messages are then iterated over for displaying. 


```
<!-- base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Sentializer</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='bulma-0.7.5/css/bulma.min.css') }}">
</head>
<body>
  <nav class="navbar is-light" role="navigation" aria-label="main navigation">
    <div class="container">
        <div class="navbar-brand">
          <a href="/" class="navbar-item">Sentalizer</a>
        </div>
    </div>
  </nav>
  
  <section class="hero is-light is-fullheight-with-navbar">
    <div class="hero-head">
      <div class="container has-text-centered">
          {% block heading %}{% endblock %}
        
        <!-- user message can go in the section -->
        {% with messages = get_flashed_messages() %}
          {% if messages %}
          <article class="message is-centered" style="width: 500px; margin: auto;">
            <div class="message-body">
              {% for msg in messages %}
                <p>{{ msg }}</p>
              {% endfor %}
            </div>
          </article>
          {% endif %}
        {% endwith %}

      </div>
    </div>

    <div class="hero-body">
      <div class="container">
    
        {% block main %}{% endblock %}
    
      </div>
    </div>

  </section>

</body>
</html>

```

*** index-with-error.png ***

Next up is to import the BeautifulSoup class from the bs4 package as well as the TextBlob class from from the textblob package. Assuming a webpage is sucessfully fetched and program control passes through the try / except section the returned content is parsed into a queryable Document Object Model (DOM) representation in a BeautifulSoup object and assigned to a soup variable. The h1 element, or the page title if an h1 is not present, is extracted from the soup variable before passing all viewable text to TextBlob during it's instantiation then assigned to a variable named blob.

```
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
```

With all the necessary data collected I can now query the fields of the TextBlob object to display the overall sentiment of the page as well the extremes of the various sentences the page contains. To do this I will create a custom Python type, or class, named PageSentiment that will maintain information on a page's url, heading, overall sentiment along with the sentences having the most extreme sentiment scores. I place the PageSentiment class above the create_app function as shown below.

```
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

```

What remains now is to display the sentiment information of the submitted url's page in the results.html template. To do this I group each piece of information in the PageSentiment class object, page_results, passed to the results.html template via the render_template page in a bulma tile component as shown below. 

```
<!-- results.html -->
{% extends 'base.html' %}

{% block heading %}
<p class="title has-text-centered">
  Sentiment Result
</p>
{% endblock %}

{% block main %}

  <!-- place sentiment result tiles below -->
  
  <div class="box">
    <p class="title has-text-centered">
      <a target="_BLANK" href="{{ page_results.url }}">
        {{ page_results.header }}
      </a>
    </p>
  </div>

  <div class="tile is-ancestor">
    <div class="tile is-parent is-6">
      <div class="tile is-child box">
        <p class="title has-text-centered">
          Overall Polarity: {{ page_results.overall.polarity|round(2) }}
        </p>
      </div>
    </div>
    <div class="tile is-parent is-6">
      <div class="tile is-child box">
        <p class="title has-text-centered">
          Overall Subjectivity: {{ page_results.overall.subjectivity|round(2) }}
        </p>
      </div>
    </div>
  </div>

  <div class="tile is-ancestor">
    <div class="tile is-parent is-6">
      <div class="tile is-child box">
        <p class="title has-text-centered">
          Most Polar Sentence: {{ page_results.most_polar_sentence.sentiment.polarity|round(2) }}
        </p>
        <p class='has-text-centered'>{{ page_results.most_polar_sentence }}</p>
      </div>
    </div>
    <div class="tile is-parent is-6">
      <div class="tile is-child box">
        <p class="title has-text-centered">
          Least Polar Sentence: {{ page_results.least_polar_sentence.sentiment.polarity|round(2) }}
        </p>
        <p class='has-text-centered'>{{ page_results.least_polar_sentence }}</p>
      </div>
    </div>
  </div>

  <div class="tile is-ancestor">
    <div class="tile is-parent is-6">
      <div class="tile is-child box">
        <p class="title has-text-centered">
          Most Objective Sentence: {{ page_results.most_objective_sentence.sentiment.subjectivity|round(2) }}
        </p>
        <p class='has-text-centered'>{{ page_results.most_objective_sentence }}</p>
      </div>
    </div>
    <div class="tile is-parent is-6">
      <div class="tile is-child box">
        <p class="title has-text-centered">
          Most Subjective Sentence: {{ page_results.most_subjective_sentence.sentiment.subjectivity|round(2) }}
        </p>
        <p class='has-text-centered'>{{ page_results.most_subjective_sentence }}</p>
      </div>
    </div>
  </div>

{% endblock %}
```

Below is the output from running the very first blog post on thecodinginterface.com titled [Django Authentication Part 1: Sign Up, Login, Logout](https://thecodinginterface.com/blog/django-auth-part1/)

*** sentiment-results.png ***

### Resources for Further Learning 



### Conclusion

In this article I have demonstrated how to build a simple Python based web application in Flask that fetches web pages and performs text analytics on it using the Requests, BeautifulSoup, and TextBlob packages. I appreciate you following along and hope you round this this both useful and insteresting. In follow up articles I will be showing how to integrate Redis and Celery to implement background asynchronous tasks to fetch and analyze the pages as well as how to deploy this application to a Virtual Private Server in the cloud.