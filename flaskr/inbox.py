from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required,g
from flaskr.db import get_db

bp = Blueprint('inbox', __name__)



@bp.route('/')
def index():
    messages = f'<h1>Bienvenido</h1>'
     
    return render_template('inbox/index.html', messages=messages)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
     if request.method == 'POST':
        from_id = g.user['id']
        username = request.form['to_username']
        to_subject = request.form['subject']
        body = request.form['body']
        error = None
        db = get_db()
        if not to_subject:
            error = 'Subject is required.'            
           
        userto= db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        if userto is None:
            error = 'Recipient does not exist'
     
        if error is not None:
            flash(error)            
    
        else:
            capturaruserto=userto[0]
            db = get_db()
            db.execute(
                'INSERT INTO message ( from_id,to_id,subject, body)'
                ' VALUES (?, ?, ?, ?)',
                ( from_id,capturaruserto,to_subject, body,)
            )
            db.commit()
            return redirect(url_for('inbox.index'))
        
     return render_template('inbox/create.html')
    
 
@bp.route('/received')
@login_required
def received():
    from_id = g.user['id']
    db = get_db()
    userto= db.execute('SELECT * FROM user WHERE id= ?', (from_id,)).fetchone()
    print(userto[0],from_id,g.user['id'])
    
    messages = db.execute('SELECT p.id, from_id,to_id,u.username as dest,s.username as rem,'
                          +'body, created,subject,body FROM message p '+
                          'JOIN user u ON p.to_id = u.id JOIN user s ON s.id=p.from_id WHERE to_id = ? ORDER BY created DESC',(str(from_id))).fetchall()  
    return render_template('inbox/received.html', messages=messages)

