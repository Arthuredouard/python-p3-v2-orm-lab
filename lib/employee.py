from __init__ import CURSOR, CONN
from department import Department

class Employee:
    """Represents an employee."""

    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        """Returns a string representation of the object."""
        return (
            f"<Employee {self.id}: {self.name}, {self.job_title}, "
            + f"Department ID: {self.department_id}>"
        )

    @property
    def name(self):
        """Returns the name of the employee."""
        return self._name

    @name.setter
    def name(self, value):
        """Validates and sets the name of the employee."""
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("Name must be a non-empty string.")
        self._name = value

    @property
    def job_title(self):
        """Returns the job title of the employee."""
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        """Validates and sets the job title of the employee."""
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("Job title must be a non-empty string.")
        self._job_title = value

    @property
    def department_id(self):
        """Returns the department ID of the employee."""
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        """Validates and sets the department ID of the employee."""
        if not isinstance(value, int) or not Department.find_by_id(value):
            raise ValueError("department_id must be the ID of a persisted Department instance.")
        self._department_id = value
    
    @property
    def department(self):
        return Department.find_by_id(self.department_id)
    
    @classmethod
    def create_table(cls):
        """Creates the 'employees' table if it does not exist."""
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drops the 'employees' table if it exists."""
        sql = """
            DROP TABLE IF EXISTS employees;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Saves the employee instance to the database."""
        sql = """
            INSERT INTO employees (name, job_title, department_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, job_title, department_id):
        """Initializes a new employee instance and saves it to the database."""
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee
    
    @classmethod
    def instance_from_db(cls, row):
        """Creates or updates an Employee instance from a database row."""
        employee = cls.all.get(row[0])
        if employee:
            employee.name = row[1]
            employee.job_title = row[2]
            employee.department_id = row[3]
        else:
            employee = cls(row[1], row[2], row[3])
            employee.id = row[0]
            cls.all[employee.id] = employee
        return employee
    
    @classmethod
    def find_by_id(cls, id):
        """Finds and returns an employee by their ID."""
        sql = """
            SELECT * FROM employees WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None
    
    @classmethod
    def find_by_name(cls, name):
        """Finds and returns an employee by their name."""
        sql = """
            SELECT * FROM employees WHERE name = ?
        """
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Updates the employee's record in the database."""
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        """Deletes the employee's record from the database and the cache."""
        sql = """
            DELETE FROM employees WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        del type(self).all[self.id]
        self.id = None
        
    @classmethod
    def get_all(cls):
        """Returns a list of all Employee instances from the database."""
        sql = """
            SELECT * FROM employees
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def reviews(self):
        """
        Returns all reviews associated with this employee.
        Note: The import is done inside the method to avoid a circular import.
        """
        from review import Review
        return [review for review in Review.get_all() if review.employee_id == self.id]
