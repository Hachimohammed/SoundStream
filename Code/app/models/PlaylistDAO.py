from datetime import datetime, timedelta
import sqlite3
from app import app
from app.models.Playlist import Playlist
from app.models.PlaylistDAOInterface import PlaylistDAOInterface
import os

class PlaylistDAO(PlaylistDAOInterface):

    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'

    def _getDbConnection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn
    
    def findAll(self) -> list[Playlist]|None:
        """ Get all playlists  """
        conn = self._getDbConnection()
        playlists = conn.execute('SELECT * FROM playlist;').fetchall()
        playlistList = list()
        for playlist in playlists : 
            playlistList.append(Playlist(dict(playlist)))
        conn.close()

        if playlistList :
            return playlistList
        return None

    def findById(self, playlist_id) -> Playlist|None:
        """ Get a playlist by its ID """
        conn = self._getDbConnection()
        playlist = conn.execute(
            'SELECT * FROM playlist WHERE id_playlist = ?;',
            (playlist_id,)
        ).fetchone()
        conn.close()
        
        if playlist:
            return Playlist(dict(playlist))
        return None
    
    ####################
    ## EDIT PLAYLISTS ##
    ####################
    
    def addFileToPlaylist(self, id_playlist: int, id_file: int) -> bool:
        """
        Links an existing file to a playlist in the database.
        It checks for duplicates before inserting into the 'composition' table.

        Args:
            id_file (int): The unique ID of the file to add.
            id_playlist (int): The unique ID of the target playlist.

        Returns:
            bool: True if the file was successfully added.
                  False if the file was already in the playlist or if an error occurred.
        """
        conn = self._getDbConnection()

        try:
            #  Check if the link already exists to prevent duplicates
            query_check = "SELECT * FROM composition WHERE id_playlist = ? AND id_file = ?;"
            exists = conn.execute(query_check, (id_playlist, id_file)).fetchone()

            if not exists:
                #  Create the link in the association table
                query = "INSERT INTO composition (id_playlist, id_file) VALUES (?, ?);"
                conn.execute(query, (id_playlist, id_file))
                conn.commit()
                return True
            
            # The file is already in the playlist
            return False

        except Exception as e:
            print(f"Error linking file to playlist: {e}")
            return False    
        finally:
            # Always close the connection to avoid memory leaks
            conn.close()  
       
    def removeFileFromPlaylist(self, playlist_id: int, file_id: int) -> bool:
        """
        Removes a file from a playlist (deletes the link) and updates the modification date.

        Args:
            playlist_id (int): The ID of the playlist.
            file_id (int): The ID of the file to remove.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        conn = self._getDbConnection()
        
        try:
            # 1. Remove the link in the join table
            query_remove ="DELETE FROM composition WHERE id_playlist = ? AND id_file = ?"
            conn.execute(query_remove, (playlist_id, file_id))
            
            # 2. Update the playlist timestamp
            query_update ="UPDATE playlist SET last_update_date = ? WHERE id_playlist = ?"
            conn.execute(query_update, (datetime.now(), playlist_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error removing file from playlist: {e}")
            conn.rollback() # Cancel changes if an error occurs
            return False
            
        finally:
            # CRITICAL: Always close the connection, even if it crashes
            conn.close()

    def createPlaylist(self, name: str) -> None:
        """ Create a new playlist with the given name """
        conn = self._getDbConnection()
        print('Creating playlist in DAO:', name)
        conn.execute(
            '''INSERT INTO playlist (playlist_name, creation_date, last_update_date, expiration_date) 
            VALUES (?, ?, ?, ?);''',
            (name, datetime.now(), datetime.now(), datetime.now() + timedelta(days=30))
        )
        conn.commit()
        conn.close()

    def deletePlaylist(self, playlist_id: int) -> None:
        """ Delete a playlist by its ID """
        conn = self._getDbConnection()
        print('Deleting playlist in DAO:', playlist_id)
        conn.execute('DELETE FROM composition WHERE id_playlist = ?', (playlist_id,))
        conn.execute('DELETE FROM interaction WHERE id_playlist = ?', (playlist_id,))
        conn.execute('DELETE FROM planned WHERE id_playlist = ?', (playlist_id,))
        conn.execute('DELETE FROM playlist WHERE id_playlist = ?', (playlist_id,))
        conn.commit()
        conn.close()

    ############################
    ## EDIT PLAYLIST FOR DAYS ##
    ############################

    def getAllDays(self) -> list:
        """ Get all days in the planning """
        conn = self._getDbConnection()
        days = conn.execute('SELECT * FROM planning ORDER BY diffusing_day').fetchall()
        conn.close()
        return days
    
    def getPlannedPlaylistsForDay(self, day_name) -> list:
        conn = self._getDbConnection()
        playlists = conn.execute('''
            SELECT p.*, pl.start_time
            FROM playlist p
            JOIN planned pl ON p.id_playlist = pl.id_playlist
            WHERE pl.day_ = ?
            ORDER BY pl.start_time
        ''', (day_name,)).fetchall()
        conn.close()
        return playlists
    
    def addPlaylistToDay(self, playlist_id, day_name, start_time) -> None:
        """ Get all playlists planned for a specific day """
        conn = self._getDbConnection()
        
        exists = conn.execute('''
            SELECT * FROM planned 
            WHERE id_playlist = ? AND day_ = ?
        ''', (playlist_id, day_name)).fetchone()
        
        if exists:
            conn.execute('''
                UPDATE planned 
                SET start_time = ? 
                WHERE id_playlist = ? AND day_ = ?
            ''', (start_time, playlist_id, day_name))
        else:
            conn.execute('''
                INSERT INTO planned (id_playlist, day_, start_time)
                VALUES (?, ?, ?)
            ''', (playlist_id, day_name, start_time))
        
        conn.commit()
        conn.close()

    def removeAllPlaylistsFromDay(self, day_name) -> None:
        """ Remove all playlists from a specific day """
        conn = self._getDbConnection()
        conn.execute('DELETE FROM planned WHERE day_ = ?', (day_name,))
        conn.commit()
        conn.close()

    def deleteObsoletePlaylists(self) -> int:
        """ Delete playlists that have expired """
        conn = self._getDbConnection()
        try:
            # 1. On cible les playlists périmées (Date d'expiration < Maintenant)
            subquery = "SELECT id_playlist FROM playlist WHERE expiration_date < datetime('now')"

            # 2. On supprime les dépendances (Nettoyage en cascade manuel)
            conn.execute(f"DELETE FROM planned WHERE id_playlist IN ({subquery})")
            conn.execute(f"DELETE FROM composition WHERE id_playlist IN ({subquery})")
            conn.execute(f"DELETE FROM interaction WHERE id_playlist IN ({subquery})")
            
            # 3. On supprime enfin la playlist elle-même
            cursor = conn.execute(f"DELETE FROM playlist WHERE expiration_date < datetime('now')")
            
            count = cursor.rowcount # Nombre de playlists supprimées
            conn.commit()
            
            if count > 0:
                print(f"AUTO-CLEANUP : {count} playlists obsolètes supprimées.")
                
            return count

        except Exception as e:
            print(f"Erreur lors du nettoyage automatique : {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    ####################################
    ## Calendar view & Timetable view ##
    ####################################
    
    def getRawScheduleForDay(self, day_name: str) -> list:
        """ Retrieve raw schedule data for a specific day """
        conn = self._getDbConnection()
        conn.row_factory = sqlite3.Row

        sql = '''
            SELECT pl.start_time as playlist_start, p.playlist_name, f.file_name, f.time_length, pl.id_playlist as id_playlist
            FROM planned pl
            JOIN composition c ON pl.id_playlist = c.id_playlist
            JOIN file f ON c.id_file = f.id_file
            JOIN playlist p ON pl.id_playlist = p.id_playlist
            WHERE pl.day_ = ?
            ORDER BY pl.start_time, c.rowid
        '''
        
        cur = conn.execute(sql, (day_name,))
        rows = cur.fetchall()
        conn.close()
        return rows