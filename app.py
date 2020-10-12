import mysql.connector
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

import datetime

from Helper import DataSizeRange
from Helper import Generator as Gen
from Helper import Validator as Val

app = Flask(__name__)
app.debug = True
app.secret_key = "12345"  # use a better secret_key
app.templates_auto_reload = True
app.cache_type = "null"
app.permanent_session_lifetime = datetime.timedelta(hours=1)

DATABASE_NAME = "pill_code_db"  # mysql db_name
USERNAME = "root"
HOST = "localhost"
PASSWORD = ""


# function to read the article content and title
def read_title_and_post(article_id):
    id = article_id

    db_conn = mysql.connector.connect(
        host=HOST, user=USERNAME,
        password=PASSWORD, database=DATABASE_NAME, buffered=True)

    sql_query = "SELECT `post_title`, `post_content` FROM `articles` WHERE `post_id`=%s"

    cur = db_conn.cursor()

    result = cur.execute(sql_query, (id, ))
    data = cur.fetchone() if result else None

    db_conn.close()

    return data if data else False


# this function does the massive work in updating a users firstname, lastname and bio
# call this function then pass in the user email
# , the name of the field to update. the value to pass there is obtain from the form.
# also we take the field name and the name of the button to that form
def update_user_profile(email, set_field, field_name, btn_name):
    if not 'token' in session or not 'email' in session:
        return redirect(url_for('logout'))

    if not email:
        return False

    if not request.form or not request.method == 'POST':
        return False

    if email != session.get('email'):
        return False

    field_data = request.form.get(field_name)
    field_btn_val = request.form.get(btn_name)

    if not field_name or not field_btn_val:
        message = 'There is an empty field, please fill it out'
        cat_filter = 'danger'

    else:
        sql_query = f"UPDATE `users` SET {set_field}=%s WHERE `user_email`=%s"
        values = (field_data, email)

        db_conn = mysql.connector.connect(
            host=HOST, user=USERNAME,
            password=PASSWORD, database=DATABASE_NAME, buffered=True)

        cur = db_conn.cursor()

        result = cur.execute(sql_query, values)

        message = "update successful"
        cat_filter = 'success'

        if not result or not result.rowcount:
            message = "update unsuccessful"
            cat_filter = 'danger'

        # stamp the database - commit the changes and close connection
        db_conn.commit()
        db_conn.close()

    flash(message, cat_filter)

    return True


# index/home page
@app.route('/')
def index():
    articles = []
    try:
        db_conn = mysql.connector.connect(
            host=HOST, user=USERNAME,
            password=PASSWORD, database=DATABASE_NAME, buffered=True)

        sql_query = "SELECT `post_id`, `post_title`, `post_content`, `user_email`, `post_date` FROM `articles`  ORDER BY `post_id` DESC"

        cur = db_conn.cursor()

        cur.execute(sql_query)

        if cur:
            articles = cur.fetchall()

        db_conn.close()

    except (mysql.connector.Error, Exception) as e:
        print(str(e))

    return render_template("index.html", articles=articles)


# static pages
@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact', methods=['GET', 'POST'])
# add a basic form so that users can communicate with you
def contact():
    return render_template('contact.html')


# account settings
@app.route('/setting/', methods=['GET', 'POST'])
@app.route('/setting/profile', methods=['GET', 'POST'])
def user_profile():
    if not 'token' in session or not 'email' in session:
        return redirect(url_for('logout'))

    try:
        email = session.get('email')

        db_conn = mysql.connector.connect(
            host=HOST, user=USERNAME,
            password=PASSWORD, database=DATABASE_NAME, buffered=True)

        sql_query = "SELECT `user_first_name`, `user_last_name`, `user_bio`, `user_email` FROM `users` WHERE `user_email`=%s"

        cur = db_conn.cursor()
        cur.execute(sql_query, (email,))

        if not cur:
            return redirect(url_for('logout'))

        user_data = cur.fetchone()

        db_conn.close()

    except (mysql.connector.Error, Exception) as e:
        print(str(e))
        return redirect(url_for('logout'))

    if not user_data:
        return redirect(url_for('login'))

    return render_template('user_profile.html', user_data=user_data)


@app.route('/setting/firstname/<string:email>', methods=['GET', 'POST'])
def update_first_name(email=''):
    if update_user_profile(email, 'user_first_name', 'update_first_name', 'update_first_name_btn'):
        return redirect(url_for('user_profile'))
    else:
        return redirect(url_for('logout'))


