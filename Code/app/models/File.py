from typing import TypedDict, Dict
from datetime import datetime

class SQLValue(TypedDict):
    id_file: int
    name: str
    path: str
    time_length: str
    upload_date: datetime
    type_file: str

class File :
    def __init__(self, dico: Dict[str, SQLValue]) -> None :
        self.id_file = dico['id_file'] 
        self.name = dico['file_name']    
        self.path = dico['path']    
        self.time_length = dico['time_length'] 
        self.upload_date = dico['upload_date'] 
        self.type_file = dico['type_file'] 