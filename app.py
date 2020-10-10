from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

from Helper import DataSizeRange
from Helper import Generator as Gen
from Helper import Validator as Val
# from ssqlite import ssqlite
from smysql import smysql

app = Flask(__name__)
app.debug = True
app.secret_key = "12345"  # use a better secret_key
app.templates_auto_reload = True
app.cache_type = "null"

# database name
# DATABASE_NAME = "pill_code_db.db"  # sqlite db_name
DATABASE_NAME = "pill_code_db"  # mysql db_name
USERNAME = "root"
HOST = "localhost"
PASSWORD = ""

# check if there is session


def is_set_session():
    """ check if there is session. We do this to see if user has actually signed in """
    if not 'token' in session:
        return redirect(url_for('logout'))
    else:
        return True

# get user details by passing email as the argument


def get_user_details(email):
    """ read user details, given the email, returns False is the email=='' or the query is unsuccessful """
    if not email:
        return False

    db_conn = smysql(host=HOST, user=USERNAME,
                     password=PASSWORD, database=DATABASE_NAME)

    sql_query = "SELECT `user_first_name`, `user_last_name`, `user_bio`, `user_email` FROM `users` WHERE `user_email`=%s"

    cur = db_conn.run_query(sql_query, email)
    user_data = cur.fetchone() if cur else None
    db_conn.stamp()

    if user_data:
        return user_data
    else:
        return False


# function to read the article content and title
def read_title_and_post(article_id):
    id = article_id
    db_conn = smysql(host=HOST, user=USERNAME,
                     password=PASSWORD, database=DATABASE_NAME)

    sql_query = "SELECT `post_title`, `post_content` FROM `articles` WHERE `post_id`=%s"
    cur = db_conn.run_query(sql_query, id)
    result = cur.fetchone() if cur else None

    if result:
        return result
    else:
        return False


# this function does the massive work in updating a users firstname, lastname and bio
# call this function then pass in the user email
# , the name of the field to update. the value to pass there is obtain from the form.
# also we take the field name and the name of the button to that form
def update_user_profile(email, set_field, field_name, btn_name):
    if is_set_session():
        if not email:
            return False

        if not request.form or not request.method == 'POST':
            return False

        if not email == session.get('email'):
            return False

        if (
                not request.form.get(field_name) or
                not request.form.get(btn_name)):

            message = 'There is an empty field, please fill it out'
            cat_filter = 'danger'

        else:
            field_data = request.form.get(field_name)

            sql_query = f"UPDATE `users` SET {set_field}=%s WHERE `user_email`=%s"
            db_conn = smysql(host=HOST, user=USERNAME,
                             password=PASSWORD, database=DATABASE_NAME)

            result = db_conn.run_query(sql_query, field_data, email)

            if not result.rowcount:
                message = "update unsuccessful"
                cat_filter = 'danger'

            else:
                message = "update successful"
                cat_filter = 'success'

            # stamp the database - commit the changes and close connection
            db_conn.stamp()

        flash(message, cat_filter)

        return True


# index/home page
@app.route('/')
def index():
    # db_conn = ssqlite(DATABASE_NAME)
    db_conn = smysql(host=HOST, user=USERNAME,
                     password=PASSWORD, database=DATABASE_NAME)
    cur = db_conn.run_query(
        "SELECT * FROM `articles` ORDER BY `post_date` DESC")

    if cur != None:
        articles = cur.fetchall()

        return render_template("index.html", articles=articles)

    return render_template("index.html")


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
    if is_set_session():

        user_email = session.get('email')

        if not get_user_details(user_email):
            return redirect(url_for('login'))

        user_data = get_user_details(user_email)

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

    if is_set_session():

        message = ''
        cat_filter = "danger"

        if not request.form:
            message = "There is no request form"

        else:
            if request.method != 'POST':
                message = 'Request method is not POST'

            else:
                if (
                        not request.form.get('comment_box') or
                        not request.form.get('add_comment_btn')):

                    message = 'Comment is empty'

                else:
                    comment_text = request.form.get('comment_box')
                    user_email = session.get('email')
                    comment_date = Gen().get_current_date_time()

                    db_conn = smysql(host=HOST, user=USERNAME,
                                     password=PASSWORD, database=DATABASE_NAME)

                    sql_query = "INSERT INTO `comments`(`post_id`, `comment_text`, `comment_date`, `user_email`) VALUES(%s, %s, %s, %s)"
                    result = db_conn.run_query(
                        sql_query, article_id, comment_text, comment_date, user_email)

                    if result.rowcount > 0:
                        message = "Comment added successfully"
                        cat_filter = 'success'
                        db_conn.stamp()

                    else:
                        message = "could not add comment"
                        db_conn.stamp()

        flash(message, cat_filter)

        return redirect(url_for('read_article', article_id=article_id))


