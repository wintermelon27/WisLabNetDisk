# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User, UserFolderPath
from .forms import LoginForm, RegistrationForm
import os
from flask import current_app

def create_folder_for_registered_user(username):
    base_dir = current_app.config.get('UPLOAD_FOLDER')
    new_dir = base_dir + '\\' + username
    if os.path.exists(new_dir) is False:
        os.makedirs(new_dir)
    return new_dir

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash('You can login now.')

        new_dir = create_folder_for_registered_user(user.username)    # 为新用户新建存储文件的目录
        new_user_folder_path = UserFolderPath(username=user.username,
                                            folder_path=new_dir)
        db.session.add(new_user_folder_path)

        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()