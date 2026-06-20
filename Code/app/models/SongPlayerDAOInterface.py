from app.models.SongPlayer import SongPlayer


class SongPlayerDAOInterface :

    def createDevice(self, name_place, ip_address, address_place, city_place, postcode_place, building_name_place, orga_id) -> None:
        """
        Create a new song player in the database.

            Args:
                name_place (str): The name of the place
                ip_address (str): The IP address of the song player
                address_place (str): The address of the place
                city_place (str): The city of the place
                postcode_place (str): The postcode of the place
                building_name_place (str): The building name of the place
                orga_id (int): The ID of the organization
            Returns:
                None
        """
        pass

    def addSongPlayerInDb(self, data_form_to_form) -> None:
        """ Add a new song player to the database. """
        pass

    def updateDbSongPlayer(self, form_data, id_player) -> None:
        """ Update a song player in the database. """
        pass

    def deleteSongPlayerInDb(self,id_song_player) -> None:
        """ Delete a song player to the database """
        pass

    def findByID(self, id_song_player) -> SongPlayer:
        """ Get song player by the id of the song player """
        pass

    def findByOrganisation(self, name_orga) -> SongPlayer:
        """ Get song player by organisation name """
        pass

    def findByState(self, state) -> SongPlayer:
        """ Get song player by state """
        pass

    def findAllByOrganisationInBd(self, id_orga) -> list:
        """
        Get all song players belonging to the same organization.

            Args:
                id_orga(int): The organization ID
            Returns:
                List[SongPlayer] : A list of SongPlayer instances
        """
        pass    

    def findAllByOrganisationAndStatus(self, id_orga, status) -> list:
        """ find all song players by organisation and status """
        pass

    def findAll(self) -> list[SongPlayer]:
        """
        Get all song players from the database.

            Returns:
                List[SongPlayer]: A list of all SongPlayer instances found in the database.
        """
        pass

    def findAllBuildingNames(self) -> list:
        """Get all distinct building names from the song players."""
        pass

    def UpdateState(self, state, id_song_player) -> None :
        """ Update the state of a specific song player """
        pass