from db import *


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
app.secret_key = 'NILHYN'

@app.route("/")
def home():
    hommes_divorces = []
    vips_non_apparus = []

    if session.get('is_connected', False):
        print("Vous êtes connectées ADMIN")
    else:
        print("Vous n'etes pas connecté(e)")

    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM top_5_hommes_divorces;")
        hommes_divorces = cursor.fetchall()

        cursor.execute("SELECT * FROM vip_non_apparus_article;")
        vips_non_apparus = cursor.fetchall()

    return render_template(
        "test.html",
        hommes_divorces=hommes_divorces,
        vips_non_apparus=vips_non_apparus,
        is_connected=session.get('is_connected', False)
    )


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    results = {"VIP": [], "REVUE": [], "FILM": [], "ALBUM": [], "PHOTOS": []}
    
    if query:
        with connect() as conn:
            cursor = conn.cursor()
            
 
            cursor.execute("SELECT idVip, nom, prenom FROM vip WHERE LOWER(nom) LIKE LOWER(%s) OR LOWER(prenom) LIKE LOWER(%s)", 
                           (f"%{query}%", f"%{query}%"))
            results["VIP"] = cursor.fetchall()

        
            cursor.execute("SELECT nomRevue FROM revue WHERE LOWER(nomRevue) LIKE LOWER(%s)", (f"%{query}%",))
            results["REVUE"] = cursor.fetchall()

       
            cursor.execute("SELECT numeroVisa, idRealisateur, titre, dateRealisation, descriptif FROM film WHERE LOWER(titre) LIKE LOWER(%s)", (f"%{query}%",))
            results["FILM"] = cursor.fetchall()

      
            cursor.execute("SELECT idAlbum, nom_album FROM album WHERE LOWER(nom_album) LIKE LOWER(%s)", (f"%{query}%",))
            results["ALBUM"] = cursor.fetchall()

       
            cursor.execute("SELECT numPhoto, imageNumerise, circonstance FROM photo WHERE LOWER(circonstance) LIKE LOWER(%s)", (f"%{query}%",))
            results["PHOTOS"] = cursor.fetchall()
            
    return render_template("search_results.html", query=query, results=results)


 

@app.route("/celebrite" ,methods=['GET', 'POST'])
def render_celebrite():

    sort_order = request.args.get("sort", "asc") 
    order_clause = "ASC" if sort_order == "asc" else "DESC"
    print('Ordre de tri :')
    print(order_clause)

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM VIP ORDER BY nom {order_clause}, prenom {order_clause};")
            lst=cur.fetchall()
    conn.close()
    print("Route vers vip ok\n")
    print(lst)
    return render_template("celebrite.html", lst_celebrite = lst, is_connected = session.get('is_connected', False), sort_order=sort_order)


@app.route("/admin_celebrite", methods=["GET", "POST"])
def admin_celebrite():

    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vip")
        celebrites = cursor.fetchall()
        cursor.close()


    if request.method == 'POST' and 'supprimer' in request.form:
        celebrites_id = request.form['supprimer']
        
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vip WHERE idVip = %s", (celebrites_id,))
            conn.commit()
            cursor.close()

        
        return redirect(url_for('admin_celebrite'))

    return render_template('admin_celebrite.html', celebrites=celebrites, is_connected=session.get('is_connected', False))


@app.route("/modifier_celebrite/<int:id>", methods=["GET", "POST"])
def modifier_celebrite(id):
    with connect() as conn:
        cursor = conn.cursor()

      
        cursor.execute("SELECT * FROM vip WHERE idVip = %s", (id,))
        celebrite = cursor.fetchone()

      
        cursor.execute("SELECT taille, nomAgence FROM manequin WHERE idManequin = %s", (id,))
        mannequin_data = cursor.fetchone()
        is_mannequin = mannequin_data is not None 

    if request.method == "POST":
      
        nom = request.form['nom']
        prenom = request.form['prenom']
        sexe = request.form['sexe']
        nationalite = request.form['nationalite']
        datenais = request.form['datenais']
        datedeces = request.form.get('datedeces') or None


        is_mannequin_checked = 'is_mannequin' in request.form
        taille = request.form.get('taille') or None
        nom_agence = request.form.get('nomAgence') or None

        is_musicien_checked = 'is_musicien' in request.form
        specialite = request.form['specialite']
        nomMaisonDisque = request.form['nomMaisonDisque']

        with connect() as conn:
            cursor = conn.cursor()

       
            cursor.execute(
                """UPDATE vip 
                   SET nom = %s, prenom = %s, sexe = %s, nationalite = %s, datenais = %s, datedeces = %s 
                   WHERE idVip = %s""",
                (nom, prenom, sexe, nationalite, datenais, datedeces, id)
            )

         
            cursor.execute("SELECT COUNT(*) FROM manequin WHERE idManequin = %s", (id,))
            mannequin_exists = cursor.fetchone()[0] > 0

            if is_mannequin_checked:
                if mannequin_exists: 
                    cursor.execute(
                        "UPDATE manequin SET taille = %s, nomAgence = %s WHERE idManequin = %s",
                        (taille, nom_agence, id)
                    )
                else:  
                    cursor.execute(
                        "INSERT INTO manequin (idManequin, taille, nomAgence) VALUES (%s, %s, %s)",
                        (id, taille, nom_agence)
                    )
            elif mannequin_exists:
                cursor.execute("DELETE FROM manequin WHERE idManequin = %s", (id,))

           
            cursor.execute("SELECT COUNT(*) FROM musicien where idArtiste = %s", (id,))
            musicien_exists = cursor.fetchone()[0] > 0

            if is_musicien_checked:
                if musicien_exists:
                    cursor.execute("UPDATE musicien SET specialite = %s, nomMaisonDisque = %s WHERE idMusicien = %s", (specialite, nomMaisonDisque, id))
                
                else:
                    cursor.execute(
                        "INSERT INTO musicien (idArtiste, specialite, nomMaisonDisque) VALUES ( %s, %s, %s)", (id, specialite, nomMaisonDisque)
                    )
            elif musicien_exists:
                cursor.execute("DELETE FROM musicien WHERE idMusicien = %s", (id,))



            conn.commit()

        return redirect(url_for('admin_celebrite'))

    return render_template(
        'modifier_celebrite.html',celebrite=celebrite,is_mannequin=is_mannequin, taille=mannequin_data[0] if is_mannequin else "", nom_agence=mannequin_data[1] if is_mannequin else "",
        is_connected=session.get('is_connected', False)
    )


