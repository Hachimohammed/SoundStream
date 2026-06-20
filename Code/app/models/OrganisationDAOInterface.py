from typing import List
from app.models.Organisation import Organisation

class OrganisationDAOInterface:
    
    def createOrganisation(self, name_orga: str) -> None :
        pass
     
    def getIdByName(self, orga_name: str) -> int|None:
        pass

    def findUserOrganisation(self, username: str) -> str:
        pass

    def getAllOrganisations(self) -> List[Organisation]:
        pass