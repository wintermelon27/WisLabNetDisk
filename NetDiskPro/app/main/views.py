# -*- coding: utf-8 -*-
# from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, request
from . import main
# from .forms import NameForm
from .. import db
from ..models import *
import os
import time
from ..tools import *
from forms import UploadForm
from flask_uploads import UploadSet, configure_uploads, patch_request_class
from flask import current_app, send_from_directory
from werkzeug import secure_filename
from flask_login import current_user

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config.get('ALLOWED_EXTENSIONS')

@main.route('/files/<username>/<path:cur_dir>', methods=['GET', 'POST'])
def user_files(username, cur_dir):
    print("cur_dir: " + cur_dir)
    cur_dir_list = cur_dir.split('/')
    print("cur_dir_list: " + str(cur_dir_list))
    cuser = User.query.filter_by(username=username).first()
    if cuser is None:
        abort(404)
    file_dir = UserFolderPath.query.filter_by(username=username).first().folder_path

    tmp = u""
    for i in range(1, len(cur_dir_list)):
        tmp += unicode('\\')
        tmp += unicode(cur_dir_list[i])

    print type(tmp), tmp

    file_dir += tmp
    for root, dirs, files in os.walk(file_dir):
        print("root: " + root)  # 当前目录路径
        print(dirs)  # 当前路径下所有子目录
        print(files)  # 当前路径下所有非目录子文件
        break

    files_return_data = []
    for i in files:
        tmp = {}
        tmp['filename'] = i
        # print(file_dir + "\\" + i)
        tmp['filesize'] = getDocSize(file_dir + "\\" + i)
        # print(tmp['filesize'])

        mtime = time.ctime(os.path.getmtime(file_dir + "\\" + i))
        # print mtime
        tmp['modifytime'] = mtime

        files_return_data.append(tmp)

    dirs_return_data = []
    for i in dirs:
        tmp = {}
        tmp['dirname'] = i
        tmp['dirlink'] = cur_dir + '/' + i
        mtime = time.ctime(os.path.getmtime(file_dir + "\\" + i))
        tmp['modifytime'] = mtime
        dirs_return_data.append(tmp)

    # 上传
    if request.method == 'POST':
        ufile = request.files['file']
        if ufile and allowed_file(ufile.filename):
            # filename = secure_filename(ufile.filename)
            filename = ufile.filename
            upload_file_dir = root
            ufile.save(os.path.join(upload_file_dir, filename))

    # 返回上一级
    up_dir = u""
    if len(cur_dir_list) != 1:
        for i in range(0, len(cur_dir_list) - 1):
            if i != 0:
                up_dir += unicode('/')
            up_dir += unicode(cur_dir_list[i])
        print (u"up_dir: ", up_dir)
    else:
        up_dir = cur_dir

    return render_template('myfiles/user_file.html', user=cuser, files=files_return_data,
                           dirs=dirs_return_data, up_dir=up_dir, cur_dir=cur_dir)

@main.route('/files/download/<path:filepath>', methods=['GET'])
def download_file(filepath):
    print("filepath: " + filepath)
    filepath2 = filepath.split('/')
    file_real_path = current_app.config.get('UPLOAD_FOLDER')
    for i in range(0, len(filepath2) - 1):
        file_real_path += "\\" + filepath2[i]
    print("file_read_path: ", file_real_path)
    filename = filepath2[len(filepath2) - 1]
    print("fllename: ", filename)
    return send_from_directory(file_real_path, filename, as_attachment=True)
    # return render_template('index.html')