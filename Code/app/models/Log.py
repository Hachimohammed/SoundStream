from typing import TypedDict, Dict
from datetime import datetime

class SQLValue(TypedDict):
    id_log: int
    type_log: str
    text_log: str
    date_log: datetime
    id_orga: int


class Log:
    def __init__(self, dico: Dict[str, SQLValue]) -> None :
        self.id_log=dico['id_log']
        self.type_log=dico['type_log']
        self.text_log=dico['text_log']
        self.date_log=dico['date_log']
        self.id_orga=dico['id_orga']

    def toDict(self) -> dict :
        d =  {}
        d['id_log'] = self.id_log
        d['type_log'] = self.type_log
        d['text_log'] = self.text_log 
        d['date_log'] = self.date_log 
        d['id_orga'] = self.id_orga 
        return d