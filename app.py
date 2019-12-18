from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

from Helper import Geretator as Gen
from Helper import Validator as Val
from ssqlite import ssqlite

app = Flask(__name__)
app.debug = True
app.secret_key = "12345"  # use a better secret_key

# database name
DATABASE_NAME = "pill_code_db.db"


# index/home page
@app.route('/')
@app.route('/index')
def index():
    db_conn = ssqlite(DATABASE_NAME)
    articles = db_conn.run_query(
        "SELECT * FROM `articles` ORDER BY `post_date` DESC").fetchall()

    if articles != None:
        return render_template("index.html", articles=articles)

    return render_template("index.html")


# static pages
@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template('contact.html')


# account settings
@app.route('/email_token')
def email_token():
    return render_template('email_token_field.html')


@app.route('/user_profile')
def user_profile():
    return render_template('user_profile.html')


@app.route('/password_token')
def password_token():
    return render_template('password_token_field.html')


@app.route('/forget_password')
def forget_password():
    return render_template('forget_password.html')


@app.route('/delete_user')
def delete_user():
    pass


# comments
@app.route('/update_comment')
def update_comment():
    return render_template('update_comment.html')


@app.route('/comment/delete/<string:id>')
def delete_comment(id):
    pass


@app.route('/comment/update/<string:id>')
def update_comment(id):
    pass


