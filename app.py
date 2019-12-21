from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for, Markup)

from Helper import Generator as Gen
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


@app.route('/contact', methods=['GET', 'POST'])
# add a basic form so that users can communicate with you
def contact():
    return render_template('contact.html')


# account settings
@app.route('/email_token', methods=['GET', 'POST'])
def email_token():
    return render_template('email_token_field.html')


def get_user_details(email):
    """ read user details, given the email, returns False is the email=='' or the query is unsuccessful """
    if not email:
        return False

    db_conn = ssqlite(DATABASE_NAME)

    sql_query = "SELECT `user_first_name`, `user_last_name`, `user_bio`, `user_email` FROM `users` WHERE `user_email`=?"

    user_data = db_conn.run_query(sql_query, email).fetchone()

    if user_data:
        db_conn.stamp()
        return user_data
    else:
        return False


@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if not 'token' in session:
        return redirect(url_for('login'))

    user_email = session.get('email')

    if get_user_details(user_email):
        user_data = get_user_details(user_email)
    else:
        return redirect(url_for('login'))

    return render_template('user_profile.html', user_data=user_data)


@app.route('/password_token', methods=['GET', 'POST'])
def password_token():
    return render_template('password_token_field.html')


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    return render_template('forget_password.html')


@app.route('/delete_user/<string:email>', methods=['GET', 'POST'])
def delete_user(email=''):
    return email


# comments
@app.route('/comment/write/<string:article_id>', methods=['GET', 'POST'])
def write_comment(article_id):

    if not 'token' in session:
        return redirect(url_for('logout'))

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

                db_conn = ssqlite(DATABASE_NAME)

                sql_query = "INSERT INTO `comments`(`post_id`, `comment_text`, `comment_date`, `user_email`) VALUES(?, ?, ?, ?)"
                result = db_conn.run_query(sql_query, article_id, comment_text, comment_date, user_email)

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
    if not 'token' in session:
        return redirect(url_for('logout'))

    user_email = session.get('email')

    db_conn = ssqlite(DATABASE_NAME)
    sql_query = "SELECT `user_email`, `post_id` FROM `comments` WHERE `comment_id`=?"

    result = db_conn.run_query(sql_query, comment_id).fetchone()

    if result:
        email = result[0]
        post_id = result[1]

        if user_email == email:
            sql_query = "DELETE FROM `comments` WHERE `comment_id`=?"
            
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


    


@app.route('/comment/update/<string:comment_id>', methods=['GET', 'POST'])
def update_comment(comment_id):
    if not 'token' in session:
        return redirect(url_for('all_articles'))
    return comment_id


# signup, login and logout
@app.route('/account/signup/', methods=['GET', 'POST'])
@app.route('/account/signup/<string:email>', methods=['GET', 'POST'])
def signup(email=''):
    if 'token' in session:
        return redirect(url_for('all_articles'))

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

                                # stamp the database - commit the changes and close connection
                                connection.stamp()

                            else:

                                # create a session
                                session["token"] = Gen().generate_token()
                                session["email"] = email

                                # success
                                message = "signup successfull"
                                cat_filter = "success"

                                # stamp the database - commit the changes and close connection
                                connection.stamp()

                                # redirect to index page
                                return redirect(url_for('index'))

                else:
                    message = "Invalide email format"

    flash(message, cat_filter)

    return render_template('signup.html', email=email)


@app.route('/account/login/', methods=['GET', 'POST'])
@app.route('/account/login/<string:email>', methods=['GET', 'POST'])
def login(email=''):
    if 'token' in session:
        return redirect(url_for('all_articles'))

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

                        connection = ssqlite(DATABASE_NAME)
                        sql_query = "SELECT `user_password` FROM `users` WHERE `user_email`=?"

                        user_password = connection.run_query(
                            sql_query, email).fetchone()

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
                        connection.stamp()

            else:
                message = "Invalide email format"

    flash(message, cat_filter)
    return render_template('login.html')


@app.route("/account/logout")
def logout():
    if 'token' in session:
        session.clear()
        flash("Logout successfull", "success")
        return redirect(url_for("login"))
    else:
        return redirect(url_for('all_articles'))


# articles
@app.route('/article/')  # /article/unknow_id - return articles
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


