from app.models.SongPlayerDAO import SongPlayerDAO
from app.services.TimeTableService import TimeTableService
import subprocess
import time
import threading
import datetime
import platform
import os
from app import app

# TimeTableService est instancié ici au niveau module.
# Il ne fait PAS de requête SQL à l'import, donc c'est sans danger.
ts = TimeTableService()


class SongPlayerService:

    _current_playlist = None

    def __init__(self):
        self.spdao = SongPlayerDAO()

    def ping(self, ip):
        """
        Checks if a song player is reachable on the network.

            Args:
                ip (str): The IP address of the song player to ping.

            Returns:
                bool: True if the player responds, False otherwise.
        """
        try:
            if platform.system() == 'Windows':
                command = ["ping", "-n", "1", "-w", "1000", ip]
            else:
                command = ["ping", "-c", "1", "-w", "1", ip]

            result = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            return result.returncode == 0

        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False

    def changeState(self, id_song_player):
        """
        Checks the network status of a player and updates its state in the database.

            Args:
                id_song_player (int): The unique ID of the song player to check.
        """
        state_online  = "ONLINE"
        state_offline = "OFFLINE"

        song_player = self.spdao.findByID(id_song_player)
        if song_player:
            ip = song_player.IP_adress
            if not self.ping(ip):
                self.spdao.UpdateState(state_offline, id_song_player)
            else:
                self.spdao.UpdateState(state_online, id_song_player)

    def deleteSongPlayer(self, id_song_player):
        """
        Deletes a song player from the system and the database.

            Args:
                id_song_player (int): The unique identifier of the player to be removed.
        """
        self.spdao.deleteSongPlayerInDb(id_song_player)

    def allSongPlayer(self):
        """
        Retrieves all song players available in the system.

            Returns:
                List[SongPlayer]: A list containing all song player instances.
        """
        return self.findAll()

    def findAllSongPlayerByOrganisation(self, id_orga):
        """
        Retrieves and synchronizes the status of all players within an organization.

            Args:
                id_orga (int): The unique ID of the organization.

            Returns:
                list[dict]: A list of song players as dictionaries with refreshed
                            network statuses.
        """
        players = self.spdao.findAllByOrganisationInBd(id_orga)

        for player in players:
            self.changeState(player.id_player)

        updated_players = self.spdao.findAllByOrganisationInBd(id_orga)
        return [vars(player) for player in updated_players]

    def countNumberOfSongPlayerOnlineAndOffline(self, id_orga):
        """
        Counts the number of online and offline song players for a specific organization.

            Args:
                id_orga (int): The unique ID of the organization.

            Returns:
                tuple: A tuple containing (nb_on, nb_off).
        """
        nb_on  = 0
        nb_off = 0

        liste = self.spdao.findAllByOrganisationInBd(id_orga)
        for p in liste:
            d = vars(p)
            if d['state'] == 'ONLINE':
                nb_on += 1
            elif d['state'] == 'OFFLINE':
                nb_off += 1

        return (nb_on, nb_off)

    def run_sync(self, ip, device_name):
        sync_tasks = [
            (os.path.join(app.static_folder, 'audio/'),     "music/"),
            (os.path.join(app.static_folder, 'playlists/'), "playlists/"),
        ]

        base_dest_path = f"/home/{device_name}/SoundStreamDevice/"
        for src, subfolder in sync_tasks:
            full_remote_path = os.path.join(base_dest_path, subfolder)

            subprocess.run(
                ["ssh", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=5",
                 f"{device_name}@{ip}", f"mkdir -p {full_remote_path}"],
                timeout=15
            )

            dest = f"{device_name}@{ip}:{full_remote_path}"
            cmd  = ["rsync", "-avz", "--delete",
                    "-e", "ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5",
                    src, dest]

            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                print(f"Erreur synchro {subfolder} vers {ip} : {e}")

    def sync_to_device(self, ip, device_name):
        """ Envoie les fichiers vers la VM Debian distante dans des dossiers séparés """
        threading.Thread(target=self.run_sync, args=(ip, device_name)).start()

    def remote_play_playlist(self, ip, device_name, playlist_name):
        """ Commande le MPD distant pour charger et lire une playlist précise """
        remote_cmd = f"mpc clear && mpc load {playlist_name} && mpc play"
        ssh_cmd    = ["ssh", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=5",
                      f"{device_name}@{ip}", remote_cmd]

        try:
            subprocess.run(ssh_cmd, check=True)
            print(f"Lecture de {playlist_name} lancée sur {ip}")
        except Exception as e:
            print(f"Erreur lors du chargement de la playlist : {e}")

    def run_check(self):
        """
        Boucle principale du scheduler.

        Tournée toutes les 30 secondes, elle identifie la playlist active et
        la pousse vers les appareils en ligne si elle a changé.

        Le try/except global empêche le thread de mourir silencieusement en
        cas d'erreur passagère (réseau, DB verrouillée, etc.).
        """
        print("Scheduler démarré.")
        while True:
            try:
                now          = datetime.datetime.now()
                current_time = now.strftime("%H:%M")
                current_day  = now.strftime("%A")

                scheduled_playlist = ts.getPlaylistForTime(current_day, current_time)

                if (scheduled_playlist
                        and scheduled_playlist != SongPlayerService._current_playlist):
                    devices = self.spdao.findAllOnlineDevices()
                    if devices:
                        print(f"Changement de playlist : {scheduled_playlist}")
                        for dev in devices:
                            self.remote_play_playlist(
                                dev.IP_adress, dev.device_name, scheduled_playlist
                            )
                    SongPlayerService._current_playlist = scheduled_playlist

                elif (not scheduled_playlist
                        and SongPlayerService._current_playlist is not None):
                    print("Aucune playlist programmée pour le moment.")
                    SongPlayerService._current_playlist = None

            except Exception as e:
                # On affiche l'erreur mais le thread continue de tourner.
                print(f"[Scheduler] Erreur (cycle ignoré) : {e}")

            time.sleep(30)

    def start_background_scheduler(self):
        """ Lance run_check dans un thread daemon. """
        threading.Thread(target=self.run_check, daemon=True).start()