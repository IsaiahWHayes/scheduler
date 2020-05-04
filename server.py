from flask import Flask, redirect, render_template, request, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)
app.secret_key = "password please!"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
bcrypt = Bcrypt(app)

# ----- Index re-route
@app.route("/")
def index():
    return redirect("/login")

# ----- Index
@app.route("/login")
def login():
    return render_template('login.html')

# ----- Login form
@app.route("/login_form", methods = ["POST"])
def login_form():
    is_valid = True

    # email validation
    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter an email address")
    elif not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Valid email is required")

    # password validation
    if len(request.form['password']) < 8:
        is_valid = False
        flash("Password is incorrect")

    # if all of the above are entered and valid
    if is_valid:
        mysql = connectToMySQL('scheduler')
        query = "SELECT * FROM users WHERE email = %(email)s"
        data = {
            "email": request.form['email']
        }
        searched_user = mysql.query_db(query, data)

        if searched_user:
            if bcrypt.check_password_hash(searched_user[0]['password'], request.form['password']):
                session['user_id'] = searched_user[0]['id']
                session['users_fname'] = searched_user[0]['first_name']
                session['users_lname'] = searched_user[0]['last_name']
                return redirect("/schedule")
            else:
                is_valid = False
                flash("Email and/or password is incorrect")
                return redirect("/login")
        else:
            is_valid = False
            flash("User does not exist")
    return redirect("/login")

# ----- Registration 
@app.route("/register")
def register():
    return render_template('registration.html')

# ----- Registration form
@app.route("/registration_form", methods = ["POST"])
def registration_form():
    is_valid = True

    # first name validation
    if len(request.form['first_name']) < 1:
        is_valid = False
        flash("Please enter a first name")

    # last name validation
    if len(request.form['last_name']) < 1:
        is_valid = False
        flash("Please enter a last name")

    # email validation
    if len(request.form['email']) < 1:
        is_valid = False
        flash("Email is required")

    elif not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Must be a valid email address")

    else:
        mysql = connectToMySQL('scheduler')
        query = "SELECT * from users WHERE email = %(email)s"
        data = {
            "email": request.form['email']
        }
        searched_user = mysql.query_db(query, data)
        if searched_user:
            is_valid = False
            flash("Email is already in use")
    
    # password validation
    if len(request.form['password']) < 8:
        is_valid = False
        flash("Password must be at least 8 characters")

    if request.form['conf_pw'] != request.form['password']:
        is_valid = False
        flash("Passwords do not match")

    # if all of the above are entered and valid
    if is_valid:
        hashed_pw = bcrypt.generate_password_hash(request.form['password'])
        mysql = connectToMySQL('scheduler')
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fname)s, %(lname)s, %(email)s, %(pw)s, NOW(), NOW());"
        data = {
            "fname": request.form['first_name'],
            "lname": request.form['last_name'],
            "email": request.form['email'],
            "pw": hashed_pw
        }
        created_user = mysql.query_db(query, data)
        session['user_id'] = created_user
        session['users_fname'] = request.form['first_name']
        session['users_lname'] = request.form['last_name']
        return redirect("/schedule")
    return redirect("/register")

#  ----- Schedule dashboard
@app.route("/schedule")
def schedule():
    if 'user_id' not in session:
        return redirect('/')
    
    # searches for all tasks by the user in session
    mysql = connectToMySQL('scheduler')
    query = "SELECT tasks.id, tasks.users_id, tasks.task_name, overflow_tasks.id, overflow_tasks.users_id, overflow_tasks.tasks_id FROM tasks LEFT JOIN overflow_tasks ON tasks.id = overflow_tasks.tasks_id WHERE tasks.users_id = %(users_id)s AND overflow_tasks.tasks_id IS NULL"
    data = {
        "users_id": session['user_id']
    }
    users_tasks = mysql.query_db(query, data)

    # search for all overflow_tasks by the user in session
    mysql = connectToMySQL('scheduler')
    query = "SELECT tasks.id, tasks.users_id, tasks.task_name, overflow_tasks.users_id, overflow_tasks.tasks_id FROM tasks JOIN overflow_tasks ON tasks.id = overflow_tasks.tasks_id WHERE overflow_tasks.users_id = %(users_id)s"
    data = {
        "users_id": session['user_id']
    }
    users_overflow_tasks = mysql.query_db(query, data)
    return render_template('schedule.html', users_tasks = users_tasks, users_overflow_tasks = users_overflow_tasks)

# ----- New Task Form
@app.route("/new_task_form", methods = ["POST"])
def new_task_form():
    if 'user_id' not in session:
        return redirect('/')
    mysql = connectToMySQL('scheduler')
    query = "INSERT INTO tasks (users_id, task_name, start_time, end_time, location, category, contact, note, checklist, created_at, updated_at) VALUES (%(users_id)s, %(task_name)s, %(start_time)s, %(end_time)s, %(location)s, %(category)s, %(contact)s, %(note)s, %(list)s, NOW(), NOW());"
    data = {
        "users_id": session['user_id'],
        "task_name": request.form['task_name'],
        "start_time": request.form['start_time'],
        "end_time": request.form['end_time'],
        "location": request.form['location'],
        "category": request.form['category'],
        "contact": request.form['contact'],
        "note": request.form['note'],
        "list": request.form['checklist']
    }
    new_task = mysql.query_db(query, data)
    print(new_task)
    return redirect('/schedule')