@app.route('/article/read/<string:article_id>')
def read_article(article_id):
    article = []
    comments = []

    post_id = article_id

    db_conn = ssqlite(DATABASE_NAME)

    sql_query = "SELECT * FROM `articles` WHERE `post_id`=?"
    article = db_conn.run_query(sql_query, post_id).fetchone()

    if article:

        sql_query = "SELECT * FROM `comments` WHERE `post_id`=? ORDER BY `comment_date` DESC"
        comments_result = db_conn.run_query(sql_query, post_id).fetchall()

        if comments_result:
            comments = comments_result

    else:
        return redirect(url_for('all_articles'))

    return render_template('/article.html', article=article, comments=comments)


@app.route("/article/delete/<string:article_id>")
def delete_article(article_id):
    db_conn = ssqlite(DATABASE_NAME)

    if 'token' in session:
        user_email = session.get('email')
        sql_query = "SELECT `user_email` FROM `articles` WHERE `post_id`=?"

        email_result = db_conn.run_query(sql_query, article_id).fetchone()

        if email_result:
            if email_result[0] == user_email:
                delete_result = db_conn.run_query(
                    "DELETE FROM `articles` WHERE `post_id`=? AND `user_email`=?", article_id, user_email)

                if delete_result.rowcount:
                    flash("Article deleted successfully", 'success')
                    db_conn.stamp()
                else:
                    flash("Article deletion unsuccessful", 'danger')

                return redirect(url_for('all_articles'))

        return redirect(url_for('read_article', article_id=article_id))

    else:
        return redirect(url_for('all_articles'))


# function to read the article content and title
def read_title_and_post(article_id):
    id = article_id
    db_conn = ssqlite(DATABASE_NAME)

    sql_query = "SELECT `post_title`, `post_content` FROM `articles` WHERE `post_id`=?"
    result = db_conn.run_query(sql_query, id).fetchone()

    if result:
        return result
    else:
        return False


@app.route('/article/update/<string:article_id>', methods=['GET', 'POST'])
def update_article(article_id):
    if 'token' in session:
        if read_title_and_post(article_id):
            article = read_title_and_post(article_id)
        else:
            return redirect(url_for('all_articles'))

        post_id = article_id

        if request.form and request.method == 'POST':

            if (
                    request.form.get('update_post_title') and
                    request.form.get('update_post_content') and
                    request.form.get('update_post_submit_button')):

                post_content = request.form.get('update_post_content')
                post_title = request.form.get('update_post_title')

                db_conn = ssqlite(DATABASE_NAME)

                sql_query = "UPDATE `articles` SET  `post_content`=?, `post_title`=? WHERE `post_id`=?"
                update_result = db_conn.run_query(
                    sql_query, post_content, post_title, post_id)

                if update_result.rowcount:
                    # stamp the db
                    db_conn.stamp()
                    return redirect(url_for('read_article', article_id=post_id))
                else:
                    flash('update unsuccessful', 'danger')

                    # stamp the db
                    db_conn.stamp()
    else:
        return redirect(url_for('all_articles'))

    return render_template('update_article.html', article=article)


@app.route('/article/write', methods=['GET', 'POST'])
def write_article():
    # instead of trying to get the session['token'], we rather check if there is 'token'
    # as a key in the session global dictionary
    if 'token' in session:
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
                    print(request.form.get('post_title'), request.form.get(
                        'post_content'), request.form.get('post_submit_button'))

                else:
                    post_title = request.form.get('post_title')
                    post_content = request.form.get('post_content')

                    # need some validation and verification

                    connection = ssqlite(DATABASE_NAME)

                    sql_query = "INSERT INTO `articles`(`post_title`, `post_content`, `user_email`, `post_date`) VALUES(?, ?, ?, ?)"
                    post_date = Gen().get_current_date_time()

                    result = connection.run_query(
                        sql_query, post_title, post_content, user_email, post_date)

                    if not result.rowcount > 0:
                        message = "could not add article, please try again"
                    else:
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


# test request
with app.test_request_context():
    # index
    print(url_for('index'))
    # about
    print(url_for('about'))
    # contact
    print(url_for('contact'))
    # email token
    print(url_for('email_token'))
    # password token
    print(url_for('password_token'))
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
