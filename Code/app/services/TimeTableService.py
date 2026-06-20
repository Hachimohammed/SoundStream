from datetime import datetime, timedelta
from app import app
from app.models.PlaylistDAO import PlaylistDAO
from app.models.FileDAO import FileDAO
import os

class TimeTableService:

    def __init__(self):
        self.pdao = PlaylistDAO()
        self.fdao = FileDAO() # car comme on doit accéder a la table file on utilise le FileDAO

    def getCompleteProg(self, datehour, id_orga):
        """ Get programmation of the day :"""
        ##### PITIÉ A REVOIR JE SUIS PAS SUR QUE CA FONCTIONNE QUOI... #####
        daybdd = datehour.strftime("%A")
        rawlist = self.pdao.get_raw_playlist(daybdd)

        cursor_time = datehour.replace(hour=8, minute=0, second=0, microsecond=0)
        playlist_finale = []

        for nom, strlength, path in rawlist:
            h, m, s = map(int, strlength.split(':'))
            length = timedelta(hours=h, minutes=m, seconds=s)
            
            endhour = cursor_time + length

            if endhour > datehour:
                if cursor_time <= datehour < endhour:
                    status = "playing"
                else:
                    status = "future"
                
                is_promo = ("PROMO" in nom) or ("ads" in path)

                playlist_finale.append({
                    "hour": cursor_time.strftime("%d/%m/%Y - %H:%M"),
                    "titre": nom,
                    "status": status,
                    "is_promo": is_promo
                })

            cursor_time = endhour

        return playlist_finale
    
    ####################
    ## EDIT PLAYLISTS ##
    ####################
    
    def getAllPlaylists(self):
        return self.pdao.findAll()
    
    def getPlaylistById(self, playlist_id):
        return self.pdao.findById(playlist_id)
    
    def addFileInPlaylist(self,playlist_id,id_file) -> bool: 
        return self.pdao.addFileToPlaylist(playlist_id,id_file)
    
    def deleteFileFromPlaylist(self,playlist_id,id_file) -> bool :
        return self.pdao.removeFileFromPlaylist(playlist_id,id_file)
    
    def getPlaylistDetails(self, playlist_id):
        playlist = self.pdao.findById(playlist_id)
        if not playlist:
            return None
        files = self.fdao.getFilesInPlaylist(playlist_id)
        
        title_count = sum(1 for f in files if f.type_file.lower() == 'mp3')
        ads_count = sum(1 for f in files if f.type_file.lower() == 'ad')
        
        return {
            'playlist': playlist,
            'files': files,
            'title_count': title_count,
            'ads_count': ads_count
        }
    
    def createPlaylist(self, playlist_name) -> None:
        self.pdao.createPlaylist(playlist_name)

    def deletePlaylist(self, playlist_id) -> None:
        self.pdao.deletePlaylist(playlist_id)


    ############################
    ## EDIT PLAYLIST FOR DAYS ##
    ############################

    def getAllDaysWithPlaylists(self):
        days = self.pdao.getAllDays()
        days_data = []

        for day in days:
            day_name = day['diffusing_day'] 
            playlists = self.pdao.getPlannedPlaylistsForDay(day_name)
            
            days_data.append({
                'day_name': day_name,
                'details': day,
                'playlists': playlists
            })
            
        return days_data
    
    def updateDaySchedule(self, day_name, playlist_id, start_time):
        self.pdao.removeAllPlaylistsFromDay(day_name)
        if playlist_id is not None and start_time:
            self.pdao.addPlaylistToDay(playlist_id, day_name, start_time)

    def getPlaylistNameById(self, playlist_id):
        playlist =self.pdao.findById(playlist_id)
        if playlist:
            return playlist.name
        return None

    def generateM3uContent(self, playlist_id: int) -> str:
        ''' Generate M3U content with all the references of the files contained in the playlist'''

        # we get all the details in the playlist
        details = self.getPlaylistDetails(playlist_id)

        files = details['files']

        m3u_lines = ['#EXTM3U']

        for file in files : 
            #parsage du format MM:SS en secondes pures
            time_in_seconds = 0
            split_time = file.time_length.split(':')
            time_in_seconds = int(split_time[0])*60 + int(split_time[1])

            #add the lines of each file to the m3u file
            m3u_lines.append(f"#EXTINF:{time_in_seconds},{file.name}")

            filename_only = os.path.basename(file.path)
            m3u_lines.append(filename_only)
        
        #join all the lines to create the string 
        # which represents the conntent of the m3u file 
        # and return it 
        m3u_content= "\n".join(m3u_lines)
        return m3u_content
    

    def updateM3uFile(self, playlist_id : int) -> bool :
        '''Generate the m3u file and crush the existant file when it's an update'''
        content = self.generateM3uContent(playlist_id)
        playlist = self.getPlaylistById(playlist_id)
        playlist_name = playlist.name
        if content == None :
            return False

        folder = os.path.join(app.static_folder, 'playlists')

        file_path = os.path.join(folder, f"playlist_{playlist_name}.m3u")

        with open(file_path, 'w', encoding='utf-8') as f :
            f.write(content)

        return True


    def getPlaylistForTime(self, current_day, current_time) :
        ''' Identifie la playlist active et renvoie uniquement son nom '''
        raw_rows = self.pdao.getRawScheduleForDay(current_day)
        
        try:
            now_dt = datetime.strptime(current_time, "%H:%M")
        except ValueError:
            now_dt = datetime.strptime(current_time, "%H:%M:%S")

        cursor = 0 
        last_plist_start = 0

        for row in raw_rows:
            playlist_start = row['playlist_start']
            if not playlist_start:
                continue
            
            if playlist_start != last_plist_start:
                last_plist_start = playlist_start
                try:
                    cursor = datetime.strptime(playlist_start, "%H:%M")
                except ValueError:
                    cursor = datetime.strptime(playlist_start, "%H:%M:%S")

            duration = row['time_length']
            if duration:
                parts = list(map(int, duration.split(':')))
                if len(parts) == 3: h, m, s = parts
                elif len(parts) == 2: h, m, s = 0, parts[0], parts[1]
                else: h, m, s = 0, 0, 0
                duration_delta = timedelta(hours=h, minutes=m, seconds=s)
            else:
                duration_delta = timedelta(0)

            start_dt = cursor
            end_dt = cursor + duration_delta

            if start_dt <= now_dt < end_dt:
                return f"playlist_{row['playlist_name']}"

            cursor = end_dt

        return None

    
    def autoCleanPlaylists(self):
        return self.pdao.deleteObsoletePlaylists()

    ####################################
    ## Calendar view & Timetable view ##
    ####################################

    def getDayGrid(self, day_name: str) -> dict:
        ''' Generate a timetable grid for a specific day '''
        raw_rows = self.pdao.getRawScheduleForDay(day_name)
        grid = {}
        
        cursor = 0 
        last_plist_start = 0

        for row in raw_rows:
            playlist_start = row['playlist_start'] 
            if not playlist_start:
                continue
            
            if playlist_start != last_plist_start:
                last_plist_start = playlist_start
                try:
                    cursor = datetime.strptime(playlist_start, "%H:%M")
                except ValueError:
                    cursor = datetime.strptime(playlist_start, "%H:%M:%S")

            duration = row['time_length']
            if duration:
                parts = list(map(int, duration.split(':')))
                if len(parts) == 3: h, m, s = parts
                elif len(parts) == 2: h, m, s = 0, parts[0], parts[1]
                else: h, m, s = 0, 0, 0
                duration_delta = timedelta(hours=h, minutes=m, seconds=s)
            else:
                duration_delta = timedelta(0)

            start_key = cursor.strftime("%H:%M") 
            
            end_dt = cursor + duration_delta
            end_display = end_dt.strftime("%H:%M")

            track_info = {
                "name": row['file_name'],
                "start": start_key,
                "end": end_display
            }

            if start_key not in grid:
                grid[start_key] = []
            grid[start_key].append(track_info)

            cursor = end_dt

        return grid

    def getNextTracks(self) -> list[dict]:
        """ Get a list of the next tracks after the current time on a specific day """

        now = datetime.now()
        day_name = now.strftime("%A")

        current_time_str = now.strftime("%H:%M:%S")
        now_dt = datetime.strptime(current_time_str, "%H:%M:%S")

        raw_rows = self.pdao.getRawScheduleForDay(day_name)

        upcoming_tracks = []
        cursor = None 
        last_plist_start = None

        for row in raw_rows:
            playlist_start = row['playlist_start']

            if not playlist_start:
                continue
            
            if playlist_start != last_plist_start:
                last_plist_start = playlist_start
                cursor = datetime.strptime(playlist_start, "%H:%M")

            duration = row['time_length']
            if duration:
                parts = list(map(int, duration.split(':')))
                if len(parts) == 3: h, m, s = parts
                elif len(parts) == 2: h, m, s = 0, parts[0], parts[1]
                else: h, m, s = 0, 0, 0
                duration_delta = timedelta(hours=h, minutes=m, seconds=s)
            else:
                duration_delta = timedelta(0)

            start_dt = cursor
            end_dt = cursor + duration_delta
            if start_dt > now_dt:
                upcoming_tracks.append({
                    "name": row['name'],
                    "id_playlist": row['id_playlist'],
                    "start": start_dt.strftime("%H:%M"),
                    "end": end_dt.strftime("%H:%M")
                })
            cursor = end_dt

        return upcoming_tracks