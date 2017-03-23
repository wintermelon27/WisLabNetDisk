# -*- coding: utf-8 -*-
# from datetime import datetime
from flask import render_template, session, redirect, url_for, abort
from . import main
# from .forms import NameForm
from .. import db
from ..models import *
import os
from ..tools import *

@main.route('/', methods=['GET', 'POST'])
def index():
    '''form = NameForm()
    if form.validate_on_submit():
    # xxx
        return redirect(url_for('.index'))
    return render_template('index.html', form=form, name=session.get('name'),
                            known=session.get('known', False),
                            current_time=datetime.utcnow())'''

    return render_template('index.html')

@main.route('/user/<username>')
def user(username):
    cuser = User.query.filter_by(username=username).first()
    if cuser is None:
        abort(404)
    return render_template('user.html', user=cuser)

@main.route('/files/<username>')
def user_files(username):
    cuser = User.query.filter_by(username=username).first()
    if cuser is None:
        abort(404)

    file_dir = UserFolderPath.query.filter(username == username).first().folder_path
    for root, dirs, files in os.walk(file_dir):
        print(root)  # 当前目录路径
        print(dirs)  # 当前路径下所有子目录
        print(files)  # 当前路径下所有非目录子文件

    data = []
    for i in files:
        tmp = {}
        tmp['filename'] = i
        print(file_dir + "\\" + i)
        tmp['filesize'] = getDocSize(file_dir + "\\" + i)
        print(tmp['filesize'])
        data.append(tmp)
    return render_template('myfiles/user_file.html', user=cuser, files=data)