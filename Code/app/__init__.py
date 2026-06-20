from flask import Flask, session, redirect, url_for, request
import os
from datetime import timedelta

app = Flask(__name__, static_url_path='/static')

app.secret_key = '5f352379324c22463451387a0aec5d2f'


app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

@app.before_request
def make_session_permanent_and_check_timeout():
    session.permanent = True
    
    public_routes = ['login', 'forgotten', 'static']
    if request.endpoint in public_routes:
        return
    # Si l'utilisateur est connecté on vérifie l'inactivité
    if 'username' in session:
        import datetime
        now = datetime.datetime.now()
        last_active = session.get('last_active')
        if last_active:
            last_active = datetime.datetime.fromisoformat(last_active)
            if (now - last_active).total_seconds() > 900:  # 15 min
                session.clear()
                return redirect(url_for('login'))
        session['last_active'] = now.isoformat()

from app.controllers import *