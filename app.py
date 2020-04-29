from flask import Flask, render_template, request, flash, session, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash,check_password_hash
import os

app = Flask(__name__)
Bootstrap(app)
CKEditor(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SQLALCHEMY_DATABASE_URI']= "mysql+pymysql://username:password@localhost/blog_db"
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

class User(db.Model):
    firstname = db.Column(db.String(30))
    lastname = db.Column(db.String(30))
    username = db.Column(db.String(30), primary_key= True)
    password = db.Column(db.String(100))

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30))
    title = db.Column(db.String(20))
    body = db.Column(db.String(3000))

@app.route('/')
def index():
    blogs = Blog.query.order_by(Blog.id).all()
    return render_template('index.html',blogs=blogs)

@app.route('/register',methods = ['POST','GET'])
def register():
    if request.method == 'POST':
        Form = request.form
        result = User.query.filter_by(username=Form['username']).first()
        if result is None:
            user= User(firstname=Form['fname'], lastname=Form['lname'], username=Form['username'],password=generate_password_hash(Form['password']))
            db.session.add(user)
            db.session.commit()
            flash('Registered successfully!','success') 
            return redirect(url_for("index"))
        else:
            flash('Username not available!','warning')
    return render_template('register.html')

@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        Form = request.form
        user = User.query.filter_by(username=Form['username']).first()
        if user is None:
            flash('User not found!','warning')
        elif check_password_hash(user.password,Form['password']):
            session['user'] = user.firstname+' '+user.lastname
            session['username'] = user.username
            flash(f"Welcome {session['user']}",'success')
            return redirect(url_for('index'))
        else:
            flash('Password Incorrect!','danger')
    return render_template('login.html')
        
@app.route('/logout')
def logout():
    if session:
        session.clear()
        flash('Logged out!','info')
    return redirect(url_for('index'))

@app.route('/blogs/<id>')
def blogs(id):
    blog = Blog.query.get(id)
    # flash('ds','info')
    return render_template('blog.html',blog=blog)

@app.route('/my-blogs')
def my_blogs():
    if session.get('user'):
        blogs = Blog.query.filter_by(username=session['username']).all()
        return render_template('my_blogs.html',blogs=blogs)
    else:
        flash("You need to login first",'info')
        return redirect(url_for('login'))
    
@app.route('/write-blog',methods = ['POST','GET'])
def write_blog():
    if request.method == 'GET':
        if session.get('user'):
            return render_template('write_blog.html')
        else:
            flash("You have to login first",'info')
            return redirect(url_for('login'))
    else:
        Form = request.form
        blog = Blog(username=session['username'], title=Form['title'], body=Form['body'])
        db.session.add(blog)
        db.session.commit()
        flash("Posted Successfully!",'success')
        return redirect(url_for('index'))
    
@app.route('/edit-blog/<id>',methods = ['POST','GET'])
def edit_blog(id):
    blog=Blog.query.get(id)
    if blog.username != session.get('username'):
        flash("You are not authorized to access that section",'danger')
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('edit_blog.html',blog=blog)
    else:
        Form = request.form
        blog.title = Form['title']
        blog.body = Form['body']
        db.session.commit()
        flash("Edited Successfully!",'success')
        return redirect(url_for('my_blogs'))

@app.route('/delete-blog/<id>')
def del_blog(id):
    blog = Blog.query.get(id)
    if blog.username == session.get('username'):
        db.session.delete(blog)
        db.session.commit()
        flash("Blog Deleted!",'danger')
        return redirect(url_for('my_blogs'))
    else:
        flash("You are not authorized to access that section",'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)