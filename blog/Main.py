from flask import Flask,render_template,flash,redirect,url_for,session,request
from flask_mysqldb import MySQL 
from passlib.hash import sha256_crypt 
from functools import wraps
from Forms import *

 
app = Flask(__name__) 
app.secret_key="blog"

app.config["MYSQL_HOST"] ="localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "blog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

def login_required(f):
    @wraps(f)
    def decorator_function(*args,**kwargs):
        if "logged_in" in session:
            return f(*args,**kwargs)
        else:
            flash("You must be logged in to view this page...","danger")
            return redirect(url_for("login"))
    return decorator_function

def admin_required(f):
    @wraps(f)
    def decor_function(*args,**kwargs):
        if "user_items" in session:
            if session["user_items"]["user_type"] == 2:
               return f(*args,**kwargs)
            else:
               flash("You must be an admin to view this page....","danger")
               return redirect(url_for("login"))
    return decor_function


@app.route("/")
def main():
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles"
    result=cursor.execute(sorgu)
    if result >0:
        articles=cursor.fetchall()
        length = len(articles)
        sorgu_categories = "Select * from categories"
        cursor.execute(sorgu_categories)
        categories=cursor.fetchall()
        return render_template("home.html",articles=articles,categories=categories,length = length)
    else:
        return render_template("home.html")
    

@app.route("/about")
def about():
    cursor=mysql.connection.cursor()
    sorgu="Select * from articles where id = %s"
    result = cursor.execute(sorgu,(1,))
    if result > 0:
        about = cursor.fetchone()
        return render_template("about.html",about=about)
    else:
        return render_template("about.html")

@app.route("/login",methods=["GET","POST"])
def login():
    form = request.form
    if(request.method=="POST"):
        email=form.get("email")
        password = form.get("psw")
        cursor = mysql.connection.cursor()
        sorgu= "Select * from users where email = %s"
        result=cursor.execute(sorgu,(email,))

        if result>0:
            data=cursor.fetchone()
            real_passw=data['password']
            
            if sha256_crypt.verify(password,real_passw):
                flash("You have successfully logged in..","success")
                session["logged_in"] = True
                user_dict = {"id": data["id"],"name": data["name"],"surname":data["surname"],"user_type":data["user_type"],
                            "email":email,"user_name":data["user_name"]}
                session["user_items"] = user_dict
                

                return redirect(url_for("main"))     
            else:
                flash("You entered your password incorrectly","danger")
                return redirect(url_for("login"))
        else:
            flash("There is no such email....","danger")
            return redirect(url_for("login"))

    return render_template("login.html",form=form)

@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if(request.method=="POST"  and form.validate()):
        name=form.name.data
        surname=form.surname.data
        user_name=form.username.data
        email=form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        cursor = mysql.connection.cursor()
        sorgu_email = "Select * from users where email = %s"
        e_mail = cursor.execute(sorgu_email,(email,))
        if e_mail > 0:
            mysql.connection.commit()
            cursor.close()
            flash("You are already registered, you can login...","success")
            return redirect(url_for("login"))

        sorgu_uname = "Select * from users where user_name = %s"
        user = cursor.execute(sorgu_uname,(user_name,))
        if user > 0:
            mysql.connection.commit()
            cursor.close()
            flash("This username is being used, please enter a new username...","danger")
            return redirect(url_for("register"))
        else:
            sorgu= "Insert into users(name,surname,password,email,user_name) VALUES(%s,%s,%s,%s,%s) "
            cursor.execute(sorgu,(name,surname,password,email,user_name))
            mysql.connection.commit()
            cursor.close()
            flash("You is registered successfully...","success")
            return redirect(url_for("login"))
    else:
        return render_template("register.html",form=form)



