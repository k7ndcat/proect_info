import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QGridLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt
import sqlite3
import hashlib

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                condition TEXT,
                answer TEXT,
                hashed_answer TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                surname TEXT,
                name TEXT,
                password TEXT,
                results TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                password TEXT
            )
        ''')

        self.conn.commit()

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.name_label = QLabel("Имя пользователя:")
        self.layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_input, 1, 0, 1, 2)

        self.password_label = QLabel("Пароль:")
        self.layout.addWidget(self.password_label, 2, 0)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input, 3, 0, 1, 2)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button, 4, 0)

        self.register_button = QPushButton("Регистрация")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button, 4, 1)

    def login(self):
        name = self.name_input.text()
        password = self.password_input.text()

        self.cursor.execute("SELECT * FROM teachers WHERE name = ? AND password = ?", (name, password))
        teacher = self.cursor.fetchone()

        if teacher:
            self.close()
            self.teacher_window = TeacherWindow()
            self.teacher_window.show()
        else:
            self.cursor.execute("SELECT * FROM students WHERE name = ? AND password = ?", (name, password))
            student = self.cursor.fetchone()

            if student:
                self.close()
                self.student_window = StudentWindow()
                self.student_window.show()
            else:
                QMessageBox.warning(self, "Ошибка", "Неправильный логин или пароль")

    def register(self):
        register_window = RegisterWindow()
        register_window.show()

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.name_label = QLabel("Имя пользователя:")
        self.layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_input, 1, 0, 1, 2)

        self.password_label = QLabel("Пароль:")
        self.layout.addWidget(self.password_label, 2, 0)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input, 3, 0, 1, 2)

        self.surname_label = QLabel("Фамилия:")
        self.layout.addWidget(self.surname_label, 4, 0)

        self.surname_input = QLineEdit()
        self.layout.addWidget(self.surname_input, 5, 0, 1, 2)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button, 6, 0)

    def register(self):
        name = self.name_input.text()
        password = self.password_input.text()
        surname = self.surname_input.text()

        self.cursor.execute("INSERT INTO students (name, surname, password, results) VALUES (?, ?, ?, '')", (name, surname, password))
        self.conn.commit()

        self.close()

class TeacherWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.task_label = QLabel("Условие задания:")
        self.layout.addWidget(self.task_label, 0, 0)

        self.task_input = QTextEdit()
        self.layout.addWidget(self.task_input, 1, 0, 1, 2)

        self.answer_label = QLabel("Ответ:")
        self.layout.addWidget(self.answer_label, 2, 0)

        self.answer_input = QLineEdit()
        self.layout.addWidget(self.answer_input, 3, 0, 1, 2)

        self.add_task_button = QPushButton("Добавить задание")
        self.add_task_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_task_button, 4, 0)

        self.tasks_label = QLabel("Список заданий:")
        self.layout.addWidget(self.tasks_label, 5, 0)

        self.tasks_text = QTextEdit()
        self.layout.addWidget(self.tasks_text, 6, 0, 1, 2)

        self.load_tasks()  # Загрузка списка заданий

        self.students_label = QLabel("Успеваемость учеников:")
        self.layout.addWidget(self.students_label, 7, 0)

        self.students_text = QTextEdit()
        self.layout.addWidget(self.students_text, 8, 0, 1, 2)

        self.load_student_results()  # Загрузка успеваемости учеников

    def add_task(self):
        condition = self.task_input.toPlainText()
        answer = self.answer_input.text()
        hashed_answer = hashlib.sha256(answer.encode()).hexdigest()

        self.cursor.execute("INSERT INTO tasks (condition, answer, hashed_answer) VALUES (?, ?, ?)", (condition, answer, hashed_answer))
        self.conn.commit()

        self.task_input.clear()
        self.answer_input.clear()

        self.load_tasks()  # Обновление списка заданий

    def load_tasks(self):
        self.tasks_text.clear()
        self.cursor.execute("SELECT * FROM tasks")
        tasks = self.cursor.fetchall()

        for task in tasks:
            self.tasks_text.append(f"ID: {task[0]}, Условие: {task[1]}")

    def load_student_results(self):
        self.students_text.clear()
        self.cursor.execute("SELECT * FROM students")
        students = self.cursor.fetchall()

        for student in students:
            results = student[4]  # Предполагаем, что результаты хранятся в 5-м столбце
            self.students_text.append(f"{student[1]} {student[2]}: {results}")

class StudentWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.task_id_label = QLabel("ID задания:")
        self.layout.addWidget(self.task_id_label, 0, 0)

        self.task_id_input = QLineEdit()
        self.layout.addWidget(self.task_id_input, 1, 0, 1, 2)

        self.get_task_button = QPushButton("Получить задание")
        self.get_task_button.clicked.connect(self.get_task)
        self.layout.addWidget(self.get_task_button, 2, 0)

        self.task_label = QLabel("Условие задания:")
        self.layout.addWidget(self.task_label, 3, 0)

        self.task_text = QTextEdit()
        self.layout.addWidget(self.task_text, 4, 0, 1, 2)

        self.answer_label = QLabel("Ответ:")
        self.layout.addWidget(self.answer_label, 5, 0)

        self.answer_input = QLineEdit()
        self.layout.addWidget(self.answer_input, 6, 0, 1, 2)

        self.check_button = QPushButton("Проверить")
        self.check_button.clicked.connect(self.check)
        self.layout.addWidget(self.check_button, 7, 0)

        self.result_label = QLabel("Результат:")
        self.layout.addWidget(self.result_label, 8, 0)

        self.result_text = QTextEdit()
        self.layout.addWidget(self.result_text, 9, 0, 1, 2)

    def get_task(self):
        task_id = int(self.task_id_input.text())
        self.cursor.execute("SELECT condition FROM tasks WHERE id = ?", (task_id,))
        condition = self.cursor.fetchone()[0]

        self.task_text.setText(condition)

    def check(self):
        task_id = int(self.task_id_input.text())
        self.cursor.execute("SELECT hashed_answer FROM tasks WHERE id = ?", (task_id,))
        hashed_answer = self.cursor.fetchone()[0]

        user_answer = self.answer_input.text()
        if hashlib.sha256(user_answer.encode()).hexdigest() == hashed_answer:
            self.result_text.setText("Правильно!")
        else:
            self.result_text.setText("Неправильно!")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Создание тестового учителя
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO teachers (name, password) VALUES ('teacher', 'teacher')")
    conn.commit()

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())
