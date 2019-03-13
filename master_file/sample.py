from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt 
from mysqlconnection import connectToMySQL
app = Flask(__name__)
app.secret_key = "keep your secrets"
bcrypt = Bcrypt(app) 
@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/newUserPage", methods=["POST"])
def newUserPage():
    # this checks whether the inputs of the user are valid.
    is_valid = True
    if len(request.form['first_name']) < 1:
    	is_valid = False
    	flash("Please enter a first name")
    if len(request.form['last_name']) < 1:
    	is_valid = False
    	flash("Please enter a last name")
    if len(request.form['user_email']) < 2:
    	is_valid = False
    	flash("Occupation should be at least 2 characters")
    if len(request.form['user_password']) < 8:
    	is_valid = False
    	flash("Password should be at least 8 characters")
    
    if is_valid:
    	# add user to database
        flash("User successfully added!")
        pw_hash = bcrypt.generate_password_hash(request.form['user_password'])  
        print(pw_hash) 
        mysql = connectToMySQL("logReg")
        query = "INSERT INTO users (first_name, last_name, user_email, user_password, created_at, updated_at) VALUES (%(fnm)s, %(lnm)s, %(em)s, %(pw)s, NOW(), NOW());"
        data = {
        "fnm": request.form["first_name"],
        "lnm": request.form["last_name"],
        "em": request.form["user_email"],
        "pw": pw_hash, 
        }
        new_user_id = mysql.query_db(query, data)
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
    query = "SELECT users.id, users.first_name, users.last_name FROM users WHERE users.id != %(user_id)s ORDER BY first_name ASC;"
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

    
    print("&"*80)
    # print(session)
    # print(drop_down)
    # print(user)
    print(display_message)

    # send message functionality
    # delete functionality
    
    # , send_message = send_message

    

    return render_template("wall.html", user = user, drop_down= drop_down, display_message = display_message)

@app.route("/logOut")
def logOut():
    if "user_id" in session:
        session.pop("user_id")
    flash("you have logged out!")

    return redirect("/")

@app.route("/logIn", methods=["POST"])
def logIn():
    mysql = connectToMySQL("logReg")
    query = "SELECT * FROM users WHERE user_email = %(ue)s;"
    data = {
        'ue': request.form['log_email']
    }
    user = mysql.query_db(query, data)
    if bcrypt.check_password_hash(user[0]['user_password'],request.form['log_password']):
        if 'user_id' not in session:
            session['user_id'] = user[0]['id']
        else:
            session['user_id'] = user[0]['id']
        flash("Successfully logged in!")
        return redirect("/createUser")
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

    #this is the send message functionality
    mysql = connectToMySQL("logReg")

    query = "INSERT INTO messages (message, sender_id, receiver_id, created_at, updated_at) VALUES (%(mg)s, %(sid)s, %(rid)s, NOW(), NOW());"
    data = {
        'mg': request.form['message'],
        'sid': session['user_id'],
        'rid': request.form['location']
    }
    send_message= mysql.query_db(query,data)
    

    print("*"*80)
    # print(session)
    # print(send_message)
    # print(user)
    # print(request.form['message'])
    # print(request.form['location'])

    
    return redirect("/createUser")

# @app.route("/delete_user", methods="post")
# def delete_users():
#     mysql = connectToMySQL("logReg")
#     data = {
#         "id":id
#     }

#     query = "DELETE FROM messages WHERE (id ="+str(data['id'])+");"
    
#     delete_messsage = mysql.query_db(query,data)

#     return redirect("/users")

@app.route("/delete_user/<id>")
def delete_users(id):
    mysql = connectToMySQL("logReg")
    data = {
        "id":id
    }
    query= "DELETE FROM messages WHERE (id ="+str(data['id'])+");"
    
    delete_user = mysql.query_db(query,data)

    print("@"*80)
    print(delete_user)

    return redirect("/createUser")

if __name__ == "__main__":
    app.run(debug=True)

