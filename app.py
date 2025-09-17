from flask import Flask,render_template, request,session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()
import os
from werkzeug.utils import secure_filename
import math
import json
from datetime import datetime
from flask_mail import Mail

with open('config.json','r') as c:
    params = json.load(c)['params']

app = Flask(__name__)

app.secret_key = 'super-secret-key'

app.config['UPLOAD_FOLDER']= 'C:\\Users\\Harsh\\Desktop\\StockMarket Blog\\static'

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'harshpandya677@gmail.com',
    MAIL_PASSWORD = 'uabbtzwdpdeitkas'
)
mail =Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:Harsh%402004%40@localhost/stock"
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(30),nullable=False)
    phone_num = db.Column(db.String(10),nullable=False)
    message = db.Column(db.String(200),nullable=False)
    date = db.Column(db.String(10),nullable=True)

class Posts(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(20),nullable=False)
    tagline = db.Column(db.String(30),nullable=False)
    slug = db.Column(db.String(10),nullable=False)
    content = db.Column(db.String(30),nullable=False)
    date = db.Column(db.String(20),nullable=False)
    img_url = db.Column(db.String(100),nullable=True)

@app.route('/')
def home():
    posts=Posts.query.filter_by().all()
    last = math.ceil(len(posts)/3)

    page = request.args.get('page')

    if not str(page).isnumeric():
        page = 1
    page = int(page)

    posts = posts[(page-1)*3:(page-1)*3+3]

    if page==1:
        next = '/?page=' + str(page+1)
        prev = '#'
    elif page==last:
        next = '#'
        prev = '/?page=' + str(page-1)
    else:
        next = '/?page='+ str(page+1)
        prev = '/?page='+ str(page-1)

    return render_template('index.html',next=next,prev=prev,posts=posts,params=params)

@app.route('/about')
def about():
    return render_template('about.html',params=params)

@app.route('/posts')
def posts():
    posts=Posts.query.filter_by().all()
    return render_template('posts.html',params=params,posts=posts)

@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',post=post,params=params)

@app.route('/edit/<string:sno>',methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user']=='Admin':
        if request.method=='POST':
            title = request.form['title']
            tagline = request.form['tagline']
            slug = request.form['slug']
            content = request.form['content']
            img_url = request.form['img_url']
            date = datetime.now()

            if sno=='0':
                post = Posts(title=title,tagline=tagline,slug=slug,content=content,img_url=img_url,date=datetime.now())
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.tagline = tagline
                post.slug = slug
                post.content = content
                post.img_url = img_url
                post.date = date
                db.session.commit()
                return redirect('/dashboard') 

    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html',post=post,params=params)

@app.route('/delete/<string:sno>')
def delete(sno):
    if 'user' in session and session['user']=='Admin':
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')



@app.route('/contact',methods=['GET','POST'])
def contact():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        phone_num = request.form['phone_num']
        message = request.form['message']
        contact = Contacts(name=name,email=email,phone_num=phone_num,message=message,date = datetime.now())
        db.session.add(contact)
        db.session.commit()

        mail.send_message('New message from' + name,
                          sender = email,
                          recipients = ['harshpandya677@gmail.com'],
                          body = message + '\n'+phone_num
                          
                          )
        flash("Message is sent successfullly","success")

    return render_template('contact.html',params=params)

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if 'user' in session and session['user'] == 'Admin':
        posts = Posts.query.all()
        return render_template('dashboard.html',posts=posts,params=params)

    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        if username=='Admin' and password=='harsh123':
            session['user'] = 'Admin'
            posts = Posts.query.all()
            return render_template('dashboard.html',posts=posts,params=params)
        
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    if 'user' in session and session['user'] == 'Admin':
        session.pop('user')
        return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True , port=7000)


