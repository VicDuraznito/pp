from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL,MySQLdb
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required


from flask_wtf.csrf import generate_csrf


import mysql.connector

from config import config

# Models:
from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User



app = Flask(__name__)


csrf = CSRFProtect()

db = MySQL(app)



login_manager_app = LoginManager(app)


app.secret_key = 'tu_clave_secreta_aqui'



app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER' ]= 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'












                        #-----------------------   LOGIN ------------------------



@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


@app.route('/')
def index():
    return redirect(url_for('login'))



# Llamar a la función para probar la conexión



# @app.route('/login', methods=['GET', 'POST'])
# def login():
    
#     if request.method == 'POST':


        
#         print(request.form['username'])
#         print(request.form['password'])
        
#         user = User(0, request.form['username'], request.form['password'])
    
#         print("Before login call")
#         logged_user = ModelUser.login(db, user)
#         print("After login call")

#         if logged_user != None:
#             if logged_user.password:
#                 login_user(logged_user)
#                 return redirect(url_for('home'))
#             else:
#                 flash("Invalid password...")
#                 print('no contraseña')
#                 return render_template('auth/login.html')
#         else:
#             flash("User not found...")
#             print('no usuario')
#             return render_template('auth/login.html')
#     else:
#         return render_template('auth/login.html')

from flask_wtf.csrf import generate_csrf

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Invalid password...")
                return render_template('auth/login.html', csrf_token=generate_csrf())
        else:
            flash("User not found...")
            return render_template('auth/login.html', csrf_token=generate_csrf())
    else:
        return render_template('auth/login.html', csrf_token=generate_csrf())





@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html')







                    #--------------------   INVENARIO DE REFACCIONES    -------------------


@app.route('/inventario', methods=['GET'])
@login_required
def listar():
    cur = db.connection.cursor()
    try:
        cur.execute("SELECT * FROM refacciones")
        usuarios = cur.fetchall()
        #print(usuarios)  # Agrega esta línea para imprimir los datos
        return render_template('inventario.html', usuarios=usuarios)
    except Exception as e:
        print(f"Error executing SQL: {e}")
    finally:
        cur.close()

    return "Error al recuperar datos del inventario"



@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('query', '')

    cur = db.connection.cursor()

    # Utiliza placeholders para evitar inyecciones de SQL
    sql = """
        SELECT * 
        FROM refacciones 
        WHERE 
            
            pieza LIKE %s OR 
            codigo LIKE %s OR 
            marca LIKE %s OR 
            medida LIKE %s OR
            descripcion LIKE %s OR 
            CAST(stock AS CHAR) LIKE %s OR 
            CAST(compra AS CHAR) LIKE %s OR 
            CAST(venta AS CHAR) LIKE %s
    """
    cur.execute(sql, ( '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%' , '%' + query + '%' , '%' + query + '%', '%' + query + '%'))

    resultados = cur.fetchall()

    cur.close()

    return render_template('inventario.html', query=query, usuarios=resultados)





