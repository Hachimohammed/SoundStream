from flask import render_template, session, redirect, url_for, request, Response
from functools import wraps
from app import app
from app.controllers.LoginController import LoggedIn, reqrole
from app.services.UserService import UserService
from app.services.OrganisationService import OrganisationService
from app.services.LogService import LogService
import csv
import io
import datetime

orga = OrganisationService()
log = LogService()


class LogController:

    @app.route('/logs/<nom_orga>', methods=['GET'])
    @LoggedIn
    @reqrole(['admin'])
    def logs(nom_orga):
        metadata = {'title': 'log'}
        types_log = log.getTypesLog()
        types_log.insert(0, 'all')  # Ajouter l'option "all" pour afficher tous les types de logs
        if 'TICKET' in types_log:
            types_log.remove('TICKET')  # Supprimer le type "TICKET" de la liste des types de logs pour le filtrage

        selected_type = request.args.get('type', 'all')  # Récupérer le type sélectionné dans les paramètres de la requête ; par défaut 'all'
        
        if selected_type == 'all':
            log_list = log.getLogsByOrganisation(orga.getIdByName(nom_orga))
        else:
            log_list = log.getLogsByOrganisationByType(orga.getIdByName(nom_orga), selected_type)  # Nouvelle méthode pour filtrer les logs par type

        return render_template('logs.html', log_list=log_list, metadata=metadata, orga=nom_orga, types=types_log, selected_type=selected_type)

    @app.route('/logs/<nom_orga>/export_csv', methods=['GET'])
    @LoggedIn
    @reqrole(['admin'])
    def export_logs_csv(nom_orga):
        
        log_list = log.getLogsByOrganisation(orga.getIdByName(nom_orga))
        types_log = log.getTypesLog()

        # Créer le fichier CSV en mémoire
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # En-tête
        writer.writerow(['Type', 'Texte', 'Date'])

        # Données
        for l in log_list:
             writer.writerow([l['type_log'], l['text_log'], l['date_log']])

        output.seek(0)

        # Nom du fichier avec la date du jour
        filename = f"logs_{nom_orga}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    @app.route('/tickets', methods=['GET'])
    @LoggedIn
    @reqrole(['admin'])
    def tickets():
        metadata = {'title': 'Tickets'}
        nom_orga = session.get('organisation_name')
        id_orga = orga.getIdByName(nom_orga)
        ticket_list = log.getTicketsByOrganisation(id_orga)  # Get ticket logs for the user's organization
        return render_template('tickets.html', ticket_list=ticket_list, metadata=metadata, orga=nom_orga, id_orga=id_orga)

    @app.route('/messages_diffused/<nom_orga>', methods=['GET'])
    @LoggedIn
    @reqrole(['marketing'])
    def messages_diffused(nom_orga):
        metadata = {'title': 'Messages Diffused'}
        message_list = log.getMessageDiffusedLogs()
        return render_template('messages_diffused.html', message_list=message_list, metadata=metadata, orga=nom_orga)