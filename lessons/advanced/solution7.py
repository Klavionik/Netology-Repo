import psycopg2 as psy
from psycopg2._psycopg import Error
from datetime import datetime as dt
from contextlib import contextmanager


@contextmanager
def psql(destination, fetch=False):
    conn = psy.connect(destination)
    try:
        yield conn.cursor()
    except Error as e:
        print(f"{e.args[0]}")
    finally:
        if not fetch:
            conn.commit()
        conn.cursor()
        conn.close()


class NetologyDB:

    def __init__(self, db_name, db_user, db_password):
        self.name = db_name
        self.user = db_user
        self.password = db_password
        self.db = f'dbname={self.name} user={self.user} password={self.password}'

    def create_db(self):
        with psql(self.db) as dbhand:
            dbhand.execute("CREATE TABLE students ("
                           "id serial PRIMARY KEY, "
                           "name varchar(100) NOT NULL, "
                           "gpa numeric(10, 2), "
                           "birth timestamp with time zone)")

            dbhand.execute("CREATE TABLE courses ("
                           "id serial PRIMARY KEY NOT NULL, "
                           "name varchar(100) NOT NULL)")

        with psql(self.db) as dbhand:
            dbhand.execute("CREATE TABLE studentscourses ("
                           "id serial PRIMARY KEY,"
                           "course_id int REFERENCES courses (id),"
                           "student_id int REFERENCES students (id))")

        print("Tables are created")

    def add_course(self, course_name):
        with psql(self.db) as dbhand:
            dbhand.execute("INSERT INTO courses (name) "
                           "values (%s)", (course_name,))

        print(f"\nCourse {course_name} is added")

    def add_student(self, student):
        with psql(self.db) as dbhand:
            dbhand.execute("INSERT INTO students "
                           "(name, gpa, birth) values"
                           "(%s, %s, %s)",
                           (student['name'], student['gpa'], student['birth']))

        print(f"\nStudent {student['name']} is added")

    def get_student(self, student_id):
        with psql(self.db, fetch=True) as dbhand:
            dbhand.execute("SELECT students.name "
                           "FROM students "
                           "WHERE students.id=%s", (student_id,))
            student = dbhand.fetchall()

        return student

    def add_students(self, course_id, students):
        for student in students['students']:
            with psql(self.db) as dbhand:
                dbhand.execute("INSERT INTO students ("
                               "name, gpa, birth) values"
                               "(%s, %s, %s)",
                               (student['name'], student['gpa'], student['birth']))

            print(f"Student {student['name']} is added")

        added_students = []
        for student in students['students']:
            with psql(self.db, fetch=True) as dbhand:
                dbhand.execute("SELECT students.id, students.name "
                               "FROM students "
                               "WHERE students.name = %s AND "
                               "students.gpa = %s AND "
                               "students.birth = %s",
                               (student['name'], student['gpa'], student['birth']))
                added_students.extend(dbhand.fetchall())

        for student in added_students:
            with psql(self.db) as dbhand:
                dbhand.execute("INSERT INTO studentscourses ("
                               "course_id, student_id)"
                               "values (%s, %s)", (course_id, student[0]))

            print(f"Student {student[1]} with ID {student[0]} is registered as a student on course ID {course_id}")

    def get_students(self, course_id):
        with psql(self.db, fetch=True) as dbhand:
            dbhand.execute("SELECT s.id, s.name, c.name FROM studentscourses sc "
                           "JOIN students s ON s.id = sc.student_id "
                           "JOIN courses c ON c.id = sc.course_id "
                           "WHERE c.id = %s", (course_id,))

            students = dbhand.fetchall()

        return students


if __name__ == '__main__':
    netology_db = 'netology'
    user = ''  # INSERT USER
    password = ''  # INSERT PASSWORD

    # example students
    py_students = {'students': [{'name': 'Roman Vlasenko', 'gpa': '5.0', 'birth': dt(1993, 6, 8)},
                                {'name': 'Ivan Denisov', 'gpa': '4.3', 'birth': dt(1990, 2, 9)}]}
    js_students = {'students': [{'name': 'Philipp Ivanov', 'gpa': '3.6', 'birth': dt(1987, 12, 15)},
                                {'name': 'Nikolay Dubov', 'gpa': '5.0', 'birth': dt(1994, 7, 23)}]}

    # example courses
    py_course = "Python Programming"
    js_course = 'JS Basics'

    # create db
    handler = NetologyDB(netology_db, user, password)
    handler.create_db()

    # add example courses
    handler.add_course(py_course)
    handler.add_course(js_course)

    # add example students and enroll them on courses
    handler.add_students(1, py_students)
    handler.add_students(2, js_students)

    # get students from db by ID
    handler.get_student(1)
    handler.get_student(2)
    handler.get_student(3)
    handler.get_student(4)

    # get students from db by course ID
    print(handler.get_students(1))
    print(handler.get_students(2))
