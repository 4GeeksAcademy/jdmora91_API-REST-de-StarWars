import os
from flask_admin import Admin
from models import db, User, Planet, Character, Favorite
from flask_admin.contrib.sqla import ModelView

class FavoriteModelView(ModelView):
    column_auto_select_related = True
    column_list = ['id', 'user', 'planet', 'character']  

class UserModelView(ModelView):
    column_auto_select_related = True
    column_list = ['id', 'email' , 'password', 'is_active', 'favorites']    

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Add your models here
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(ModelView(Planet, db.session))
    admin.add_view(ModelView(Character, db.session))
    admin.add_view(FavoriteModelView(Favorite, db.session))