from flask import Flask, render_template, redirect, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import dotenv
import os
from datetime import datetime
import smtplib

new_file = dotenv.find_dotenv()
dotenv.load_dotenv(new_file)

# Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

# CONNECT TO FLASK
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET")
ckeditor = CKEditor(app)
Bootstrap(app)

# DEVELOPER DETAILS
name_of_dev = os.environ.get("DEVELOPER")
surname = os.getenv("SURNAME")
LINKEDIN = os.environ.get("LINKED-IN")
GITHUB = os.getenv("GIT-HUB")
TWITTER = os.environ.get("TWITTER_")
MY_RESUME = os.getenv("RESUME")
MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASS = os.getenv("EMAIL_PASSWORD")
THIRD_EMAIL = os.environ.get("OTHER_EMAIL")
SECOND_EMAIL = os.environ.get("SECOND_EMAIL")
mail_list = [SECOND_EMAIL, MY_EMAIL, THIRD_EMAIL]
dev_api_key = os.environ.get("API_KEY")

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    """Database Model for manipulating records in the database."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    last_edit = db.Column(db.String(250))


# WTForm
class CreatePostForm(FlaskForm):
    """Creates a quick HTML form to post articles"""
    title = StringField("Blog Post Title", validators=[InputRequired()])
    subtitle = StringField("Subtitle", validators=[InputRequired()])
    author = StringField("Your Name", validators=[InputRequired()])
    img_url = StringField("Blog Image URL", validators=[InputRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[InputRequired()])
    submit = SubmitField("Submit Post")


class ContactForm(FlaskForm):
    """Creates a quick HTML form to accept user feedback"""
    name = StringField("", render_kw={"placeholder": "Name"}, validators=[InputRequired()])
    email = StringField("", render_kw={"placeholder": "Email Address"}, validators=[InputRequired()])
    mobile = StringField("", render_kw={"placeholder": "Phone Number"}, validators=[InputRequired()])
    message = CKEditorField("", render_kw={"placeholder": "Message"}, validators=[InputRequired()])


with app.app_context():
    db.create_all()     # creates all the records in the database
    date_ = datetime.now()      # gets the current date and time
    current_date = date_.strftime("%B %d, %Y")      # displays only the date as a string i.e. May 10, 2019
    current_year = date_.year       # displays only the year
    posts = db.session.query(BlogPost).all()    # returns the number of records(posts) in the database as a list.
    posts.sort(key=lambda r: r.date)    # sorts the list returned above by date

    @app.route('/')
    def get_all_posts():
        """Displays all posts/articles in the database on the screen"""
        global posts
        posts = db.session.query(BlogPost).all()    # retrieves all records from the database and stores them in a list
        posts.sort(key=lambda r: r.date)    # sorts the list by data
        return render_template("index.html", all_posts=posts, name=name_of_dev, surname=surname, year=current_year,
                               github=GITHUB, linkedin=LINKEDIN, twitter=TWITTER)

    @app.route("/post/<int:index>")
    def show_post(index):
        """Displays more details concerning the article that the user selected."""
        requested_post = None
        for blog_post in posts:    # searches each post for its article ID and determines if it matches the index value.
            if blog_post.id == index:
                requested_post = blog_post   # the selected article is saved as requested post to be displayed
        return render_template("post.html", post=requested_post, year=current_year, github=GITHUB,
                               linkedin=LINKEDIN, twitter=TWITTER)

    @app.route("/about")
    def about():
        """Details of the developer/blogger appear here"""
        return render_template("about.html", year=current_year, github=GITHUB, linkedin=LINKEDIN, twitter=TWITTER)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        """Blogger's contact details and mailto:"""
        if request.method == "POST":
            # the request.form.get is used to retrieve the data from the contact form
            user = request.form.get("name")
            email = request.form.get("email")
            mobile = request.form.get("phone")
            message = request.form.get("message")
            # SMTPlib is one of the ways to quickly send an email with python
            with smtplib.SMTP(host="smtp.office365.com:587") as connection:
                connection.starttls()   # starts the user session
                connection.login(user=MY_EMAIL, password=MY_PASS)   # inputs your username and pw
                # code below handles the body(subject included) of the email, afterwards the email is implicitly sent
                connection.sendmail(from_addr=MY_EMAIL, to_addrs=mail_list,
                                    msg=f"Subject: Notification from {user.title()} with email {email}.\n\n"
                                        f"Hello {name_of_dev.title()}, {user.title()} has left you a message.\n"
                                        f"Details below:\n"
                                        f"Name: {user.title()}\n"
                                        f"Email: {email}\n"
                                        f"Mobile: {mobile}\n"
                                        f"Message: {message}\n")
        return render_template("contact.html", year=current_year, github=GITHUB, linkedin=LINKEDIN, twitter=TWITTER)

    @app.route("/new-post", methods=["GET", "POST"])
    def post_article():
        """Handles new and edited posts/articles."""
        global date_, current_date
        date_ = datetime.now()  # gets the current date and time
        current_date = date_.strftime("%B %d, %Y")      # displays only the date as a string i.e. May 10, 2019
        new_blog_post = CreatePostForm()    # creates a form to input the details of a new article
        heading = "New Post"
        # After the user submits the form
        if new_blog_post.validate_on_submit():
            title_search = request.form.get("title")    # retrieves the article title
            print(title_search)
            post_to_edit = BlogPost.query.filter_by(title=title_search).first()   # searches the database for the title
            # if the title does not exist in the database, then it is a new article
            if post_to_edit is None:
                new_post = BlogPost(
                    title=request.form.get("title"),
                    subtitle=request.form.get("subtitle"),
                    date=current_date,
                    body=request.form.get("body"),
                    author=request.form.get("author"),
                    img_url=request.form.get("img_url"),
                    last_edit=current_date
                )
                db.session.add(new_post)
                print(f"{new_post.title} has been added to db.")
            else:      # if the title exists in the database, then it is an existing article
                # the requested_post variable stores the
                date_of_post = post_to_edit.date    # extracts the date the original article was posted
                db.session.delete(post_to_edit)     # deletes the original article from the database
                db.session.commit()     # saves so that the records don't conflict later causing an IntegrityError
                # The edit_record variable below stores a new record created with the updated data from the edit form
                edit_record = BlogPost(
                    title=request.form.get("title"),
                    subtitle=request.form.get("subtitle"),
                    date=date_of_post,
                    body=request.form.get("body"),
                    author=request.form.get("author"),
                    img_url=request.form.get("img_url"),
                    last_edit=current_date
                )
                db.session.add(edit_record)   # adds the edited record to the database
                print(f"{edit_record.title} record has been changed in the db.")
            db.session.commit()    # changes are saved
            return redirect("/")    # back to homepage to display the changes
        return render_template("make-post.html", new=new_blog_post, year=current_year, heading=heading)

    @app.route("/edit-post/<post_id>", methods=["GET", "POST"])
    def edit_post(post_id):
        """Opens the edit form to accept changes to be made by the user"""
        heading = "Edit Post"   # changes the heading from "New Post" to "Edit Post"
        # locates and retrieves the record to be edited from the database through the post id
        record_to_edit = BlogPost.query.get(post_id)
        # opens the form and populates the fields with the existing record to be edited
        edit_article = CreatePostForm(
            title=record_to_edit.title,
            subtitle=record_to_edit.subtitle,
            date=record_to_edit.date,
            body=record_to_edit.body,
            author=record_to_edit.author,
            img_url=record_to_edit.img_url,
            last_edit=record_to_edit.last_edit
        )
        edit_article.title.render_kw = {'readonly': True}  # sets the title field to read-only
        return render_template("make-post.html", heading=heading, post=record_to_edit, new=edit_article,
                               year=current_year, github=GITHUB, linkedin=LINKEDIN, twitter=TWITTER)

    @app.route("/delete/<post_id>")
    def delete_post(post_id):
        """Deletes an article from the database."""
        # locates and retrieves the record to be deleted from the database through the post id
        post_to_delete = BlogPost.query.get(post_id)
        db.session.delete(post_to_delete)   # deletes the record
        db.session.commit()     # saves changes to the database
        return redirect("/")    # reloads the homepage for changes to take effect

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