@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/article/<string:id>")
def article(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * from articles where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0:
        article_info= cursor.fetchone()
        return render_template("article.html",article=article_info)
    else:
        return render_template("article.html")


@app.route("/addArticle",methods=["GET","POST"])
@login_required
@admin_required
def add_article():
    form=ArticleForm(request.form)
    if request.method=="POST" and form.validate:
        title = form.title.data
        author = form.author.data
        content = form.content.data
        category = form.category.data
        about = form.about.data
        user = session["user_items"]["id"]
        cursor = mysql.connection.cursor()
        sorgu="Insert into articles (name,author,category,content,about,user_id) VALUES(%s,%s,%s,%s,%s,%s)"
        cursor.execute(sorgu,(title,author,category,content,about,user))
        mysql.connection.commit()
        sorgu_id = "Select * from articles where name= %s"
        cursor.execute(sorgu_id,(title,))
        info=cursor.fetchone()
        id = info["id"]
        #sorgu_category = "Select * from articles where name= %s"
        #cursor.execute(sorgu_category,(category,))
        #info=cursor.fetchone()
        cursor.close()
        flash("Article is saved successfully!...","success")
        return redirect(url_for("article", id=id))
    return render_template("addarticle.html",form=form)

@app.route("/editArticle/<string:id>",methods=["GET","POST"])
@login_required
@admin_required
def edit_article(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where  id = %s and user_id = %s "
        result = cursor.execute(sorgu,(id,session["user_items"]["id"]))
        if result == 0:
            flash("There is no article or you can not edit the article!!","danger")
            session.clear()
            return redirect(url_for("main"))
        else:
            article_info=cursor.fetchone()
            form =ArticleForm()
            form.title.data =  article_info["name"]
            form.content.data =  article_info["content"]
            form.category.data =  article_info["category"]
            form.about.data =  article_info["about"]
            cursor.close()
            return render_template("editArticle.html",form = form)
    else:
        form = ArticleForm(request.form)
        newtitle=form.title.data
        newcategory = form.category.data
        newcontent = form.content.data
        newabout = form.about.data
        sorgu2="Update articles Set name = %s, category = %s, content = %s, about = %s where id=%s"
        cursor= mysql.connection.cursor()
        cursor.execute(sorgu2,(newtitle, newcategory, newcontent, newabout, id))
        mysql.connection.commit()
        cursor.close()
        flash("Article is edited successfully","success")
        return redirect(url_for("article", id=id))

@app.route("/deleteArticle/<string:id>")
@login_required
@admin_required
def delete_article(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * from articles where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0:
        sorgu2="Delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("main"))
    else:
        flash("There is no article or you can not delete the article!!","danger")
        return redirect(url_for("main"))

@app.route("/editProfile",methods=["GET","POST"])
@login_required
def edit_profile():
    if request.method == "GET":
        form =RegisterForm()
        form.name.data = session["user_items"]["name"]
        form.surname.data = session["user_items"]["surname"]
        form.email.data = session["user_items"]["email"]
        form.username.data = session["user_items"]["user_name"]
        return render_template("editProfile.html",form = form)

    elif(request.method=="POST"):
        form = RegisterForm(request.form)
        newname=form.name.data
        newsurname = form.surname.data
        newemail = form.email.data
        newusername = form.username.data
        newpassword = sha256_crypt.encrypt(form.password.data)
        cursor= mysql.connection.cursor()
        sorgu_update="Update users Set name = %s, surname = %s, password = %s, email = %s, user_name = %s where id=%s"
        cursor.execute(sorgu_update,(newname, newsurname, newpassword, newemail, newusername, session["user_items"]["id"]))
        mysql.connection.commit()
        cursor.close()
        session.clear()
        flash("Your profile is edited, please login again!","success")
        return redirect(url_for("login"))

@app.route("/deleteProfile")
@login_required
def delete_profile():
        cursor= mysql.connection.cursor()
        sorgu_delete="Delete from users where id = %s"
        cursor.execute(sorgu_delete,(session["user_items"]["id"],))
        mysql.connection.commit()
        cursor.close()
        session.clear()
        flash("Your profile is deleted successfully!","success")
        return redirect(url_for("main"))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logout!","success")
    return redirect(url_for("main"))


@app.errorhandler(404)
def error(e):
    return render_template("error.html")

if __name__ =="__main__": 
    app.run(debug = True) 
 