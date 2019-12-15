from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

from Helper import Genetator as Gen
from Helper import Validator as Val
from ssqlite import ssqlite

app = Flask(__name__)
app.debug = True
app.secret_key = "12345"  # use a better secret_key


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/articles')
def all_articles():
    return render_template('all_articles.html')


@app.route('/article/<string:id>/')
def article(id):
    return render_template('/article.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/email_token')
def email_token():
    return render_template('email_token_field.html')


@app.route('/password_token')
def password_token():
    return render_template('password_token_field.html')


@app.route('/forget_password')
def forget_password():
    return render_template('forget_password.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/update_article')
def update_article():
    return render_template('update_article.html')


@app.route('/update_comment')
def update_comment():
    return render_template('update_comment.html')


@app.route('/user_profile')
def user_profile():
    return render_template('user_profile.html')


@app.route('/write_article')
def write_article():
    return render_template('write_article.html')


if __name__ == "__main__":
    app.run()
