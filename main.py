from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

today = date.today()
formatted_date = today.strftime('%B %d, %Y')

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


# Form configuration
class BlogForm(FlaskForm):
    class Meta:
        csrf = False  # Enable CSRF

    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    body = CKEditorField('Body')
    author = StringField('Author', validators=[DataRequired()])
    img_url = StringField('Image', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    result = db.session.execute(db.select(BlogPost))
    all_blogs_list = result.scalars()
    posts = []
    for post in all_blogs_list.all():
        posts.append(post)
    return render_template("index.html", all_posts=posts)


# TODO: Add a route so that you can click on individual posts.
@app.route('/post/')
def show_post():
    # TODO: Retrieve a BlogPost from the database based on the post_id
    query = request.args.getlist('post_id')
    print(query)
    print(type(query[0]))
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == int(query[0]))).scalar()
    print(requested_post.id)
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route('/add/', methods=["GET", "POST"])
def add_post():
    form_template = BlogForm()
    newpost = BlogPost()
    if form_template.validate_on_submit():
        print("True")
        print(type(form_template.title))
        newpost.title = str(form_template.title.data)
        newpost.subtitle = str(form_template.subtitle.data)
        newpost.author = str(form_template.author.data)
        newpost.body = str(form_template.body.data)
        newpost.date = str(formatted_date)
        newpost.img_url = str(form_template.img_url.data)
        with app.app_context():
            db.session.add(newpost)
            db.session.expire_on_commit = False
            blog_id = db.session.execute(db.select(BlogPost).where(BlogPost.title == newpost.title)).scalar().id
            db.session.commit()
        return redirect(url_for('show_post', post_id=blog_id))
    return render_template("make-post.html", form=form_template)


# TODO: edit_post() to change an existing blog post
@app.route('/edit/<post_id>', methods=["PATCH", "GET", "POST"])
def edit_post(post_id):
    edited_post = BlogPost()
    print(post_id)
    # Get post from DB
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == int(post_id))).scalar()

    form_template = BlogForm(
        id=requested_post.id,
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        body=requested_post.body,
        author=requested_post.author,
        img_url=requested_post.img_url
    )
    if form_template.validate_on_submit():
        with app.app_context():
            post_to_update = db.session.execute(db.select(BlogPost).where(BlogPost.id == int(post_id))).scalar()
            post_to_update.title = str(form_template.title.data)
            post_to_update.subtitle = str(form_template.subtitle.data)
            post_to_update.author = str(form_template.author.data)
            post_to_update.body = str(form_template.body.data)
            post_to_update.date = str(requested_post.date)
            post_to_update.img_url = str(form_template.img_url.data)
            db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template("make-post.html", form=form_template)


# TODO: delete_post() to remove a blog post from the database
@app.route("/delete/<post_id>", methods=["DELETE", "GET", "POST"])
def delete_post(post_id):
    result = db.get_or_404(ident=int(post_id), entity=BlogPost)
    with app.app_context():
        post_to_delete = db.session.execute(db.select(BlogPost).where(BlogPost.id == int(post_id))).scalar()
        db.session.delete(post_to_delete)
        db.session.commit()
    return redirect(url_for('get_all_posts'))





# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