# ----- Completed Task
@app.route("/schedule/completed/<task_id>")
def completed(task_id):
    if 'user_id' not in session:
        return redirect("/")

    # search and delete from "overflow tasks" table first
    mysql = connectToMySQL('scheduler')
    query = "SELECT * FROM overflow_tasks WHERE tasks_id = %(overflow_task)s"
    data = {
        "overflow_task": int(task_id)
    }
    overflowed_task = mysql.query_db(query, data)

    if overflowed_task:
        mysql = connectToMySQL('scheduler')
        query = "DELETE FROM overflow_tasks WHERE tasks_id = %(id)s;"
        data = {
            "id": int(task_id),
        }
        mysql.query_db(query, data)
    
    # search and delete from the 'Tasks' table
    mysql = connectToMySQL('scheduler')
    query = "DELETE FROM tasks WHERE id = %(id)s AND users_id = %(users_id)s;"
    data = {
        "id": int(task_id),
        "users_id": session['user_id']
    }
    mysql.query_db(query, data)
    return redirect("/schedule")

# ----- Adds a a task to the 'Overflow Tray'
@app.route("/overflow_tray/<task_id>")
def overflow(task_id):
    if 'user_id' not in session:
        return redirect("/")

    # searching for this specific task
    mysql = connectToMySQL('scheduler')
    query = "SELECT users.id, tasks.id, tasks.users_id, task_name, location, start_time, end_time, contact, note, checklist FROM users JOIN tasks ON tasks.users_id = users.id WHERE tasks.id = %(this_task)s;"
    data = {
        "this_task": int(task_id)
    }
    this_task = mysql.query_db(query, data)
    
    if this_task:
        mysql = connectToMySQL('scheduler')
        query = "SELECT * FROM overflow_tasks WHERE tasks_id = %(tasks_id)s;"
        data = {
            "tasks_id": int(task_id)
        }
        overflowed_task = mysql.query_db(query, data)

    if overflowed_task:
        pass
    else:
        mysql = connectToMySQL('scheduler')
        query = "INSERT INTO overflow_tasks (tasks_id, users_id, created_at, updated_at) VALUES (%(tasks_id)s, %(users_id)s, NOW(), NOW());"
        data = {
            "tasks_id": int(task_id),
            "users_id": session['user_id']
        }
        mysql.query_db(query, data)
    return redirect("/schedule")


# ----- Displays the details for a speicific task
@app.route("/task_details/<task_id>")
def details(task_id):
    if 'user_id' not in session:
        return redirect("/")

    # searching for all tasks to display in the "Task" pane
    mysql = connectToMySQL('scheduler')
    query = "SELECT * FROM tasks WHERE users_id = %(users_id)s"
    data = {
        "users_id": session['user_id']
    }
    users_tasks = mysql.query_db(query, data)

    # searching for this specific task to display it's details in the details pane
    mysql = connectToMySQL('scheduler')
    query = "SELECT users.id, tasks.id, tasks.users_id, task_name, location, start_time, end_time, contact, note, checklist FROM users JOIN tasks ON tasks.users_id = users.id WHERE tasks.id = %(this_task)s;"
    data = {
        "this_task": int(task_id)
    }
    this_task = mysql.query_db(query, data)
    session['detailed_task'] = int(task_id)
    print(this_task)
    return render_template("task_details.html", users_tasks = users_tasks, this_task = this_task[0])

# ----- Updates a previously created task
@app.route("/task_details/update", methods =["POST"])
def update_task():
    if 'user_id' not in session:
        return redirect("/")

    mysql = connectToMySQL('scheduler')
    query = "SELECT * FROM tasks WHERE tasks.id = %(this_task)s"
    data = {
        "this_task": session['detailed_task']
    }
    this_task = mysql.query_db(query, data)

    # edit the task
    mysql = connectToMySQL('scheduler')
    query = "UPDATE tasks SET task_name = %(task_name)s, start_time = %(start_time)s, end_time = %(end_time)s, location = %(location)s, category = %(category)s, contact = %(contact)s, note = %(note)s, checklist = %(list)s, created_at = NOW(), updated_at = NOW() WHERE tasks.id = %(this_task)s;"
    data = {
        "this_task": session['detailed_task'],
        "task_name": request.form['task_name'],
        "end_time": request.form['end_time'],
        "location": request.form['location'],
        "category": request.form['category'],
        "contact": request.form['contact'],
        "note": request.form['note'],
        "list": request.form['checklist']
    }
    mysql.query_db(query, data)
    return redirect('/schedule')

# ----- Logout
@app.route("/logout")
def logout():
    session.clear
    return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)