@app.route('/comment/delete/<string:comment_id>', methods=['GET', 'POST'])
def delete_comment(comment_id):
    if is_set_session():
        user_email = session.get('email')

        db_conn = smysql(host=HOST, user=USERNAME,
                         password=PASSWORD, database=DATABASE_NAME)
        sql_query = "SELECT `user_email`, `post_id` FROM `comments` WHERE `comment_id`=%s"

        cur = db_conn.run_query(sql_query, comment_id)
        result = cur.fetchone() if cur else None

        if result:
            email = result[0]
            post_id = result[1]

            if user_email == email:
                sql_query = "DELETE FROM `comments` WHERE `comment_id`=%s"

                result = db_conn.run_query(sql_query, comment_id)

                if result.rowcount == 1:
                    message = "comment deleted successfully"
                    cat_filter = "success"

                else:
                    message = "could not delete comment"
                    cat_filter = "danger"

                db_conn.stamp()
                flash(message, cat_filter)

            return redirect(url_for('read_article', article_id=post_id))

        else:
            return redirect(url_for('logout'))


# read comment
def read_comment(comment_id):
    """ return a tuple of the post_id, comment_text and user_email """
    db_conn = smysql(host=HOST, user=USERNAME,
                     password=PASSWORD, database=DATABASE_NAME)

    sql_query = "SELECT `comment_id`, `comment_text`, `post_id`, `user_email` FROM `comments` WHERE `comment_id`=%s"

    cur = db_conn.run_query(sql_query, comment_id)
    result = cur.fetchone() if cur else None
    db_conn.stamp()

    if result:
        return result
    else:
        return False


@app.route('/comment/update/<string:comment_id>', methods=['GET', 'POST'])
def update_comment(comment_id):
    if is_set_session():

        user_email = session.get('email')

        if not read_comment(comment_id):
            return redirect(url_for('all_articles'))

        # read the comment data
        data = read_comment(comment_id)

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
                if (
                        not request.form.get('update_comment_content') or
                        not request.form.get('update_comment_submit_button')):

                    message = 'Select a comment you wrote'

                    return redirect(url_for('read_article', article_id=post_id))

                else:
                    comment_text = request.form.get('update_comment_content')

                    db_conn = smysql(host=HOST, user=USERNAME,
                                     password=PASSWORD, database=DATABASE_NAME)
                    sql_query = "UPDATE `comments` SET `comment_text`=%s WHERE `comment_id`=%s AND `user_email`=%s"

                    result = db_conn.run_query(
                        sql_query, comment_text, comment_id, user_email)

                    if not result.rowcount:
                        message = "could not update the comment"

                    else:
                        # a row is affected
                        message = "comment updated successfully"
                        cat_filter = "success"

                    # stamp the database - commit the changes and close connection
                    db_conn.stamp()

                    flash(message, cat_filter)

                    # redirect to to read_article with the article id
                    return redirect(url_for('read_article', article_id=post_id))

        flash(message, cat_filter)

        return render_template('update_comment.html', comment=data)