@app.route('/setting/lastname/<string:email>', methods=['GET', 'POST'])
def update_last_name(email=''):
    if update_user_profile(email, 'user_last_name', 'update_last_name', 'update_last_name_btn'):
        return redirect(url_for('user_profile'))
    else:
        return redirect(url_for('logout'))


@app.route('/setting/bio/<string:email>', methods=['GET', 'POST'])
def update_bio(email=''):
    if update_user_profile(email, 'user_bio', 'update_bio', 'update_bio_btn'):
        return redirect(url_for('user_profile'))
    else:
        return redirect(url_for('logout'))


@app.route('/setting/email/<string:email>', methods=['GET', 'POST'])
def email_token(email=''):
    # return render_template('email_token_field.html')
    return redirect(url_for('user_profile'))


@app.route('/setting/password/<string:email>', methods=['GET', 'POST'])
def password_token(email=''):
    # return render_template('password_token_field.html')
    return redirect(url_for('user_profile'))


@app.route('/setting/forget_password', methods=['GET', 'POST'])
def forget_password():
    return render_template('forget_password.html')
    # return redirect(url_for('logout'))


@app.route('/setting/reset_password/<string:email>', methods=['GET', 'POST'])
def reset_password(email=''):
    return render_template('reset_password.html')
    # return redirect(url_for('logout'))


# comments
@app.route('/comment/write/<string:article_id>', methods=['GET', 'POST'])
def write_comment(article_id):

    if not 'token' in session or not 'email' in session:
        return redirect(url_for('logout'))

    message = ''
    cat_filter = "danger"

    if not request.form:
        message = "There is no request form"

    else:
        if request.method != 'POST':
            message = 'Request method is not POST'

        else:
            comment_text = request.form.get('comment_box')
            add_comment_btn = request.form.get('add_comment_btn')

            if not comment_text or not add_comment_btn:
                message = 'Comment is empty'

            else:
                user_email = session.get('email')
                comment_date = Gen().get_current_date_time()

                db_conn = mysql.connector.connect(
                    host=HOST, user=USERNAME,
                    password=PASSWORD, database=DATABASE_NAME, buffered=True)

                sql_query = "INSERT INTO `comments`(`post_id`, `comment_text`, `comment_date`, `user_email`) VALUES(%s, %s, %s, %s)"
                values = (article_id, comment_text, comment_date, user_email)

                cur = db_conn.cursor()
                result = cur.execute(sql_query, values)

                if result.rowcount:
                    message = "Comment added successfully"
                    cat_filter = 'success'

                else:
                    message = "could not add comment"

                db_conn.commit()
                db_conn.close()

    flash(message, cat_filter)

    return redirect(url_for('read_article', article_id=article_id))


@app.route('/comment/delete/<string:comment_id>', methods=['GET', 'POST'])
def delete_comment(comment_id):
    if not 'token' in session or not 'email' in session:
        return redirect(url_for('logout'))

    user_email = session.get('email')

    db_conn = mysql.connector.connect(
        host=HOST, user=USERNAME,
        password=PASSWORD, database=DATABASE_NAME, buffered=True)

    sql_query = "SELECT `user_email`, `post_id` FROM `comments` WHERE `comment_id`=%s"

    select_cur = db_conn.cursor()
    select_cur = cur.execute(sql_query, (comment_id,))

    result = select_cur.fetchone() if select_cur else None

    if result:
        email = result[0]
        post_id = result[1]

        if user_email == email:
            sql_query = "DELETE FROM `comments` WHERE `comment_id`=%s"

            delete_cur = db_conn.cursor()
            result = delete_cur.execute(sql_query, (comment_id,))

            if result.rowcount:
                message = "comment deleted successfully"
                cat_filter = "success"

            else:
                message = "could not delete comment"
                cat_filter = "danger"

            db_conn.commit()

            flash(message, cat_filter)

    db_conn.close()

    return redirect(url_for('read_article', article_id=post_id))


# read comment
def read_comment(comment_id):
    """ return a tuple of the post_id, comment_text and user_email """
    db_conn = mysql.connector.connect(
        host=HOST, user=USERNAME,
        password=PASSWORD, database=DATABASE_NAME, buffered=True)

    sql_query = "SELECT `comment_id`, `comment_text`, `post_id`, `user_email` FROM `comments` WHERE `comment_id`=%s"

    cur = db_conn.cursor()
    cur = cur.execute(sql_query, (comment_id, ))

    result = cur.fetchone() if cur else None

    db_conn.close()

    return result if result else False


