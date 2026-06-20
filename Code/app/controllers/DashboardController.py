from flask import render_template, session, redirect, url_for, request
from functools import wraps
from app import app
from app.controllers.LoginController import LoggedIn, reqrole
from app.services.UserService import UserService
from app.services.TimeTableService import TimeTableService
from app.services.SongPlayerService import SongPlayerService
from app.services.OrganisationService import OrganisationService
from app.services.LogService import LogService
from app.services.FileService import FileService
import datetime
import subprocess


us=UserService()
tts=TimeTableService()
sps=SongPlayerService()
ogs=OrganisationService()
los=LogService()
file_service = FileService()


class DashboardController:
    
    @app.route('/dashboard/<nom_orga>', methods=['GET', 'POST'])
    @LoggedIn
    def dashboard(nom_orga):
        metadata= {'title': 'Dashboard'}
        session['organisation_name'] = nom_orga

        print(sps.findAllSongPlayerByOrganisation(ogs.getIdByName(nom_orga)))

        # Get organization ID once to optimize database queries
        id_orga = ogs.getIdByName(nom_orga)

        # Get all players for this organization as a list of dictionaries
        liste_song_player_dict = sps.findAllSongPlayerByOrganisation(id_orga)

        # Retrieve the count of online and offline players for this organization
        nb_on_and_nb_off = sps.countNumberOfSongPlayerOnlineAndOffline(id_orga)
        
        # Unpack counters from the result list/tuple
        nb_on = nb_on_and_nb_off[0]
        nb_off = nb_on_and_nb_off[1]

        tts.autoCleanPlaylists()
        id_orga = ogs.getIdByName(nom_orga)

        # Render the dashboard with all collected metrics and player data
        return render_template('dashboard.html', 
                                metadata=metadata, 
                                orga=nom_orga, 
                                us=us, 
                                tts=tts, 
                                sps=sps, 
                                ogs=ogs, 
                                los=los,
                                nb_on=nb_on,
                                nb_off=nb_off, 
                                liste_song_player=liste_song_player_dict)
    
    @app.route('/emergencyMessage', methods=['POST'])
    @reqrole(['sales'])
    @LoggedIn
    def emergencyMessage():
        """Message d'urgence avec avance dans le temps pour respecter le planning"""
        metadata = {'title': 'Add Emergency Message'}

        nom_orga = session.get('organisation_name')

        # Vérifications
        if 'uploadfile' not in request.files:
            return redirect(url_for('dashboard', nom_orga=nom_orga))
            
        file_storage = request.files['uploadfile']
        if not file_storage or file_storage.filename == '':
            return redirect(url_for('dashboard', nom_orga=nom_orga))

        # Sauvegarde du fichier
        form = request.form.to_dict() # Conversion propre pour éviter les erreurs
        form['file_type'] = 'mp3'
        file_id = file_service.createFileFromForm(form, file_storage)
            
        if file_id == -1:
            return redirect(url_for('dashboard', nom_orga=nom_orga))

        # Récupérer la durée du message (Depuis la BD)
        emergency_file = file_service.fdao.findFileById(file_id)
        filename = emergency_file.name # Nom du fichier
            
        # Calcul de la durée en secondes (Ex: "01:30" -> 90s) en plus détaillé 1×60+30=90 secondes 
        duration_seconds = 30 # Valeur par défaut
        try:
            if emergency_file.time_length:
                parts = emergency_file.time_length.split(':')
                # Gère le cas MM:SS ou HH:MM:SS en gros si 
                if len(parts) == 2:
                    duration_seconds = int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    duration_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except Exception as e:
            print(f"Erreur calcul durée (défaut 30s) : {e}")

        # Diffusion sur les lecteurs
        orga_id = ogs.getIdByName(nom_orga)
        devices = sps.findAllSongPlayerByOrganisation(orga_id)

        for device in devices:
            # On tente l'envoi même si marqué OFFLINE (au cas où il vient de revenir)
            ip = device['IP_adress']
            user_vm = "synapse" 
                
            # Sync le fichier 
            try:
                sps.sync_to_device(ip, user_vm)
            except Exception as e:
                print(f"Erreur Sync {ip}: {e}")
                continue

            # B. Tu peux supprimer après c'est juste pour expliquer en bein gui
            # - update --wait : On est sûr que le fichier est connu
            # - insert : On met l'urgence juste après le son actuel
            # - next : On coupe le son actuel et on lance l'urgence
            # - wait : On attend (proprement) que l'urgence finisse
            # - prev : On revient au son d'avant (il recommence au début)
            # - seek : On avance du temps perdu (+duration)
            # - play : On relance
                
            cmd = (
                f"mpc update --wait && "
                f"mpc insert \"{filename}\" && "
                f"mpc next && "
                f"mpc wait && "
                f"mpc prev && "
                f"mpc seek +{duration_seconds} && "
                f"mpc play"
            )
                
            # Exécuter en subprocess
            try:
                subprocess.Popen(
                    ["ssh", "-o", "StrictHostKeyChecking=no", f"{user_vm}@{ip}", cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print(f" Urgence envoyée à {ip} (Rattrapage : +{duration_seconds}s)")
            except Exception as e:
                print(f" Erreur sur {ip}: {e}")

        # 5. Logger
        username = session.get('username')
        los.ldao.createLog(
            "UPLOAD_EMERGENCY",
            f"User {username} diffusé urgence: {filename}",
            datetime.datetime.now(),
            orga_id
        )

        return redirect(url_for('dashboard', nom_orga=nom_orga))
    
    @app.route('/advertisement', methods=['POST'])
    @reqrole(['sales'])
    @LoggedIn
    def advertisement(nom_orga):
        """Upload d'un message publicitaire"""
        metadata = {'title': 'Upload Advertisement Message'}

        nom_orga = session.get('organisation_name')
        
        # Vérifications
        if 'uploadfile' not in request.files:
            return redirect(url_for('dashboard', nom_orga=nom_orga))
            
        file_storage = request.files['uploadfile']
        if not file_storage or file_storage.filename == '':
            return redirect(url_for('dashboard', nom_orga=nom_orga))

        # Sauvegarde du fichier
        form = request.form.to_dict() # Conversion propre pour éviter les erreurs
        form['file_type'] = 'mp3'
        file_id = file_service.createFileFromForm(form, file_storage)
            
        if file_id == -1:
            return redirect(url_for('dashboard', nom_orga=nom_orga))

        # 5. Logger
        username = session.get('username')
        orga_id = ogs.getIdByName(nom_orga)
        los.ldao.createLog(
            "UPLOAD_ADVERTISEMENT",
            f"User {username} uploaded advertisement message: {file_storage.filename}",
            datetime.datetime.now(),
            orga_id
        )

        return redirect(url_for('dashboard', nom_orga=nom_orga))