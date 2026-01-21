import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User, Post, Media, Comment, Follower


def setup_admin(app):
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(Media, db.session))
    admin.add_view(ModelView(Comment, db.session))
    admin.add_view(ModelView(Follower, db.session))
