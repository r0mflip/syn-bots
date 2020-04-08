import os
from flask import Flask, render_template

from model.prediction import do_prediction

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'for_cookies')


@app.route('/')
def home():
    return render_template('main.html')


@app.route('/predict/<hndle>')
def get_prediction(hndle):
    return do_prediction(hndle)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
