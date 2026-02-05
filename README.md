# Magazine People - Gestion de Journal Divertif

**Magazine People** est un projet de site web dynamique. Il permet de gérer les actualités des célébrités (VIP) : carrières, relations et publications média via une interface liée à une base de données.

##  Auteur
* **Linhny Nguyen**

##  Technologies
* **Backend** : Python (Flask)
* **Base de données** : PostgreSQL
* **Frontend** : HTML, CSS (Jinja2)

## Fonctionnalités
* **Recherche Globale** : Moteur de recherche pour trouver des VIPs, des films, des albums ou des articles.
* **Fiches VIP Détaillées** : Suivi des films, albums, défilés, mariages et liaisons.
* **Interface Administrateur** : Espace sécurisé permettant d'ajouter, modifier ou supprimer du contenu (VIPs, articles, photos, etc.).
* **Vues SQL Avancées** : Statistiques automatisées (ex: Top 5 des divorces, VIPs non apparus récemment).

##  Installation
1. Importer le schéma SQL `Projet_BDD_NGUYEN-Linhny.sql` dans votre instance PostgreSQL.
2. Configurer les accès dans `db.py`.
3. Lancer l'application :
   ```bash
   python3 main.py
