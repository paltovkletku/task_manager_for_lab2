from flask import Flask, redirect, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    db_path = app.config.get('DATABASE', 'todo.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# запретим работать с пустыми задачами
@app.route('/addTask', methods=['GET'])
def add_task():
    task = request.args.get('task')
    if not task:
        return redirect('/')  # просто игнорируем
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks(task) VALUES(?)", (task,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/getTasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    row = cursor.fetchall()
    conn.close()
    return render_template("index.html", tasks=row)


@app.route('/move-to-done/<int:id>/<string:task_name>')
def move_to_done(id, task_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE tid = ?", (id,))
    task = cursor.fetchone()
    if task:
        cursor.execute("INSERT INTO done(task, task_id) VALUES(?,?)", (task_name, id))
        cursor.execute("DELETE FROM tasks WHERE tid = ?", (id,))
        conn.commit()
    conn.close()
    return redirect('/')


@app.route('/deleteTask/<int:id>')
def deleteTask(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE tid=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/delete-completed/<int:id>')
def deleteCompletedTask(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM done WHERE did=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    row = cursor.fetchall()
    cursor.execute("SELECT * FROM done")
    row2 = cursor.fetchall()
    conn.close()
    return render_template('index.html', tasks=row, done=row2)


# API эндпоинты — используются ТОЛЬКО для интеграционных тестов
@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    task_list = [{"tid": task["tid"], "task": task["task"]} for task in tasks]
    return {"tasks": task_list}


@app.route('/api/done', methods=['GET'])
def api_get_done():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM done")
    done_tasks = cursor.fetchall()
    conn.close()
    done_list = [{"did": task["did"], "task": task["task"], "task_id": task["task_id"]} for task in done_tasks]
    return {"done": done_list}


if __name__ == "__main__":
    app.run(debug=True)