@app.route('/comment/update/<string:comment_id>', methods=['GET', 'POST'])
def update_comment(comment_id):
    if not 'token' in session or not 'email' in session:
        return redirect(url_for('logout'))

    user_email = session.get('email')

    # read the comment data
    data = read_comment(comment_id)

    if not data:
        return redirect(url_for('all_articles'))

    # comment_id = data[0]
    # comment_text = data[1]
    post_id = data[2]
    email = data[3]

    cat_filter = 'danger'
    message = ''

    if not email == user_email:
        message = "edit an article you wrote"
        return redirect(url_for('all_articles'))

    if not request.form:
        message = "There is no request form"

    else:
        if request.method != 'POST':
            message = 'Request method is not POST'

        else:

            comment_text = request.form.get('update_comment_content')
            update_comment_submit_btn = request.form.get(
                'update_comment_submit_button')

            if not comment_text or not update_comment_submit_btn:
                message = 'Select a comment you wrote'
                return redirect(url_for('read_article', article_id=post_id))

            else:

                db_conn = mysql.connector.connect(
                    host=HOST, user=USERNAME,
                    password=PASSWORD, database=DATABASE_NAME, buffered=True)

                sql_query = "UPDATE `comments` SET `comment_text`=%s WHERE `comment_id`=%s AND `user_email`=%s"
                values = (comment_text, comment_id, user_email)

                cur = db_conn.cursor()

                result = cur.execute(sql_query, values)

                if not result.rowcount:
                    message = "could not update the comment"

                else:
                    # a row is affected
                    message = "comment updated successfully"
                    cat_filter = "success"

                # stamp the database - commit the changes and close connection
                db_conn.commit()
                db_conn.close()

                flash(message, cat_filter)

                # redirect to to read_article with the article id
                return redirect(url_for('read_article', article_id=post_id))

    flash(message, cat_filter)

    return render_template('update_comment.html', comment=data)


# signup, login, Logout and delete account
@app.route('/account/signup/', methods=['GET', 'POST'])
@app.route('/account/signup/<string:email>', methods=['GET', 'POST'])
def signup(email=''):
    if 'token' in session or 'email' in session:
        return redirect(url_for('logout'))

    message = ''
    cat_filter = "danger"

    if not request.form:
        message = "There is no request form"

    else:
        if request.method != 'POST':
            message = 'Request method is not POST'

        else:

            first_name = request.form.get('sign_up_first_name')
            last_name = request.form.get('sign_up_last_name')
            bio = request.form.get('sign_up_user_bio')
            email = request.form.get('sign_up_email')
            sign_up_password = request.form.get('sign_up_password')
            confirm_password = request.form.get('sign_up_confirm_password')
            register_button = request.form.get('register_button')

            if (
                    not first_name or not last_name or not email or not sign_up_password or
                    not confirm_password or not bio or not register_button):

                message = 'There are empty fields, please fill them out'

            else:

                if Val().is_email_valid(email):

                    if not Val().is_valid_password(sign_up_password) or not Val().is_valid_password(confirm_password):
                        message = "Invalid password format"

                    else:
                        if not Val().validate_size(sign_up_password, DataSizeRange(6, 20)):
                            message = "Check password length, 6 - 20"

                        else:
                            hashed_passwd = Gen().get_bcrypt_hashed_passwd(sign_up_password)
                            registered_date = Gen().get_current_date_time()

                            db_conn = mysql.connector.connect(
                                host=HOST, user=USERNAME,
                                password=PASSWORD, database=DATABASE_NAME, buffered=True)

                            sql_query = "SELECT user_email FROM `users` WHERE `user_email`=%s"

                            select_cur = db_conn.cursor()

                            result = select_cur.execute(sql_query, (email, ))

                            if result:
                                return redirect(url_for('login', email=email))

                            sql_query = "INSERT INTO `users`(`user_first_name`, `user_last_name`, `user_email`, `user_password`, `user_bio`, `user_register_date`) VALUES(%s, %s, %s, %s, %s, %s)"

                            values = (first_name, last_name, email,
                                      hashed_passwd, bio, registered_date)

                            insert_cur = db_conn.cursor()

                            try:
                                result = insert_cur.execute(sql_query, values)

                                # create a session
                                session["token"] = Gen().generate_token()
                                session["email"] = email

                                print(session)

                                # success
                                message = "signup successful"
                                cat_filter = "success"

                                # stamp the database - comNoblessemit the changes and close connection
                                db_conn.commit()
                                db_conn.close()

                                # redirect to index page
                                return redirect(url_for('index'))
                            except (mysql.connector.Error, Exception) as e:
                                print(str(e))
                                message = "signup unsuccessful"
                                cat_filter = "danger"
                                return render_template('signup.html', email=email)

                else:
                    message = "Invalide email format"

    flash(message, cat_filter)

    return render_template('signup.html', email=email)


