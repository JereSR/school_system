# utils.py
def puede_modificar_usuario(rango_actual, rango_objetivo):
    return rango_actual > rango_objetivo

def puede_crear_usuario(rango):
    return rango >= 3  # solo vice, director o secreto

def puede_modificar_alumno(rango):
    return rango >= 2  # preceptor o superior
