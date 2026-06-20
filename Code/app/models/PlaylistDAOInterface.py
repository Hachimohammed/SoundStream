from app.models.Playlist import Playlist


class PlaylistDAOInterface :

    def findAll(self) -> list[Playlist]|None:
        """ Get all playlists  """
        pass

    def findById(self, playlist_id) -> Playlist|None:
        """ Get a playlist by its ID """
        pass

    ####################
    ## EDIT PLAYLISTS ##
    ####################

    def addFileToPlaylist(self, id_playlist: int, id_file: int) -> bool:
        """ Add a file to a playlist """
        pass

    def removeFileFromPlaylist(self, playlist_id: int, file_id: int) -> bool:
        """ Remove a file from a playlist """
        pass

    def createPlaylist(self, name: str) -> None:
        """ Create a new playlist with the given name """
        pass

    ############################
    ## EDIT PLAYLIST FOR DAYS ##
    ############################

    def getAllDays(self) -> list:
        """ Get all days in the planning """
        pass

    def getPlannedPlaylistsForDay(self, day_name) -> list:
        """ Get all playlists planned for a specific day """
        pass

    def addPlaylistToDay(self, playlist_id, day_name, start_time) -> None:
        """ Add a playlist to a specific day with a start time """
        pass
    
    def removeAllPlaylistsFromDay(self, day_name) -> None:
        """ Remove all playlists from a specific day """
        pass

    ####################################
    ## Calendar view & Timetable view ##
    ####################################

    def getRawScheduleForDay(self, day_name: str) -> list:
        """ Retrieve raw schedule data for a specific day """
        pass

