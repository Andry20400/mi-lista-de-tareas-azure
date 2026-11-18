import os
import time
from flask import Flask, jsonify, request
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)

def db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "lista_user"),
        password=os.getenv("DB_PASSWORD", "cambia_esta_clave"),
        database=os.getenv("DB_NAME", "lista_tareas"),
        cursorclass=DictCursor,
        autocommit=True,
        charset="utf8mb4",
    )

def initialize_database():
    last_error = None
    for _ in range(30):
        try:
            connection = db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tasks (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(90) NOT NULL,
                            completed BOOLEAN NOT NULL DEFAULT FALSE,
                            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """)
            finally:
                connection.close()
            return
        except Exception as error:
            last_error = error
            time.sleep(2)
    raise RuntimeError(f"No fue posible conectar con MySQL: {last_error}")

@app.get("/api/health")
def health():
    try:
        connection = db_connection()
        connection.close()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as error:
        return jsonify({"status": "error", "database": "disconnected", "detail": str(error)}), 503

@app.get("/api/tasks")
def get_tasks():
    connection = db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, completed, created_at FROM tasks ORDER BY id DESC")
            rows = cursor.fetchall()
        for row in rows:
            row["completed"] = bool(row["completed"])
            row["created_at"] = row["created_at"].isoformat()
        return jsonify(rows)
    finally:
        connection.close()

@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    if not name:
        return jsonify({"error": "El nombre de la tarea es obligatorio"}), 400
    if len(name) > 90:
        return jsonify({"error": "La tarea no puede superar 90 caracteres"}), 400

    connection = db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO tasks (name) VALUES (%s)", (name,))
            task_id = cursor.lastrowid
            cursor.execute("SELECT id, name, completed, created_at FROM tasks WHERE id = %s", (task_id,))
            task = cursor.fetchone()
        task["completed"] = bool(task["completed"])
        task["created_at"] = task["created_at"].isoformat()
        return jsonify(task), 201
    finally:
        connection.close()

@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    if "completed" not in data or not isinstance(data["completed"], bool):
        return jsonify({"error": "Se requiere completed como valor booleano"}), 400

    connection = db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE tasks SET completed = %s WHERE id = %s", (data["completed"], task_id))
            if cursor.rowcount == 0:
                cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
                if not cursor.fetchone():
                    return jsonify({"error": "Tarea no encontrada"}), 404
            cursor.execute("SELECT id, name, completed, created_at FROM tasks WHERE id = %s", (task_id,))
            task = cursor.fetchone()
        task["completed"] = bool(task["completed"])
        task["created_at"] = task["created_at"].isoformat()
        return jsonify(task)
    finally:
        connection.close()

@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    connection = db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": "Tarea no encontrada"}), 404
        return "", 204
    finally:
        connection.close()

@app.delete("/api/tasks/completed")
def delete_completed():
    connection = db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE completed = TRUE")
            deleted = cursor.rowcount
        return jsonify({"deleted": deleted})
    finally:
        connection.close()

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000)
