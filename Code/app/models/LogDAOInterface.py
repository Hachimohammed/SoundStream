from typing import *
from datetime import datetime
from app.models.Log import Log
class LogDAOInterface:

    def findAll(self) -> list[Log]:
        pass

    def findAllByOrganization(self, org_id: int) -> list[Log]:
        pass

    def createLog(self, type_log: str, text_log: str, date_log: datetime , id_orga: int) -> bool:
        pass

    def findTicketsByOrganization(self, org_id: int) -> list[Log]:
        pass
    
    def findAllTickets(self) -> list[Log]:
        pass

    def findAllMessageDiffused(self) -> list[Log]:
        pass

    def findTypesLog(self) -> list[str]:
        pass

    def findLogsByOrganizationByType(self, org_id: int, type_log: str) -> list[Log]:
        pass