@app.route('/account/login/', methods=['GET', 'POST'])
@app.route('/account/login/<string:email>', methods=['GET', 'POST'])
def login(email=''):
    message = ''
    cat_filter = 'danger'

    if 'token' in session or 'email' in session:
        return redirect(url_for('logout'))

    if request.method != 'POST':
        message = 'Enter the needed credentials'
        flash(message, cat_filter)
        return render_template('login.html', email=email)

    email = request.form.get('login_email')
    password = request.form.get('login_password')
    login_button = request.form.get('login_button')

    if not email or not password or not login_button:
        message = 'Email and Password are required for a login, please...'
        flash(message, cat_filter)
        return render_template('login.html', email=email)

    if (
            not Val().is_email_valid(email) or
            not Val().validate_size(password, DataSizeRange(6, 20)) or
            not Val().is_valid_password(password)):

        message = "Invalide credentials, check and enter again"
        flash(message, cat_filter)
        return render_template('login.html', email=email)

    try:
        db_conn = mysql.connector.connect(
            host=HOST, user=USERNAME,
            password=PASSWORD, database=DATABASE_NAME, buffered=True)

        sql_query = "SELECT `user_password` FROM `users` WHERE `user_email`=%s"

        cur = db_conn.cursor()
        cur.execute(sql_query, (email,))

        if not cur:
            return redirect(url_for('signup', email=email))

        result = cur.fetchone()
        hashed_password = result[0]

        if not Val().is_valid_hash(password, hashed_password):
            message = "Invalid credentials, please check and enter again ..."
            flash(message, cat_filter)
            return render_template('login.html', email=email)

    except (mysql.connector.Error, Exception) as e:
        print(str(e))
        message = "There was an error when loging in, please try again in a few seconds later..."
        flash(message, cat_filter)
        return render_template('login.html', email=email)

    session["token"] = Gen().generate_token()
    session["email"] = email

    # success
    message = "login successfull"
    cat_filter = "success"

    return redirect(url_for('index'))


@app.route("/account/logout")
def logout():
    if 'token' in session:
        flash("Logout successfull", "success")

    session.clear()

    return redirect(url_for("login"))


@app.route('/account/delete/<string:email>', methods=['GET', 'POST'])
def delete_user(email=''):
    return redirect(url_for('user_profile'))


# articles
@app.route('/article/')  # /article/unknow_id - return articles
@app.route('/articles')
def all_articles():
    articles = []

    try:
        db_conn = mysql.connector.connect(
            host=HOST, user=USERNAME,
            password=PASSWORD, database=DATABASE_NAME, buffered=True)

        sql_query = "SELECT `post_id`, `post_title`, `user_email`, `post_date` FROM `articles`  ORDER BY `post_id` DESC"

        cur = db_conn.cursor()
        cur.execute(sql_query)

        if cur:
            articles = cur.fetchall()

        db_conn.close()
    except (mysql.connector.Error, Exception) as e:
        print(str(e))

    return render_template('all_articles.html', articles=articles)


@app.route('/article/read/<string:article_id>')
def read_article(article_id):
    article = []
    comments = []

    try:
        post_id = article_id

        db_conn = mysql.connector.connect(
            host=HOST, user=USERNAME,
            password=PASSWORD, database=DATABASE_NAME, buffered=True)

        sql_query = "SELECT * FROM `articles` WHERE `post_id`=%s"

        articles_cur = db_conn.cursor()
        articles_cur.execute(sql_query, (post_id, ))

        if not articles_cur:
            return redirect(url_for('all_articles'))

        article = articles_cur.fetchone()
        print('0000000 article')
        print(article)

        # select comments
        sql_query = "SELECT * FROM `comments` WHERE `post_id`=%s ORDER BY `comment_date` DESC"

        comments_cur = db_conn.cursor()
        comments_cur.execute(sql_query, (post_id, ))

        if comments_cur:
            comments = comments_cur.fetchall()

        print('0000000 comments')
        print(comments)

        db_conn.close()

    except (mysql.connector.Error, Exception) as e:
        print('error', str(e))

    return render_template("article.html", article=article, comments=comments)