# signup, login and logout
@app.route('/signup/', methods=['GET', 'POST'])
@app.route('/signup/<string:email>', methods=['GET', 'POST'])
def signup(email=''):
    message = ''
    cat_filter = "danger"

    if not request.form:
        message = "There is no request form"

    else:
        if request.method != 'POST':
            message = 'Request method is not POST'

        else:
            if (
                    not request.form.get('sign_up_first_name') or
                    not request.form.get('sign_up_last_name') or
                    not request.form.get('sign_up_email') or
                    not request.form.get('sign_up_password') or
                    not request.form.get('sign_up_confirm_password') or
                    not request.form.get('sign_up_user_bio') or
                    not request.form.get('register_button')):

                message = 'There are empty fields, please fill them out'

            else:
                first_name = request.form.get('sign_up_first_name')
                last_name = request.form.get('sign_up_last_name')
                bio = request.form.get('sign_up_user_bio')

                email = request.form.get('sign_up_email')

                if Val().is_email_valid(email):
                    sign_up_password = request.form.get('sign_up_password')
                    confirm_password = request.form.get(
                        'sign_up_confirm_password')

                    if not Val().is_valid_password(sign_up_password) or not Val().is_valid_password(confirm_password):
                        message = "Invalid password format"

                    else:
                        if not Val().validate_size(sign_up_password):
                            message = "Check password length, 6 - 20"

                        else:
                            hashed_passwd = Gen().get_bcrypt_hashed_passwd(sign_up_password)
                            registered_date = Gen().get_current_date_time()

                            connection = ssqlite(DATABASE_NAME)
                            sql_query = "INSERT INTO `users`(`user_first_name`, `user_last_name`, `user_email`, `user_password`, `user_bio`, `user_register_date`) VALUES(?, ?, ?, ?, ?, ?)"

                            result = connection.run_query(
                                sql_query, first_name, last_name, email, hashed_passwd, bio, registered_date)

                            if not result:
                                message = "Error"

                            else:

                                # create a session
                                session["token"] = Gen().generate_token()
                                session["email"] = email

                                # success
                                message = "signup successfull"
                                cat_filter = "success"

                                # redirect to index page
                                return redirect(url_for('index'))

                            # stamp the database - commit the changes and close connection
                            connection.stamp()

                else:
                    message = "Invalide email format"

    flash(message, cat_filter)

    return render_template('signup.html', email=email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    cat_filter = 'danger'

    if request.form and request.method != 'POST':
        message = 'Request method is not POST'

    else:
        if (
                not request.form.get('login_email') or
                not request.form.get('login_password') or
                not request.form.get('login_button')):

            message = 'There are empty fields, please fill them out'

        else:
            email = request.form.get('login_email')

            if Val().is_email_valid(email):
                password = request.form.get('login_password')

                if not Val().is_valid_password(password):
                    message = "Invalid password format"

                else:
                    if not Val().validate_size(password):
                        message = "Check password length, 6 - 20"

                    else:
                        hashed_password = Gen().get_bcrypt_hashed_passwd(password)

                        connection = ssqlite(DATABASE_NAME)
                        sql_query = "SELECT `user_password` FROM `users` WHERE `user_email`=?"

                        user_password = connection.run_query(
                            sql_query, email).fetchone()

                        if user_password != None:
                            if user_password[0] != hashed_password:
                                message = "Invalid credentials..."

                            else:
                                # create a session
                                session["token"] = Gen().generate_token()
                                session["email"] = email

                                # success
                                message = "login successfull"
                                cat_filter = "success"

                                # redirect to index page
                                return redirect(url_for('index'))
                        else:
                            # redirect user to sign up page with the email
                            # message = "Kindly login, strange credentials..."
                            return redirect(url_for('signup', email=email))

                        # stamp the database - commit the changes and close connection
                        connection.stamp()

            else:
                message = "Invalide email format"

    flash(message, cat_filter)
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    flash("Logout successfull", "success")
    return redirect(url_for("login"))


# articles
@app.route('/article')
@app.route('/articles')
def all_articles():

    articles = ''

    connection = ssqlite(DATABASE_NAME)

    sql_query = "SELECT `post_id`, `post_title`, `user_email`,`post_date` FROM `articles` ORDER BY `post_id` DESC"

    result = connection.run_query(sql_query)

    if result:
        articles = result.fetchall()

    connection.stamp()

    return render_template('all_articles.html', articles=articles)


@app.route('/article/read/<string:id>/')
def read_article(id):
    article = []
    comments = []

    post_id = id

    db_conn = ssqlite(DATABASE_NAME)

    sql_query = "SELECT * FROM `articles` WHERE `post_id`=?"
    article_result = db_conn.run_query(sql_query, post_id)

    if article_result:
        article = article_result.fetchone()

        sql_query = "SELECT * FROM `comments` WHERE `post_id`=? ORDER BY `comment_date` DESC"
        comments_result = db_conn.run_query(sql_query, post_id)

        if comments_result:
            comments = comments_result.fetchall()

    else:
        redirect(url_for('articles'))

    return render_template('/article.html', article=article, comments=comments)


@app.route("/article/delete/<string:id>")
def delete_article(id):
    pass


@app.route('/article/update/<string:id>', methods=['GET', 'POST'])
def update_article(id):
    return render_template('update_article.html')


@app.route('/article/write', methods=['GET', 'POST'])
def write_article():
    # instead of trying to get the session['token'], we rather check if there is 'token'
    # as a key in the session global dictionary
    if 'token' in session:
        user_email = session['email']

        message = ''
        cat_filter = "danger"

        if not request.form:
            message = "There is no request form"

        else:
            if request.method != 'POST':
                message = 'Request method is not POST'

            else:
                if (
                        not request.form.get('post_title') or
                        not request.form.get('post_content') or
                        not request.form.get('post_submit_button')):

                    message = 'There are empty fields, please fill them out'
                    print(request.form.get('post_title'), request.form.get(
                        'post_content'), request.form.get('post_submit_button'))

                else:
                    post_title = request.form.get('post_title')
                    post_content = request.form.get('post_content')

                    # if post_title == "" or post_content == "":
                    #     message = ""
                    # need some validation and verification

                    connection = ssqlite(DATABASE_NAME)

                    sql_query = "INSERT INTO `articles`(`post_title`, `post_content`, `user_email`, `post_date`) VALUES(?, ?, ?, ?)"
                    post_date = Gen().get_current_date_time()

                    result = connection.run_query(
                        sql_query, post_title, post_content, user_email, post_date)

                    # stamp the database - commit the changes and close connection
                    connection.stamp()

                    # success
                    message = "article added successfully"
                    cat_filter = "success"

                    # redirect to index page
                    return redirect(url_for('index'))

    else:
        message = "Please login first"
        return redirect(url_for('login'))

    flash(message, cat_filter)

    return render_template('write_article.html')


if __name__ == "__main__":
    app.run()
