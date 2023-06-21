import os
from flask import Flask, render_template, request
import pymysql
from pymysql import IntegrityError
from markupsafe import Markup

user_type = user_email = user_name = ""
app = Flask(__name__)

@app.route("/profile",methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        global user_type, user_email
        user_type = request.form["u_type"]
        user_email = request.form["email"]
        password = request.form["psw"]
        
        try:
            conn = pymysql.connect(host="localhost", user="root", password="", db="se_project")
            cur = conn.cursor()
            cur.execute("insert into users (email,password,type) values (%s,%s,%s)",(user_email,password,user_type))
            conn.commit()
        except IntegrityError:
            return "<html><body><h1>Email is already registered.</h1></body></html>"
        except:
            return "<html><body><h1>Some error occured. Please try later.</h1></body></html>"
        else:
            return render_template('EditProfile.html', u_type=user_type)
        finally:
            cur.close()
            conn.close()

@app.route("/fp",methods=['POST','GET'])
def set_profile():
    if request.method == 'POST':
        global user_name
        user_name = request.form["name"].title()
        dob = request.form['dob']
        ph = request.form['ph']
        addr = request.form['addr']
        
        try:
            conn = pymysql.connect(host="localhost", user="root", password="", db="se_project")
            cur = conn.cursor()

            cur.execute("update users set name = %s, dob = %s, contact = %s, address = %s where email = %s",(user_name,dob,ph,addr,user_email))
            conn.commit()

            if user_type == 'Student':
                college = request.form['College'].title()
                degree = request.form['deg'].title()
                branch = request.form['branch'].title()
                cur.execute("update users set college = %s, degree = %s, branch = %s where email = %s",(college,degree,branch,user_email))
            elif user_type == 'Faculty':
                college = request.form['College'].title()
                post = request.form['post'].title()        
                cur.execute("update users set college = %s, post = %s where email = %s",(college,post,user_email))
            else:
                company = request.form['Company'].title()
                post = request.form['post'].title()
                cur.execute("update users set company = %s, post = %s where email = %s",(company,post,user_email))
            conn.commit()
        except:
            return "<html><body><h1>Some error occured. Please try later.</h1></body></html>"
        else:
            return render_template("Fp.html",name= user_name)
        finally:
            cur.close()
            conn.close()

@app.route("/fp1",methods=['POST','GET'])
def login():
    u_type = request.form["u_type"]
    email = request.form["email"]
    password = request.form["psw"]
            
    try:
        conn = pymysql.connect(host="localhost", user="root", password="", db="se_project")
        cur = conn.cursor()
        cur.execute("select password,name,type from users where email =%s",(email))
        record = cur.fetchone()
        if record:
            if password == record[0] and u_type == record[2]:
                global user_type, user_email, user_name
                user_type = u_type;
                user_email = email;
                user_name = record[1]
                return render_template("Fp.html",name = user_name)
            else:
                return "<html><body><h1>Invalid user type or password.</h1></body></html>"
        else:
            return "<html><body><h1>Email not registered.</h1></body></html>"
    except:     
        return "<html><body><h1>Error connecting to database. Please try later.</h1></body></html>"
    finally:
        cur.close()
        conn.close()

@app.route("/view-profile",methods=['POST','GET'])
def viewProfile():
    try:
        conn = pymysql.connect(host="localhost", user="root", password="", db="se_project")
        cur = conn.cursor()
        
        if user_type == 'Student':
            cur.execute("select name, dob, degree, branch, college, contact, address from users where email =%s",(user_email))
            record = cur.fetchone()
            return render_template('ShowProfile.html', u_type = 'Student', name=record[0], dob=record[1].strftime("%m-%d-%Y"), degree=record[2], branch=record[3], college=record[4], contact=record[5], address=record[6])
        elif user_type == 'Faculty':
            cur.execute("select name, dob, post, college, contact, address from users where email =%s",(user_email))
            record = cur.fetchone()
            return render_template('ShowProfile.html', u_type = 'Faculty', name=record[0], dob=record[1].strftime("%m-%d-%Y"), post=record[2], college=record[3], contact=record[4], address=record[5])
        else:
            cur.execute("select name, dob, post, company, contact, address from users where email =%s",(user_email))
            record = cur.fetchone()
            return render_template('ShowProfile.html', u_type = 'Faculty', name=record[0], dob=record[1].strftime("%m-%d-%Y"), post=record[2], company=record[3], contact=record[4], address=record[5])
    except:
        return "<html><body><h1>Error connecting to database. Please try later.</h1></body></html>"
    finally:
        cur.close()
        conn.close()
        
@app.route("/edit-profile",methods=['POST','GET'])
def editProfile():
    return render_template('EditProfile.html', u_type=user_type)

@app.route("/add-project",methods=['POST','GET'])
def addProject():
    return render_template("AddProject.html")
@app.route("/add-project1",methods=['POST','GET'])
def addProject1():
    if request.method == 'POST':
        names = request.form["names"].title()
        topic = request.form["topic"].title()
        domain = request.form["domain"]
        year = request.form["year"]
        desc = request.form["desc"]
        keywords = request.form["keyw"]
        future = request.form["future"]
        awards = request.form["award"]
        contacts = request.form["contact"]
        
        try:
            conn = pymysql.connect(host="localhost", user="root", password="", db="se_project")
            cur = conn.cursor()
            
            desc = desc.replace("\n","</br>")
            future = future.replace("\n","</br>")
            awards = awards.replace("\n","</br>")
            cur.execute("insert into projects (creators, topic, domain, year, description, keywords, future_scope, awards, contacts, added_by) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(names, topic, domain, year, desc, keywords, future, awards, contacts, user_email))
            conn.commit()
            
            desc = Markup(desc)
            future = Markup(future)
            awards = Markup(awards)
            return render_template("ProjectPage.html",names=names, topic=topic, domain=domain, year=year, description=desc, keywords=keywords, future_scope=future, awards=awards, contacts=contacts)
        except:
            return "<html><body><h1>Error connecting to database. Please try later.</h1></body></html>"
        finally:
            cur.close()
            conn.close()
    
@app.route("/fp2",methods=['POST','GET'])
def home():
    if request.method == 'POST':
        return render_template("Fp.html",name= user_name)

@app.route("/search-project",methods=['POST','GET'])
def searchProject():
    return render_template("Search.html")

@app.route("/show-project",methods=['POST','GET'])
def show_poject():
    if request.method == 'POST':
        topic = request.form["topic"].lower()
            
        try:
            conn = pymysql.connect(host="localhost", user="root", password="", db="se_project")
            cur = conn.cursor()
                
            cur.execute("select * from projects where topic = %s",(topic))
            
            record = cur.fetchone()
            
            
            
            if record:
                record = list(record)
                for i in range(len(record)):
                    record[i] = Markup(record[i])
                return render_template("ProjectPage.html",names=record[0], topic=record[1], domain=record[2], year=record[3], description=record[4], keywords=record[5], future_scope=record[6], awards=record[7], contacts=record[8])
            else:
                similar_projects = []

                cur.execute("select topic from projects")
                a=cur.fetchall()
                
                topic = topic.split(" ")
                words_found = 0
                for (b,) in a:
                    for i in topic:
                        c = b.lower().split(" ")
                        if i in c:
                            words_found+=1
                    
                    if words_found >=  len(topic)/2:
                        similar_projects.append(b)
                    words_found=0
            
                return "<html><body><h1>No such project found. Similar projects: <br> " + str(similar_projects).strip("[]").replace(", ","</br> ")+"</h1></body></html>"
        except:
            return "<html><body><h1>Error connecting to database. Please try later.</h1></body></html>"
        finally:
            cur.close()
            conn.close()
        
@app.route("/sign-out",methods=['POST','GET'])
def signout():
    if request.method == 'POST':
        try:
            conn = pymysql.connect(host="localhost", user="root", password="", db="se_project")
            cur = conn.cursor()
               
            cur.execute("delete from users where email = %s",(user_email))
            cur.execute("delete from projects where added_by = %s",(user_email))
            conn.commit()
            
            return render_template("SignUp.html")
                
        except:
            return "<html><body><h1>Error connecting to database. Please try later.</h1></body></html>"


app.run()