@app.route("/revue")
def render_revue():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT nomRevue, dateparution FROM revue;")
            lst=cur.fetchall()
    conn.close()
    print("Route vers revue ok\n")
    print(lst)
    return render_template("revue.html", lst_revues = lst, is_connected = session.get('is_connected', False))

@app.route("/ajouter_revue", methods=["GET", "POST"])
def ajouter_revue():
    if request.method == "POST":

        nom = request.form['nom_revue']
        date = request.form['dateParution']

        with connect() as conn:
            cursor = conn.cursor()


        cursor.execute(
            "INSERT INTO revue (nomRevue, dateParution) VALUES (%s, %s)",
            (nom, date)
        )


        conn.commit()
        cursor.close()
        conn.close()


        return redirect(url_for('render_revue'))
    return render_template("ajouter_revue.html", is_connected=session.get('is_connected', False))

    
@app.route("/article/<id_revue>")
def render_article(id_revue) :
    print("Id revue concernée :")
    print(id_revue) 
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * from article NATURAL JOIN contenu_article NATURAL JOIN revue where revue.NomRevue = %s", (id_revue,))
            lst=cur.fetchall()
    conn.close()
    print("Route vers article ok\n")
    print(lst)
    return render_template("article.html", lst_article= lst, is_connected=session.get('is_connected', False))

@app.route("/film")
def render_film():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT nom, prenom, titre, dateRealisation, descriptif FROM film JOIN vip ON vip.idvip = film.idRealisateur;")
            lst=cur.fetchall()
    conn.close()
    print("Route vers film ok\n")
    print(lst)
    return render_template("film.html", lst_films = lst)

@app.route("/defile")
def render_defile():
    with connect() as conn:
        cursor = conn.cursor()


        cursor.execute("""
            SELECT * from defile NATURAL LEFT JOIN adefile NATURAL LEFT JOIN Arealise;
        """)
        lst_defile = cursor.fetchall()
        print(lst_defile)

    return render_template("defile.html", lst_defile=lst_defile, is_connected=session.get('is_connected', False))


@app.route("/album")
def render_album():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * from album NATURAL LEFT JOIN a_composer ;")
            lst=cur.fetchall()
    conn.close()
    print("Route vers album ok\n")
    print(lst)
    return render_template("album.html", lst_album=lst, is_connected = session.get('is_connected', False))

@app.route('/modifier_album/<int:id_album>', methods=['GET', 'POST'])
def modifier_album(id_album):
    with connect() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT nom_album, daterealisation FROM album WHERE idAlbum = %s", (id_album,))
        album = cursor.fetchone()

   
        cursor.execute("""
            SELECT idArtiste FROM a_composer WHERE idAlbum = %s
        """, (id_album,))
        artistes_associes = [row[0] for row in cursor.fetchall()]

     
        cursor.execute("SELECT idArtiste, nom, prenom from musicien JOIN vip on idArtiste=idVip;")
        lst_vip = cursor.fetchall()

    if request.method == 'POST':
        nom_album = request.form['nom_album']
        daterealisation = request.form['daterealisation']
        idArtistes = request.form.getlist('idArtistes')

        with connect() as conn:
            cursor = conn.cursor()

       
            cursor.execute("""
                UPDATE album 
                SET nom_album = %s, daterealisation = %s 
                WHERE idAlbum = %s
            """, (nom_album, daterealisation, id_album))

          
            cursor.execute("DELETE FROM a_composer WHERE idAlbum = %s", (id_album,))

            
            for id_vip in idArtistes:
                cursor.execute("INSERT INTO a_composer (idAlbum, idArtiste) VALUES (%s, %s)", (id_album, id_vip))

            conn.commit()

        return redirect(url_for('render_album'))

    return render_template('modifier_album.html', album=album, lst_vip=lst_vip, artistes_associes=artistes_associes, is_connected=session.get('is_connected', False))


