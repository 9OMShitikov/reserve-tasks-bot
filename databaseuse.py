import sqlite3


class TasksDatabase:
    def __init__(self, _database_name):
        database_name = _database_name
        with sqlite3.connect(database_name) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name VARCHAR(255),
                    second_name VARCHAR(255),
                    user_group VARCHAR(255),
                    chat_id VARCHAR(255),
                    problems VARCHAR(255),
                    is_active BOOLEAN
                )''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255),
                    number INTEGER,
                    solve_limit INTEGER
                )''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task INTEGER,
                    user INTEGER,
                    FOREIGN KEY(task) REFERENCES tasks(id),
                    FOREIGN KEY(user) REFERENCES users(id)
                )''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS teacher (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name VARCHAR(255),
                    second_name VARCHAR(255),
                    chat_id VARCHAR(255),
                    tasks_count INTEGER
                )''')
            cur.execute('''INSERT INTO teacher (chat_id) VALUES ('temporary_id')''')
            conn.commit()


class TeacherRepository:
    @staticmethod
    def set_teacher(first_name, second_name, chat_id, conn):
        cur = conn.cursor()
        query = '''UPDATE teacher SET first_name = "{}", second_name = "{}", chat_id = "{}", tasks_count = 0'''
        cur.execute(query.format(first_name, second_name, chat_id))
        return

    @staticmethod
    def check_teacher(conn):
        cur = conn.cursor()
        query = '''SELECT teacher.id
                   FROM teacher
                   WHERE chat_id = 'temporary_id' '''
        cur.execute(query)
        return len(cur.fetchall()) == 0

    @staticmethod
    def check_id_teacher(chat_id, conn):
        cur = conn.cursor()
        query = '''SELECT teacher.id
                   FROM teacher
                   WHERE chat_id = "{}"'''
        cur.execute(query.format(chat_id))
        return len(cur.fetchall()) != 0

    @staticmethod
    def get_teacher_chat_id(conn):
        cur = conn.cursor()
        query = '''SELECT teacher.chat_id FROM teacher'''
        cur.execute(query)
        return cur.fetchall()[0][0]


class UsersRepository:
    @staticmethod
    def check_student(first_name, second_name, group, conn):
        cur = conn.cursor()
        query = '''SELECT users.id
                   FROM users
                   WHERE first_name = "{}" AND second_name = "{}" AND user_group = "{}"'''
        cur.execute(query.format(first_name, second_name, group))
        return len(cur.fetchall()) != 0

    @staticmethod
    def check_id_student(chat_id, conn):
        cur = conn.cursor()
        query = '''SELECT users.id
                   FROM users
                   WHERE chat_id = "{}"'''
        cur.execute(query.format(chat_id))
        return len(cur.fetchall()) != 0

    @staticmethod
    def is_active(first_name, second_name, group, conn):
        cur = conn.cursor()
        query = '''SELECT users.is_active
                   FROM users
                   WHERE first_name = "{}" AND second_name = "{}" AND user_group = "{}"'''
        cur.execute(query.format(first_name, second_name, group))
        status = cur.fetchall()
        return len(status) > 0 and status[0][0] == 1

    @staticmethod
    def add_student(first_name, second_name, group, chat_id, conn):
        cur = conn.cursor()
        query = '''SELECT teacher.tasks_count FROM teacher'''
        cur.execute(query)
        tasks_count = cur.fetchall()
        query = '''INSERT INTO users (first_name, second_name, user_group, chat_id, problems, is_active) 
        VALUES ("{}", "{}", "{}", "{}", "{}", 0)'''
        cur.execute(query.format(first_name, second_name, group, chat_id, "0"*(tasks_count[0][0])))
        return

    @staticmethod
    def set_active(first_name, second_name, group, conn):
        cur = conn.cursor()
        query = '''UPDATE users
                   SET is_active = 1 
                   WHERE first_name = "{}" AND second_name = "{}" AND user_group = "{}"'''
        cur.execute(query.format(first_name, second_name, group))
        return

    @staticmethod
    def get_student_chat_id(first_name, second_name, group, conn):
        cur = conn.cursor()
        query = '''SELECT users.chat_id FROM users WHERE 
                   first_name = "{}" AND second_name = "{}" AND user_group = "{}"'''
        cur.execute(query.format(first_name, second_name, group))
        return cur.fetchall()[0][0]

    @staticmethod
    def get_students(conn):
        cur = conn.cursor()
        query = '''SELECT users.first_name, users.second_name, users.user_group, users.problems FROM users'''
        cur.execute(query)
        students = cur.fetchall()
        ans = ""
        for student in students:
            ans += (student[0] + " " + student[1] + " " + student[2] + ": tasks information: " +
                    " ".join(list(student[3])) + "\n")
        return ans


class ReservationsRepository:

    @staticmethod
    def check_reservation(task_name, chat_id, conn):
        cur = conn.cursor()
        query = '''SELECT reservations.id FROM reservations WHERE 
                   task = (SELECT tasks.id FROM tasks WHERE name = "{}") AND 
                   user = (SELECT users.id FROM users WHERE chat_id = "{}")'''
        cur.execute(query.format(task_name, chat_id))
        row = cur.fetchall()
        return len(row) != 0

    @staticmethod
    def add_reservation(task_name, chat_id, conn):
        cur = conn.cursor()
        query = '''INSERT INTO reservations (task, user) VALUES (
                   (SELECT tasks.id FROM tasks WHERE name = "{}"),
                   (SELECT users.id FROM users WHERE chat_id = "{}"))'''
        cur.execute(query.format(task_name, chat_id))
        query = '''SELECT tasks.solve_limit FROM tasks WHERE name = "{}"'''
        cur.execute(query.format(task_name))
        row = cur.fetchall()
        query = '''UPDATE tasks SET solve_limit = {} WHERE name = "{}"'''
        cur.execute(query.format(str(row[0][0] - 1), task_name))
        return

    @staticmethod
    def delete_reservation(task, first_name, second_name, group, conn):
        cur = conn.cursor()
        query = '''DELETE FROM reservations WHERE 
                   task = (SELECT tasks.id FROM tasks WHERE name = "{}") AND 
                   user = (SELECT users.id FROM users WHERE first_name = "{}" AND second_name = "{}" AND 
                                                                                  user_group = "{}")'''
        cur.execute(query.format(task, first_name, second_name, group))
        query = '''SELECT tasks.solve_limit FROM tasks WHERE name = "{}"'''
        cur.execute(query.format(task))
        row = cur.fetchall()
        query = '''UPDATE tasks SET solve_limit = {} WHERE name = "{}"'''
        cur.execute(query.format(str(row[0][0] + 1), task))
        return

    @staticmethod
    def confirm_reservation(task, first_name, second_name, group, conn):
        cur = conn.cursor()
        query = '''DELETE FROM reservations WHERE 
                   task = (SELECT tasks.id FROM tasks WHERE name = "{}") AND 
                   user = (SELECT users.id FROM users WHERE first_name = "{}" AND second_name = "{}" AND 
                                                                                  user_group = "{}")'''
        cur.execute(query.format(task, first_name, second_name, group))
        query = '''SELECT tasks.number FROM tasks WHERE name = "{}"'''
        cur.execute(query.format(task))
        row = cur.fetchall()
        query = '''SELECT users.problems 
                   FROM users 
                   WHERE first_name = "{}" AND second_name = "{}" AND user_group = "{}"'''
        cur.execute(query.format(first_name, second_name, group))
        tasksline = cur.fetchall()[0][0]
        tasksline = tasksline[: row[0][0] - 1] + '1' + tasksline[row[0][0] + 1:]
        query = '''UPDATE users 
                   SET problems = "{}" 
                   WHERE first_name = "{}" AND second_name = "{}" AND user_group = "{}"'''
        cur.execute(query.format(tasksline, first_name, second_name, group))
        return

    @staticmethod
    def check_valid_reservation(task_name, conn):
        cur = conn.cursor()
        query = '''SELECT tasks.solve_limit 
                           FROM tasks 
                           WHERE name = "{}"'''
        cur.execute(query.format(task_name))
        row = cur.fetchall()
        if len(row) == 0:
            return 0
        if row[0][0] == 0:
            return 0
        return 1


class TasksRepository:
    @staticmethod
    def add_task(task, limit, conn):
        cur = conn.cursor()
        query = '''SELECT teacher.tasks_count FROM teacher'''
        cur.execute(query)
        tasks_count = cur.fetchall()
        query = '''UPDATE teacher SET tasks_count = {}'''
        cur.execute(query.format(str(tasks_count[0][0]+1)))
        query = '''SELECT users.id, users.problems FROM users'''
        cur.execute(query)
        students = cur.fetchall()
        for student in students:
            query = '''UPDATE users SET problems = "{}" WHERE id = {}'''
            cur.execute(query.format(student[1]+"0", student[0]))
        query = '''INSERT INTO tasks (name, number, solve_limit) VALUES ("{}", {}, {})'''
        cur.execute(query.format(task, tasks_count[0][0], limit))
        return

    @staticmethod
    def check_task(name, conn):
        cur = conn.cursor()
        query = '''SELECT tasks.id
                   FROM tasks
                   WHERE name = "{}"'''
        cur.execute(query.format(name))
        return len(cur.fetchall()) != 0

    @staticmethod
    def get_tasks(conn):
        cur = conn.cursor()
        query = '''SELECT tasks.number, tasks.name, tasks.solve_limit FROM tasks'''
        cur.execute(query)
        tasks = cur.fetchall()
        tasks = list(tasks)
        tasks.sort()
        ans = ""
        for task in tasks:
            ans += (task[1] + " " + str(task[2]) + "\n")
        return ans
