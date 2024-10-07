import sqlite3

class DatabaseOperations:
    def __init__(self, db_name='college_timetable.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff_departments (
                id INTEGER PRIMARY KEY,
                staff_id INTEGER,
                department_id INTEGER,
                FOREIGN KEY (staff_id) REFERENCES staff (id),
                FOREIGN KEY (department_id) REFERENCES departments (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department_id INTEGER,
                periods_per_week INTEGER NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff_courses (
                id INTEGER PRIMARY KEY,
                staff_id INTEGER,
                course_id INTEGER,
                FOREIGN KEY (staff_id) REFERENCES staff (id),
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS timetable (
                id INTEGER PRIMARY KEY,
                day TEXT NOT NULL,
                period INTEGER,
                shift INTEGER,
                course_id INTEGER,
                staff_id INTEGER,
                FOREIGN KEY (course_id) REFERENCES courses (id),
                FOREIGN KEY (staff_id) REFERENCES staff (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS extra_activities (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department_id INTEGER,
                periods_per_week INTEGER NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS labs (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department_id INTEGER,
                periods_per_week INTEGER NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lab_staff (
                id INTEGER PRIMARY KEY,
                lab_id INTEGER,
                staff_id INTEGER,
                FOREIGN KEY (lab_id) REFERENCES labs (id),
                FOREIGN KEY (staff_id) REFERENCES staff (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff_extra_activities (
                id INTEGER PRIMARY KEY,
                staff_id INTEGER,
                extra_activity_id INTEGER,
                FOREIGN KEY (staff_id) REFERENCES staff (id),
                FOREIGN KEY (extra_activity_id) REFERENCES extra_activities (id)
            )
        ''')
        self.conn.commit()

    def add_department(self, name):
        self.cursor.execute('INSERT INTO departments (name) VALUES (?)', (name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_staff(self, name):
        self.cursor.execute('INSERT INTO staff (name) VALUES (?)', (name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_course(self, name, department_id, periods_per_week):
        self.cursor.execute('''
            INSERT INTO courses (name, department_id, periods_per_week) 
            VALUES (?, ?, ?)
        ''', (name, department_id, periods_per_week))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_extra_activity(self, name, department_id, periods_per_week):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO extra_activities (name, department_id, periods_per_week)
            VALUES (?, ?, ?)
        """, (name, department_id, periods_per_week))
        self.conn.commit()

    def get_department_extra_activities(self, department_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, periods_per_week
            FROM extra_activities
            WHERE department_id = ?
        """, (department_id,))
        return cursor.fetchall()

    def assign_lab_to_staff(self, lab_id, staff_id):
        self.cursor.execute('''
            INSERT INTO lab_staff (lab_id, staff_id)
            VALUES (?, ?)
        ''', (lab_id, staff_id))
        self.conn.commit()

    def assign_course_to_staff(self, staff_id, course_id):
        self.cursor.execute('INSERT INTO staff_courses (staff_id, course_id) VALUES (?, ?)', (staff_id, course_id))
        self.conn.commit()

    def add_timetable_entry(self, day, period, shift, course_id, staff_id):
        self.cursor.execute('INSERT INTO timetable (day, period, shift, course_id, staff_id) VALUES (?, ?, ?, ?, ?)',
                            (day, period, shift, course_id, staff_id))
        self.conn.commit()

    def get_departments(self):
        self.cursor.execute('SELECT * FROM departments')
        return self.cursor.fetchall()

    def get_department(self, department_id):
        self.cursor.execute('SELECT * FROM departments WHERE id = ?', (department_id,))
        return self.cursor.fetchone()

    def get_courses(self, department_id=None):
        if department_id:
            self.cursor.execute('SELECT * FROM courses WHERE department_id = ?', (department_id,))
        else:
            self.cursor.execute('SELECT * FROM courses')
        return self.cursor.fetchall()

    def get_staff(self, staff_id=None):
        if staff_id:
            self.cursor.execute('SELECT id, name FROM staff WHERE id = ?', (staff_id,))
            return self.cursor.fetchall()
        else:
            self.cursor.execute('SELECT id, name FROM staff')
            return self.cursor.fetchall()

    def assign_staff_to_department(self, staff_id, department_id):
        self.cursor.execute('INSERT INTO staff_departments (staff_id, department_id) VALUES (?, ?)', (staff_id, department_id))
        self.conn.commit()

    def get_staff_extra_activities(self, staff_id):
        self.cursor.execute('''
            SELECT ea.id, ea.name, ea.periods_per_week
            FROM extra_activities ea
            JOIN staff_extra_activities sea ON ea.id = sea.extra_activity_id
            WHERE sea.staff_id = ?
        ''', (staff_id,))
        return self.cursor.fetchall()

    def assign_extra_activity_to_staff(self, staff_id, extra_activity_id):
        self.cursor.execute('INSERT INTO staff_extra_activities (staff_id, extra_activity_id) VALUES (?, ?)', 
                            (staff_id, extra_activity_id))
        self.conn.commit()

    def delete_staff_departments(self, staff_id):
        self.cursor.execute('DELETE FROM staff_departments WHERE staff_id = ?', (staff_id,))
        self.conn.commit()

    def get_courses_by_department(self, department_id):
        self.cursor.execute('SELECT * FROM courses WHERE department_id = ?', (department_id,))
        return self.cursor.fetchall()

    def update_department(self, dept_id, name):
        self.cursor.execute('UPDATE departments SET name = ? WHERE id = ?', (name, dept_id))
        self.conn.commit()

    def remove_extra_activity_from_staff(self, staff_id, extra_activity_id):
        self.cursor.execute('DELETE FROM staff_extra_activities WHERE staff_id = ? AND extra_activity_id = ?', 
                        (staff_id, extra_activity_id))
        self.conn.commit()

    def delete_department(self, dept_id):
        self.cursor.execute('DELETE FROM departments WHERE id = ?', (dept_id,))
        self.cursor.execute('DELETE FROM courses WHERE department_id = ?', (dept_id,))
        self.cursor.execute('DELETE FROM staff_departments WHERE department_id = ?', (dept_id,))
        self.cursor.execute('DELETE FROM extra_activities WHERE department_id = ?', (dept_id,))
        self.conn.commit()

    def delete_staff_courses(self, staff_id):
        self.cursor.execute('DELETE FROM staff_courses WHERE staff_id = ?', (staff_id,))
        self.conn.commit()

    def delete_staff_extra_activities(self, staff_id):
        self.cursor.execute('DELETE FROM staff_extra_activities WHERE staff_id = ?', (staff_id,))
        self.conn.commit()

    def get_staff_departments(self, staff_id):
        self.cursor.execute('''
            SELECT d.id, d.name
            FROM departments d
            JOIN staff_departments sd ON d.id = sd.department_id
            WHERE sd.staff_id = ?
        ''', (staff_id,))
        return self.cursor.fetchall()

    def get_extra_activities(self):
        self.cursor.execute('SELECT * FROM extra_activities')
        return self.cursor.fetchall()

    def get_staff_courses(self, staff_id):
        self.cursor.execute('''
            SELECT c.id, c.name
            FROM courses c
            JOIN staff_courses sc ON c.id = sc.course_id
            WHERE sc.staff_id = ?
        ''', (staff_id,))
        return self.cursor.fetchall()

    def get_department_courses(self, department_id):
        self.cursor.execute('SELECT * FROM courses WHERE department_id = ?', (department_id,))
        return self.cursor.fetchall()

    def get_timetable(self, shift, department_id=None):
        if department_id:
            self.cursor.execute('''
                SELECT t.day, t.period, t.shift, c.name, GROUP_CONCAT(s.name, ', ')
                FROM timetable t
                LEFT JOIN courses c ON t.course_id = c.id
                LEFT JOIN staff s ON t.staff_id = s.id
                WHERE t.shift = ? AND c.department_id = ?
                GROUP BY t.day, t.period, t.shift, c.name
            ''', (shift, department_id))
        else:
            self.cursor.execute('''
                SELECT t.day, t.period, t.shift, c.name, GROUP_CONCAT(s.name, ', ')
                FROM timetable t
                LEFT JOIN courses c ON t.course_id = c.id
                LEFT JOIN staff s ON t.staff_id = s.id
                WHERE t.shift = ?
                GROUP BY t.day, t.period, t.shift, c.name
            ''', (shift,))
        return self.cursor.fetchall()

    def get_course_staff(self, course_id):
        self.cursor.execute('''
            SELECT s.id, s.name
            FROM staff s
            JOIN staff_courses sc ON s.id = sc.staff_id
            WHERE sc.course_id = ?
        ''', (course_id,))
        return self.cursor.fetchall()

    def get_free_staff(self, day, period, shift):
        self.cursor.execute('''
            SELECT DISTINCT s.id, s.name
            FROM staff s
            JOIN staff_courses sc ON s.id = sc.staff_id
            WHERE s.id NOT IN (
                SELECT staff_id
                FROM timetable
                WHERE day = ? AND period = ? AND shift = ?
            )
        ''', (day, period, shift))
        return self.cursor.fetchall()

    def get_course_periods_today(self, course_id, day, shift):
        self.cursor.execute('''
            SELECT COUNT(*)
            FROM timetable
            WHERE course_id = ? AND day = ? AND shift = ?
        ''', (course_id, day, shift))
        return self.cursor.fetchone()[0]

    def get_timetable_entry(self, day, period, shift, department_id=None):
        if department_id:
            self.cursor.execute('''
                SELECT *
                FROM timetable t
                JOIN courses c ON t.course_id = c.id
                WHERE t.day = ? AND t.period = ? AND t.shift = ? AND c.department_id = ?
            ''', (day, period, shift, department_id))
        else:
            self.cursor.execute('''
                SELECT *
                FROM timetable
                WHERE day = ? AND period = ? AND shift = ?
            ''', (day, period, shift))
        return self.cursor.fetchone()

    def update_staff(self, staff_id, name, department_id):
        self.cursor.execute('UPDATE staff SET name = ? WHERE id = ?', (name, staff_id))
        self.cursor.execute('DELETE FROM staff_departments WHERE staff_id = ?', (staff_id,))
        self.cursor.execute('INSERT INTO staff_departments (staff_id, department_id) VALUES (?, ?)', (staff_id, department_id))
        self.conn.commit()

    def get_timetable_entry_by_staff(self, day, period, shift, staff_id):
        self.cursor.execute('''
            SELECT * FROM timetable
            WHERE day = ? AND period = ? AND shift = ? AND staff_id = ?
        ''', (day, period, shift, staff_id))
        return self.cursor.fetchone()

    def update_course(self, course_id, name, department_id, periods_per_week):
        self.cursor.execute('''
            UPDATE courses
            SET name = ?, department_id = ?, periods_per_week = ?
            WHERE id = ?
        ''', (name, department_id, periods_per_week, course_id))
        self.conn.commit()

    def get_staff_by_department(self, department_id):
        self.cursor.execute('''
            SELECT s.id, s.name
            FROM staff s
            JOIN staff_departments sd ON s.id = sd.staff_id
            WHERE sd.department_id = ?
        ''', (department_id,))
        return self.cursor.fetchall()

    def delete_course(self, course_id):
        self.cursor.execute('DELETE FROM courses WHERE id = ?', (course_id,))
        self.cursor.execute('DELETE FROM staff_courses WHERE course_id = ?', (course_id,))
        self.cursor.execute('DELETE FROM timetable WHERE course_id = ?', (course_id,))
        self.conn.commit()

    def delete_course_from_staff(self, staff_id, course_id):
        self.cursor.execute('DELETE FROM staff_courses WHERE staff_id = ? AND course_id = ?', (staff_id, course_id))
        self.conn.commit()

    def delete_timetable(self, shift, department_id=None):
        if department_id:
            self.cursor.execute('''
                DELETE FROM timetable
                WHERE shift = ? AND course_id IN (SELECT id FROM courses WHERE department_id = ?)
            ''', (shift, department_id))
        else:
            self.cursor.execute('DELETE FROM timetable WHERE shift = ?', (shift,))
        self.conn.commit()

    def update_extra_activity(self, activity_id, name=None, periods_per_week=None):
        update_fields = []
        values = []
        if name is not None:
            update_fields.append("name = ?")
            values.append(name)
        if periods_per_week is not None:
            update_fields.append("periods_per_week = ?")
            values.append(periods_per_week)
        
        if not update_fields:
            return  # Nothing to update
        
        query = f"UPDATE extra_activities SET {', '.join(update_fields)} WHERE id = ?"
        values.append(activity_id)
        
        self.cursor.execute(query, tuple(values))
        self.conn.commit()

    def delete_extra_activity(self, activity_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM extra_activities
            WHERE id = ?
        """, (activity_id,))
        self.conn.commit()

    def add_lab(self, name, department_id, periods_per_week):
        self.cursor.execute('INSERT INTO labs (name, department_id, periods_per_week) VALUES (?, ?, ?)', 
                            (name, department_id, periods_per_week))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_lab_staff(self, lab_id):
        self.cursor.execute('''
            SELECT s.id, s.name
            FROM staff s
            JOIN lab_staff ls ON s.id = ls.staff_id
            WHERE ls.lab_id = ?
        ''', (lab_id,))
        return self.cursor.fetchall()

    def get_department_labs(self, department_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, periods_per_week
            FROM labs
            WHERE department_id = ?
        """, (department_id,))
        return cursor.fetchall()

    def update_lab(self, lab_id, name=None, periods_per_week=None):
        update_fields = []
        values = []
        if name is not None:
            update_fields.append("name = ?")
            values.append(name)
        if periods_per_week is not None:
            update_fields.append("periods_per_week = ?")
            values.append(periods_per_week)
        
        if not update_fields:
            return  # Nothing to update
        
        query = f"UPDATE labs SET {', '.join(update_fields)} WHERE id = ?"
        values.append(lab_id)
        
        self.cursor.execute(query, tuple(values))
        self.conn.commit()

    def delete_lab(self, lab_id):
        self.cursor.execute('DELETE FROM labs WHERE id = ?', (lab_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()