@app.route('/supprimer_album/<int:id_album>', methods=['POST'])
def supprimer_album(id_album):
    with connect() as conn:
        cursor = conn.cursor()

    
        cursor.execute("DELETE FROM a_composer WHERE idAlbum = %s", (id_album,))
        cursor.execute("DELETE FROM album WHERE idAlbum = %s", (id_album,))
        conn.commit()

    return redirect(url_for('render_album'))




@app.route("/ajouter_celebrite", methods=["GET", "POST"])
def ajouter_celebrite():
    if request.method == "POST":
  
        nom = request.form['nom']
        prenom = request.form['prenom']
        sexe = request.form['sexe']
        nationalite = request.form['nationalite']
        datenais = request.form['datenais']
        datedeces = request.form['datedeces']

        is_mannequin = 'is_mannequin' in request.form
        taille = request.form.get('taille') or None
        nom_agence = request.form.get('nomAgence') or None

        if not datedeces:
            datedeces=None

     
        with connect() as conn:
            cursor = conn.cursor()

   
        cursor.execute(
            "INSERT INTO vip (nom, prenom,sexe,nationalite, datenais, datedeces) VALUES (%s, %s, %s, %s, %s, %s) RETURNING idVip",
            (nom, prenom, sexe, nationalite, datenais, datedeces)
        )

        id_vip = cursor.fetchone()[0]
     
        if is_mannequin:
            cursor.execute(
                "INSERT INTO manequin (idManequin, taille, nomAgence) VALUES (%s, %s, %s)",
                (id_vip, taille, nom_agence)
            )

     
        conn.commit()
        cursor.close()
        conn.close()

    
        return redirect(url_for('render_celebrite'))
    
    return render_template('ajouter_celebrite.html', is_connected = session.get('is_connected', False))


@app.route('/ajouter_album', methods=['GET', 'POST'])
def ajouter_album():
    lst_vip = [] 
    
    try:
       
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT idArtiste, nom, prenom FROM musicien JOIN vip on idArtiste=idVip;")
            lst_vip = cursor.fetchall()

        if request.method == 'POST':
       
            nom_album = request.form.get('nom_album')
            daterealisation = request.form.get('daterealisation')
            idArtistes = request.form.getlist('idArtistes') 

            print(nom_album)
            print(daterealisation)
            print(idArtistes)

      
            if not nom_album or not daterealisation or not idArtistes:
                return redirect(url_for('ajouter_album'))

       
            with connect() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT MAX(idAlbum) FROM album")
                max_id_album = cursor.fetchone()[0]

         
                if max_id_album is None:
                    next_id_album = 1
                else:
                    next_id_album = max_id_album + 1 
                print(f"Prochain idAlbum : {next_id_album}")

                cursor.execute(
                    "INSERT INTO album (idAlbum, nom_album, daterealisation) VALUES (%s, %s, %s) RETURNING album.idalbum",
                    (next_id_album, nom_album, daterealisation)
                )
                id_album = cursor.fetchone()[0] 
                print("Id de l'album créé :")
                print(id_album)


               
                print("\nArtistes ayant composé l'album :")
                print(idArtistes)
                for id_vip in idArtistes:
                  
                    cursor.execute(
                        "SELECT COUNT(*) FROM musicien WHERE idArtiste = %s",
                        (id_vip,)
                    )
                    is_musicien = cursor.fetchone()[0]

                  
                    if not is_musicien:
                        print(f"Ajout de l'artiste {id_vip} dans la table 'musicien'")
                        cursor.execute(
                            "INSERT INTO musicien (idArtiste, specialite, nomMaisonDisque) VALUES (%s, %s, %s)",
                            (id_vip, None, None) 
                        )

                   
                    cursor.execute(
                        "INSERT INTO a_composer (idAlbum, idArtiste) VALUES (%s, %s)",
                        (id_album, id_vip)
                    )
                conn.commit()  

      
            return redirect(url_for('render_album'))

    except Exception as e:
        print(f"Erreur : {e}") 

 
    return render_template('ajouter_album.html', vips=lst_vip, is_connected = session.get('is_connected', False))


