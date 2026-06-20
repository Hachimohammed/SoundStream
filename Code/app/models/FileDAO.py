from app import app
from typing import *
from datetime import datetime
import sqlite3
from app.models.FileDAOInterface import FileDAOInterface
from app.models.File import File


class FileDAO(FileDAOInterface) :

    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'
    
    def _getDbConnection(self) -> sqlite3.Connection:
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn

    def findFileById(self,id_file :int) -> Optional[File]:
        """Return a file from the database using its unique identifier."""
        conn = self._getDbConnection()
        query = "SELECT * FROM file WHERE id_file = ?;"

        file=conn.execute(query,(id_file,)).fetchone()

        conn.close()
        if file :
            return File(dict(file))
        else :
            return None
        
    def findByName(self, name: str) -> Optional[File]:
        '''Return a file from the database using its name'''
        conn = self._getDbConnection()
        query = "SELECT * FROM file WHERE file_name = ?;"
        
        row = conn.execute(query, (name,)).fetchone()
        conn.close()

        if row:
            return File(dict(row))
        return None
    
    def findAllFile(self)->list[File]:
        '''Return all files stored in the database'''
        conn = self._getDbConnection()

        all_file=conn.execute("SELECT * FROM file ;").fetchall()

        conn.close()
        
        instance_file=[]
        if all_file :
            instance_file=[]
            for file in all_file:
                instance_file.append(File(dict(file)))
        return instance_file

    def createFile(self,name:str ,path:str ,time_length:str, type_file:str ) -> int :
        '''Insert a new file entry into the database'''
        conn = self._getDbConnection()
        
        # J'ajoute upload_date car il est dans ta requête, vérifie qu'il est dans ta table !
        query = "INSERT INTO file (file_name, path, time_length, upload_date, type_file) VALUES (?, ?, ?, ?, ?);"
        data = (name, path, time_length, datetime.now(), type_file)
        try:
            cursor = conn.execute(query, data)
            conn.commit()
            new_id = cursor.lastrowid
            
            return new_id
        except Exception as e: 
            print("error") 
            return -1
        finally:
            conn.close()

    def deleteFile(self,id_file:int) -> bool :
        '''Delete a file and its associations from the database'''
        conn = self._getDbConnection()
        query_composition_table = "DELETE FROM composition WHERE id_file = ?;"
        query_file_table= "DELETE FROM file WHERE id_file=?;"

        try :
            conn.execute(query_composition_table,(id_file,))
            conn.commit()

            conn.execute(query_file_table,(id_file,))
            conn.commit()
        except :
            return False
        else :
            return True
        finally:
            conn.close()

    def getFilesInPlaylist(self, playlist_id: int) -> List[File]:
        """
        Retrieves all file objects associated with a specific playlist.

        It joins the 'file' table with the 'composition' table to find
        which files belong to the given playlist ID.

        Args:
            playlist_id (int): The unique identifier of the playlist.

        Returns:
            List[File]: A list of File objects (empty list if none found).
        """
        conn = self._getDbConnection()
        
        # Execute the SQL query using a JOIN to link files and playlists
        files = conn.execute('''
            SELECT f.*
            FROM file f
            JOIN composition c ON f.id_file = c.id_file
            WHERE c.id_playlist = ?
            ORDER BY f.file_name;
        ''', (playlist_id,)).fetchall()
        
        conn.close()
        instance_file = []
        for f in files:
            instance_file.append(File(dict(f)))

        return instance_file



        

        

