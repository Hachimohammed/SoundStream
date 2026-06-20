from flask import render_template, session, redirect, url_for, request
from functools import wraps
from app import app
from app.services.LogService import LogService
from app.services.OrganisationService import OrganisationService
from app.services.UserService import UserService
import datetime

usr = UserService()
orga = OrganisationService()
log = LogService()

import bcrypt
####################################
## DECORATEURS D'AUTHENTIFICATION ##
####################################

def LoggedIn(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def reqrole(roles_needed):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Checkpoint logged in
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            # Then check if the role in session matches the required role
            if session.get('role') not in roles_needed:
                return "You do not have the correct role...", 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


################
## LOGIN PAGE ##
################
class LoginController:

    @app.route('/', methods=['GET', 'POST'])
    def empty():
        
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        metadata= {'title': 'Login'}
        
        if request.method == 'POST':
            # Récupération des données du formulaire
            username = request.form['username']
            password = request.form['password']
            
            # Recherche de l'utilisateur dans la base de données
            user = usr.findByUsername(username)
            
            if user:
                # Vérification du mot de passe -> à implémenter dans le UserDAO                
                hashed_pw = user.password.encode('utf-8') 
                input_pw = password.encode('utf-8')

                if bcrypt.checkpw(input_pw, hashed_pw):
                    # Authentification réussie renvoie vers la page d'organisation et création de la session
                    session['user_id'] = user.id_user
                    session['username'] = user.username
                    session['role'] = user.role
                    return redirect(url_for('organisation')) 
                
                else:
                    return render_template('login.html', metadata=metadata, error="Mot de passe incorrect")
            else:
                return render_template('login.html', metadata=metadata, error="Utilisateur inconnu")
        return render_template('login.html', metadata=metadata)
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))