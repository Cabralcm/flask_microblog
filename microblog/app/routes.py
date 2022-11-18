from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user
from flask_login import logout_user, login_required
from app.models import User

from datetime import datetime

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm

# ...


# Index Page
@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [{
        "author" : {'username' : 'John'},
        'body' : 'Beautiful day in the land of Port!',
    },
    {
        'author' : {'username' : 'Susan'},
        'body' : 'That movie was lit!',
    }
    ]
    return render_template('index.html', title='Home', posts=posts)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Authenticate User
    if current_user.is_authenticated:
        return redirect(url_for('index')) #'index' == index function found in routes.py (this file)
    
    # Form object for LoginForm
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        email = User.query.filter_by(email=form.username.data.lower()).first()

        invalid_access_message = "Invalid username/email or password"

        if user is None and email is None:
            flash(invalid_access_message)
            return redirect(url_for('login'))
        if user is not None and not user.check_password(form.password.data):
            flash(invalid_access_message)
            return redirect(url_for('login'))
        if email is not None and not email.check_password(form.password.data):
            flash(invalid_access_message)
            return redirect(url_for('login'))    
        
        # Either User or Email are Not None, and their passwords are correct!
        # We want the User/Email object that is not None, and save it to the "user" variable
        user = user if user is not None else email
            
        #if user is None or not user.check_password(form.password.data):
        #    flash('Invalid username or password')
        #    return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next') #in this case, /login?next=/index, thus .get('next') will return '/index'

        #If no next_page, or next_page is an absolute path (i.e. network location is not empty), then default to index route function.
        if not next_page or url_parse(next_page).netloc != "": 
            next_page = url_for('index')
        
        # Only parsed if the network location (netloc) is a relative path
        return redirect(next_page)

        #flash('Login requested for user {}, remember_me={}'.format(
        #    form.username.data, form.remember_me.data))
        #return redirect( url_for('index') )
    return render_template('login.html', title='Sign In', form=form)

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register User
@app.route('/register', methods=['GET','POST'])
def register():

    if current_user.is_authenticated: #Redirect logged in user away from registration form
        return redirect( url_for('index') )

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data.lower(), email=form.email.data.lower())
        user.set_password(form.password.data.lower())
        db.session.add(user) #Add the user to the db session
        db.session.commit() #Commit the session to the database (this is to ensure data integrity and atomic operations)

        flash('Congratulations, you are now a registered user!')
        return redirect( url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

# User Page
@app.route('/user/<username>')
@login_required #only allow logged in users to access this page
def user(username):
    user = User.query.filter_by(username = username).first_or_404() #Better than first(), if no results, then sends a 404_error back to the client. 
    posts = [
        {'author' : user, 'body' : 'Test post #1'},
        {'author' : user, 'body' : 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

# Execute the decorated function right before the view function. View functions are above which are set for the different URLs (e.g. /user/<username>, /index, etc...)
@app.before_request #Decorator that runs the below function BELOW any request is sent from the server to the client
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit() #don't need db.session.add(current_user), since this user is already here! We only run this part if we have verified that the user exists.
    
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    
    # Submitting the form - That is, A POST request
    if form.validate_on_submit():
        current_user.username = form.username.data.lower() #extract the values from the EditProfileForm()
        current_user.about_me = form.about_me.data #extract the values from the EditProfileForm()
        db.session.commit() #commit the changes to the database
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    
    # Populate the fields on the form from the values from the current_user object
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    
    return render_template('edit_profile.html', title='Edit Profile', form=form)