from flask import Flask, render_template
from flask import redirect, url_for
from flask import request
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)


def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'), # host
        user=os.getenv('DB_USER'), # usuario
        password=os.getenv('DB_PASSWORD'), # clave
        db=os.getenv('DB_NAME'), # esquema al que se va a apuntar
        port=int(os.getenv('DB_PORT')), # puerto (int)
        cursorclass=pymysql.cursors.DictCursor # datos devueltos como diccionarios
    )
    return connection


@app.route('/')
def form():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('ObtenerEstudiantes')
            estudiantes = cursor.fetchall()
            print(estudiantes)
    finally:
        conn.close()
    return render_template('estudiantes.html', estudiantes=estudiantes)


@app.route('/eliminar/<dni>', methods=['POST'])
def eliminar_estudiante(dni):
    conn = get_db_connection() # conectarme
    try:
        with conn.cursor() as cursor: # ejecutar con el cursor
            cursor.callproc('EliminarEstudiante', [dni]) # llamar al SP con el valor dni
            conn.commit() # hacer un commit
    finally:
        conn.close() # cerrar la conexión

    return redirect(url_for('form'))  # Asegúrate que este nombre coincide con tu ruta


@app.route('/crear', methods=['GET', 'POST'])
def crear_estudiante():
    mensaje = None # si no estamos bajo método POST

    if request.method == 'POST':
        dni = request.form['dni']
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.callproc('CrearAlumno', [dni, nombre, apellido_paterno, apellido_materno])

                # Si el procedimiento retorna un SELECT con el mensaje
                mensaje = cursor.fetchone()
                if mensaje and 'Mensaje' in mensaje:
                    mensaje = mensaje['Mensaje']
                else:
                    mensaje = "Estudiante creado correctamente"

                conn.commit()
        except pymysql.MySQLError as err:
            mensaje = f"Error: {err}"
        finally:
            conn.close()

    return render_template('crear.html', mensaje=mensaje)


app.run(debug=True, port=5002)