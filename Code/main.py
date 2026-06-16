from app import app
from app.services.SongPlayerService import SongPlayerService
import sqlite3
import os

def _database_is_ready():
    """
    Retourne True si la DB existe et contient toutes les tables requises.
    Retourne False sinon.
    """
    db_path = os.path.join(app.static_folder, 'database', 'database.db')

    if not os.path.exists(db_path):
        return False

    required_tables = {'planned', 'user', 'organisation', 'role',
                   'playlist', 'planning', 'work_link', 'song_player'}
    try:
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        existing_tables = {row[0] for row in rows}
        return required_tables.issubset(existing_tables)
    except Exception:
        return False


def init_database():
    """
    Exécute initdb.py pour créer le schéma et insérer les données de départ.
    Appelé uniquement si la base n'est pas prête.
    """
    initdb_path = os.path.join(
        app.static_folder, 'database', 'initdb.py'
    )
    if not os.path.exists(initdb_path):
        raise FileNotFoundError(
            f"initdb.py introuvable : {initdb_path}\n"
            "Crée la base manuellement avant de relancer l'application."
        )
    import runpy
    runpy.run_path(initdb_path)


sps = SongPlayerService()

if __name__ == "__main__":

    
    if not _database_is_ready():
        print("Base de données manquante ou incomplète — initialisation...")
        init_database()
        print("Base de données prête.")

  
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        sps.start_background_scheduler()

    app.run(host="0.0.0.0", port=8000, debug=True)