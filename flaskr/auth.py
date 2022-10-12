import functools
import random
import yagmail as yagmail
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from.import utils
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')



@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email= request.form['email']
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error='email is required'
            
                
        if email != None and username!= None:
            temp = db.execute('SELECT * FROM activationlink WHERE email= ? AND state= ? AND username=?', (email, utils.U_UNCONFIRMED,username)
            ).fetchone()
            if temp != None:
                yag = yagmail.SMTP('uninortepruebasciclo3@gmail.com' , 'taougyvfvxjvfndp')
                print(email,username)
                yag.send(to= email, 
                subject= f"Bienvenido {username} a tu cuenta", 
                contents=f'<h1>Gracias por registrarte!</h1><br><h2>Ya puedes ingresar a la plataforma para enviar y leer tus mensajes.</h2>'
                'please click on this link ' + url_for('auth.activate', _external=True) + '?auth=' + number)            
                                
                flash('Please check in your registered email to activate your account')
                
        salt = hex(random.getrandbits(128))[2:]
        hashP=generate_password_hash(password)
        number = hex(random.getrandbits(512))[2:]  
       
        if error is None:
            try:
                db.execute("INSERT INTO activationlink (challenge, state,username, password,salt, email) VALUES (?, ?, ?, ?, ?, ?)",
                           (number, utils.U_UNCONFIRMED, username, hashP, salt, email),)
                db.commit()
                yag = yagmail.SMTP('uninortepruebasciclo3@gmail.com' , 'taougyvfvxjvfndp')
                print(email,username)
                yag.send(to= email, 
                subject= f"Bienvenido {username} a tu cuenta", 
                contents=f'<h1>Gracias por registrarte!</h1><br><h2>Ya puedes ingresar a la plataforma para enviar y leer tus mensajes.</h2>'
                'please click on this link ' + url_for('auth.activate', _external=True) + '?auth=' + number)            
                                
                flash('Please check in your registered email to activate your account')
            except db.IntegrityError:
                error = f"User {username} is already registered."
                return redirect(url_for("auth.register"))

            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/activate', methods=('GET', 'POST'))
def activate():
    try:
        if g.user:
            return redirect(url_for('inbox.received'))
        
        if request.method == 'GET': 
            number = request.args['auth'] 
            print(number)
            db = get_db()
            attempt = db.execute('SELECT * FROM activationlink WHERE challenge= ? AND state= ?', (number, utils.U_UNCONFIRMED)
            ).fetchone()

            if attempt is not None:
                db.execute('UPDATE activationlink SET state= ? WHERE id = ? ',(utils.U_CONFIRMED,attempt['id'])
                )
                db.execute('INSERT INTO user (username, password, salt, email) VALUES( ?, ?, ?, ?)',
            (attempt['username'], attempt['password'], attempt['salt'], attempt['email'])
                )
                db.commit()

        return redirect(url_for('auth.login'))
    except Exception as e:
        print(e)
        return redirect(url_for('auth.login'))
    
@bp.route('/forgot', methods=('GET', 'POST'))
def forgot():
    try:
        if g.user:
            return redirect(url_for('inbox.received'))
        
        if request.method == 'POST':
            email = request.form['email']
            
            if (not email or (not utils.isEmailValid(email))):
                error = 'Email Address Invalid'
                flash(error)
                return render_template('auth/forgot.html')

            db = get_db()
            user = db.execute(
                'SELECT * FROM user WHERE email=?',(email,)
            ).fetchone()
            #print(user[0],user[1],user[2])
            if user != None:
                number = hex(random.getrandbits(512))[2:]
                #print(number)
                db.execute('INSERT INTO forgotlink (userid, challenge, state) VALUES(?, ?, ?)',
                    (user['id'], number,utils.F_ACTIVE)                
                )
                db.commit()
                
                yag = yagmail.SMTP('uninortepruebasciclo3@gmail.com' , 'taougyvfvxjvfndp')
                print(email,user['username'])
                yag.send(to= email, 
                subject= f"Cambia a tu cuenta", 
                contents=f'<h1>Solicitud de cambio de contraseña!</h1><br>'
                'please click on this link ' + url_for('auth.change', _external=True) + '?auth=' + number)            
                                
                                
                flash('Please check in your registered email')
            else:
                error = 'Email is not registered'
                flash(error)            

        return render_template('auth/forgot.html')
    except:
        return render_template('auth/forgot.html')
    
@bp.route('/change', methods=('GET', 'POST'))
def change():
    try:
        if g.user:
            return redirect(url_for('inbox.received'))
        
        if request.method == ('GET'): 
            number = request.args['auth'] 
            print(number)
            db = get_db()
            attempt = db.execute(
                'SELECT * FROM forgotlink WHERE challenge=? AND state=?', (number, utils.F_ACTIVE)
            ).fetchone()
            #print(attempt[1])
            if attempt is not None:
                return render_template('auth/change.html', number=number)
        
        return render_template('auth/forgot.html')
    except:
        return render_template('auth/forgot.html')

@bp.route('/confirm', methods=('GET', 'POST'))
def confirm():
    try:
        if g.user:
            return redirect(url_for('inbox.received'))

        if request.method == 'POST': 
            password = request.form['password']
            password1 = request.form['password1']
            authid = request.form['authid']

            if not authid:
                flash('Invalid')
                return render_template('auth/forgot.html')

            if not password:
                flash('Password required')
                return render_template('auth/change.html', number=authid)

            if not password1:
                flash('Password confirmation required')
                return render_template('auth/change.html', number=authid)

            if password1 != password:
                flash('Both values should be the same')
                return render_template('auth/change.html', number=authid)

            if not utils.isPasswordValid(password):
                error = 'Password should contain at least a lowercase letter, an uppercase letter and a number with 8 characters long.'
                flash(error)
                return render_template('auth/change.html', number=authid)

            db = get_db()
            attempt = db.execute(
                'SELECT * FROM forgotlink WHERE challenge=? AND state= ?', (authid, utils.F_ACTIVE)
            ).fetchone()
            print(attempt,authid)
            if attempt != None:
                
                salt = hex(random.getrandbits(128))[2:]
                hashP = generate_password_hash(password)  
                print(attempt)
                db.execute('UPDATE forgotlink SET state= ? WHERE id = ? ',(utils.F_INACTIVE,attempt['id'])
                ) 
                db.execute(
                    'UPDATE user SET password= ?, salt=? WHERE id = ? ', (hashP, salt, attempt['userid'])
                )
                db.commit()
                return redirect(url_for('auth.login'))
            else:
                flash('Invalid')
                return render_template('auth/forgot.html')

        return render_template('auth/forgot.html')
    except:
        return render_template('auth/forgot.html')



@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view