@app.route('/vip/<int:id_vip>')
def render_vip_summary(id_vip):
    try:
        vip_info = {}
        with connect() as conn:
            cursor = conn.cursor()
            
          
            cursor.execute("SELECT nom, prenom, sexe, nationalite, datenais, datedeces FROM vip WHERE vip.idVip = %s", (id_vip,))
            vip_info['details'] = cursor.fetchone()
            
          
            cursor.execute("""
                SELECT nom_album, daterealisation 
                FROM album 
                NATURAL JOIN a_composer 
                WHERE idArtiste = %s
            """, (id_vip,))
            vip_info['albums'] = cursor.fetchall()

       
            cursor.execute("""
                SELECT datedefile, lieu 
                FROM defile 
                NATURAL JOIN adefile 
                WHERE idManequin = %s
            """, (id_vip,))
            vip_info['defiles'] = cursor.fetchall()
            
         
            cursor.execute("""
                SELECT titre, dateRealisation, descriptif 
                FROM film 
                NATURAL JOIN joue 
                WHERE idActeur = %s
            """, (id_vip,))
            vip_info['films'] = cursor.fetchall()
            
      
            cursor.execute("""
                SELECT * 
                FROM photo JOIN apparait_photo ON apparait_photo.numPhoto=photo.numPhoto 
                WHERE idVip = %s
            """, (id_vip,))
            vip_info['photos'] = cursor.fetchall()

        
            cursor.execute("""
                SELECT 
                v1.nom AS Nom_VIP1, v1.prenom AS Prenom_VIP1,
                v2.nom AS Nom_VIP2, v2.prenom AS Prenom_VIP2,
                m.dateMariage AS DateMariage,
                m.dateSeparation AS DateSeparation,
                m.lieu AS Lieu
                FROM mariage m
                JOIN VIP v1 ON m.idVip1 = v1.idVip
                JOIN VIP v2 ON m.idVip2 = v2.idVip
                WHERE m.idVip1 = %s or m.idVip2 = %s;
            """,(id_vip,id_vip))
            vip_info['mariage']=cursor.fetchall()

            print("Marriage" +str(vip_info['mariage']))

            cursor.execute("""
                SELECT 
                v1.nom AS Nom_VIP1, v1.prenom AS Prenom_VIP1,
                v2.nom AS Nom_VIP2, v2.prenom AS Prenom_VIP2,
                l.dateLiaison AS DateLiaison,
                l.dateSeparation AS DateSeparation,
                l.motifSeparation AS MotifSeparation
                FROM liaison l
                JOIN VIP v1 ON l.idVip1 = v1.idVip
                JOIN VIP v2 ON l.idVip2 = v2.idVip
                WHERE l.idVip1 = %s OR l.idVip2 = %s;
            """,(id_vip, id_vip))
            vip_info['liaisons']=cursor.fetchall()
            print("Liaisons" +str(vip_info['liaisons']))


            print("ok jusqu'a article\n")
            print(vip_info["details"][1])
            print(vip_info["details"][0])
      
            cursor.execute("""
                SELECT * 
                from apparait_article 
                NATURAL JOIN article NATURAL JOIN contenu_article NATURAL JOIN revue
                where idvip = %s;""",(id_vip,))
            vip_info['articles'] = cursor.fetchall()
            print(vip_info['articles'])



        print(f"Données pour le VIP {id_vip} récupérées : {vip_info}")
        return render_template('vip_summary.html', vip_info=vip_info)

    except Exception as e:
        print(f"Erreur : {e}")
        return "Une erreur s'est produite lors de la récupération des données."


@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():

    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT idVip, nom, prenom FROM vip")
    vips = cursor.fetchall() 
    cursor.close()
    connection.close()


    if request.method == 'POST':
        
        file = request.files['image']
        photographe = request.form['photographe']
        lieu = request.form['lieu']
        circonstance = request.form['circonstance']
        selected_vips = request.form.getlist('vips')

        print(file)
        print(photographe)
        print(lieu)
        print(circonstance)
        
        if file:
        
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
          
            connection = connect()
            cursor = connection.cursor()

            cursor.execute("SELECT MAX(numPhoto) FROM photo")
            max_id_photo = cursor.fetchone()[0]

          
            if max_id_photo is None:
                next_id_photo = 1
            else:
                next_id_photo = max_id_photo + 1 
            print(f"Prochain idPhoto : {next_id_photo}")


            cursor.execute("""
                INSERT INTO photo (numPhoto, imageNumerise, photographe, lieu, circonstance) 
                VALUES (%s, %s, %s, %s, %s) RETURNING photo.numPhoto
            """, (next_id_photo, filename, photographe, lieu, circonstance))

            id_photo=cursor.fetchone()[0]
            print("Id de la photo uploadé :")
            print(id_photo)
            

            for id_vip in selected_vips:
                cursor.execute("""
                    INSERT INTO apparait_photo (idVip, numPhoto) 
                    VALUES (%s, %s)
                """, (id_vip, id_photo))
            connection.commit()

            cursor.close()
            connection.close()

       
            return redirect(url_for('render_photos'))

    return render_template('upload_photo.html', vips=vips, is_connected = session.get('is_connected', False))



