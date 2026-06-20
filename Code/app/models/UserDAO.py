import sqlite3
from app import app
from app.models.User import User
from app.models.UserDAOInterface import UserDAOInterface

import bcrypt

class UserDAO(UserDAOInterface):
    
    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'
    
    def _getDbConnection(self):
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn

    def _generatePWDHash(self, password) -> str:
        """ Generate password hash from plain text password """
        password_bytes = password.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        password_hashed = hashed_bytes.decode('utf-8')
        return password_hashed
    
    def createUser(self, username, password, role, organisation, email='', phone_number='') -> None:
        """ create a new user """
        if username in self.findUsersInOrganisation(organisation):
            raise ValueError("Username already exists in this organisation")
        
        conn = self._getDbConnection()

        if username not in self.findAllUsername():
            hashed_password = self._generatePWDHash(password)
            # ✅ CORRECTION : email et phone_number ajoutés dans l'INSERT (colonnes NOT NULL dans le schéma)
            query = 'INSERT INTO user (username, password, role, email, phone_number) VALUES (?,?,?,?,?);'
            conn.execute(query, (username, hashed_password, role, email, phone_number))

        conn.commit()
        conn.close()

        self.createLinkUserOrganisation(username, organisation)

    def createLinkUserOrganisation(self, username, organisation) -> None:
        """ Create a link between a user and an organisation """
        conn = self._getDbConnection()

        query_idUser = """
            SELECT u.id_user
            FROM user u
            WHERE u.username = ?
        """
        user_id = conn.execute(query_idUser, (username,)).fetchone()[0]


        query_idOrga = """
            SELECT o.id_orga
            FROM organisation o
            WHERE o.name_orga = ?
        """
        orga_id = conn.execute(query_idOrga, (organisation,)).fetchone()[0]
        print(user_id, orga_id)


        links = (user_id, orga_id)
        conn.execute("INSERT INTO work_link (id_user, id_orga) VALUES (?, ?)", links)
    
        conn.commit()
        conn.close()
        
    def findByUsername(self, username) -> User:
        """ Get user by username """
        conn = self._getDbConnection()
        res = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        conn.close()
        if res:
            return User(dict(res))
        return None

    # ✅ CORRECTION : méthode déplacée À L'INTÉRIEUR de la classe (indentation correcte)
    def findByEmail(self, email) -> 'User':
        """Get user by email"""
        conn = self._getDbConnection()
        res = conn.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
        conn.close()
        if res:
            return User(dict(res))
        return None

    # ✅ CORRECTION : méthode déplacée À L'INTÉRIEUR de la classe (indentation correcte)
    def updateEmail(self, username, new_email) -> None:
        """Update user email"""
        conn = self._getDbConnection()
        conn.execute('UPDATE user SET email = ? WHERE username = ?', (new_email, username))
        conn.commit()
        conn.close()
    
    def findUsersInOrganisation(self, organisation) -> list:
        """ Get all the users of an organisation """
        conn = self._getDbConnection()
        query = """
            SELECT u.username
            FROM user u
            JOIN work_link w ON u.id_user = w.id_user
            JOIN organisation o ON w.id_orga = o.id_orga
            WHERE o.name_orga = ?
        """
        res = conn.execute(query, (organisation,)).fetchall()
        conn.close()
        return [row[0] for row in res]

    def verifyUser(self, username, password) -> bool:
        """Verify if username and password are correct"""
        user = self.findByUsername(username)
        if user is None:
            return False
        hashed_pw = user.password.encode('utf-8')
        input_pw = password.encode('utf-8')
        return bcrypt.checkpw(input_pw, hashed_pw)
    
    def changePassword(self, username, password) -> None:
        """Change the password of the user"""
        conn = self._getDbConnection()
        hashed_password = self._generatePWDHash(password)
        query = 'UPDATE user SET password = ? WHERE username = ?'
        conn.execute(query, (hashed_password, username))
        conn.commit()
        conn.close()

    def deleteByUsername(self, username) -> None:
        """ Delete a user by username """ 
        conn = self._getDbConnection()
        query = 'DELETE FROM work_link WHERE id_user = (SELECT id_user FROM user WHERE username = ?)'
        conn.execute(query, (username,))
        conn.commit()
        query = 'DELETE FROM user WHERE username = ?'
        conn.execute(query, (username,))
        conn.commit()
        conn.close()

    def deleteUserOfOrganisation(self, username, organisation) -> None:
        """ Delete the user of an organisation """
        conn = self._getDbConnection()
        query = """
            DELETE FROM work_link
            WHERE id_user = (SELECT id_user FROM user WHERE username = ?)
            AND id_orga = (SELECT id_orga FROM organisation WHERE name_orga = ?)
        """
        conn.execute(query, (username, organisation))
        conn.commit()
        conn.close()

    def updateUserRole(self, username, new_role) -> None:
        """Update user role"""
        conn = self._getDbConnection()
        query = 'UPDATE user SET role = ? WHERE username = ?'
        conn.execute(query, (new_role, username))
        conn.commit()
        conn.close()

    def getOrganisationsByUsername(self, username) -> list:
        """Get the organisation names of a user"""
        conn = self._getDbConnection()
        query = """
            SELECT o.name_orga 
            FROM organisation o
            JOIN work_link w USING (id_orga)
            JOIN user u USING (id_user)
            WHERE u.username = ?
        """
        rows = conn.execute(query, (username,)).fetchall()
        result = [row['name_orga'] for row in rows]
        conn.close()
        return result if result else None
    
    def getRoleByUsername(self, username) -> str:
        """Get the role of a user"""
        conn = self._getDbConnection()
        query = 'SELECT role FROM user WHERE username = ?'
        result = conn.execute(query, (username,)).fetchone()
        conn.close()
        return result['role'] if result else None

    def getAllRoles(self) -> list:
        """Get all available roles from the role table"""
        conn = self._getDbConnection()
        query = 'SELECT role FROM role'
        results = conn.execute(query).fetchall()
        conn.close()
        return [row[0] for row in results]

    def findAll(self) -> list:
        """ Get all users """
        conn = self._getDbConnection()
        users = conn.execute('SELECT * FROM user;').fetchall()
        userList = [User(dict(user)) for user in users]
        conn.close()
        return userList
    
    def findAllUsername(self) -> list:
        """ Get all usernames """
        conn = self._getDbConnection()
        users = conn.execute('SELECT username FROM user;').fetchall()
        usernameList = [user['username'] for user in users]
        conn.close()
        return usernameList 
    
    def updatePhoneNumber(self, username, new_phone_number) :
        """Update user phone number"""
        conn = self._getDbConnection()
        conn.execute('UPDATE user SET phone_number = ? WHERE username = ?', (new_phone_number, username))
        conn.commit()
        conn.close()

    def updateUsername(self, username, new_username) :
        """Update username of an user"""
        conn = self._getDbConnection()
        conn.execute('UPDATE user SET username = ? WHERE username = ?', (new_username, username))
        conn.commit()
        conn.close()