@app.route('/agregar_refaccion', methods=['GET', 'POST'])
def agregar_refaccion():
    if request.method == 'POST':
        # Get data from the form
        pieza = request.form.get('pieza')
        codigo = request.form.get('codigo')
        marca = request.form.get('marca')
        medida = request.form.get('medida')
        descripcion = request.form.get('descripcion')
        stock = request.form.get('stock')
        compra = request.form.get('compra')
        venta = request.form.get('venta')
        

        # Validate the data (add your own validation logic here)

        # Insert the new data into the database
        cur = db.connection.cursor()
        try:
            sql = """
                INSERT INTO refacciones (pieza, codigo, marca, medida, descripcion, stock, compra, venta  )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (pieza, codigo, marca, medida, descripcion, stock, compra, venta))
            db.connection.commit()
            flash('Data added successfully!', 'success')
            return redirect(url_for('listar'))  # Redirect to the history page
        except Exception as e:
            db.connection.rollback()
            flash(f'Error adding data: {e}', 'danger')
        finally:
            cur.close()

    return render_template('inventario.html')  # Create a new HTML template for adding data


@app.route('/actualizar_refaccion/<int:id>', methods=['GET', 'POST'])
def actualizar_refaccion(id):
    if request.method == 'POST':
        # Obtener los datos actualizados desde el formulario
        pieza = request.form.get('pieza')
        codigo = request.form.get('codigo')
        marca = request.form.get('marca')
        medida = request.form.get('medida')
        descripcion = request.form.get('descripcion')
        stock = request.form.get('stock')
        compra = request.form.get('compra')
        venta = request.form.get('venta')
        # Repite estos pasos para los demás campos

        # Actualizar los campos en la base de datos
        cur = db.connection.cursor()
        try:
            sql = """
                UPDATE refacciones
                SET pieza=%s, codigo=%s, marca=%s, medida=%s, descripcion=%s, stock=%s, compra=%s, venta=%s
                WHERE id=%s
            """
            cur.execute(sql, (pieza, codigo, marca, medida, descripcion, stock, compra, venta, id))
            db.connection.commit()
            flash('Registro actualizado correctamente.', 'success')
            return redirect(url_for('listar'))
        except Exception as e:
            db.connection.rollback()
            flash(f'Error al actualizar el registro: {e}', 'danger')
        finally:
            cur.close()

    # Obtener el registro actual para mostrar en el formulario
    cur = db.connection.cursor()
    try:
        cur.execute("SELECT * FROM refacciones WHERE id=%s", (id,))
        mostrar = cur.fetchone()
        return render_template('actualizar_refaccion.html', mostrar=mostrar)
    except Exception as e:
        print(f"Error executing SQL: {e}")
    finally:
        cur.close()

    return "Error al recuperar datos para actualizar"

@app.route('/eliminar_refaccion/<int:id>', methods=['GET', 'POST'])
def eliminar_refaccion(id):
    cur = db.connection.cursor()
    try:
        cur.execute("DELETE FROM refacciones WHERE id=%s", (id,))
        db.connection.commit()
        flash('Registro eliminado correctamente.', 'success')
    except Exception as e:
        db.connection.rollback()
        flash(f'Error al eliminar el registro: {e}', 'danger')
    finally:
        cur.close()

    return redirect(url_for('listar'))




                        #------------------HISTORIAL DE CARRO------------------------




# @app.route('/agregar_historial', methods=['GET', 'POST'])
# def agregar_historial():
#     if request.method == 'POST':
#         # Get data from the form
#         model = request.form.get('model')
#         brand = request.form.get('brand')
#         engine = request.form.get('engine')
#         refacciones = request.form.get('refacciones')
#         service = request.form.get('service')
#         status = request.form.get('status')
#         payment = request.form.get('payment')
#         cost = request.form.get('cost')
#         entry_date = request.form.get('entry_date')
#         exit_date = request.form.get('exit_date')
#         mechanic = request.form.get('mechanic')

#         # Validate the data (add your own validation logic here)

#         # Insert the new data into the database
#         cur = db.connection.cursor()
#         try:
#             sql = """
#                 INSERT INTO autorecord (model, brand, engine, refacciones, service, status, payment, cost, entry_date, exit_date, mechanic)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#             cur.execute(sql, (model, brand, engine, refacciones, service, status, payment, cost, entry_date, exit_date, mechanic))
#             db.connection.commit()
#             flash('Data added successfully!', 'success')
#             return redirect(url_for('historial'))  # Redirect to the history page
#         except Exception as e:
#             db.connection.rollback()
#             flash(f'Error adding data: {e}', 'danger')
#         finally:
#             cur.close()

#     return render_template('record.html')  # Create a new HTML template for adding data


