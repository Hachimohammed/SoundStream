from typing import TypedDict, Dict
from datetime import datetime

class SQLValue(TypedDict):
    id_orga: int
    name_orga: str


class Organisation:
    
    def __init__(self, dico: Dict[str, SQLValue] ) -> None :
        self.id_orga=dico['id_orga']
        self.name_orga=dico['name_orga']