import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from Database.DatabaseConfig import create_user,get_password_by_username,is_username_available
import Users.valid_username as valid_username


app = Flask(__name__)
app.secret_key = 'beehive'



@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        correct_password = get_password_by_username(username)
        if password == correct_password:  
            flash('Login successful!', 'success')
            return redirect(url_for("profile")) # this part is in under development
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
       
        first_name = request.form['firstname']

        last_name = request.form['lastname']

        email = request.form['email']

        username = request.form['username']

        password = request.form['password']

        confirm_password = request.form['confirm_password']

        account_created_at = None
        
        if valid_username.is_valid_username(username) == False:
            flash("Username doesn't follow the rules","danger")
        elif password != confirm_password:
            flash('Passwords do not match, please try again.', 'danger')
        else:
            if is_username_available(username):
                account_created_at = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                create_user(first_name,last_name,email,username,password,account_created_at)
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            else:
                flash('This Username already taken.','danger')

    return render_template("register.html")

    
if __name__ == '__main__':
    app.run(debug=True)
