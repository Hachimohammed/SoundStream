from typing import TypedDict, Dict
from datetime import datetime

class SQLValue(TypedDict):
    id_playlist: int
    name: str
    creation_date: datetime
    expiration_date: datetime
    last_update_date: datetime

class Playlist : 
    def __init__(self, dico: Dict[str, SQLValue]) -> None :
        self.id_playlist = dico['id_playlist']
        self.name = dico['playlist_name']
        self.creation_date = dico['creation_date']
        self.expiration_date = dico['expiration_date']
        self.last_update_date = dico['last_update_date']