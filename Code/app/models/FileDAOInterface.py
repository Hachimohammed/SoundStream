from typing import Optional, List
from app.models.File import File

class FileDAOInterface :

    def createFile(self, name:str, path:str, time_length:str, type_file:str ) -> int :
        pass

    def deleteFile(self, id_file: int) -> bool :
        pass

    def findAllFile(self) -> List[File]:
        pass

    def findFileById(self,id_file: int) -> Optional[File]:
        pass

    def findByName(self, name: str) -> Optional[File]:
        pass

    def getFilesInPlaylist(self, playlist_id: int) -> List[File]:
        pass