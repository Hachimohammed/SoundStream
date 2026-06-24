import sys
import os
import sqlite3

# Add parent directory to path to import app and DAO
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.models.UserDAO import UserDAO
from app.models.LogDAO import LogSqliteDAO

def test_forget_password_tickets():
    print("=== STARTING FORGET PASSWORD TICKETS TEST ===")
    
    # 1. Clear forget_password table and log table (TICKET type logs) for testing
    udao = UserDAO()
    ldao = LogSqliteDAO()
    
    conn = sqlite3.connect(udao.databasename)
    conn.execute("DELETE FROM forget_password")
    conn.execute("DELETE FROM log WHERE type_log = 'TICKET'")
    conn.commit()
    conn.close()
    
    # 2. Check that database is empty of reset tickets
    tickets_org = ldao.findTicketsByOrganization(1)
    if len(tickets_org) != 0:
        print("❌ Echec: Le tableau des tickets n'est pas vide au départ.")
        return False
    
    # 3. Simulate client POST request to /forgotten
    with app.test_client() as client:
        # Romain has email 'romain@soundstream.local' and user_id=2
        user = udao.findByUsername("Romain")
        if not user:
            print("❌ Echec: Utilisateur 'Romain' non trouvé.")
            return False
            
        print(f"Demande de réinitialisation pour {user.username} (email: {user.email})")
        response = client.post('/forgotten', data={
            'email': user.email
        }, follow_redirects=True)
        
        if response.status_code != 200:
            print(f"❌ Echec: POST /forgotten a retourné {response.status_code}")
            return False
            
        print("✅ POST /forgotten exécuté avec succès.")
        
        # 4. Check that no logs of type 'TICKET' were created in log table
        conn = sqlite3.connect(udao.databasename)
        conn.row_factory = sqlite3.Row
        logs = conn.execute("SELECT * FROM log WHERE type_log = 'TICKET'").fetchall()
        if len(logs) > 0:
            print("❌ Echec: Un log de type 'TICKET' a été créé alors qu'on ne devait plus en créer.")
            conn.close()
            return False
        print("✅ Aucun log de type 'TICKET' n'a été créé.")
        
        # 5. Check that a row was added in the forget_password table
        fps = conn.execute("SELECT * FROM forget_password WHERE id_user = ?", (user.id_user,)).fetchall()
        if len(fps) != 1:
            print("❌ Echec: Devrait y avoir exactement 1 enregistrement dans la table 'forget_password'.")
            conn.close()
            return False
        print("✅ Premier enregistrement trouvé dans la table 'forget_password'.")
        conn.close()

        # 5.5 Perform a second password reset request for Romain to verify it persists alongside the first
        print("Deuxième demande de réinitialisation pour Romain...")
        response2 = client.post('/forgotten', data={
            'email': user.email
        }, follow_redirects=True)
        if response2.status_code != 200:
            print(f"❌ Echec: Deuxième POST /forgotten a retourné {response2.status_code}")
            return False

        conn = sqlite3.connect(udao.databasename)
        conn.row_factory = sqlite3.Row
        fps2 = conn.execute("SELECT * FROM forget_password WHERE id_user = ?", (user.id_user,)).fetchall()
        if len(fps2) != 2:
            print(f"❌ Echec: Devrait y avoir exactement 2 enregistrements pour Romain, obtenu : {len(fps2)}")
            conn.close()
            return False
        print("✅ Deuxième enregistrement trouvé dans 'forget_password' (historique conservé !).")
        
        # 6. Retrieve tickets via the updated LogDAO and check the result
        tickets = ldao.findTicketsByOrganization(1) # Romain belongs to Orga1 (id=1)
        if len(tickets) < 2:
            print(f"❌ Echec: findTicketsByOrganization a retourné {len(tickets)} tickets au lieu de 2.")
            conn.close()
            return False
            
        ticket1 = tickets[0]
        ticket2 = tickets[1]
        print(f"Ticket 1 : text='{ticket1.text_log}', date='{ticket1.date_log}', id_log={ticket1.id_log}")
        print(f"Ticket 2 : text='{ticket2.text_log}', date='{ticket2.date_log}', id_log={ticket2.id_log}")
        if ticket1.id_log == ticket2.id_log:
            print("❌ Echec: Les id_log des deux tickets sont identiques.")
            conn.close()
            return False
            
        print("✅ Les tickets ont des id_log uniques et ont été correctement formatés.")
        conn.close()

        # 7. Test that logs page works and doesn't crash (since TICKET logs are deleted)
        # Login as admin
        client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        }, follow_redirects=True)
        
        response_logs = client.get('/logs/Orga1')
        if response_logs.status_code != 200:
            print(f"❌ Echec: GET /logs/Orga1 a retourné {response_logs.status_code} (crash possible)")
            return False
        print("✅ La page des logs fonctionne correctement sans crasher.")
        
    print("=== TOUS LES TESTS FORGET PASSWORD PASSÉS ===")
    return True

if __name__ == "__main__":
    success = test_forget_password_tickets()
    sys.exit(0 if success else 1)
