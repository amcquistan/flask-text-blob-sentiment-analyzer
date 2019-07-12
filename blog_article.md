# Text Analytics with Flask, TextBlob, BeautifulSoup, and Requests: Dev to Deploy

### Introduction

This article introduces how to use build a Python based web application using the FLask web framework for performing text analytics on internet resources like blog pages utilizing Requests, BeautifulSoup, and TextBlob. I demonstrate how to setup the local development project environment, build the app using these technologies in this local development environment and, how to deploy to a Linux Virtual Private Server (VPS).

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

TextBlob is a wrapper around the [Natural Language Toolkit (NLTK)](http://www.nltk.org/) library with the purpose of abstracting its complexities and, thus, the user must install the NLTK corpora files which it uses to guide the evaulation text data. This installs the corpus data files in a directory named nltk_data in the current user's home directory.

```
python -m textblob.download_corpora
```

### Building Flask Sentalizer App

With the necessary Python libraries and supporting data installed I begin building the application starting with creating a application package named sentalizer then open it in my favorite text editor / IDE Visual Studio Code.

```
(venv) mkdir sentalizer
```

I add a __init__.py module turning the directory into a package. In the __init__.py module I create an application factory method for making an instance of the Flask application as shown in offical [Flask docs](https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/).

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

Pointing my browser of choice to http://127.0.0.1:5000/ shows the following.

*** howdy.png ***

Obviously that isn't too exciting so lets move on. Next I add a couple of new directories inside the sentializer package. One dirctory is named templates and is for the Jinja HTML templates. The other directory is named static and contains a CSS framework named [Bulma](https://bulma.io/) to take away that blah plain HTML look. Below is the tree ouput so you see what I'm working with.

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
 
I will start by building out the base.html template which serves as a master layout for the other two pages. This base.html template sources the bulma css, creates a navbar with a logo item link that redirects to the index route and defines a main content Jinja block.

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
  
  {% block main %}{% endblock %}

</body>
</html>
```

Note the use of url_for(...) template filter which is automatically injected into the context of each Jinja template. Here I am using it to reference the bulma css file. Another noteworthy item is the definition of the main content block 

```
{% block main %}{% endblock %}
```

which will serve as the point where the other two templates will inject their content into this base.html template.

Next I scaffold out the index.html template starting by extending the base.html template which I accomplish with the extends template context helper followed by the name of the base.html file in quotes. Then I provide an implementation for the main block which, right now, just contains a bulma hero section and a comment for where I will later add a form along with an input field for collecting webpage urls along with a submit button.

```
<!-- index.html -->
{% extends 'base.html' %}

{% block main %}
<section class="hero is-light is-fullheight-with-navbar">
  <div class="hero-head">
    <div class="container">
        <p class="title has-text-centered">
          Enter a webpage url for Sentiment Analysis
        </p>
    </div>
  </div>
  <div class="hero-body">
    <div class="container">

      <!-- place form code here for submitting the url -->


    </div>
  </div>
</section>
{% endblock %}
```
I do something similar for the results.html template which will eventually show a series of tiles which each one containing a calculated sentiment value for the text analytics output of the submitted url's page.

```
<!-- results.html -->
{% extends 'base.html' %}

{% block main %}
<section class="hero is-light is-fullheight-with-navbar">
  <div class="hero-head">
    <div class="container">
      <p class="title has-text-centered">
        Sentiment Result
      </p>
    </div>
  </div>
  <div class="hero-body">
    <div class="container">

      <!-- place sentiment result tiles below -->


    </div>
  </div>
</section>
{% endblock %}
```

Thats a good start on the templates. Next I move on to getting the Flask application to serve up the index.html and results.html templates. Back over in the __init__.py module I add a couple of common imports from the Flask package I'll be working with in. The import I want to focus on right now is the render_template function. I use this to load the index.html template which gets processed and returned as html then returned to be served by the Flask app when the / url is requested. Below is the updated __init__.py module.


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

    return app
```

Upon saving the __init__.py module the Flask dev server should reload itself if the dev server is still running, otherwise start it again, so I can reload the browser pointing to http://127.0.0.1:5000/ and see the following.

*** index-scaffolding.png ***

At this point I need to make a new route and view function for serving up the results.html template.  To do this I define a new function named results(...) and decorate it with the @app.route('/results') decorator and similarly have it return the template using render_template function.  However, there is one change to be made to the route(...) decorator which includes specifying that it should only accept the POST request method as shown below.

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

As you can see from the above newly introduced results() view function it expects to get a form field named url which can be retrieved by the form dict field on the global request object I imported from the flask package previously. I have also added some comments that describe the program flow that is to take place in the new view function to perform the text analytics. I have also introduced a new argument to the render_template function which is a keyword arg named page_results that for the moment is just an empty dictionary.

Now that I have a /results route to POST a url to I can add a form to the index.html. Notice in the below form element I've again used url_for(...) method but this time I've supplied a argument of 'results' which is the name of the view_function I want the url for POSTing the form to.

```
<!-- index.html -->
{% extends 'base.html' %}

{% block main %}
<section class="hero is-light is-fullheight-with-navbar">
  <div class="hero-head">
    <div class="container">
        <p class="title has-text-centered">
          Enter a webpage url for Sentiment Analysis
        </p>
    </div>
  </div>
  <div class="hero-body">
    <div class="container">

      <!-- place form code here for submitting the url -->
      <div class="columns">
        <div class="column is-offset-2 is-8">
          <form action="{{ url_for('results') }}" method="POST">
            <div class="field has-addons">
              <div class="control is-expanded">
                <input type="text" name="url" class="input" placeholder="Enter url of page to perform sentiment analysis on">
              </div>
              <div class="control">
                <button class="button is-primary">Submit</button>
              </div>
            </div>
          </form>
        </div>
      </div>

    </div>
  </div>
</section>
{% endblock %}
```

*** index-with-form.png ***

The app is now capable of accepting a url representing a page to perform sentiment analysis on so, I better get going on implementing the text analytics functionality. As already alluded to in the results(...) view function comment I first need to fetch the page using the POSTed url which I can do by importing the requests library and calling it's requests.get(...) method passing it the url.  This is a HTTP request being made with unvalidated posted url string that may or may not point to a real web resource so, an exception being raised is a real posibility. In the event of an exception being raised an error message is shown to the user. (set up message flashing for this).



### Deploying to Virtual Private Server (VPS)



### Resources for Further Learning 



### Conclusion