from app import app
import sqlite3
from app.models.OrganisationDAOInterface import OrganisationDAOInterface
from app.models.Organisation import Organisation
from typing import List

class OrganisationDAO(OrganisationDAOInterface):
    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'
            
    def _getDbConnection(self) -> sqlite3.Connection:
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn
    
    def createOrganisation(self, name_orga: str) -> None:
        conn = self._getDbConnection()
        try:
            query = "INSERT INTO organisation (name_orga) VALUES (?);"
            conn.execute(query, (name_orga,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception("Error creating organisation : " + str(e)) # On signale l'erreur s'il y a un problème de création (= Exception levée)
        finally:
            conn.close()

    def getIdByName(self, orga_name: str) -> int|None:
        conn = self._getDbConnection()
        query = """ SELECT id_orga FROM organisation WHERE name_orga = ? """

        cursor = conn.execute(query, (orga_name,))
        result = cursor.fetchone()
        
        conn.close()
        
        # Si un résultat est trouvé, result est un tuple comme (112,)
        if result:
            return result[0] # On retourne juste le chiffre 112
        
        return None
    
    def findUserOrganisation(self, username: str) -> str:
        """ Get the organisation of a user by username """
        conn = self._getDbConnection()
        query = """
            SELECT o.name_orga 
            FROM user u
            JOIN work_link w ON u.id_user = w.id_user
            JOIN organisation o ON w.id_orga = o.id_orga
            WHERE u.username = ?
        """
        res = conn.execute(query, (username,)).fetchall()
        conn.close()
        return [row[0] for row in res]
    
    def getAllOrganisations(self) -> List[Organisation]:
        conn = self._getDbConnection()
        query = "SELECT * FROM organisation"

        cursor = conn.execute(query)
        results = cursor.fetchall()
        
        conn.close()
        
        return results