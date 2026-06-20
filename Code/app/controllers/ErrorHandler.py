from flask import render_template
from app import app


@app.errorhandler(404)
def page_not_found(e):
    metadata= {'title': '404 - Page Not Found',
               'error_code': '404',
               'description': 'This page does not exist / Not found...'}
    return render_template('error.html', metadata=metadata), 404

@app.errorhandler(403)
def page_not_found(e):
    metadata= {'title': '403 - Forbidden',
               'error_code': '403',
               'description': 'You do not have permission to access this page.'}
    return render_template('error.html', metadata=metadata), 403