# signup, login, Logout and delete account
@app.route('/account/signup/', methods=['GET', 'POST'])
@app.route('/account/signup/<string:email>', methods=['GET', 'POST'])
def signup(email=''):
    if is_set_session():

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
                            if not Val().validate_size(sign_up_password, DataSizeRange(6, 20)):
                                message = "Check password length, 6 - 20"

                            else:
                                hashed_passwd = Gen().get_bcrypt_hashed_passwd(sign_up_password)
                                registered_date = Gen().get_current_date_time()

                                db_conn = smysql(host=HOST, user=USERNAME,
                                                 password=PASSWORD, database=DATABASE_NAME)

                                sql_query = "SELECT user_email FROM `users` WHERE `user_email`=%s"

                                cur = db_conn.run_query(sql_query, email)

                                if cur:
                                    return redirect(url_for('login', email=email))

                                sql_query = "INSERT INTO `users`(`user_first_name`, `user_last_name`, `user_email`, `user_password`, `user_bio`, `user_register_date`) VALUES(%s, %s, %s, %s, %s, %s)"

                                result = db_conn.run_query(
                                    sql_query, first_name, last_name, email, hashed_passwd, bio, registered_date)

                                # if not result:
                                #     message = "Error"

                                #     # stamp the database - commit the changes and close connection
                                #     db_conn.stamp()

                                # else:

                                # create a session
                                session["token"] = Gen().generate_token()
                                session["email"] = email

                                # success
                                message = "signup successful"
                                cat_filter = "success"

                                # stamp the database - commit the changes and close connection
                                db_conn.stamp()

                                # redirect to index page
                                return redirect(url_for('index'))

                    else:
                        message = "Invalide email format"

        flash(message, cat_filter)

        return render_template('signup.html', email=email)


@app.route('/account/login/', methods=['GET', 'POST'])
@app.route('/account/login/<string:email>', methods=['GET', 'POST'])
def login(email=''):
    if is_set_session():

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
                        if not Val().validate_size(password, DataSizeRange(6, 20)):
                            message = "Check password length, 6 - 20"

                        else:

                            db_conn = smysql(host=HOST, user=USERNAME,
                                             password=PASSWORD, database=DATABASE_NAME)
                            sql_query = "SELECT `user_password` FROM `users` WHERE `user_email`=%s"

                            cur = db_conn.run_query(
                                sql_query, email)
                            user_password = cur.fetchone() if cur else None

                            if user_password != None:
                                hashed_password = user_password[0]

                                if not Val().is_valid_hash(password, hashed_password):
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
                            db_conn.stamp()

                else:
                    message = "Invalide email format"

        flash(message, cat_filter)
        return render_template('login.html', email=email)


@app.route("/account/logout")
def logout():
    if 'token' in session:
        session.clear()
        flash("Logout successfull", "success")

    return redirect(url_for("login"))


@app.route('/account/delete/<string:email>', methods=['GET', 'POST'])
def delete_user(email=''):
    return redirect(url_for('user_profile'))


# articles
@app.route('/article/')  # /article/unknow_id - return articles
@app.route('/articles')
def all_articles():

    articles = []

    db_conn = smysql(host=HOST, user=USERNAME,
                     password=PASSWORD, database=DATABASE_NAME)

    sql_query = "SELECT `post_id`, `post_title`, `user_email`,`post_date` FROM `articles` ORDER BY `post_id` DESC"

    cur = db_conn.run_query(sql_query)

    articles = cur.fetchall() if cur else NoneI

    db_conn.stamp()

    return render_template('all_articles.html', articles=articles)


@app.route('/article/read/<string:article_id>')
def read_article(article_id):
    article = []
    comments = []

    post_id = article_id

    db_conn = smysql(host=HOST, user=USERNAME,
                     password=PASSWORD, database=DATABASE_NAME)

    sql_query = "SELECT * FROM `articles` WHERE `post_id`=%s"

    cur = db_conn.run_query(sql_query, post_id)
    article = cur.fetchone() if cur else None

    if not article:
        return redirect(url_for('all_articles'))

    sql_query = "SELECT * FROM `comments` WHERE `post_id`=%s ORDER BY `comment_date` DESC"

    cur = db_conn.run_query(sql_query, post_id)
    comments_result = cur.fetchall() if cur else None

    if comments_result:
        comments = comments_result

    return render_template('/article.html', article=article, comments=comments)


