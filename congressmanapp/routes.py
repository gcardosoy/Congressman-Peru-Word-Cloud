from flask import render_template, url_for, flash, redirect, request
from congressmanapp import app, db, bcrypt
from congressmanapp.forms import RegistrationForm, LoginForm, OpinionForm, LoginPublicForm
from congressmanapp.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
from congressmanapp.congresistas import Congresistas


@app.route("/")
@login_required
def home():
    return redirect(url_for('login'))


@app.route("/bancadas")
@login_required
def bancadas():
    df = Congresistas.getPartidos()
    return render_template('partidos.html', df=df)

@app.route("/bancadas/<string:bancada_id>")
@login_required
def congresistasPorBancada(bancada_id):
    df = Congresistas.getCongresistasPorBancada(bancada_id)
    return render_template('congresistas.html', df=df)


@app.route("/about")
@login_required
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('bancadas'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('bancadas'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/publicLogin", methods=['GET', 'POST'])
def loginpublic():
    if current_user.is_authenticated:
        return redirect(url_for('bancadas'))

    vemail = "public@gmail.com"
    vpassword = "123"

    user = User.query.filter_by(email=vemail).first()
    if user and bcrypt.check_password_hash(user.password, vpassword):
        login_user(user, remember=True)
        return redirect(url_for('bancadas'))

    return render_template('login.html', title='Login', form=LoginForm())

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


@app.route("/wordcloud", methods=['POST'])
@login_required
def wordcloud():
    if request.method == 'POST':
        form = request.form
        congresistaUser = form.get('congresistaSeleccionado')
        # imagePath = Congresistas.mostrarWordCloud(congresista)
        imagePath = Congresistas.getWordCloud(congresistaUser)
        print(imagePath)
        imagenComercio = Congresistas.getWordCloudComercio(congresistaUser)
        print(imagenComercio)

        congresistaInfo = Congresistas.getCongresista(congresistaUser)
        positivo, negativo = Congresistas.getSentimentValues(congresistaUser)

        return render_template('wordcloud.html', imagen=imagePath, form=OpinionForm(),
                               twitter_user=congresistaUser,
                               congresistaName=''.join(congresistaInfo["twitter_username"]),
                               congresistaImg=''.join(congresistaInfo["img"]),
                               pos=positivo,
                               neg=negativo,
                               imagenComercio = imagenComercio
                               )


@app.route("/wordcloud/<string:twitter_user>/", methods=['GET'])
@login_required
def wordcloudcongresista(twitter_user):
    if request.method == 'GET':
        congresistaUser = twitter_user
        print(congresistaUser)
        imagePath = "../../" + Congresistas.getWordCloud(congresistaUser)
        print(imagePath)

        imagenComercio = "../../"+Congresistas.getWordCloudComercio(congresistaUser)
        print(imagenComercio)

        congresistaInfo = Congresistas.getCongresista(congresistaUser)
        positivo, negativo = Congresistas.getSentimentValues(congresistaUser)

        return render_template('wordcloud.html', imagen=imagePath, form=OpinionForm(),
                               twitter_user=congresistaUser,
                               congresistaName=''.join(congresistaInfo["twitter_username"]),
                               congresistaImg=''.join(congresistaInfo["img"]),
                               pos=positivo,
                               neg=negativo,
                               imagenComercio=imagenComercio
                               )


@app.route("/enviaropinion", methods=['POST'])
@login_required
def enviaropinion():
    form = OpinionForm()
    newOpinion = form.opinion.data
    user = form.congresistaUser.data

    message = Congresistas.saveOpinion(user, newOpinion)
    flash(message, 'success')

    return redirect(url_for('wordcloudcongresista', twitter_user=user))
