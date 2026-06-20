from app.models.LogDAO import LogSqliteDAO as LogDAO
from typing import *
from datetime import datetime

class LogService:
    ''' This class will manipulate the log to give 
    what the LogController wants.'''

    def __init__(self):
        self.ldao = LogDAO()

    def getLogs(self) -> dict:
        logs = self.ldao.findAll()
        list_logs = list()

        for log in logs:
            list_logs.append(log.toDict())

        return list_logs
    
    def getLogsByOrganisation(self, id_orga: int) -> list[dict]:
        logs = self.ldao.findAllByOrganization(id_orga)
        list_logs = list()
        for log in logs :
            list_logs.append(log.toDict())

        return list_logs
    
    def getTicketsByOrganisation(self, id_orga: int) -> list[dict]:
        tickets = self.ldao.findTicketsByOrganization(id_orga)  # New method to get ticket logs by organization
        list_tickets = list()
        for ticket in tickets :
            list_tickets.append(ticket.toDict())

        return list_tickets
    
    def getTicketLogs(self) -> list[dict]:
        tickets = self.ldao.findAllTickets()  # New method to get ticket logs
        list_tickets = list()
        for ticket in tickets :
            list_tickets.append(ticket.toDict())

        return list_tickets
    
    def getMessageDiffusedLogs(self) -> list[dict]:
        messages = self.ldao.findAllMessageDiffused()  # New method to get message diffused logs
        list_messages = list()
        for message in messages :
            list_messages.append(message.toDict())

        return list_messages
    
    def getTypesLog(self) -> list[str]:
        return self.ldao.findTypesLog()
    
    def getLogsByOrganisationByType(self, id_orga: int, type_log: str) -> list[dict]:
        logs = self.ldao.findLogsByOrganizationByType(id_orga, type_log)  # New method to get logs by organization and type
        list_logs = list()
        for log in logs :
            list_logs.append(log.toDict())

        return list_logs
    
    def createLog(self, type_log: str, text_log: str, date_log: datetime , id_orga: int) :
        ''' Insert a new log in the database '''
        return self.ldao.createLog(type_log, text_log, date_log, id_orga)