# Mi Lista de Tareas — versión full-stack

Esta versión conserva la interfaz HTML/CSS/JavaScript y agrega una API REST en Flask y persistencia en MySQL.

## Arquitectura
- Frontend: HTML, CSS, JavaScript servido por Nginx.
- Backend: Python + Flask + Gunicorn.
- Base de datos: MySQL 8.4.
- Orquestación: Docker Compose.

El navegador consume `/api/...` a través de Nginx. Nginx reenvía esas solicitudes al servicio `backend`; Flask lee y escribe en MySQL.

## Preparación
1. Copia `.env.example` como `.env`.
2. Cambia `DB_PASSWORD` y `DB_ROOT_PASSWORD` por contraseñas seguras y diferentes.
3. Ejecuta `docker compose up -d --build`.
4. Comprueba los servicios con `docker compose ps`.
5. Prueba la API: `curl http://localhost:8080/api/health`.
6. Abre `http://IP_PUBLICA:8080`.

## API
- `GET /api/health`: estado de la API y conexión a MySQL.
- `GET /api/tasks`: lista las tareas.
- `POST /api/tasks`: crea una tarea. JSON: `{"name":"Estudiar"}`
- `PATCH /api/tasks/<id>`: cambia el estado. JSON: `{"completed":true}`
- `DELETE /api/tasks/<id>`: elimina una tarea.
- `DELETE /api/tasks/completed`: elimina todas las completadas.

## Importante para Azure
- Mantén abierto el acceso SSH por TCP 22.
- Para la demostración web, el NSG debe permitir TCP 8080.
- No publiques los puertos 3306 (MySQL) ni 5000 (Flask) en la IP pública. Solo se exponen a la red interna de Docker.
- El volumen `mysql_data` conserva los datos aunque se recree el contenedor.
- No compartas el archivo `.env`; contiene credenciales.

## Desarrollo local
Requiere Docker Engine y Docker Compose v2. Los datos quedan en el volumen Docker `mysql_data`.
