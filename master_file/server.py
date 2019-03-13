from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
import datetime
import re
from datetime import timedelta
from mysqlconnection import connectToMySQL
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+-]+@[a-zA-Z0-9._-]+.[a-zA-Z]+$')
#email does: characters "@" characters  "." characters
PASS_REGEX= re.compile(r"^(?=.[\d])(?=.[A-Z])(?=.[a-z])(?=.[@#$])[\w\d@#$]{8,}$")
#pass does: one upper one lower one number one special character 8 characters or more
USER_REGEX=re.compile(r'^(?=.{4,10}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$')
#username 4-10 characters long no . or _ the name


#make sure to import all needed resources
app = Flask(__name__)
app.secret_key = "keep your secrets"
bcrypt = Bcrypt(app) 
@app.route("/")
def index():
    #This renders the initial login and registration page
    return render_template("index.html")


@app.route("/newUserPage", methods=["POST"])
def newUserPage():
    # this checks whether the inputs of the user are valid.
    is_valid = True
    if len(request.form['first_name']) < 1 or not request.form['first_name'].isalpha():
    	is_valid = False
    	flash("Please enter a first name")
    if len(request.form['last_name']) < 1 or not request.form['last_name'].isalpha():
    	is_valid = False
    	flash("Please enter a last name")
    if len(request.form['user_name']) < 3 :
        is_valid = False
        flash("Username should have at least 4 characters")
    if not EMAIL_REGEX.match(request.form['user_email']):
    	is_valid = False
    	flash("please enter valid email")
    # if not PASS_REGEX.match(request.form['user_password']):
    if len(request.form['user_password']) < 3 :
    	is_valid = False
    	flash("Password should be include one upper case one lower case one number one special character and should be 8 characters or more")
    if request.form['user_password'] != request.form['confirm_password']:
        is_valid = False
        flash("Password does not match confirmation")
        
    
    if is_valid:
        # print("*"*80)
    	# add user to database
        flash("User successfully added!")
        # this makes sure that when the password is added to the database it is encrypted
        pw_hash = bcrypt.generate_password_hash(request.form['user_password'])  
        # print(pw_hash) 
        mysql = connectToMySQL("logReg")
        #this query allows you to enter first name, last name, username and email of the user
        query = "INSERT INTO users (first_name, last_name, user_name, user_email, user_password, created_at, updated_at) VALUES (%(fnm)s,%(lnm)s,%(un)s,%(em)s, %(pw)s, NOW(), NOW());"
        data = {
        "fnm": request.form["first_name"],
        "lnm": request.form["last_name"],
        "un": request.form['user_name'],
        "em": request.form["user_email"],
        "pw": pw_hash, 
        }
        new_user_id = mysql.query_db(query, data)
        # print("*"*80)
        # print(new_user_id)
        if "user_id" in session:
            session['user_id'] = new_user_id
        else:
            session['user_id'] = new_user_id
        return redirect("/createUser")
    if is_valid == False:
        return redirect("/")

@app.route("/createUser")
def success():
    #this is used to get the first name so I can display the welcome name
    mysql = connectToMySQL("logReg")
    query = "SELECT first_name FROM users WHERE id = %(user_id)s;"
    data = {
        'user_id': session['user_id']
    }
    user = mysql.query_db(query, data)

    #this is for the drop down.  this removes the current user so mesages cannot be sent to himself
    mysql = connectToMySQL("logReg")
    query = "SELECT users.id, users.first_name, users.last_name, users.user_name FROM users WHERE users.id != %(user_id)s ORDER BY first_name ASC;"
    data = {
        'user_id': session['user_id']
    }
    drop_down= mysql.query_db(query,data)

    # this is to show what messages the user has currently
    mysql = connectToMySQL("logReg")
    query = "SELECT users.first_name, users.last_name, messages.id, messages.message, messages.sender_id, messages.receiver_id, messages.created_at FROM messages JOIN users ON users.id = messages.sender_id WHERE receiver_id = %(user_id)s ORDER BY messages.created_at ASC;"
    data = {
        'user_id': session['user_id']
    }
    display_message= mysql.query_db(query,data)

    currentDT = datetime.datetime.now()
    # print (str(currentDT))
    
    # print("&"*80)
    # print(session)
    # print(drop_down)
    # print(user)
    # print(display_message)

    return render_template("wall.html", user = user, drop_down= drop_down, display_message = display_message, currentDT = currentDT)