@app.route('/supprimer_photo/<int:numPhoto>', methods=["GET", "POST"])
def supprimer_photo(numPhoto):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute("SELECT imageNumerise FROM photo WHERE numPhoto = %s", (numPhoto,))
    photo = cursor.fetchone()

    if photo:
        image_filename = photo[0]
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

 
        if os.path.exists(image_path):
            os.remove(image_path)
        
 
        cursor.execute("DELETE FROM apparait_photo WHERE numPhoto = %s", (numPhoto,))
        cursor.execute("DELETE FROM photo WHERE numPhoto = %s", (numPhoto,))
        connection.commit()

    cursor.close()
    connection.close()

  
    return redirect(url_for('render_photos'))
    


@app.route('/ajouter_article', methods=["GET", "POST"])
def ajouter_article():
    lst_revues = []
    
    
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT idVip, nom, prenom FROM vip")
    vips = cursor.fetchall()  
    cursor.close()
    connection.close()


    with connect() as conn:
        cursor = conn.cursor()

   
        cursor.execute("""
            SELECT * FROM revue 
            NATURAL LEFT JOIN contenu_article 
            NATURAL LEFT JOIN article;
        """)
        lst_revues = cursor.fetchall()
        print("Liste des revues qui sont choissisables :")
        print(lst_revues)

        cursor.execute("SELECT MAX(idArticle) FROM article")
        max_id_article = cursor.fetchone()[0] 

  
        if max_id_article is None:
            next_id_article = 1
        else:
            next_id_article = max_id_article + 1 
        print(f"Prochain idArticle : {next_id_article}")

        if request.method == 'POST':
            try:
      
                titre = request.form['titre']
                resume = request.form['resume']
                nomRevue = request.form.get('nomRevue')
                selected_vips = request.form.getlist('vips')
                if not nomRevue or nomRevue == 'None':
                    print("Erreur : Aucun nomRevue valide fourni.")
                    return redirect(url_for('ajouter_article'))
                print("Nom de la revue reçu :", nomRevue)

        
                if not titre or not resume or not nomRevue:
                    return redirect(url_for('ajouter_article'))

      
                cursor.execute("INSERT INTO article (idArticle, titre, resume) VALUES (%s, %s, %s);", (next_id_article, titre, resume))
                

                print("Id du nouvel article:", next_id_article)

       
                cursor.execute("INSERT INTO contenu_article (idArticle, nomRevue) VALUES (%s, %s)", (next_id_article, nomRevue))
                

                for id_vip in selected_vips:
                    cursor.execute("""
                    INSERT INTO apparait_article (idVip, idArticle) 
                    VALUES (%s, %s)
                    """, (id_vip, next_id_article))

            
                conn.commit()

                return redirect(url_for('render_revue'))
            except Exception as e:
               
                conn.rollback()
                print(f"Error: {e}")
                return f"An error occurred: {e}", 500
            finally:
                cursor.close()
    
  
    return render_template('ajouter_article.html', lst_revues=lst_revues, vips=vips, is_connected=session.get('is_connected', False))


@app.route('/ajouter_defile', methods=["GET", "POST"])
def ajouter_defile():
    if request.method == "POST":
  
        nom_defile = request.form['nom_defile']
        date_defile = request.form['date_defile']
        lieu = request.form['lieu']
        id_realisateur = request.form['id_realisateur']
        id_mannequins = request.form.getlist('id_mannequins')

        try:
            with connect() as conn:
                cursor = conn.cursor()

            
                cursor.execute(
                    "INSERT INTO defile (nomDefile, dateDefile, lieu) VALUES (%s, %s, %s)",
                    (nom_defile, date_defile, lieu)
                )

                cursor.execute("SELECT MAX(idDefile) FROM defile")
                max_id_defile = cursor.fetchone()[0] 

               
                if max_id_defile is None:
                    next_id_defile = 1
                else:
                    next_id_defile = max_id_defile
                print(f"idDefile : {next_id_defile}")

          
                cursor.execute(
                    "INSERT INTO arealise (idDefile, idVip) VALUES (%s, %s)",
                    (next_id_defile, id_realisateur)
                )

             
                for id_mannequin in id_mannequins:
                    cursor.execute(
                        "INSERT INTO adefile (idManequin, idDefile) VALUES (%s, %s)",
                        (id_mannequin, next_id_defile)
                    )

                conn.commit() 

            return redirect(url_for('render_defile'))

        except Exception as e:
            print(f"Erreur lors de l'ajout du défilé : {e}")
            return "Une erreur est survenue."

 
    with connect() as conn:
        cursor = conn.cursor()
      
        cursor.execute("SELECT idVip, nom, prenom FROM vip;")
        vips = cursor.fetchall()

        
        cursor.execute("SELECT * from manequin JOIN vip ON manequin.idmanequin = vip.idvip;")
        mannequins = cursor.fetchall()

    return render_template('ajouter_defile.html', vips=vips, mannequins=mannequins, is_connected=session.get('is_connected', False))