@app.route("/article/delete/<string:article_id>")
def delete_article(article_id):
    if not 'token' in session or not 'email' in session:
        return redirect(url_for('logout'))

    db_conn = mysql.connector.connect(
        host=HOST, user=USERNAME,
        password=PASSWORD, database=DATABASE_NAME, buffered=True)

    sql_query = "SELECT `user_email` FROM `articles` WHERE `post_id`=%s"

    select_articles_cur = db_conn.cursor()

    articles_result = select_articles_cur.execute(sql_query, (article_id,))

    data = articles_result.fetchone() if articles_result else None

    user_email = session.get('email')

    if result:
        result_email = data[0]

        if result_email == user_email:

            sql_query = "DELETE FROM `articles` WHERE `post_id`=%s AND `user_email`=%s"
            values = (article_id, user_email)

            delete_articles_cur = db_conn.cursor()

            delete_result = delete_articles_cur.execute(sql_query, values)

            if delete_result.rowcount:
                # delete all comments related to this article.
                # it is a success either a row is affected or not

                sql_query = "DELETE FROM `comments` WHERE `post_id`=%s"

                delete_comments_cur = db_conn.cursor()

                delete_comments_cur.execute(sql_query, (article_id,))

                flash("Article deleted successfully", 'success')

            else:
                flash("Article deletion unsuccessful", 'danger')

            db_conn.commit()
            db_conn.close()

            return redirect(url_for('all_articles'))

    db_conn.close()

    return redirect(url_for('read_article', article_id=article_id))


@app.route('/article/update/<string:article_id>', methods=['GET', 'POST'])
def update_article(article_id):
    if not 'token' in session or not 'email' in session:
        return redirect(url_for('logout'))

    # TODO: rewrite this functionality


@app.route('/article/write', methods=['GET', 'POST'])
def write_article():
    if not 'token' in session or not 'email' in session:
        return redirect(url_for('logout'))

    message = ''
    cat_filter = "danger"

    if request.method != 'POST':
        return render_template('write_article.html')

    post_title = request.form.get('post_title')
    post_content = request.form.get('post_content')
    post_submit_button = request.form.get('post_submit_button')

    if not post_title or not post_content or not post_submit_button:
        message = 'There are empty fields, please fill them out'

        return render_template(
            'write_article.html', post_title=post_title, post_content=post_content)

    # need some validation and verification

    try:
        db_conn = mysql.connector.connect(
            host=HOST, user=USERNAME,
            password=PASSWORD, database=DATABASE_NAME, buffered=True)

        user_email = session.get('email')
        post_date = Gen().get_current_date_time()

        sql_query = "INSERT INTO `articles`(`post_title`, `post_content`, `user_email`, `post_date`) VALUES(%s, %s, %s, %s)"
        values = (post_title, post_content, user_email, post_date)

        cur = db_conn.cursor()
        cur.execute(sql_query, values)

        if not cur:
            message = "An error while creating an article, please try again in a few seconds later"

            db_conn.close()

            flash(message, cat_filter)
            return render_template(
                'write_article.html', post_title=post_title, post_content=post_content)

        db_conn.commit()
        db_conn.close()

        message = "article added successfully"
        cat_filter = "success"

        flash(message, cat_filter)
        return redirect(url_for('index'))

    except (mysql.connector.Error, Exception) as e:
        print(str(e))
        return render_template(
            'write_article.html', post_title=post_title, post_content=post_content)


# test request
with app.test_request_context():
    # index
    print(url_for('index'))
    # about
    print(url_for('about'))
    # contact
    print(url_for('contact'))
    # email token
    print(url_for('email_token', email='hello@hmail.com'))
    # password token
    print(url_for('password_token', email='hello@hmail.com'))
    # user profile
    print(url_for('user_profile'))
    # forget password
    print(url_for('forget_password'))
    # delete user
    print(url_for('delete_user', email='hello@hmail.com'))
    # write comment
    print(url_for('write_comment', article_id='1'))
    # delete comment
    print(url_for('delete_comment', comment_id='1'))
    # update comment
    print(url_for('update_comment', comment_id='1'))
    # signup
    print(url_for('signup'))
    print(url_for('signup', email="A@amail.com"))
    # login
    print(url_for('login'))
    print(url_for('login', email='A@amail.com'))
    # logout
    print(url_for('logout'))
    # article
    print(url_for('all_articles'))
    # read article
    print(url_for('read_article', article_id='1'))
    # update article
    print(url_for('update_article', article_id='1'))
    # write article
    print(url_for('write_article'))
    # delete article
    print(url_for('delete_article', article_id='1'))
    # print(url_for())
    # print(url_for())


if __name__ == "__main__":
    app.run()
