from app.models.UserDAO import UserDAO

class UserService():

    def __init__(self):
        # cette ligne utilise le Data Access Object (DAO) dédié aux fichier JSON
        self.udao = UserDAO()
    
    def findUsersInOrganisation(self, organisation):
        """ Get all the users of an organisation """
        return self.udao.findUsersInOrganisation(organisation)
    
    def createUser(self, username, password, role, organisation, email='', phone_number=''):
        """ create a new user """
        return self.udao.createUser(username, password, role, organisation, email, phone_number)
    
    def deleteByUsername(self, username):
        """ Delete user by username """
        return self.udao.deleteByUsername(username)
    
    def deleteUserOfOrganisation(self, username, organisation):
        """ Delete the user of an organisation """
        return self.udao.deleteUserOfOrganisation(username, organisation)
    
    def getOrganisationsByUsername(self, username):
        """Get the organisation names of a user"""
        return self.udao.getOrganisationsByUsername(username)
    
    def getRoleByUsername(self, username):
        """Get the role of a user"""
        return self.udao.getRoleByUsername(username)

    def findByUsername(self, username):
        """ Get user by username  """
        return self.udao.findByUsername(username)
    
    def findAllUsername(self) -> list[str]:
        """ Get all usernames """
        return self.udao.findAllUsername()
    
    def findAll(self) -> list:
        """ Get all users """
        return self.udao.findAll()

    def findByEmail(self, email):
        """Get user by email"""
        return self.udao.findByEmail(email)

    def updateEmail(self, username, new_email):
        """Update user email"""
        return self.udao.updateEmail(username, new_email)

    def changePassword(self, username, password):
        """Change user password"""
        return self.udao.changePassword(username, password)

    def getAdminEmailByOrga(self, orga_name):
        """Récupère les emails de tous les admins d'une organisation"""
        conn = self.udao._getDbConnection()
        res = conn.execute('''
            SELECT u.email FROM user u
            JOIN work_link wl ON u.id_user = wl.id_user
            JOIN organisation o ON wl.id_orga = o.id_orga
            WHERE o.name_orga = ? AND u.role = 'admin'
            ''', (orga_name,)).fetchall()
        conn.close()
    #    Retourne une liste d'emails des admins de l'organisation, en filtrant les entrées nulles
        return [r['email'] for r in res if r['email']]
    
    def updatePhoneNumber(self, username, new_phone_number) :
        """Change user phone number"""
        return self.udao.updatePhoneNumber(username, new_phone_number)

    def updateUsername(self, username, new_username) :
        """Change username of an user"""
        return self.udao.updateUsername(username, new_username)

    def getAllRoles(self):
        """Get all available roles from the role table"""
        return self.udao.getAllRoles()

    def updateUserRole(self, username, new_role) :
        """Update user role"""
        return self.udao.updateUserRole(username, new_role)