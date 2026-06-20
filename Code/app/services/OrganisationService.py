from app.models.OrganisationDAO import OrganisationDAO
import os

class OrganisationService:

    def __init__(self) :
        self.odao = OrganisationDAO()

    def findUserOrganisation(self, username):
        """ Get the organisation of a user by username and return the list of organisations """
        return  self.odao.findUserOrganisation(username)
    
    def getIdByName(self, orga_name):
        return self.odao.getIdByName(orga_name)