@app.route('/choisir_defile', methods=["GET", "POST"])
def choisir_defile_a_modifier():
    try:
        with connect() as conn:
            cursor = conn.cursor()

            # Récupérer la liste des défilés
            cursor.execute("SELECT idDefile, nomDefile, dateDefile, lieu FROM defile")
            defiles = cursor.fetchall()

        return render_template('choisir_defile.html', defiles=defiles, is_connected=session.get('is_connected', False))

    except Exception as e:
        return f"Une erreur est survenue : {e}"


@app.route('/modifier_defile/<int:id_defile>', methods=["GET", "POST"])
def modifier_defile(id_defile):
    if request.method == "POST":
        
        pass
    else:
        try:
            with connect() as conn:
                cursor = conn.cursor()

               
                cursor.execute("SELECT * FROM defile WHERE idDefile = %s", (id_defile,))
                defile = cursor.fetchone()
                if defile is None:
                    return f"Aucun défilé trouvé avec l'ID {id_defile}"

              
                cursor.execute("SELECT idVip FROM arealise WHERE idDefile = %s", (id_defile,))
                result = cursor.fetchone()
                id_realisateur = result[0] if result else None

               
                cursor.execute("SELECT idManequin FROM adefile WHERE idDefile = %s", (id_defile,))
                mannequins_actuels = [row[0] for row in cursor.fetchall()] if cursor.rowcount > 0 else []

               
                cursor.execute("SELECT idVip, nom, prenom FROM vip")
                vips = cursor.fetchall()

               
                cursor.execute("SELECT * from manequin;")
                mannequins = cursor.fetchall()

            return render_template(
                'modifier_defile.html',
                defile=defile,
                id_realisateur=id_realisateur,
                mannequins_actuels=mannequins_actuels,
                vips=vips,
                mannequins=mannequins,is_connected=session.get('is_connected', False)
            )

        except Exception as e:
            return f"Une erreur est survenue : {e}"
    return redirect(url_for('render_defile'))


@app.route('/supprimer_defile/<int:id_defile>', methods=['POST'])
def supprimer_defile(id_defile):
    try:
        with connect() as conn:
            cursor = conn.cursor()

            
            cursor.execute("DELETE FROM adefile WHERE idDefile = %s", (id_defile,))
            cursor.execute("DELETE FROM arealise WHERE idDefile = %s", (id_defile,))

         
            cursor.execute("DELETE FROM defile WHERE idDefile = %s", (id_defile,))
            conn.commit()

        return redirect(url_for('choisir_defile_a_modifier'))
    except Exception as e:
        print(f"Erreur lors de la suppression : {e}")
        return f"Erreur : {e}", 500





@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    account = {'Admin': 'ADMIN1234', 'LE LOUCH': 'BRITANIA'}

    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']

        if user_id in account and account[user_id] == password:
            session['is_connected'] = True  
            return redirect(url_for('home'))  

      
        session['is_connected'] = False

        print(session.get('is_connected', False))

        return render_template('connexion.html', error="Invalid credentials")

    return render_template('connexion.html')

@app.route('/deconnexion')
def deconnexion():
    session['is_connected'] = False
    return redirect(url_for('home'))


@app.route('/liaison', methods=['GET', 'POST'])
def gerer_liaisons():
    with connect() as conn:
        cursor = conn.cursor()

      
        cursor.execute("SELECT idVip, nom, prenom FROM VIP")
        vips = cursor.fetchall()

        if request.method == 'POST':
            idVip1 = request.form['idVip1']
            idVip2 = request.form['idVip2']
            dateLiaison = request.form['dateLiaison']
            dateSeparation = request.form.get('dateSeparation') or None
            motifSeparation = request.form.get('motifSeparation') or None

            cursor.execute("""
                INSERT INTO liaison (idVip1, idVip2, dateLiaison, dateSeparation, motifSeparation)
                VALUES (%s, %s, %s, %s, %s)
            """, (idVip1, idVip2, dateLiaison, dateSeparation, motifSeparation))
            conn.commit()
            return redirect(url_for('afficher_relations'))

        cursor.execute("SELECT * FROM liaison")
        liaisons = cursor.fetchall()
        

    return render_template('liaison.html', liaisons=liaisons, vips=vips, is_connected=session.get('is_connected', False))



@app.route('/mariage', methods=['GET', 'POST'])
def gerer_mariages():
    with connect() as conn:
        cursor = conn.cursor()

       
        cursor.execute("SELECT idVip, nom, prenom FROM VIP")
        vips = cursor.fetchall()

        if request.method == 'POST':
            idVip1 = request.form['idVip1']
            idVip2 = request.form['idVip2']
            dateMariage = request.form['dateMariage']
            lieu = request.form['lieu']
            dateSeparation = request.form.get('dateSeparation') or None

            cursor.execute("""
                INSERT INTO mariage (idVip1, idVip2, dateMariage, lieu, dateSeparation)
                VALUES (%s, %s, %s, %s, %s)
            """, (idVip1, idVip2, dateMariage, lieu, dateSeparation))
            conn.commit()
            return redirect(url_for('afficher_relations'))

        cursor.execute("SELECT * FROM mariage")
        mariages = cursor.fetchall()

    return render_template('mariage.html', mariages=mariages, vips=vips, is_connected=session.get('is_connected', False))


