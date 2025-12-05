from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///todo.db"
db=SQLAlchemy(app)
class TODO(db.Model):
    sn=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(20),nullable=False)
    desc=db.Column(db.String(49),nullable=False)
    date=db.Column(db.DateTime,default= datetime.now)

    def __repr__(self):
        return (f"{self.title}---> {self.desc}")
@app.route('/',methods=["GET","POST"])
def insert():
    alltodo=TODO.query.all()
    if request.method=="POST":
        if request.form["title"] and request.form["desc"]:
            todo=TODO(title=request.form["title"],desc=request.form["desc"])
            db.session.add(todo)
            db.session.commit()
            return redirect('/')
    return render_template("index.html",alltodo=alltodo)
@app.route("/delete/<int:sn>")
def delete(sn):
    faltodo=TODO.query.get(sn)
    db.session.delete(faltodo)
    db.session.commit()
    return redirect("/")
@app.route("/update/<int:sn>",methods=['GET','POST'])
def update(sn):
    todo=TODO.query.filter_by(sn=sn).first()
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