@app.route('/agregar_historial', methods=['POST'])
def agregar_historial():
    if request.method == 'POST':
        # Obtener los datos del formulario
        model = request.form.get('model')
        brand = request.form.get('brand')
        engine = request.form.get('engine')
        refacciones = request.form.get('refacciones')
        service = request.form.get('service')
        status = request.form.get('status')
        payment = request.form.get('payment')
        cost = request.form.get('cost')
        entry_date = request.form.get('entry_date')
        exit_date = request.form.get('exit_date')
        mechanic = request.form.get('mechanic')
        
        # Insertar el nuevo registro en la tabla autorecord
        cur = db.connection.cursor()
        try:
            sql = """
                INSERT INTO autorecord (model, brand, engine, refacciones, service, status, payment, cost, entry_date, exit_date, mechanic)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (model, brand, engine, refacciones, service, status, payment, cost, entry_date, exit_date, mechanic))
            db.connection.commit()
            
            # Restar uno del stock de refacciones
            cur.execute("UPDATE refacciones SET stock = stock - 1 WHERE pieza = %s", (refacciones,))
            db.connection.commit()
            
            flash('Registro agregado correctamente.', 'success')
            return redirect(url_for('historial'))
        except Exception as e:
            db.connection.rollback()
            flash(f'Error al agregar el registro: {e}', 'danger')
        finally:
            cur.close()

    return redirect(url_for('historial'))



# Asumiendo que tienes un objeto 'autorecord' para manejar la base de datos

# @app.route('/actualizar_registro/<int:id>', methods=['GET', 'POST'])
# def actualizar_registro(id):
#     if request.method == 'POST':
#         # Obtener los datos actualizados desde el formulario
#         model = request.form.get('model')
#         brand = request.form.get('brand')
#         engine = request.form.get('engine')
#         refacciones = request.form.get('refacciones')
#         service = request.form.get('service')
#         status = request.form.get('status')
#         payment = request.form.get('payment')
#         cost = request.form.get('cost')
#         entry_date = request.form.get('entry_date')
#         exit_date = request.form.get('exit_date')
#         mechanic = request.form.get('mechanic')
#         # Repite estos pasos para los demás campos

#         # Actualizar los campos en la base de datos
#         cur = db.connection.cursor()
#         try:
#             sql = """
#                 UPDATE autorecord
#                 SET model=%s, brand=%s, engine=%s, refacciones=%s, service=%s, status=%s, payment=%s, cost=%s, entry_date=%s, exit_date=%s, mechanic=%s
#                 WHERE id=%s
#             """
#             cur.execute(sql, (model, brand, engine, refacciones, service, status, payment, cost, entry_date, exit_date, mechanic, id))
#             db.connection.commit()
#             flash('Registro actualizado correctamente.', 'success')
#             return redirect(url_for('historial'))
#         except Exception as e:
#             db.connection.rollback()
#             flash(f'Error al actualizar el registro: {e}', 'danger')
#         finally:
#             cur.close()

#     # Obtener el registro actual para mostrar en el formulario
#     cur = db.connection.cursor()
#     try:
#         cur.execute("SELECT * FROM autorecord WHERE id=%s", (id,))
#         mostrar = cur.fetchone()
#         return render_template('actualizar_registro.html', mostrar=mostrar)
#     except Exception as e:
#         print(f"Error executing SQL: {e}")
#     finally:
#         cur.close()

#     return "Error al recuperar datos para actualizar"


