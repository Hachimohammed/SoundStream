from app import app
from typing import *
from datetime import datetime
import sqlite3
from app.models.LogDAOInterface import LogDAOInterface
from app.models.Log import Log

class LogSqliteDAO(LogDAOInterface):
    ''' This class will manage the datas of the log table in the Sqlite3 database
    to facilitate the manipulation of the logs in the LogService class.
    '''
    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'

    def _getDbConnection(self) -> sqlite3.Connection:
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn
    
    def findAll(self) -> list[Log] :
        ''' Return the list of the all the logs without any sorting'''
        
        conn = self._getDbConnection()
        query = "SELECT * FROM log ;"

        logs = conn.execute(query).fetchall()
        logs_instances = list()

        for log in logs :
            logs_instances.append(Log(dict(log)))

        conn.close()

        return logs_instances

    def findAllByOrganization(self, id_orga: int) -> list[Log]:
        ''' Return the list of the all the logs by the organization id in argument'''
        
        conn = self._getDbConnection()
        query = "SELECT * FROM log WHERE id_orga = ? AND type_log != 'TICKET' ORDER BY date_log DESC;"

        logs = conn.execute(query, (id_orga,)).fetchall()
        logs_instances = list()

        for log in logs :
            logs_instances.append(Log(dict(log)))

        conn.close()

        return logs_instances
    
    def createLog(self, type_log: str, text_log: str, date_log: datetime , id_orga: int) -> bool:
        ''' Insert a new log in the database '''
        conn = self._getDbConnection()
        query = 'INSERT INTO log (type_log, text_log, date_log, id_orga) VALUES (?, ?, ?, ?) ;'
        try :
            conn.execute(query, (type_log, text_log, date_log, id_orga))
            conn.commit()
            conn.close()
        except :
            return False

        else : 
            return True
        
    def findTicketsByOrganization(self, id_orga: int) -> list[Log]:
        ''' Return the list of all the tickets from forget_password by the organization id '''
        
        conn = self._getDbConnection()
        query = """
            SELECT fp.id_forget, fp.id_user, fp.new_password, fp.forget_state, fp.date_forget, u.username
            FROM forget_password fp
            JOIN user u ON fp.id_user = u.id_user
            JOIN work_link wl ON u.id_user = wl.id_user
            WHERE wl.id_orga = ?
            ORDER BY fp.date_forget DESC;
        """

        tickets = conn.execute(query, (id_orga,)).fetchall()
        tickets_instances = list()

        for ticket in tickets :
            log_dico = {
                'id_log': ticket['id_forget'],
                'type_log': 'TICKET',
                'text_log': f"Une demande de réinitialisation du mot de passe pour {ticket['username']} a été effectuée",
                'date_log': ticket['date_forget'],
                'id_orga': id_orga
            }
            tickets_instances.append(Log(log_dico))

        conn.close()

        return tickets_instances

    def findAllTickets(self) -> list[Log]:
        ''' Return the list of all the tickets from forget_password '''

        conn = self._getDbConnection()
        query = """
            SELECT fp.id_forget, fp.id_user, fp.new_password, fp.forget_state, fp.date_forget, u.username, wl.id_orga
            FROM forget_password fp
            JOIN user u ON fp.id_user = u.id_user
            LEFT JOIN work_link wl ON u.id_user = wl.id_user
            ORDER BY fp.date_forget DESC;
        """

        tickets = conn.execute(query).fetchall()
        tickets_instances = list()

        for ticket in tickets :
            log_dico = {
                'id_log': ticket['id_forget'],
                'type_log': 'TICKET',
                'text_log': f"Une demande de réinitialisation du mot de passe pour {ticket['username']} a été effectuée",
                'date_log': ticket['date_forget'],
                'id_orga': ticket['id_orga'] if ticket['id_orga'] is not None else 0
            }
            tickets_instances.append(Log(log_dico))

        conn.close()

        return tickets_instances
    
    def findAllMessageDiffused(self) -> list[Log]:
        ''' Return the list of the all the message diffused logs'''

        conn = self._getDbConnection()
        query = "SELECT * FROM log WHERE type_log = 'UPLOAD_EMERGENCY' OR type_log = 'UPLOAD_ADVERTISEMENT' ORDER BY date_log DESC;"

        tickets = conn.execute(query).fetchall()
        tickets_instances = list()

        for ticket in tickets :
            tickets_instances.append(Log(dict(ticket)))

        conn.close()

        return tickets_instances
    
    def findTypesLog(self) -> list[str]:
        ''' Return the list of the all the types of logs in the database'''
        conn = self._getDbConnection()
        query = "SELECT DISTINCT type_log FROM log ;"

        types_log = conn.execute(query).fetchall()
        types_log_list = list()

        for type_log in types_log :
            types_log_list.append(type_log['type_log'])

        conn.close()

        return types_log_list
    
    def findLogsByOrganizationByType(self, id_orga: int, type_log: str) -> list[Log]:
        ''' Return the list of the all the logs by the organization id and the type of log in argument'''
        
        conn = self._getDbConnection()
        query = "SELECT * FROM log WHERE id_orga = ? AND type_log = ? ORDER BY date_log DESC;"

        logs = conn.execute(query, (id_orga, type_log)).fetchall()
        logs_instances = list()

        for log in logs :
            logs_instances.append(Log(dict(log)))

        conn.close()

        return logs_instances