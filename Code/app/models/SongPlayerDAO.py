import sqlite3
from app import app
from app.models.SongPlayer import SongPlayer
from app.models.SongPlayerDAOInterface import SongPlayerDAOInterface

class SongPlayerDAO(SongPlayerDAOInterface) :
    
    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'
    
    def _getDbConnection(self) -> sqlite3.Connection:
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn

    def createDevice(self, name_place, ip_address, state, place_address, place_postcode, place_city, place_building_name, device_name, orga_id) -> None:
        """ Create a new song player in the database. """
        conn = self._getDbConnection()
        try:
            query = '''
            INSERT INTO song_player
            (name_place, IP_adress, player_state, last_synchronization, address_place, postcode_place, city_place, building_name_place, device_name, id_orga)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?);
            '''
            conn.execute(query, (name_place, ip_address, state, place_address, place_postcode, place_city, place_building_name, device_name, orga_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def addSongPlayerInDb(self, data_form_to_form) -> None:
        """ Add a new song player to the database. """
        conn = self._getDbConnection()
        try:
            query = '''
            INSERT INTO song_player
            (name_place, IP_adress, player_state, last_synchronization, address_place, postcode_place, city_place, building_name_place, device_name, id_orga)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?);
            '''
            conn.execute(query, data_form_to_form)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    def updateDbSongPlayer(self, form_data, id_player) -> None:
        """ Update a song player in the database. """
        # Get a database connection
        conn = self._getDbConnection()
        
        #Get all key from the form
        updated_columns=list(form_data.keys())

        # Get all values from the form
        values = list(form_data.values())

        # Create the SQL update query
        # Each column uses "column = ?" to protect against SQL injection
        set_clause = ', '.join([f'{col} = ?' for col in updated_columns])
        requete = f"UPDATE song_player SET {set_clause} WHERE id_player = ?"
        # Execute the query with parameters
        # Using "?" protects the query from SQL injection
        conn.execute(requete, tuple(values) + (id_player,))

        # Save changes to the database
        conn.commit()
        
    def deleteSongPlayerInDb(self,id_song_player) -> None:
        """ Delete a song player to the database """
        conn = self._getDbConnection()

        requete = '''DELETE FROM song_player WHERE id_player = ?'''
        conn.execute(requete,(id_song_player,))

        conn.commit()

    def findByID(self, id_player) -> SongPlayer:
        """ Get song player by the id of the song player """
        conn = self._getDbConnection()
        # Use a parameterized query to prevent SQL injection
        res = conn.execute('SELECT * FROM song_player WHERE id_player = ?;', (id_player,)).fetchone()
        conn.close()

        if res:
            return SongPlayer(dict(res))
        return  []
    
    def findByOrganisation(self, name_orga) -> SongPlayer:
        """ Get song player by organisation name """
        conn = self._getDbConnection()
        songplayers = conn.execute('SELECT * FROM song_player JOIN organisation USING(id_orga) WHERE name_orga = ?;', (name_orga,)).fetchall()
        songplayerList = list()
        for songplayer in songplayers : 
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList:
            return songplayerList
        return []
    
    def findByState(self, state) -> SongPlayer:
        """ Get song player by state """
        conn = self._getDbConnection()
        songplayers = conn.execute('SELECT * FROM song_player WHERE player_state = ?;', (state,)).fetchall()
        songplayerList = list()
        for songplayer in songplayers :
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList:
            return songplayerList
        return []
    
    def findAllByOrganisationInBd(self, id_orga) -> list:
        """
        LA TCHIM C PAS EN DOUBLE CA ?
        """
        conn = self._getDbConnection()
        songplayers = conn.execute("""SELECT * FROM song_player WHERE id_orga = ?;""", (id_orga,)).fetchall()
        songplayerList = list()
        for songplayer in songplayers : 
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList :
            return songplayerList
        return []

    def findAllByOrganisationAndStatus(self, id_orga, status) -> list:
        """ find all song players by organisation and status """
        conn = self._getDbConnection()

        sql = "SELECT * FROM song_player WHERE id_orga = ? AND player_state = ?;"

        songplayers = conn.execute(sql, (id_orga, status)).fetchall()

        songplayerList = list()
        for songplayer in songplayers: 
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList:
            return songplayerList
        return []

    def findAll(self) -> list[SongPlayer]:
        conn = self._getDbConnection()
        songplayers = conn.execute('SELECT * FROM song_player;').fetchall()
        songplayerList = list()
        for songplayer in songplayers : 
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList :
            return songplayerList
        return []
    
    def findAllBuildingNames(self) -> list:
        """Get all distinct building names from the song players."""
        conn = self._getDbConnection()
        query = "SELECT building_name FROM building;"
        cursor = conn.execute(query)
        results_query = cursor.fetchall()
        conn.close()
        
        # Extract building names from the result set
        building_names = []
        for row_query in results_query:
            building_names.append(row_query['building_name'])

        return building_names
    
    def UpdateState(self, state, id_player) -> None :
        """ Update the state of a specific song player """
        conn = self._getDbConnection()
        conn.execute('UPDATE song_player SET player_state = ? WHERE id_player =  ?;', (state,id_player))
        conn.commit()
        conn.close()

    def findAllOnlineDevices(self) -> list[SongPlayer]:
        conn = self._getDbConnection()
        songplayers = conn.execute("SELECT * FROM song_player WHERE player_state = 'ONLINE';").fetchall()
        players_online_list = list()

        for songplayer in songplayers :
            players_online_list.append(SongPlayer(dict(songplayer)))
        
        conn.close()
        return players_online_list