@app.route('/actualizar_registro/<int:id>', methods=['GET', 'POST'])
def actualizar_registro(id):
    if request.method == 'POST':
        # Obtener los datos actualizados desde el formulario
        model = request.form.get('model')
        brand = request.form.get('brand')
        engine = request.form.get('engine')
        refacciones = request.form.get('refacciones')
        service = request.form.get('service')
        status = request.form.get('status')
        payment = request.form.get('payment')
        cost = request.form.get('cost')
        entry_date = request.form.get('entry_date')
        exit_date = request.form.get('exit_date')
        mechanic = request.form.get('mechanic')
        # Repite estos pasos para los demás campos

        # Actualizar los campos en la base de datos
        cur = db.connection.cursor()
        try:
            sql = """
                UPDATE autorecord
                SET model=%s, brand=%s, engine=%s, refacciones=%s, service=%s, status=%s, payment=%s, cost=%s, entry_date=%s, exit_date=%s, mechanic=%s
                WHERE id=%s
            """
            cur.execute(sql, (model, brand, engine, refacciones, service, status, payment, cost, entry_date, exit_date, mechanic, id))
            db.connection.commit()
            
            # Restar uno del stock de refacciones
            cur.execute("UPDATE refacciones SET stock = stock - 1 WHERE pieza = %s", (refacciones,))
            db.connection.commit()
            
            flash('Registro actualizado correctamente.', 'success')
            return redirect(url_for('historial'))
        except Exception as e:
            db.connection.rollback()
            flash(f'Error al actualizar el registro: {e}', 'danger')
        finally:
            cur.close()

    # Obtener el registro actual para mostrar en el formulario
    cur = db.connection.cursor()
    try:
        cur.execute("SELECT * FROM autorecord WHERE id=%s", (id,))
        mostrar = cur.fetchone()

        # Obtener las piezas y los servicios
        piezas = obtener_piezas()
        servicios = obtener_servicios()

        return render_template('actualizar_registro.html', mostrar=mostrar, piezas=piezas, servicios=servicios)
    except Exception as e:
        print(f"Error executing SQL: {e}")
    finally:
        cur.close()

    return "Error al recuperar datos para actualizar"








@app.route('/eliminar_registro/<int:id>', methods=['GET', 'POST'])
def eliminar_registro(id):
    cur = db.connection.cursor()
    try:
        cur.execute("DELETE FROM autorecord WHERE id=%s", (id,))
        db.connection.commit()
        flash('Registro eliminado correctamente.', 'success')
    except Exception as e:
        db.connection.rollback()
        flash(f'Error al eliminar el registro: {e}', 'danger')
    finally:
        cur.close()

    return redirect(url_for('historial'))







# @app.route('/historial', methods=['GET'])
# def historial():
#     cur = db.connection.cursor()
#     try:
#         cur.execute("SELECT * FROM autorecord")
#         usuarios = cur.fetchall()
#         #print(usuarios)  # Agrega esta línea para imprimir los datos
        
#         # Agregar el código adicional aquí
#         try:
#             piezas = obtener_piezas()
#             print('jalo')  # Agrega este mensaje para verificar si la función se ejecuta
#             return render_template('record.html', usuarios=usuarios, piezas=piezas)
#         except Exception as e:
#             print(f"Error en la función historial: {e}")
#             return "Error al recuperar datos del inventario"
        
#     except Exception as e:
#         print(f"Error executing SQL: {e}")
#     finally:
#         cur.close()

#     return "Error al recuperar datos del inventario"

from datetime import datetime

@app.route('/historial', methods=['GET'])
@login_required
def historial():
    cur = db.connection.cursor()
    try:
        cur.execute("SELECT * FROM autorecord")
        usuarios = cur.fetchall()

        # Obtener las piezas y los servicios
        try:
            piezas = obtener_piezas()
            servicios = obtener_servicios()
            
            # Actualizar el stock de refacciones
            actualizar_refacciones()
            
            # Obtener la fecha actual
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            print('jalo')  # Agrega este mensaje para verificar si la función se ejecuta
            return render_template('record.html', usuarios=usuarios, piezas=piezas, servicios=servicios, current_date=current_date)
        except Exception as e:
            print(f"Error en la función historial: {e}")
            return "Error al recuperar datos del inventario"
        
    except Exception as e:
        print(f"Error executing SQL: {e}")
    finally:
        cur.close()

    return "Error al recuperar datos del inventario"











