from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'
load_dotenv()

# Configuración de conexión a MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

#----seccion login manager----

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor inicia sesión para acceder a esta página."

#Modelo de usuario
class User(UserMixin):
    def __init__(self, id,nombre,telefono, email, password):
        self.id = id
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.password = password
        
@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre, telefono, email, contraseña FROM usuarios WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user[0], user[1], user[2],user[3],user[4])
    return None

###rutas###
@app.route('/')
def inicio():
    data = obtener_datos()  # Trae el diccionario con los valores de las dos tablas
    jugadores_datos = data.get('tabla_jugadores', {}).get('datos', [])
    labels1 = [row[0] for row in jugadores_datos]
    values1 = [row[1] for row in jugadores_datos]
    
    equipos_datos = data.get('tabla_equipos', {}).get('datos2', [])
    labels2 = [row[0] for row in equipos_datos]
    values2 = [row[1] for row in equipos_datos]
    
    if 'username' in session:
        return redirect(url_for('inicio_usuario', labels1=labels1, values1=values1, labels2=labels2, values2=values2))
        
    return render_template('inicio.html', labels1=labels1, values1=values1, labels2=labels2, values2=values2)

@app.route('/inicio_usuario')
def inicio_usuario():
    data = obtener_datos()
    jugadores_datos = data.get('tabla_jugadores', {}).get('datos', [])
    labels1 = [row[0] for row in jugadores_datos]
    values1 = [row[1] for row in jugadores_datos]
    
    equipos_datos = data.get('tabla_equipos', {}).get('datos2', [])
    labels2 = [row[0] for row in equipos_datos]
    values2 = [row[1] for row in equipos_datos]
    
    if 'username' in session:
        return render_template('inicio_usuario.html', labels1=labels1, values1=values1, labels2=labels2, values2=values2)
    return redirect(url_for('inicio', labels1=labels1, values1=values1, labels2=labels2, values2=values2))

@app.route('/iniciousuario')
def iniciousuario():
    return render_template('inicio_usuario.html')

@app.route('/redirect_to_iniciousuario')
def redirect_to_iniciousuario():
    return redirect(url_for('iniciousuario'))

@app.route('/noticia')
def noticia():
    return render_template('noticia.html')

@app.route('/redirect_to_noticia')
def redirect_to_noticia():
    return redirect(url_for('noticia'))

@app.route('/noticia2')
def noticia2():
    return render_template('noticia2.html')

@app.route('/redirect_to_noticia2')
def redirect_to_noticia2():
    return redirect(url_for('noticia2'))

@app.route('/noticia3')
def noticia3():
    return render_template('noticia3.html')

@app.route('/redirect_to_noticia3')
def redirect_to_noticia3():
    return redirect(url_for('noticia3'))

@app.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')

@app.route('/redirect_to_estadisticas')
def redirect_to_estadisticas():
    return redirect(url_for('estadisticas'))

### Login ###
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and user[4] == contraseña:  # Suponiendo que la contraseña está en el índice 4
            user_obj = User(user[0], user[1], user[2], user[3], user[4])
            login_user(user_obj)  # Para iniciar el usuario en flask login
            
            session['username'] = user[1]  # Suponiendo que 'nombre' está en el índice 1
            return redirect(url_for('inicio_usuario'))
        else:
            flash('Correo electrónico o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    logout_user()
    return redirect(url_for('inicio'))

### Registro ###
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (nombre, email, telefono, contraseña) VALUES (%s, %s, %s, %s)",
                    (nombre, email, telefono, contraseña))
        mysql.connection.commit()
        cur.close()

        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

## Voto jugador ##
@app.route('/carga_voto_jugador', methods=['GET', 'POST'])
def carga_voto_jugador():
    if request.method == 'POST':
        voto = request.form['voto_jugador']
        votante = current_user.id

    usuario_ya_voto = verificar_voto_jugador(current_user.id)
    if not usuario_ya_voto:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jugadores (nombre_jugador, id_votante) VALUES (%s, %s)",
                    (voto, votante))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('inicio_usuario'))

## Voto equipo ##
@app.route('/carga_voto_equipo', methods=['GET', 'POST'])
def carga_voto_equipo():
    if request.method == 'POST':
        voto = request.form['voto_equipo']
        votante = current_user.id

    usuario_ya_voto = verificar_voto_equipo(current_user.id)
    if not usuario_ya_voto:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO equipos (nombre_equipo, id_votante) VALUES (%s, %s)",
                    (voto, votante))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('inicio_usuario'))

### Verificar si usuario ha votado ###
def verificar_voto_jugador(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_votante FROM jugadores WHERE id_votante = %s", (id,))
    existing_user = cur.fetchone()
    cur.close()
    return existing_user is not None

### Verificar si usuario ha votado ###
def verificar_voto_equipo(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_votante FROM equipos WHERE id_votante = %s", (id,))
    existing_user = cur.fetchone()
    cur.close()
    return existing_user is not None

## Obtener datos de BDD ##
def obtener_datos():
    cur = mysql.connection.cursor()
    # Estadísticas de jugadores
    cur.execute('SELECT nombre_jugador, COUNT(*) FROM jugadores GROUP BY nombre_jugador')
    datos_jugadores = cur.fetchall()
    # Estadísticas de equipos
    cur.execute('SELECT nombre_equipo, COUNT(*) FROM equipos GROUP BY nombre_equipo')
    datos_equipos = cur.fetchall()

    cur.close()

    # Organizar los datos en un diccionario
    tabla = {
        'tabla_jugadores': {
            'datos': datos_jugadores  # Datos de los jugadores como lista de tuplas
        },
        'tabla_equipos': {
            'datos2': datos_equipos  # Datos de los equipos como lista de tuplas
        }
    }

    return tabla

if __name__ == '__main__':
    app.run(debug=True)