@app.route('/relations', methods=['GET'])
def afficher_relations():
    with connect() as conn:
        cursor = conn.cursor()

       
        cursor.execute("SELECT idVip, nom, prenom FROM VIP")
        vips = cursor.fetchall()

       
        relations = []

        for vip in vips:
            idVip = vip[0]
            nom = vip[1]
            prenom = vip[2]

            
            cursor.execute("""
                SELECT v2.nom, v2.prenom, liaison.dateLiaison, liaison.dateSeparation, liaison.motifSeparation, v2.idVip
                FROM liaison
                JOIN vip v2 ON (liaison.idVip2 = v2.idVip OR liaison.idVip1 = v2.idVip) AND v2.idVip != %s
                WHERE (liaison.idVip1 = %s OR liaison.idVip2 = %s)
            """, (idVip, idVip, idVip))
            liaisons = cursor.fetchall()

           
            cursor.execute("""
                SELECT v2.nom, v2.prenom, mariage.dateMariage, mariage.lieu, mariage.dateSeparation, v2.idVip
                FROM mariage
                JOIN vip v2 ON (mariage.idVip2 = v2.idVip OR mariage.idVip1 = v2.idVip) AND v2.idVip != %s
                WHERE (mariage.idVip1 = %s OR mariage.idVip2 = %s)
            """, (idVip, idVip, idVip))
            mariages = cursor.fetchall()

         
            relations.append({
                'vip_id': idVip,
                'vip': f"{nom} {prenom}",
                'liaisons': liaisons,
                'mariages': mariages
            })

    return render_template('relations.html', relations=relations, is_connected=session.get('is_connected', False))



@app.route('/modifier_liaison/<int:idVip1>/<int:idVip2>/<date>', methods=['GET', 'POST'])
def modifier_liaison(idVip1, idVip2, date):
    with connect() as conn:
        cursor = conn.cursor()

        
        cursor.execute("""
            SELECT idVip1, idVip2, dateLiaison, dateSeparation, motifSeparation 
            FROM liaison 
            WHERE idVip1 = %s AND idVip2 = %s AND dateLiaison = %s
        """, (idVip1, idVip2, date))
        liaison = cursor.fetchone()

        if request.method == 'POST':
           
            dateSeparation = request.form.get('dateSeparation') or None
            motifSeparation = request.form.get('motifSeparation') or None

            cursor.execute("""
                UPDATE liaison 
                SET dateSeparation = %s, motifSeparation = %s 
                WHERE idVip1 = %s AND idVip2 = %s AND dateLiaison = %s
            """, (dateSeparation, motifSeparation, idVip1, idVip2, date))
            conn.commit()
            return redirect(url_for('afficher_relations'))

    return render_template('modifier_liaison.html', liaison=liaison, is_connected=session.get('is_connected', False))


@app.route('/supprimer_liaison/<int:idVip1>/<int:idVip2>/<date>', methods=['POST'])
def supprimer_liaison(idVip1, idVip2, date):
    with connect() as conn:
        cursor = conn.cursor()

      
        cursor.execute("""
            DELETE FROM liaison 
            WHERE (idVip1 = %s AND idVip2 = %s AND dateLiaison = %s)
               OR (idVip1 = %s AND idVip2 = %s AND dateLiaison = %s)
        """, (idVip1, idVip2, date, idVip2, idVip1, date))
        conn.commit()
    
    return redirect(url_for('afficher_relations'))




@app.route('/modifier_mariage/<int:idVip1>/<int:idVip2>/<date>', methods=['GET', 'POST'])
def modifier_mariage(idVip1, idVip2, date):
    with connect() as conn:
        cursor = conn.cursor()

        
        cursor.execute("""
            SELECT idVip1, idVip2, dateMariage, lieu, dateSeparation 
            FROM mariage 
            WHERE idVip1 = %s AND idVip2 = %s AND dateMariage = %s
        """, (idVip1, idVip2, date))
        mariage = cursor.fetchone()

        if request.method == 'POST':
            
            lieu = request.form['lieu']
            dateSeparation = request.form.get('dateSeparation') or None

            cursor.execute("""
                UPDATE mariage 
                SET lieu = %s, dateSeparation = %s 
                WHERE idVip1 = %s AND idVip2 = %s AND dateMariage = %s
            """, (lieu, dateSeparation, idVip1, idVip2, date))
            conn.commit()
            return redirect(url_for('afficher_relations'))

    return render_template('modifier_mariage.html', mariage=mariage, is_connected=session.get('is_connected', False))