@app.route('/buscarh', methods=['GET'])
def buscarhisto():
    query = request.args.get('query', '')

    cur = db.connection.cursor()

    # Utiliza placeholders para evitar inyecciones de SQL
    sql = """
        SELECT * 
        FROM autorecord
        WHERE 
            model LIKE %s OR 
            brand LIKE %s OR 
            engine LIKE %s OR 
            refacciones LIKE %s OR 
            service LIKE %s OR 
            status LIKE %s OR 
            payment LIKE %s OR 
            CAST(cost AS CHAR) LIKE %s OR 
            entry_date LIKE %s OR 
            exit_date LIKE %s OR 
            mechanic LIKE %s
    """
    cur.execute(sql, ('%' + query + '%','%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))

    resultados = cur.fetchall()

    cur.close()

    return render_template('record.html', query=query, usuarios=resultados)






             #-----------------------------SERVICIOS--------------------------


@app.route('/servicios', methods=['GET'])
@login_required
def servicios():
    cur = db.connection.cursor()
    try:
        cur.execute("SELECT * FROM servicios")
        usuarios = cur.fetchall()
        #print(usuarios)  # Agrega esta línea para imprimir los datos
        return render_template('servicios.html', usuarios=usuarios)
    except Exception as e:
        print(f"Error executing SQL: {e}")
    finally:
        cur.close()

    return "Error al recuperar datos del inventario"



# @app.route('/buscarservicio', methods=['GET'])
# def buscarservicio():
#     query = request.args.get('query', '')

#     cur = db.connection.cursor()

#     # Utiliza placeholders para evitar inyecciones de SQL
#     sql = """
#         SELECT * 
#         FROM servicios
#         WHERE 
#             afinacion LIKE %s OR 
#             frenos LIKE %s OR 
#             llantas LIKE %s OR 
#             suspenciones LIKE %s OR 
#             pintura LIKE %s OR 
#             motores LIKE %s 
#     """
#     cur.execute(sql, ('%' + query + '%','%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))

#     resultados = cur.fetchall()

#     cur.close()

#     return render_template('servicios.html', query=query, usuarios=resultados)



@app.route('/buscarservicio', methods=['GET'])
def buscarservicio():
    query = request.args.get('query', '')

    cur = db.connection.cursor()

    # Utiliza placeholders para evitar inyecciones de SQL
    sql = """
        SELECT * 
        FROM servicios
        WHERE 
            servicios LIKE %s
    """
    cur.execute(sql, ('%' + query + '%',))

    resultados = cur.fetchall()

    cur.close()

    return render_template('servicios.html', query=query, usuarios=resultados)






# @app.route('/agregar_servicios', methods=['GET', 'POST'])
# def agregar_servicios():
#     if request.method == 'POST':
#         Get data from the form
#         afinacion = request.form.get('afinacion')
#         frenos = request.form.get('frenos')
#         llantas = request.form.get('llantas')
#         suspenciones = request.form.get('suspenciones')
#         pintura = request.form.get('pintura')
#         motores = request.form.get('motores')
        
        

#         Validate the data (add your own validation logic here)

#         Insert the new data into the database
#         cur = db.connection.cursor()
#         try:
#             sql = """
#                 INSERT INTO servicios (afinacion, frenos, llantas, suspenciones, pintura, motores)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#             """
#             cur.execute(sql, (afinacion, frenos, llantas, suspenciones, pintura, motores))
#             db.connection.commit()
#             flash('Data added successfully!', 'success')
#             return redirect(url_for('servicios'))  # Redirect to the history page
#         except Exception as e:
#             db.connection.rollback()
#             flash(f'Error adding data: {e}', 'danger')
#         finally:
#             cur.close()

#     return render_template('servicios.html')  # Create a new HTML template for adding data


@app.route('/agregar_servicios', methods=['GET', 'POST'])
def agregar_servicios():
    if request.method == 'POST':
        # Obtener datos del formulario
        servicio = request.form.get('servicios')

        # Validar los datos (añadir tu propia lógica de validación aquí)

        # Insertar los nuevos datos en la base de datos
        cur = db.connection.cursor()
        try:
            sql = """
                INSERT INTO servicios (servicios)
                VALUES (%s)
            """
            cur.execute(sql, (servicio,))
            db.connection.commit()
            flash('¡Datos agregados exitosamente!', 'success')
            return redirect(url_for('servicios'))  # Redirigir a la página de historial
        except Exception as e:
            db.connection.rollback()
            flash(f'Error al agregar datos: {e}', 'danger')
        finally:
            cur.close()

    return render_template('servicios.html')  # Crear un nuevo HTML para agregar datos



@app.route('/eliminar_servicio/<int:id>', methods=['GET', 'POST'])
def eliminar_servicio(id):
    cur = db.connection.cursor()
    try:
        cur.execute("DELETE FROM servicios WHERE id=%s", (id,))
        db.connection.commit()
        flash('Registro eliminado correctamente.', 'success')
    except Exception as e:
        db.connection.rollback()
        flash(f'Error al eliminar el registro: {e}', 'danger')
    finally:
        cur.close()

    return redirect(url_for('servicios'))







                #-----------------   INNER JOIN REFACCIONES---------------




def actualizar_refacciones():
    try:
        # Establecer la conexión con la base de datos
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="test"
        )

        # Crear un cursor para ejecutar consultas SQL
        cursor = conexion.cursor()

        # Consulta SQL para actualizar las refacciones en la tabla autorecord
        consulta_actualizacion = """
        UPDATE autorecord AS ar
        INNER JOIN refacciones AS r ON ar.refacciones = r.pieza
        SET ar.refacciones = r.pieza
        """

        # Ejecutar la consulta de actualización
        cursor.execute(consulta_actualizacion)

        # Confirmar los cambios en la base de datos
        conexion.commit()

        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
    except mysql.connector.Error as error:
        print(f"Error al actualizar refacciones: {error}")

# Llamar a la función para actualizar las refacciones
actualizar_refacciones()

# Función para obtener los datos de la tabla "refacciones"
def obtener_piezas():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="test"
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT pieza FROM refacciones")
        piezas = cursor.fetchall()
        cursor.close()
        conexion.close()
        return piezas
    except mysql.connector.Error as error:
        print(f"Error al obtener las piezas: {error}")
        return []




# Función para actualizar las refacciones en la tabla autorecord








# @app.route('/agregar_histor', methods=['GET'])
# def historiales():
#     try:
#         piezas = obtener_piezas()
#         print('jalo')  # Agrega este mensaje para verificar si la función se ejecuta
#         return render_template('record.html', piezas=piezas)
#     except Exception as e:
#         print(f"Error en la función historial: {e}")
#         return "Error al recuperar datos del inventario"







                        #---------------- INNER JOIN SERVICIOS------------------------




def actualizar_servicios():
    try:
        # Establecer la conexión con la base de datos
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="test"
        )

        # Crear un cursor para ejecutar consultas SQL
        cursor = conexion.cursor()

        # Consulta SQL para actualizar los servicios en la tabla autorecord
        # consulta_actualizacion = """
        # UPDATE autorecord AS ar
        # INNER JOIN servicios AS s ON ar.servicio = s.servicios
        # SET ar.servicio = s.Servicios
        # """
           
        consulta_actualizacion = """
        UPDATE autorecord AS ar
        INNER JOIN servicios AS s ON ar.service = s.servicios
        SET ar.service = s.servicios
        """



        

        # Ejecutar la consulta de actualización
        cursor.execute(consulta_actualizacion)

        # Confirmar los cambios en la base de datos
        conexion.commit()

        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
    except mysql.connector.Error as error:
        print(f"Error al actualizar servicios: {error}")

# Llamar a la función para actualizar los servicios
actualizar_servicios()

# Función para obtener los datos de la tabla "servicios"
def obtener_servicios():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="test"
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT servicios FROM servicios")
        servicios = cursor.fetchall()
        cursor.close()
        conexion.close()
        return servicios
    except mysql.connector.Error as error:
        print(f"Error al obtener los servicios: {error}")
        return []


















@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"


def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


if __name__ == '__main__':
    
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()



