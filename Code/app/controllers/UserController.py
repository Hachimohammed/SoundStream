from flask import Flask, render_template, session, redirect, url_for, request, flash
from functools import wraps
from app import app
from app.controllers.LoginController import LoggedIn, reqrole
from app.services.UserService import UserService
from app.services.OrganisationService import OrganisationService
from app.services.LogService import LogService
from re import match
import datetime


log = LogService()
ogs=OrganisationService()
us=UserService()

class UserController :

    @app.route('/users/<nom_orga>', methods =['GET'])
    @LoggedIn
    @reqrole(['admin'])
    def users(nom_orga):
        metadata= {'title': 'Users'}

        return render_template('users.html', metadata=metadata, ogs=ogs, us=us, orga=nom_orga)

    @app.route('/deleteUsn/<username>',methods=['POST','GET'])
    @LoggedIn
    @reqrole(['admin'])
    def deleteUser(username):

        # Claim the organizations of the user to delete and its id to create the log
        user_orga = us.getOrganisationsByUsername(username)
        orga_name = session.get('organisation_name')

        orga_id = ogs.getIdByName(orga_name)
        print(user_orga)

        user_role = us.getRoleByUsername(username)

        if user_role != 'admin':
            if user_orga and len(user_orga) == 1:
                us.deleteByUsername(username)
                log.ldao.createLog("DELETE", f"l'utilisateur {username} a été supprimé de la base de données.",
                                    datetime.datetime.now(), orga_id)
            elif user_orga and len(user_orga) > 1:
                us.deleteUserOfOrganisation(username, orga_name)
                log.ldao.createLog("DELETE", f"l'utilisateur {username} a été supprimé de l'organisation {orga_name}",
                                    datetime.datetime.now(), orga_id)
            message = f"L'utilisateur {username} a été supprimé avec succès"
        else:
            message = "Vous ne pouvez pas supprimer un utilisateur avec un rôle admin"

        metadata= {'title': 'Users'}
        orga_name = session.get('organisation_name')
        
        return render_template('users.html', metadata=metadata, ogs=ogs, us=us, message=message, orga=orga_name)
    
    @app.route('/editUsn/<username>', methods=['GET', 'POST'])
    @LoggedIn
    @reqrole(['admin'])
    def editUser(username):
        
        if request.method == 'POST':
            # Récupération des données du formulaire
            new_password = request.form.get('password')
            new_role = request.form.get('role')
            new_email = request.form.get('email')
            new_phone_number = request.form.get('phone_number')

            message = ""
            

            # Récupérer tous les rôles disponibles pour validation
            available_roles = us.udao.getAllRoles()


            # Récupérer tous les emails existants pour validation
            existing_emails = [user.email for user in us.findAll()]
            existing_emails.remove(us.findByUsername(username).email)  # Remove the current user's email from the list


            # Récupérer l'organisation pour redirection
            orga_name = session.get('organisation_name')
            
            if not orga_name:
                orga_name = 'default'

            # Récupérer tous les numéros de téléphone pour validation
            existing_phone_number = [user.phone_number for user in us.findAll()]
            existing_phone_number.remove(us.findByUsername(username).phone_number)

            # Vérification du rôle
            if not new_role or new_role not in available_roles:
                return "Erreur : Rôle invalide", 400
            

            # Mise à jour du mot de passe si fourni
            if new_password and new_password.strip():
                us.udao.changePassword(username, new_password)
            

            user_name_session = session.get('username')
            orga_id = session.get('organisation_name')
            log.ldao.createLog("EDIT",
                               f"Le mot de passe de l'utilisateur {username} a été changé par {user_name_session}",
                               datetime.datetime.now(),
                               orga_id
                            )
            

            # Mise à jour du rôle
            us.udao.updateUserRole(username, new_role)
            log.ldao.createLog("EDIT",
                               f"Le rôle de l'utilisateur {username} a été changé en {new_role} par {user_name_session}",
                               datetime.datetime.now(),
                               orga_id
                            )
            

            # Mise à jour de l'email
            if match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email) and new_email not in existing_emails:
                if new_email != us.findByUsername(username).email:
                    us.udao.updateEmail(username, new_email)
                    log.ldao.createLog("EDIT",
                                        f"L'email de l'utilisateur {username} a été changé en '{new_email}' par {user_name_session}",
                                        datetime.datetime.now(),
                                        orga_id
                                    )
                    message = "Utilisateur modifié avec succès."
            else:
                if not match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
                    message = "Email non valide"
                else:
                    for user in us.findAll():
                        if user.email == new_email:
                            user_with_email = user.username
                            break
                    
                    message = f"Le nouvel email est similaire à un email existant (utilisé par {user_with_email})"
            

            # Mise à jour du numéro de téléphone
            if new_phone_number not in existing_phone_number :
                if new_phone_number != us.findByUsername(username).phone_number :
                    us.udao.updatePhoneNumber(username, new_phone_number)
                    log.ldao.createLog("EDIT",
                                        f"Le numéro de l'utilisateur {username} a été modifié en '{new_phone_number}' par {user_name_session}",
                                        datetime.datetime.now(),
                                        orga_id
                                    )
                    if not "similaire" in message :
                        message = "Utilisateur modifié avec succès."
            else:
                if new_phone_number in existing_phone_number :
                    for user in us.findAll() :
                        if user.phone_number == new_phone_number :
                            user_with_phone_number = user.username
                            break
                    
                    message = f'Le nouveau numéro de téléphone est similaire à un numéro existant (utilisé par "{user_with_phone_number}")'

            if message == "Utilisateur modifié avec succès." :
                metadata={'title': 'Users'}
                return render_template('users.html', metadata=metadata, ogs=ogs, us=us, message=message, orga=orga_name)
            else :
                return render_template('edit_user.html',
                                        metadata={'title': 'Modifier Utilisateur'},
                                        user=us.findByUsername(username),
                                        orga=orga_name,
                                        roles=available_roles,
                                        message=message
                                        )
        
        else:
            # AFFICHAGE DU FORMULAIRE (GET)
            user = us.findByUsername(username)
            
            if not user:
                return "Utilisateur non trouvé", 404
            
            # Récupérer l'organisation de l'utilisateur
            orga_name = session.get('organisation_name')
            
            if not orga_name:
                orga_name = 'Harman_Kardon'
            
            # Récupérer tous les rôles disponibles
            available_roles = us.udao.getAllRoles()
            
            # Affichage du formulaire pré-rempli
            metadata = {'title': 'Modifier Utilisateur'}
            return render_template('edit_user.html', 
                                 metadata=metadata, 
                                 user=user,
                                 orga=orga_name,
                                 roles=available_roles,
                                )
        

    @app.route('/addUser', methods=['GET', 'POST'])
    @LoggedIn
    @reqrole(['admin'])
    def addUser():
        
        if request.method == 'POST':
            # Récupération des données du formulaire
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            email = request.form.get('email') 

            # Récupérer l'organisation pour redirection et association au nouvel utilisateur
            orga_name = session.get('organisation_name')
            
            # Récupérer tous les rôles disponibles pour validation
            available_roles = us.udao.getAllRoles()
            
            # Vérification du rôle
            if not role or role not in available_roles:
                return "Erreur : Rôle invalide", 400

            user_name_session = session.get('username')
            
            users = us.findAll()

            user_organizations = us.getOrganisationsByUsername(username)

            for user in users:
                if user.username == username:

                    if orga_name in user_organizations:
                        message = "L'utilisateur existe déjà dans cette organisation"
                        return render_template('add_user.html',
                                                metadata={'title': 'Ajouter Utilisateur'},
                                                orga=orga_name,
                                                roles=available_roles,
                                                message=message
                                                )
                    
                    user_with_email = user.email


            existing_emails = [user.email for user in us.findAll()]

            # Create the log and insert it in the database
            orga_id = ogs.getIdByName(orga_name)

            if match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                if email not in existing_emails or email == user_with_email:
                    # Création de l'utilisateur
                    us.createUser(username, password, role, orga_name, email)

                    log.ldao.createLog("ADD", f"l'utilisateur {username} a été implémenté dans la base de données.",
                                        datetime.datetime.now(), orga_id)
                
                message = f"L'utilisateur {username} a été créé avec succès"
                metadata = {"title" : "Users"}

                return render_template('users.html', metadata=metadata, ogs=ogs, us=us, message=message, orga=orga_name)
            else:
                if not match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    message = "Email non valide"
                else:
                    for user in us.findAll():
                        if user.email == email:
                            user_with_email = user.username
                            break
                    message = "Le nouvel email est similaire à un email existant (utilisé par " + user_with_email + ")"
            
                return render_template('add_user.html',
                                        metadata={'title': 'Ajouter Utilisateur'},
                                        orga=orga_name,
                                        roles=available_roles,
                                        message=message
                                        )
        
        else:
            # AFFICHAGE DU FORMULAIRE (GET)
            
            # Récupérer l'organisation de où se situe
            orga_name = session.get('organisation_name')
            
            if not orga_name:
                orga_name = 'Harman_Kardon'
            
            # Récupérer tous les rôles disponibles
            available_roles = us.udao.getAllRoles()
            
            # Affichage du formulaire pré-rempli
            metadata = {'title': 'Ajouter Utilisateur'}
            return render_template('add_user.html',
                                 metadata=metadata,
                                 orga=orga_name,
                                 roles=available_roles)  # <- Passage des rôles au template
        
    @app.route('/forgotten', methods=['GET', 'POST'])
    def forgotten():
        metadata = {'title': 'Forgotten Password'}
        if request.method == 'POST':
            email = request.form.get('email')
            user = us.findByEmail(email)

            if user:
                # Générer un nouveau mot de passe aléatoire
                import random, string
                new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

                # Changer le mot de passe en BDD
                us.changePassword(user.username, new_password)

                # Envoyer le mail
                from app.services.EmailService import send_reset_email
                send_reset_email(email, user.username, new_password)

                username = us.findByEmail(email).username
                organisations = us.getOrganisationsByUsername(user.username)

                for orga in organisations:
                    orga_id = ogs.getIdByName(orga)

                    log.ldao.createLog("TICKET",
                                        f"Une demande de réinitialisation du mot de passe pour {username} a été effectuée",
                                        datetime.datetime.now(),
                                        orga_id
                                    )

                return render_template('forgotten.html', metadata=metadata, success="Un nouveau mot de passe a été envoyé à votre adresse mail.")
            else:
                return render_template('forgotten.html', metadata=metadata, error="Aucun compte trouvé avec cet email.")

        return render_template('forgotten.html', metadata=metadata)
    

    @app.route('/parametre', methods=['GET', 'POST'])
    @LoggedIn
    def ConfigurationUser():
        username = session.get("username")
        
        if request.method == 'POST':
            # Récupération des données du formulaire
            new_password = request.form.get('password')
            new_email = request.form.get('email')
            new_phone_number = request.form.get('phone_number')

            message = ""


            # Récupérer tous les rôles disponibles pour validation
            available_roles = us.udao.getAllRoles()


            # Récupérer tous les emails existants pour validation
            existing_emails = [user.email for user in us.findAll()]
            existing_emails.remove(us.findByUsername(username).email)  # Remove the current user's email from the list


            # Récupérer l'organisation pour redirection
            orga_name = session.get('organisation_name')

            # Récupérer tous les numéros de téléphone pour validation
            existing_phone_number = [user.phone_number for user in us.findAll()]
            existing_phone_number.remove(us.findByUsername(username).phone_number)
            
            if not orga_name:
                orga_name = 'default'

            
            orga_id = session.get('organisation_name')
            

            # Mise à jour du mot de passe si fourni
            if new_password and new_password.strip():
                us.udao.changePassword(username, new_password)
                log.ldao.createLog("EDIT",
                                   f"{username} a modifié son mot de passe",
                                   datetime.datetime.now(),
                                   orga_id
                                )
            

            # Mise à jour de l'email
            if match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email) and new_email not in existing_emails:
                if new_email != us.findByUsername(username).email:
                    us.udao.updateEmail(username, new_email)
                    log.ldao.createLog("EDIT",
                                        f"{username} a modifié son email par '{new_email}'",
                                        datetime.datetime.now(),
                                        orga_id
                                    )
                    message = "Utilisateur modifié avec succès."
            else:
                if not match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
                    message = "Email non valide"
                else:
                    for user in us.findAll():
                        if user.email == new_email:
                            user_with_email = user.username
                            break
                    
                    message = "Le nouvel email est similaire à un email existant (utilisé par " + user_with_email + ")"
            
            
            # Mise à jour du numéro de téléphone
            if new_phone_number not in existing_phone_number :
                if new_phone_number != us.findByUsername(username).phone_number :
                    us.udao.updatePhoneNumber(username,new_phone_number)
                    log.ldao.createLog("EDIT",
                                        f'{username} a modifié son numéro de téléphone par "{new_phone_number}"',
                                        datetime.datetime.now(),
                                        orga_id
                                    )
                    if "non valide" in message or "utilisé par" in message or message == "":
                        message = "Utilisateur modifié avec succès."
            else:
                if new_phone_number in existing_phone_number :
                    for user in us.findAll():
                        if user.phone_number == new_phone_number :
                            user_with_phone_number = user.username
                            break
                    
                    message = f'Le nouveau numéro de téléphone est similaire à un numéro existant (utilisé par "{user_with_phone_number}")'

            return render_template('parametre.html',
                                    metadata={'title': 'Configurer Utilisateur'},
                                    user=us.findByUsername(username),
                                    orga=orga_name,
                                    roles=available_roles,
                                    message=message
                                    )
        
        else:
            # AFFICHAGE DU FORMULAIRE (GET)
            user = us.findByUsername(username)
            
            if not user:
                return "Utilisateur non trouvé", 404
            
            # Récupérer l'organisation de l'utilisateur
            orga_name = session.get('organisation_name')
            
            if not orga_name:
                orga_name = 'Harman_Kardon'
            
            # Récupérer tous les rôles disponibles
            available_roles = us.udao.getAllRoles()
            
            # Affichage du formulaire pré-rempli
            metadata = {'title': 'Configurer Utilisateur'}
            return render_template('parametre.html', 
                                 metadata=metadata, 
                                 user=user,
                                 orga=orga_name,
                                 roles=available_roles,
                                )