from flask import Flask, request, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
import math


with open('config.json', 'r') as c:
    params =json.load(c)["params"]

local_server= True

app = Flask(__name__) # template_folder='templates')
app.secret_key = 'super-secret-key'
app.config.update(

    MAIL_SERVER= 'smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL='True',
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password'],

)

mail = Mail(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/codingthunder'

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI']=params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI']=params['prod_uri']

app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
db = SQLAlchemy(app)

class Contacts(db.Model):
    '''sno, name, email, phone_num, msg, date'''
    sno=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    email=db.Column(db.String(30), nullable=False)
    phone_num=db.Column(db.String(12), nullable=False)
    msg=db.Column(db.String(120), nullable=False)
    date=db.Column(db.String(12), nullable=True)


class Posts(db.Model):
    '''sno, title, slug, content, date'''
    sno=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(80), nullable=False)
    tagline=db.Column(db.String(250), nullable=False)
    slug=db.Column(db.String(30), nullable=False)
    content=db.Column(db.String(500), nullable=False)
    date=db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts= Posts.query.filter_by().all() #[0:3] 
    last= math.ceil(len(posts)/int(params['no_of_posts']))
    # posts=posts[]
    page=request.args.get('page')
    if (not str(page).isnumeric()):
       page=1
    page= int(page)	
    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    #pagination
    if (page==1):
        prev= "#"
        next= "/?page="+ str(page+1)
    elif (page==last):
        prev= "/?page="+ str(page-1)
        next= "#"
    else:
        prev= "/?page="+ str(page-1)
        next= "/?page="+ str(page+1)


    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)



@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params,post=post)
    #post=post passes the post variable above to the template we have mentioned


@app.route("/about")
def about():
    return render_template('about.html',  params=params)

@app.route("/admin", methods=['GET', 'POST'])
def admin():
        if ('user' in session and session['user']==params['admin_user']):
            posts = Posts.query.all()
            return render_template('admin.html', params=params, posts=posts)

        if request.method=='POST':
            username = request.form.get('uname') 
            userpass = request.form.get('pass')
            if (username==params['admin_user'] and userpass==params['admin_password']):
                session['user']=username
                posts = Posts.query.all()
                return render_template('admin.html', params=params, posts=posts)
        else:
            return render_template('login.html', params=params)
            
@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
        
        if ("user" in session and session['user']==params['admin_user']):
            if request.method =='POST':
                box_title = request.form.get('title')
                tline = request.form.get('tline')
                slug = request.form.get('slug')
                content = request.form.get('content')
                date = datetime.now()

                if sno=='0':
                    post=Posts(title=box_title, tagline=tline, slug=slug, content=content, date=date)
                    db.session.add(post)
                    db.session.commit()
                else:
                    post = Posts.query.filter_by(sno=sno).first()
                    post.title = box_title
                    post.tagline = tline
                    post.slug = slug
                    post.content = content
                    post.date = date
                    db.session.commit()
                    return redirect('/edit/'+sno)

            post = Posts.query.filter_by(sno=sno).first()
            return render_template('edit.html', params=params, post=post, sno=sno) 

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''ADD ENTRY TO THE DATABASE'''
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        entry = Contacts(name=name, email=email, phone_num=phone, msg=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message( sender='rohit',          
                           recipients=[params['gmail-user']],
                           subject='CONTACT FORM',
                           body= message+"\n"+"\n"+name+"\n"+"email: "+email+"\n"+"phone: "+phone  
                           )
    return render_template('contactt.html',  params=params)


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/admin')

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if ("user" in session and session['user']==params['admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/admin')



''' test route only check if the routes are working '''

@app.route("/test")
def test():
    return " rohit 007   "
    #return render_template('test.html')
    


if __name__ == "__main__":
    app.run(debug=True)
