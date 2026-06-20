from typing import TypedDict, Dict
from datetime import datetime

class SQLValue(TypedDict):
    id_player: int
    name_place: str
    IP_adress: str
    state: str
    last_synchronization: datetime
    place_adress: str
    place_postcode: str
    place_city: str
    place_building_name: str
    device_name: str
    id_orga: int
    
class SongPlayer : 
    def __init__(self, dico: Dict[str, SQLValue]) -> None :
        self.id_player = dico['id_player']
        self.name_place = dico['name_place']
        self.IP_adress = dico['IP_adress']
        self.state = dico['player_state']
        self.last_synchronization = dico['last_synchronization']
        self.place_adress = dico['address_place']
        self.place_postcode = dico['postcode_place']
        self.place_city = dico['city_place']
        self.place_building_name = dico['building_name_place']
        self.device_name = dico['device_name']
        self.id_orga = dico['id_orga']