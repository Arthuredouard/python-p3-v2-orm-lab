from __init__ import CURSOR, CONN

class Department:
    """Représente un département."""
    
    # Dictionnaire d'objets en cache pour stocker les instances de département
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        """Retourne une représentation en chaîne de caractères de l'objet."""
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @property
    def name(self):
        """Retourne le nom du département."""
        return self._name

    @name.setter
    def name(self, value):
        """Valide et définit le nom du département."""
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("Le nom doit être une chaîne de caractères non vide.")
        self._name = value

    @property
    def location(self):
        """Retourne l'emplacement du département."""
        return self._location

    @location.setter
    def location(self, value):
        """Valide et définit l'emplacement du département."""
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("L'emplacement doit être une chaîne de caractères non vide.")
        self._location = value

    @classmethod
    def create_table(cls):
        """Crée la table 'departments' si elle n'existe pas."""
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Supprime la table 'departments' si elle existe."""
        sql = """
            DROP TABLE IF EXISTS departments;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Sauvegarde l'instance de département dans la base de données."""
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """
        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, location):
        """Initialise une nouvelle instance et la sauvegarde dans la base de données."""
        department = cls(name, location)
        department.save()
        return department
    
    @classmethod
    def instance_from_db(cls, row):
        """Crée ou met à jour une instance de Department à partir d'une ligne de la base de données."""
        department = cls.all.get(row[0])
        if department:
            department.name = row[1]
            department.location = row[2]
        else:
            department = cls(row[1], row[2])
            department.id = row[0]
            cls.all[department.id] = department
        return department
    
    @classmethod
    def find_by_id(cls, id):
        """Trouve et retourne un département par son ID."""
        sql = """
            SELECT * FROM departments WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None
    
    @classmethod
    def find_by_name(cls, name):
        """Trouve et retourne un département par son nom."""
        sql = """
            SELECT * FROM departments WHERE name = ?
        """
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Met à jour l'enregistrement du département dans la base de données."""
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Supprime l'enregistrement du département de la base de données et de l'objet en cache."""
        sql = """
            DELETE FROM departments WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        del type(self).all[self.id]
        self.id = None
        
    @classmethod
    def get_all(cls):
        """Retourne une liste de toutes les instances de Department de la base de données."""
        sql = """
            SELECT * FROM departments
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def employees(self):
        """
        Retourne tous les employés associés à ce département.
        Note: The import is done inside the method to avoid a circular import.
        """
        from employee import Employee
        return [employee for employee in Employee.get_all() if employee.department_id == self.id]
