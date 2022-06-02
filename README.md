# django-app-palabritas
Aplicación web desarrollada en Django. Permite la gestión de fichas de alumnos, cursos y lista de espera. Sistema creado en base a la necesidad del cliente.

## Contenido
El proyecto contiene 2 ramas de trabajo: master y develop. La rama de **develop** es utilizada para aplicar nuevas mejoras al sistemas antes de aplicarlas en el proyecto final.

## Cómo clonar
Se requiere lo siguiente:
* Python 3.8
* PIP
* XAMPP o gestor para base de datos MySQL

## Instalación
Para instalar el proyecto se debe crear un entorno virtual de Python y ejecutar
```bash
pip install -r requirements.txt
```

Se debe crear un archivo **.env** en la misma carpeta que **settings.py**. Setear variables.
* SECRET_KEY
* DJANGO_DEBUG
* DATABASE_NAME
* DATABASE_USER
* DATABASE_PASS
* DATABASE_HOST
* DATABASE_PORT
* EMAIL_USER
* EMAIL_PASSWORD

## Vista previa
Ventana principal con menú de navegación
![image](https://user-images.githubusercontent.com/73400105/171694766-2de6a23f-5acc-43a5-8b9e-a5d769201feb.png)

Ventana de listado de cursos
![image](https://user-images.githubusercontent.com/73400105/171695131-5f90abd3-d013-40c8-ad71-d9f07f417ae1.png)

Ventana de detalle curso
![image](https://user-images.githubusercontent.com/73400105/171695001-0af06cf1-3e44-4c8c-8523-53c3ec3c59b9.png)

## Notas
Proyecto realizado como trabajo de práctica laboral.
Creación propia.
