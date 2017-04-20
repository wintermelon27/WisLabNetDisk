#coding:utf-8
# from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, request, flash
from . import main
from .forms import NewFolderForm, UploadForm, AskExtractcodeForm
from .. import db
from ..models import *
import os
import time
from ..tools import *
from flask_uploads import UploadSet, configure_uploads, patch_request_class
from flask import current_app, send_from_directory
from werkzeug import secure_filename
from flask_login import current_user
import redis

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
    uploadform = UploadForm()
    if uploadform.validate_on_submit():
        filename = uploadform.upload.data.filename
        print(u"uploadFile: ", filename)
        upload_file_dir = root
        uploadform.upload.data.save(os.path.join(upload_file_dir, filename))
        return redirect(url_for('main.user_files', username=username, cur_dir=cur_dir))

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

    # 新建文件夹
    foldername = None
    newfform = NewFolderForm()
    if newfform.validate_on_submit():
        foldername = newfform.FolderName.data
        print (u"new folder name： ", foldername)
        newfform.FolderName.data = ''
        if not os.path.exists(os.path.join(root, foldername)):
            os.makedirs(os.path.join(root, foldername))
        return redirect(url_for('main.user_files', username=username, cur_dir=cur_dir))

    return render_template('myfiles/user_file.html', user=cuser, files=files_return_data,
                           dirs=dirs_return_data, up_dir=up_dir, cur_dir=cur_dir,
                           newfform=newfform, uploadform=uploadform)

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

@main.route('/files/delete_file/<username>/<path:folderpath>/x/<path:filepath>', methods=['GET'])
def delete_file(username, filepath, folderpath):
    filepath2 = filepath.split('/')
    file_real_path = current_app.config.get('UPLOAD_FOLDER')
    for i in range(0, len(filepath2)):
        file_real_path += "\\" + filepath2[i]
    os.remove(file_real_path)
    return redirect(url_for('main.user_files', username=username, cur_dir=folderpath))

@main.route('/files/delete_folder/<username>/<path:folderpath>/x/<path:delfolderpath>', methods=['GET'])
def delete_folder(username, folderpath, delfolderpath):
    delfolderpath2 = delfolderpath.split('/')
    delfolder_real_path = current_app.config.get('UPLOAD_FOLDER')
    for i in range(0, len(delfolderpath2)):
        delfolder_real_path += "\\" + delfolderpath2[i]
    os.removedirs(delfolder_real_path)
    return redirect(url_for('main.user_files', username=username, cur_dir=folderpath))

@main.route('/files/share/<username>/<path:filepath>')
def share_file(username, filepath):
    r = redis.Redis(host="localhost", port=6379, db=0)  # 连接redis服务
    ranstr = random_str()
    while r.exists(ranstr):
        ranstr = random_str()
    r.set(ranstr, filepath, ex=3600) # 3days 259200
    print(filepath)
    print(ranstr)
    filepath2 = filepath.split('/')
    sharefilename = filepath2[len(filepath2) - 1]
    return render_template('myfiles/share.html', id=ranstr, sharefilename=sharefilename)

@main.route('/files/share_private/<username>/<path:filepath>')
def share_private_file(username, filepath):
    r = redis.Redis(host="localhost", port=6379, db=0)  # 连接redis服务
    ranstr = random_str()
    while r.exists(ranstr):
        ranstr = random_str()
    rancode = random_str(4)     # 提取码
    r.rpush(ranstr, rancode)
    r.rpush(ranstr, filepath)
    r.rpush(ranstr, username)   # 分享人
    r.expire(ranstr, 3600)    # 设置过期时间 3days 259200
    print(filepath)
    print(ranstr)
    filepath2 = filepath.split('/')
    sharefilename = filepath2[len(filepath2) - 1]
    return render_template('myfiles/share_private.html', id=ranstr, extractcode=rancode, sharefilename=sharefilename)


@main.route('/share/files/<str_id>', methods=['GET', 'POST'])
def get_share_file(str_id):
    r = redis.Redis(host="localhost", port=6379, db=0)  # 连接redis服务
    if r.exists(str_id):
        if r.type(str_id) == "list":    # 私密分享
            rancode = r.lindex(str_id, 0)
            print("rancode: ", rancode)
            filepath = r.lindex(str_id, 1)
            print("filepath: ", filepath)
            share_user = r.lindex(str_id, 2)
            extractcodeform = AskExtractcodeForm()
            if extractcodeform.validate_on_submit():
                t_code = extractcodeform.extractcode.data
                print("t_code: ", t_code)
                if t_code == rancode:
                    filepath2 = filepath.split('/')
                    file_real_path = current_app.config.get('UPLOAD_FOLDER')
                    for i in range(0, len(filepath2) - 1):
                        file_real_path += "\\" + filepath2[i]
                    print("file_read_path: ", file_real_path)
                    filename = filepath2[len(filepath2) - 1]
                    print("fllename: ", filename)
                    return send_from_directory(unicode(file_real_path), unicode(filename), as_attachment=True)
                else:
                    flash(u'提取码错误！')
            return render_template('myfiles/ask_for_extractcode.html', askforextractcodeform=extractcodeform, shareuser=share_user)
        else:
            filepath = r.get(str_id)
            filepath2 = filepath.split('/')
            file_real_path = current_app.config.get('UPLOAD_FOLDER')
            for i in range(0, len(filepath2) - 1):
                file_real_path += "\\" + filepath2[i]
            print("file_read_path: ", file_real_path)
            filename = filepath2[len(filepath2) - 1]
            print("fllename: ", filename)
            return send_from_directory(unicode(file_real_path), unicode(filename), as_attachment=True)
    else:
        return render_template('myfiles/share_not_exist.html')