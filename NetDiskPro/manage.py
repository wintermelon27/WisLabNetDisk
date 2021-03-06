#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from app import create_app, db
from app.models import User, Role, UserFolderPath
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = create_app(os.getenv('development') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, UserFolderPath=UserFolderPath)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()