@app.route("/logOut")
def logOut():
    if "user_id" in session:
        session.pop("user_id")
    flash("you have logged out!")

    return redirect("/")

@app.route("/logIn", methods=["POST"])
def logIn():
    is_valid = True
    # this checks if the length of the input is at least one character long
    # this also checks versus invalid email input, password input or both
    if len(request.form['log_email']) < 1 or len(request.form['log_password']) < 1:
    	is_valid = False
    	flash("email or password is invalid")
    
    if is_valid:
        mysql = connectToMySQL("logReg")
        query = "SELECT * FROM users WHERE user_email = %(ue)s;"
        data = {
            'ue': request.form['log_email'],
        }
        user = mysql.query_db(query, data)
        # print("*"*80)
        # print(user)
        
        if user == ():
            flash("email or password is invalid ")
            return redirect("/")

        # if again!!!

        if bcrypt.check_password_hash(user[0]['user_password'],request.form['log_password']):
            if 'user_id' not in session:
                session['user_id'] = user[0]['id']
            else:
                session['user_id'] = user[0]['id']
            flash("Successfully logged in!")
            # print("*"*80)
            # print(user)
            return redirect("/createUser")
        else:
            flash("email or password is invalid ")
            return redirect("/")

    if is_valid == False:
        flash("You could not be logged in")
        return redirect("/")

@app.route("/messaging", methods=["POST"])
def sendMessage():
    #this will get the receiver_id
    mysql = connectToMySQL("logReg")
    query = "SELECT id FROM users WHERE id = %(user_id)s;"
    data = {
        'user_id': session['user_id']
    }
    user = mysql.query_db(query, data)

    is_valid = True
    if len(request.form['message']) < 1:
    	is_valid = False
    	flash("Please enter a message")

    if is_valid:
        #this is the send message functionality
        mysql = connectToMySQL("logReg")
        query = "INSERT INTO messages (message, sender_id, receiver_id, created_at, updated_at) VALUES (%(mg)s, %(sid)s, %(rid)s, NOW(), NOW());"
        data = {
            'mg': request.form['message'],
            'sid': session['user_id'],
            'rid': request.form['location']
        }
        send_message= mysql.query_db(query,data)
        
        #troubleshooting
        # print("*"*80)
        # print(session)
        # print(send_message)
        # print(user)
        # print(request.form['message'])
        # print(request.form['location'])
        return redirect("/createUser")
    
    if is_valid == False:
        return redirect("/createUser")


@app.route("/delete_user/<id>")
def delete_messages(id):
    #delete messages to you from your home page
    mysql = connectToMySQL("logReg")
    data = {
        "id":id
    }
    query= "DELETE FROM messages WHERE (id ="+str(data['id'])+");"
    
    delete_user = mysql.query_db(query,data)

    # print("@"*80)
    # print(delete_user)

    return redirect("/createUser")

@app.route("/username", methods=['POST'])
def name_checker():
    # print("*"*90)
    #This checks if Name is available or taken
    found = False
    mysql = connectToMySQL('logReg')
    query = "SELECT users.user_name FROM logReg.users WHERE users.user_name = %(user)s;"
    data = { 'user': request.form['user_name'] }
    result = mysql.query_db(query, data)
    if result:
        found = True
    # print("*"*90)
    # print(result)
    return render_template('partials/username.html', found=found)

@app.route("/search_bar", methods=['POST'])
def search_bar():
    found = False
    mysql = connectToMySQL("logReg")
    query = "SELECT * FROM users WHERE user_name LIKE %%(name)s;"
    data = {
        "name" : request.form['search'] + "%"
    }
    results = mysql.query_db(query, data)
    if results:
        found = True
    print("*"*80)
    print(results)
    return render_template("partials/searchforusers.html", users = results, found=found)
    

if __name__ == "__main__":
    app.run(debug=True)

