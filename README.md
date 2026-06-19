# SAE 401 : Développement d'une application
## 🎵 Projet : Diffusion sonore

**Groupe :** Neptune 4  
**Dépôt du projet :** [🔗 GitHub - SoundStream](https://github.com/Hachimohammed/SoundStream)

---

### 👥 Membres de l'équipe

* **ALJANE** Saïf-eddine
* **CASSEL** Kadir
* **HACHIM** Mohammed
* **SEFRAOUI** Nassim
* **SY** Aboubakry

###  Compétence 5 : Analyse de l'existant

* **[Critères d'analyse](/SoundStream/00-Documents/Compétence5_S4/Critères_d’analyse.pdf)**

Voici les rapports d'analyse des différents projets (un document par projet) :

* **Projet du groupe S3 Neptune B :** [Rapport d'analyse de HeyDo](/SoundStream/00-Documents/Compétence5_S4/RAPPORT_D'ANALYSE_HeyDo.pdf)
* **Projet du groupe S3 Neptune C :** [Rapport d'analyse de SoundStream](/SoundStream/00-Documents/Compétence5_S4/nom_du_fichier.pdf) *(lien à compléter)*
* **Projet du groupe S3 Neptune D :** [Rapport d'analyse de SoundStream](/SoundStream/00-Documents/Compétence5_S4/nom_du_fichier.pdf) *(lien à compléter)*
* **Projet du groupe S3 Neptune E :** [Rapport d'analyse de MusiQuali](/SoundStream/00-Documents/Compétence5_S4/Rapport_analyse_MusiQuali.pdf)

**Projet choisi (Neptune A) - Analyse approfondie :**
*  **[Rapport d'analyse de SoundStream](/SoundStream/00-Documents/Compétence5_S4/Rapport_analyse_SoundStream.pdf)**

---

### 📋 Tâches à réaliser

- [ ] Ajouter le fichier Excel avant la soutenance.

    
 


### Comment lancer l'application :
Il est nécessaire d'utiliser un environnement virtuel Python pour isoler les dépendances.

```bash
python3 -m venv env

# Windows
.\env\Scripts\activate

# macOS / Linux
source env/bin/activate

pip install -r requirements.txt

# Dans le répertoire SoundStream/Code
python3 main.py

```
Puis mettre l'URL http://127.0.0.1:8000/ dan votre navigateur.

### Qu'est ce que SoundStream
SoundStream est un projet que nous sommes en train de réaliser dans le cadre de la SAÉ S301 (SAÉ = projet évalué qui regroupe un ensemble de compétances afin de pouvoir appliquer les principes théoriques vus en cours). Elle est réalisée en groupe et consiste en le développement d'une application web complète.


### 🖊️ Descriptif du projet

Dans beaucoup d’organisations (entreprises, collectivités, gares, campus…), il faut assurer une diffusion musicale continue, avec insertion de messages publicitaires et possibilité de lancer des messages urgents. L’enjeu est de garantir la continuité de service : même en cas de coupure réseau, il doit toujours y avoir de la musique qui joue. La supervision permet en plus de vérifier que chaque lecteur est bien en fonctionnement et que ses playlists de secours sont correctement synchronisées.

L’idée serait de mettre en place un système de supervision qui permette :
- de suivre l’état des lecteurs
- de mettre à jour en central la playlist locale et de la synchroniser automatiquement sur les lecteurs
- de vérifier que la playlist locale de secours est bien à jour
- de consigner les messages diffusés (musique, publicité, urgent)
- et de déclencher des alertes en cas de problème (lecteur KO, playlist obsolète,absence de diffusion).

Les étudiants développeraient la solution pour un pilote :
1. Deux lecteurs test (site principal + 2 sites distants)
2. Tableau de bord simple (état, synchro, “now playing”)
3. Stocker l’historique.
4. Scénarios de test : coupure réseau, coupure électrique, diffusion d’un message urgent, respect du planning des publicités.