@app.route('/supprimer_mariage/<int:idVip1>/<int:idVip2>/<date>', methods=['POST'])
def supprimer_mariage(idVip1, idVip2, date):
    with connect() as conn:
        cursor = conn.cursor()

     
        cursor.execute("""
            DELETE FROM mariage 
            WHERE (idVip1 = %s AND idVip2 = %s AND dateMariage = %s)
               OR (idVip1 = %s AND idVip2 = %s AND dateMariage = %s)
        """, (idVip1, idVip2, date, idVip2, idVip1, date))
        conn.commit()
    
    return redirect(url_for('afficher_relations'))


@app.route("/gerer_revues", methods=["GET", "POST"])
def gerer_revues():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nomRevue FROM revue")
        revues = cursor.fetchall()

    if request.method == "POST":
        action = request.form.get("action")
        nom_revue = request.form.get("nomRevue")

        if action == "modifier":
            return redirect(url_for("modifier_revue", nom_revue=nom_revue))
        elif action == "supprimer":
            return redirect(url_for("supprimer_revue", nom_revue=nom_revue))

    return render_template("gerer_revues.html", revues=revues, is_connected=session.get("is_connected", False))



@app.route("/modifier_revue/<string:nom_revue>", methods=["GET", "POST"])
def modifier_revue(nom_revue):
    with connect() as conn:
        cursor = conn.cursor()

       
        cursor.execute("SELECT nomRevue, dateParution FROM revue WHERE nomRevue = %s", (nom_revue,))
        revue = cursor.fetchone()

    if request.method == "POST":
        nouveau_nom = request.form["nom_revue"]
        nouvelle_date = request.form["dateParution"]

        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE revue 
                SET nomRevue = %s, dateParution = %s 
                WHERE nomRevue = %s
            """, (nouveau_nom, nouvelle_date, nom_revue))
            conn.commit()

        return redirect(url_for("render_revue"))

    return render_template("modifier_revue.html", revue=revue, is_connected=session.get("is_connected", False))

@app.route("/gerer_articles", methods=["GET", "POST"])
def gerer_articles():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idArticle, titre 
            FROM article
        """)
        articles = cursor.fetchall()

    if request.method == "POST":
        action = request.form.get("action")
        id_article = request.form.get("idArticle")

        if action == "modifier":
            return redirect(url_for("modifier_article", id_article=id_article))
        elif action == "supprimer":
            return redirect(url_for("supprimer_article", id_article=id_article))

    return render_template("gerer_articles.html", articles=articles, is_connected=session.get("is_connected", False))



@app.route("/supprimer_revue/<string:nom_revue>", methods=["POST"])
def supprimer_revue(nom_revue):
    try:
        with connect() as conn:
            cursor = conn.cursor()

          
            cursor.execute("DELETE FROM contenu_article WHERE nomRevue = %s", (nom_revue,))
            cursor.execute("DELETE FROM revue WHERE nomRevue = %s", (nom_revue,))
            conn.commit()

        print(f"La revue '{nom_revue}' a été supprimée avec succès.", "success")
    except Exception as e:
        print(f"Erreur lors de la suppression de la revue : {e}", "danger")

    return redirect(url_for("render_revue"))





@app.route("/modifier_article/<int:id_article>", methods=["GET", "POST"])
def modifier_article(id_article):
    with connect() as conn:
        cursor = conn.cursor()

       
        cursor.execute("""
            SELECT article.idArticle, titre, resume, nomRevue 
            FROM article
            NATURAL JOIN contenu_article
            WHERE idArticle = %s
        """, (id_article,))
        article = cursor.fetchone()

    if request.method == "POST":
        nouveau_titre = request.form["titre"]
        nouveau_resume = request.form["resume"]
        nouvelle_revue = request.form["nomRevue"]

        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE article 
                SET titre = %s, resume = %s 
                WHERE idArticle = %s
            """, (nouveau_titre, nouveau_resume, id_article))
            cursor.execute("""
                UPDATE contenu_article 
                SET nomRevue = %s 
                WHERE idArticle = %s
            """, (nouvelle_revue, id_article))
            conn.commit()

        return redirect(url_for("render_article", id_revue=nouvelle_revue))

    return render_template("modifier_article.html", article=article, is_connected=session.get("is_connected", False))


@app.route("/supprimer_article/<int:id_article>", methods=["POST"])
def supprimer_article(id_article):
    try:
        with connect() as conn:
            cursor = conn.cursor()

           
            cursor.execute("DELETE FROM apparait_article WHERE idArticle = %s", (id_article,))
            cursor.execute("DELETE FROM contenu_article WHERE idArticle = %s", (id_article,))
            cursor.execute("DELETE FROM article WHERE idArticle = %s", (id_article,))
            conn.commit()

        print(f"L'article avec l'ID {id_article} a été supprimé avec succès.", "success")
    except Exception as e:
        print(f"Erreur lors de la suppression de l'article : {e}", "danger")

    return redirect(url_for("gerer_articles"))




@app.route('/photos')
def render_photos():
  
    
    with connect() as conn:
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM photo;")
        photos=cursor.fetchall()
    return render_template('photos.html', photos=photos, is_connected=session.get('is_connected', False))

if __name__ == '__main__':
    print("compilation main ok\n")
    app.run() 
