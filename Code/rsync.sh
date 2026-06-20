#!/bin/bash

# Configuration à modifier
username_distant_raspberry="tristan"
IP_distant_raspberry="192.168.1.23"
Dossier_source_flask="/app/static/audio"
Dossier_destination_raspberry="/home/SoundStreamDevice"
Playlist="playlist_Romain" # Nom de la playlist à jouer

# Retirer la connexion (Arrêter le service de musique à distance)
echo "Arrêt du lecteur distant..."
ssh $username_distant_raspberry@$IP_distant_raspberry sudo -S sytemctl stop mpd
echo "Lecteur distant arrêté"

# Synchronisation avec rsync
echo "Synchronisation des fichiers en cours..."
rsync -avz --progress --include '*.mp3' -e ssh $Dossier_source_flask $username_distant_raspberry@$IP_distant_raspberry:"$Dossier_destination_raspberry"
echo "Synchronisation des fichiers terminée"

# Relancer le lecteur à distance
echo "Redémarrage du lecteur distant..."
ssh $username_distant_raspberry@$IP_distant_raspberry sudo -S systemctl restart mpd
echo "Lecteur distant redémarré"

# Lancer le lecteur à distance
echo "Lancement de la lecture musicale distante..."
ssh $username_distant_raspberry@$IP_distant_raspberry sudo -S systemctl start mpd
echo "Lecture musicale distante lancée"

# Lancer la musique
ssh $username_distant_raspberry@$IP_distant_raspberry "mpc update && mpc clear && mpc load $Playlist.m3u && mpc play"