@app.route("/article/delete/<string:article_id>")
def delete_article(article_id):
    if is_set_session():
        user_email = session.get('email')
        db_conn = smysql(host=HOST, user=USERNAME,
                         password=PASSWORD, database=DATABASE_NAME)

        sql_query = "SELECT `user_email` FROM `articles` WHERE `post_id`=%s"

        cur = db_conn.run_query(sql_query, article_id)
        email_result = cur.fetchone() if cur else None

        if email_result:
            if email_result[0] == user_email:
                delete_result = db_conn.run_query(
                    "DELETE FROM `articles` WHERE `post_id`=%s AND `user_email`=%s", article_id, user_email)

                if delete_result.rowcount:
                    # delete all comments related to this article.
                    # it is a success either a row is affected or not
                    db_conn.run_query(
                        "DELETE FROM `comments` WHERE `post_id`=%s", article_id)
                    flash("Article deleted successfully", 'success')

                else:
                    flash("Article deletion unsuccessful", 'danger')

                db_conn.stamp()
                return redirect(url_for('all_articles'))

        return redirect(url_for('read_article', article_id=article_id))


@app.route('/article/update/<string:article_id>', methods=['GET', 'POST'])
def update_article(article_id):
    if is_set_session():
        if not read_title_and_post(article_id):
            return redirect(url_for('all_articles'))

        article = read_title_and_post(article_id)
        post_id = article_id

        if request.form and request.method == 'POST':

            if (
                    request.form.get('update_post_title') and
                    request.form.get('update_post_content') and
                    request.form.get('update_post_submit_button')):

                post_content = request.form.get('update_post_content')
                post_title = request.form.get('update_post_title')

                db_conn = smysql(host=HOST, user=USERNAME,
                                 password=PASSWORD, database=DATABASE_NAME)

                sql_query = "UPDATE `articles` SET  `post_content`=%s, `post_title`=%s WHERE `post_id`=%s"
                update_result = db_conn.run_query(
                    sql_query, post_content, post_title, post_id)

                if update_result.rowcount:
                    # stamp the db
                    db_conn.stamp()

                    flash("article updated successfully", 'success')
                    return redirect(url_for('read_article', article_id=post_id))

                else:
                    # stamp the db
                    db_conn.stamp()
                    flash('update unsuccessful', 'danger')

    return render_template('update_article.html', article=article)


@app.route('/article/write', methods=['GET', 'POST'])
def write_article():
    if is_set_session():
        user_email = session.get('email')

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
                    # print(request.form.get('post_title'), request.form.get(
                    # 'post_content'), request.form.get('post_submit_button'))

                else:
                    post_title = request.form.get('post_title')
                    post_content = request.form.get('post_content')

                    # need some validation and verification

                    db_conn = smysql(host=HOST, user=USERNAME,
                                     password=PASSWORD, database=DATABASE_NAME)

                    sql_query = "INSERT INTO `articles`(`post_title`, `post_content`, `user_email`, `post_date`) VALUES(%s, %s, %s, %s)"
                    post_date = Gen().get_current_date_time()

                    result = db_conn.run_query(
                        sql_query, post_title, post_content, user_email, post_date)

                    if not result.rowcount:
                        message = "could not add article, please try again"
                    else:
                        # stamp the database - commit the changes and close connection
                        db_conn.stamp()

                        # success
                        message = "article added successfully"
                        cat_filter = "success"

                        flash(message, cat_filter)

                        # redirect to index page
                        return redirect(url_for('index'))

    flash(message, cat_filter)

    return render_template('write_article.html')


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
