from app.models.User import User


class UserDAOInterface :
    def createUser(self, username, password, role, organisation, email='', phone_number='') -> None:
        """ create a new user """
        pass

    def createLinkUserOrganisation(self, username, organisation) -> None:
        """ Create a link between a user and an organisation """
        pass

    def findByUsername(self, username) -> User:
        """ Get user by username """
        pass

    def findByEmail(self, email) -> User:
        """ Get user by email """
        pass

    def updateEmail(self, username, new_email) -> None:
        """ Update the email of an user """
        pass
    
    def findUsersInOrganisation(self, organisation) -> list:
        """ Get all the users of an organisation """
        pass
    
    def verifyUser(self, username, password) -> bool:
        """Verify if username and password are correct"""
        pass

    def changePassword(self, username, password) -> None:
        """Change the password of the user"""
        pass
    
    def deleteByUsername(self, username) -> None:
        """ Delete user by username """
        pass

    def deleteUserOfOrganisation(self, username, organisation) -> None:
        """ Delete the user of an organisation """
        pass

    def updateUserRole(self, username, new_role) -> None:
        """Update user role"""
        pass

    def getOrganisationsByUsername(self, username) -> list:
        pass
    
    def getAllRoles(self) -> list:
        """Get all available roles from the role table"""
        pass

    def getRoleByUsername(self, username) -> str:
        """Get the role of a user"""
        pass

    def findAll(self) -> list[User]:
        """ Get all users """
        pass

    def findAllUsername(self) -> list[str]:
        """ Get all usernames """
        pass

    def updatePhoneNumber(self, username, new_phone_number) -> None:
        """ Update the phone number of an user """
        pass

    def updateUsername(self, username, new_username) -> None :
        """ Update the phone number of an user """
        pass