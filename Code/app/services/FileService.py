import os
import math
from typing import *

# Werkzeug: Flask's utility library
from werkzeug.utils import secure_filename      # Essential security tool to clean filenames (prevents hacking)
from werkzeug.datastructures import FileStorage # Used only for type hinting (helps IDE auto-completion)
from tinytag import TinyTag

from app import app
from app.models.FileDAO import FileDAO

class FileService:
    """
    Service responsible for managing audio files.
    It handles physical storage on the disk and database interactions.
    """

    # List of allowed file extensions for security
    ALLOWED_EXTENSIONS = ["mp3"]

    def __init__(self):
        """
        Initializes the FileService.
        Creates the upload folder if it does not exist.
        """
        self.fdao = FileDAO()
        # Define 'audio' as the physical storage folder
        self.upload_folder = os.path.join(app.static_folder, 'audio')

        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def _fileIsAllowed(self, filename: str) -> bool:
        """
        Checks if the uploaded file has a valid extension.

        Args:
            filename (str): The name of the file.

        Returns:
            bool: True if the extension is allowed, False otherwise.
        """
        # Logic explanation:
        # Check if '.' is in the filename.
        # rsplit('.', 1): Split string from the right, once.
        # [1]: Take the second part (the extension).
        # lower(): Convert to lowercase to avoid case sensitivity issues.
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def _getTimeLengthOfFile(self, absolute_path: str) -> str:
        """
        Calculates the audio file duration in MM:SS format.
        Reads the file's metadata using the TinyTag library.

        Args:
            absolute_path (str): The full path to the file on the disk.

        Returns:
            str: The duration in 'MM:SS' format.
                 Returns '00:00' if the metadata cannot be read.
        """
        try:
            # 1. Check if the file exists on the disk
            if not os.path.exists(absolute_path):
                return "00:00"
            
            # 2. Read the audio metadata
            tag = TinyTag.get(absolute_path)
            
            if tag.duration is None:
                return "00:00"
        
            # 3. Format the duration into minutes and seconds
            length_in_seconds = int(tag.duration)
            minutes = length_in_seconds // 60
            seconds = length_in_seconds % 60
            
            return f"{minutes:02d}:{seconds:02d}"

        except Exception as e:
            print(f"Error reading metadata: {e}")
            return "00:00"

    def createFileFromForm(self, form_data: dict, file_storage: FileStorage) -> int:
        """
        Main method to handle the file upload process.

        Args:
            form_data (dict): Contains form text data (e.g., file_type).
            file_storage (FileStorage): The file object from the request.

        Returns:
            int: The ID of the file in the database.
                 Returns -1 if an error occurs.
        """
        # Check if file exists in the request
        if not file_storage or not file_storage.filename:
            return -1
            
        # Validate extension
        if not self._fileIsAllowed(file_storage.filename):
            print(f"Forbidden extension: {file_storage.filename}")
            return -1
        
        try:
            # Physical Save
            # secure_filename removes dangerous characters (for example "../")
            name_file = secure_filename(file_storage.filename) 
            absolute_path = os.path.join(self.upload_folder, name_file)
            relative_path = f"audio/{name_file}"

            #  save the file physically 
            file_storage.save(absolute_path) 

            # Duration Analysis (now that the file exists on disk)
            length = self._getTimeLengthOfFile(absolute_path)

            # Database Interaction
            # .get('key', 'default') prevents crashing if 'file_type' is missing
            file_type = form_data.get('file_type', 'mp3')
            existing_file = self.fdao.findByName(name_file)

            # Check for duplicates to prevent adding the same file twice
            if existing_file:
                return existing_file.id_file
            else:
                # Create new entry
                id_file = self.fdao.createFile(name_file, relative_path, length, file_type)
                return id_file # Return the new ID to the controller

        except Exception as e:
            print(f"Service error: {e}")
            return -1
        
    def deleteFileFromPlaylist(self, id_file: int) -> bool:
        """
        Permanently deletes a file from the system.
        
        It performs two actions:
        -Removes the physical file from the disk (audio folder).
        -Removes the file entry from the database.

        Args:
            id_file (int): The unique identifier of the file to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        # 1. Retrieve file info to get the filename
        file_to_delete = self.fdao.findFileById(id_file) 

        if not file_to_delete:
            return False
            
        try:
            # Construct the absolute path to the physical file
            absolute_path = os.path.join(self.upload_folder, file_to_delete.name)

            # 2. Delete the physical file if it exists
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
            else:
                print(f"Warning: File not found on disk: {absolute_path}")
                
        except Exception as e:
            print(f"Error deleting physical file: {e}")
            # We continue execution to ensure the database entry is removed even if the file is missing

        # 3. Delete from Database and return the boolean result (True/False)
        return self.fdao.deleteFile(id_file)
        


