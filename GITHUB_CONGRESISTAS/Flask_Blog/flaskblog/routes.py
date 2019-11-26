from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, OpinionForm, CongresistasSelectForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
from flaskblog.congresistas import Congresistas

@app.route("/")
@login_required
def home():
    df = Congresistas.getCongresistas()
    return render_template('congresistas.html', df = df)

@app.route("/wordcloud", methods=['GET', 'POST'])
def wordcloud():
    if request.method == 'POST':
        form = request.form
        congresista = form.get('congresistaSeleccionado')
        imagePath = Congresistas.mostrarWordCloud(congresista)
        return render_template('wordcloud.html', imagen = imagePath, twitter_user = congresista)
    
    return congresista


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    form = OpinionForm()
    if form.validate_on_submit():
        flash(f'Gracias por opinar, {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('account.html', title='Account', form=form)
