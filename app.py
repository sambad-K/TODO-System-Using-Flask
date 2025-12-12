from flask import Flask,render_template,redirect,url_for,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import Email,Length,DataRequired,ValidationError
from passlib.hash import sha256_crypt
from flask_login import LoginManager,login_user,logout_user,current_user,UserMixin,login_required
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret'
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(100))
    def __init__(self,email,password):
        self.email=email
        self.password=sha256_crypt.hash(password)
    def checkpw(self,password):
        return sha256_crypt.verify(password,self.password)
class Register(FlaskForm):
    email=StringField("email",validators=[DataRequired(),Email(),Length(min=20)],render_kw={'placeholder':"email"})
    password=StringField("password",validators=[DataRequired(),Length(max=20)],render_kw={'placeholder':"password"})
    submit=SubmitField("Register")
class Login(FlaskForm):
    email=StringField("email",validators=[DataRequired(),Email(),Length(min=20)],render_kw={'placeholder':"email"})
    password=StringField("password",validators=[DataRequired(),Length(max=20)],render_kw={'placeholder':"password"})
    submit=SubmitField("Login")





class TODO(db.Model):
    sn=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(20),nullable=False)
    desc=db.Column(db.String(49),nullable=False)
    date=db.Column(db.DateTime,default= datetime.now)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    def __repr__(self):
        return (f"{self.title}---> {self.desc}")
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)
@app.route('/register',methods=['POST','GET'])
def register():
    form=Register()
    if form.validate_on_submit():
        user=User(email=form.email.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
@app.route('/login',methods=['GET','POST'])
def login():
    form=Login()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            if user.checkpw(form.password.data):
                login_user(user)
                return redirect(url_for('insert'))
            else:
                form.password.errors.append('Wrong password')
        else:
            form.password.errors.append("Wrong user")
    return render_template('login.html',form=form)
@app.route('/',methods=["GET","POST"])
@login_required
def insert():
    alltodo=TODO.query.filter_by(user_id=current_user.id).all()
    if request.method=="POST":
        if request.form["title"] and request.form["desc"]:
            todo=TODO(title=request.form["title"],desc=request.form["desc"],user_id=current_user.id)
            db.session.add(todo)
            db.session.commit()
            return redirect('/')
    return render_template("index.html",alltodo=alltodo)
@app.route("/delete/<int:sn>")
@login_required
def delete(sn):
    faltodo=TODO.query.filter_by(sn=sn,user_id=current_user.id).first()
    db.session.delete(faltodo)
    db.session.commit()
    return redirect("/")
@app.route("/update/<int:sn>",methods=['GET','POST'])
@login_required
def update(sn):
    todo=TODO.query.filter_by(sn=sn,user_id=current_user.id).first()
    if request.method=="POST":
        title=request.form['title']
        des=request.form['desc']
        todo.title=title
        todo.desc=des
        todo.date=datetime.now()
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
    return render_template("update.html",todo=todo)
# main driver function
if __name__ == '__main__':
    app.run(debug=True,port=2000)