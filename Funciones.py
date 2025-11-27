import sqlite3
import hashlib
from tabulate import tabulate

#Guardar usuario
#Verificar contraseña
#Mostrar usuarios

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()





def guardar_usuario(line):
    conn = sqlite3.connect("data.db")  # tu base de datos
    cursor = conn.cursor()
    codigo_str, user_id, password, = line.split(",")
    try:
        hashed_password = hash_password(password)
        cursor.execute("""
        INSERT INTO usuario (user, password)
        VALUES (?, ?)
        """, (user_id, hashed_password))

        conn.commit()
        print(f"Usuario {user_id} guardado correctamente.")

    except sqlite3.IntegrityError as e:
        print("Error al guardar usuario:", e)

    finally:
        conn.close()




def mostrar_usuarios():
    conn = sqlite3.connect("data.db")  # tu base de datos
    cursor = conn.cursor()

    # Asegurarse de que la tabla exista
    # Obtener todos los registros
    cursor.execute("SELECT * FROM usuario")
    registros = cursor.fetchall()

    conn.close()

    if registros:
        # Mostrar en formato tabla usando tabulate
        print(tabulate(registros, headers=["ID", "User", "Password"], tablefmt="fancy_grid"))
    else:
        print("No hay usuarios registrados.")


mostrar_usuarios()

def verificar_contraseña(user_id, password_ingresada):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Obtener el hash de la contraseña guardada para ese usuario
    cursor.execute("SELECT password FROM usuario WHERE user = ?", (user_id,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        password_guardada = resultado[0]
        if hash_password(password_ingresada) == password_guardada:
            print("Iniciar sesion")
            return True
            
        else:
            print("Contraseña incorrecto")
            return False
            
    else:
        print("Usuario no encontrado.")
        return False
    


def obtener_dia_x(dia):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Medidax FROM medidas WHERE DATE(timestamp) = ?", (dia,))
        resultados = cursor.fetchall()
        # Extraer los valores del tuple y ponerlos en un array
        x_values = [fila[0] for fila in resultados]
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        x_values = []
    finally:
        conn.close()
    
    return x_values

import sqlite3

def obtener_incidentes(dia):
    """
    Obtiene los registros del día especificado donde danger = 1,
    retornando una lista de tuplas: (fecha, valor_x, valor_y, valor_z)
    
    Parámetros:
        dia (str): Fecha en formato 'YYYY-MM-DD'
    
    Retorna:
        List[Tuple]: Lista de registros filtrados
    """
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        # Consulta filtrando por fecha y danger=1
        cursor.execute("""
            SELECT timestamp, Medidax, Mediday, Medidaz
            FROM medidas
            WHERE DATE(timestamp) = ? AND danger = 1
            ORDER BY timestamp ASC
        """, (dia,))
        resultados = cursor.fetchall()
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        resultados = []
    finally:
        conn.close()
    
    return resultados


def obtener_dia_y(dia):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Mediday FROM medidas WHERE DATE(timestamp) = ?", (dia,))
        resultados = cursor.fetchall()
        # Extraer los valores del tuple y ponerlos en un array
        x_values = [fila[0] for fila in resultados]
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        x_values = []
    finally:
        conn.close()
    
    return x_values

def obtener_dia_z(dia):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Medidaz FROM medidas WHERE DATE(timestamp) = ?", (dia,))
        resultados = cursor.fetchall()
        # Extraer los valores del tuple y ponerlos en un array
        x_values = [fila[0] for fila in resultados]
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        x_values = []
    finally:
        conn.close()
    
    return x_values




def guardar_medidas(limite,line, conn):
    """
    Recibe una línea con formato 'codigo,x,y,z'.
    NO guarda el código en la base de datos.
    Guarda solo x, y, z en la tabla 'medidas'.
    """
    cursor = conn.cursor()
    try:
        # Separar valores
        danger = 0
        codigo_str, x_str, y_str, z_str = line.split(",")
        
        # Convertir a número
        # codigo = int(codigo_str)   # <— si lo quieres usar en futuro, aquí está
        x = float(x_str)
        y = float(y_str)
        z = float(z_str)
        if((x  > limite or y  > limite  or z >limite)):
          danger = 1
        
        cursor.execute("""
            INSERT INTO medidas (Danger,Medidax, Mediday, Medidaz)
            VALUES (?,?, ?, ?)
        """, (danger,x, y, z))

        conn.commit()

        # Mostrar por consola
        print("Se guardó en la base de datos:")
        print(f"X = {x}, Y = {y}, Z = {z}")
        print("---")

    except ValueError:
        print("Error al parsear la línea:", line)
