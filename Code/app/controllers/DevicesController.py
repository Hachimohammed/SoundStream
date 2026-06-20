from flask import render_template, session, redirect, url_for, request, jsonify
from functools import wraps
import datetime
from app import app
from app.controllers.LoginController import LoggedIn, reqrole
from app.services.UserService import UserService
from app.services.SongPlayerService import SongPlayerService
from app.services.OrganisationService import OrganisationService
from app.services.LogService import LogService
from app.services.EmailService import send_offline_alert


log = LogService()
sps = SongPlayerService()
ogs = OrganisationService()

class DevicesController:

    @app.route('/devices/<nom_orga>', methods=['GET'])
    @LoggedIn
    @reqrole(['admin', 'marketing'])
    def devices(nom_orga):
        metadata = {'title': 'Devices'}
        id_orga = ogs.getIdByName(nom_orga)
        liste_song_player_dict = sps.findAllSongPlayerByOrganisation(id_orga)
        nb_on_and_nb_off = sps.countNumberOfSongPlayerOnlineAndOffline(id_orga)
        nb_on = nb_on_and_nb_off[0]
        nb_off = nb_on_and_nb_off[1]
        return render_template('devices.html', metadata=metadata, liste_song_player=liste_song_player_dict, nb_on=nb_on, nb_off=nb_off, orga=nom_orga)

    @app.route('/update/<int:id_player>', methods=['POST', 'GET'])
    @LoggedIn
    @reqrole(['admin'])
    def update(id_player):
        # Récupérer l'état AVANT le ping
        player_before = sps.spdao.findByID(id_player)
        old_state = player_before.state if player_before else None

        # Mettre à jour l'état
        sps.changeState(id_player)

        # Récupérer l'état APRÈS le ping
        player_after = sps.spdao.findByID(id_player)
        new_state = player_after.state if player_after else None

        #  Notification email si le device vient de passer OFFLINE
        if old_state == 'ONLINE' and new_state == 'OFFLINE':
            try:
                from app.services.UserService import UserService
                from app.services.OrganisationService import OrganisationService
                us = UserService()
                ogs_local = OrganisationService()
                nom_orga = session.get('organisation_name')
                # Récupérer l'email de l'admin de l'organisation
                admin_emails = us.getAdminEmailByOrga(nom_orga)
                for admin_email in admin_emails:
                    send_offline_alert(admin_email, player_after.name_place, player_after.IP_adress)
            except Exception as e:
                print(f"Erreur notification offline : {e}")

        return redirect(request.referrer)

    @app.route('/delete/<int:id_player>', methods=['POST', 'GET'])
    @LoggedIn
    @reqrole(['admin'])
    def delete(id_player):
        player = sps.spdao.findByID(id_player)
        log.ldao.createLog(
            "DELETE",
            f"le lecteur {player.name_place} a été supprimé",
            datetime.datetime.now(),
            player.id_orga)
        sps.deleteSongPlayer(id_player)
        return redirect(request.referrer)

    # Route AJAX  pas de GET/POST car ne transit que du JSON
    @app.route('/auto_update_status/<nom_orga>')
    @LoggedIn
    @reqrole(['admin'])
    def get_status(nom_orga):
        id_orga = ogs.getIdByName(nom_orga)
        players = sps.findAllSongPlayerByOrganisation(id_orga)
        status_data = []

        for p in players:
            sps.changeState(p['id_player'])
            status_data.append({
                'id_player': p['id_player'],
                'state': p['state']
            })

        return jsonify(status_data)

    
    @app.route('/sync_all/<nom_orga>', methods=['POST'])
    @LoggedIn
    @reqrole(['admin'])
    def sync_all(nom_orga):
        id_orga = ogs.getIdByName(nom_orga)
        devices = sps.findAllSongPlayerByOrganisation(id_orga)

        results = []
        success_count = 0
        fail_count = 0

        for device in devices:
            if device['state'] == 'ONLINE':
                ip = device['IP_adress']
                device_name = device.get('device_name', 'synapse')
                try:
                    sps.sync_to_device(ip, device_name)
                    results.append({'name': device['name_place'], 'ip': ip, 'status': 'success'})
                    success_count += 1
                except Exception as e:
                    results.append({'name': device['name_place'], 'ip': ip, 'status': 'error', 'message': str(e)})
                    fail_count += 1

        # Logger la synchronisation globale
        username = session.get('username')
        log.ldao.createLog(
            "SYNC_ALL",
            f"{username} a lancé une synchronisation globale : {success_count} succès, {fail_count} échecs.",
            datetime.datetime.now(),
            id_orga
        )

        return jsonify({
            'success': success_count,
            'fail': fail_count,
            'results': results
        })

    @app.route('/edit/<int:id_player>', methods=['GET', 'POST'])
    @LoggedIn
    @reqrole(['admin'])
    def edit_player(id_player):
        """
        Route pour modifier les informations d'un lecteur
        
        EXPLICATION mes loulous que j'aime:
        
        Cette route permet à un utilisateur connecté de modifier les infos d'un lecteur.
        
        Comment ça marche en bien gui , putain le senegal a fait match nul?
        1. L'utilisateur clique sur "Modifier" dans devices.html
        2. GET /edit/123 → On affiche un formulaire pré-rempli avec les données actuelles
        3. L'utilisateur modifie les champs qu'il veut
        4. POST /edit/123 → On enregistre les nouvelles valeurs dans la BDD
        5. Redirection vers la page devices pour voir le résultat
        
        Paramètres:
            id_player (int): L'ID du lecteur à modifier
        
        Retourne:
            - Si GET : Page HTML avec formulaire d'édition
            - Si POST : Redirection vers la page devices après modification
        """

        if request.method == 'POST':
            #  TRAITEMENT DU FORMULAIRE (POST)
            
            # Récupération des données envoyées par le formulaire
            # request.form contient tout ce que l'utilisateur a tapé
            name_place = request.form.get('name_place')
            ip_address = request.form.get('ip_address')
            place_address = request.form.get('place_address')
            place_city = request.form.get('place_city')
            place_postcode = request.form.get('place_postcode')
            place_building_name = request.form.get('place_building_name')
            device_name = request.form.get('device_name')

            if not name_place or not ip_address or not place_address:
                return "Erreur : Tous les champs sont obligatoires", 400

            form_data = {
                'name_place': name_place,
                'IP_adress': ip_address,
                'address_place': place_address,
                'city_place': place_city,
                'postcode_place': place_postcode,
                'building_name_place': place_building_name,
                'device_name': device_name
            }

            sps.spdao.updateDbSongPlayer(form_data, id_player)
            return redirect(request.referrer)

        else:
            player = sps.spdao.findByID(id_player)
            if not player:
                return "Lecteur non trouvé", 404

            available_buildings = sps.spdao.findAllBuildingNames()
            orga = ogs.getIdByName(session.get("organisation_name"))
            metadata = {'title': 'Modifier Lecteur'}
            return render_template('edit_player.html',
                                   metadata=metadata,
                                   player=player,
                                   orga=orga,
                                   buildings=available_buildings)

    @app.route('/addPlayer', methods=['GET', 'POST'])
    @LoggedIn
    @reqrole(['admin'])
    def addPlayer():

        if request.method == 'POST':
            name_place = request.form.get('name_place')
            ip_address = request.form.get('ip_address')
            state = "OFFLINE"
            place_address = request.form.get('place_address')
            place_city = request.form.get('place_city')
            place_postcode = request.form.get('place_postcode')
            place_building_name = request.form.get('place_building_name')
            device_name = request.form.get('device_name')
            orga_name = session.get('organisation_name')
            orga_id = ogs.getIdByName(orga_name)

            sps.spdao.createDevice(
                name_place, ip_address, state,
                place_address, place_postcode, place_city,
                place_building_name, device_name, orga_id)

            return redirect(url_for('devices', nom_orga=orga_name))

        else:
            orga = ogs.getIdByName(session.get('organisation_name'))
            available_buildings = sps.spdao.findAllBuildingNames()
            metadata = {'title': 'Ajouter Lecteur'}
            return render_template('add_player.html',
                                   metadata=metadata,
                                   orga=orga,
                                   buildings=available_buildings)