-- Suppression des tables existantes
DROP TABLE IF EXISTS VIP CASCADE;
DROP TABLE IF EXISTS film CASCADE;
DROP TABLE IF EXISTS acteur CASCADE;
DROP TABLE IF EXISTS manequin CASCADE;
DROP TABLE IF EXISTS defile CASCADE;
DROP TABLE IF EXISTS musicien CASCADE;
DROP TABLE IF EXISTS album CASCADE;
DROP TABLE IF EXISTS article CASCADE;
DROP TABLE IF EXISTS revue CASCADE;
DROP TABLE IF EXISTS photo CASCADE;
DROP TABLE IF EXISTS liaison CASCADE;
DROP TABLE IF EXISTS mariage CASCADE;
DROP TABLE IF EXISTS aRealise CASCADE;
DROP TABLE IF EXISTS a_composer CASCADE;
DROP TABLE IF EXISTS apparait_photo CASCADE;
DROP TABLE IF EXISTS apparait_dans_revue CASCADE;
DROP TABLE IF EXISTS contenu_article CASCADE;
DROP TABLE IF EXISTS joue CASCADE;
DROP TABLE IF EXISTS adefile CASCADE;
DROP TABLE IF EXISTS apparait_article;

CREATE TABLE VIP (
    idVip SERIAL PRIMARY KEY,
    nom VARCHAR(25) NOT NULL,
    prenom VARCHAR(25) NOT NULL,
    sexe CHAR(1) NOT NULL check(sexe IN ('M', 'F')),
    nationalite VARCHAR(25),
    dateNais DATE,
    dateDeces DATE,
    CHECK(dateDeces IS NULL OR dateDeces > dateNais)
);

CREATE TABLE film (
    numeroVisa INT PRIMARY KEY, 
    idRealisateur INT REFERENCES VIP(idVip),
    titre VARCHAR(50) NOT NULL,
    dateRealisation DATE NOT NULL,
    descriptif TEXT,
    CHECK (dateRealisation >= (SELECT dateNais 
                               FROM VIP 
                               WHERE VIP.idVip = idRealisateur))

    
);

CREATE TABLE acteur (
    idActeur INT PRIMARY KEY,
    datePremierTournage DATE NOT NULL, 
    filmDejaRealise CHAR(2),
    CONSTRAINT fk_acteur_id FOREIGN KEY (idActeur) REFERENCES VIP(idVip)
    CHECK (datePremierTournage >= (SELECT dateNais 
                               FROM VIP 
                               WHERE VIP.idVip = idRealisateur))
);

CREATE TABLE manequin (
    idManequin INT PRIMARY KEY,
    taille INT CHECK (taille BETWEEN 50 AND 250), 
    nomAgence VARCHAR(50),
    CONSTRAINT fk_manequin_id FOREIGN KEY (idManequin) REFERENCES VIP(idVip)
);

CREATE TABLE defile (
    idDefile serial PRIMARY KEY,
    nomDefile varchar(50) NOT NULL,
    dateDefile DATE NOT NULL, 
    lieu VARCHAR(50) NOT NULL
);

CREATE TABLE musicien (
    idArtiste INT PRIMARY KEY ,
    specialite VARCHAR(50),
    nomMaisonDisque VARCHAR(50),
    CONSTRAINT fk_musicien_id FOREIGN KEY (idArtiste) REFERENCES VIP(idVip)
);

CREATE TABLE album (
    idAlbum serial PRIMARY KEY, 
    nom_album VARCHAR(50) NOT NULL, 
    dateRealisation DATE
);

CREATE TABLE article (
    idArticle serial PRIMARY KEY, 
    titre VARCHAR(100),
    numPageDebut INT,
    resume TEXT
);

CREATE TABLE revue (
    nomRevue VARCHAR(100) PRIMARY KEY,
    dateParution DATE
);

CREATE TABLE photo (
    numPhoto serial PRIMARY KEY,
    imageNumerise VARCHAR(50),
    photographe VARCHAR(50),
    lieu VARCHAR(50), 
    circonstance TEXT
);

CREATE TABLE liaison (
    idVip1 INT REFERENCES VIP(idVip),
    idVip2 INT REFERENCES VIP(idVip),
    dateLiaison DATE, 
    dateSeparation DATE, 
    motifSeparation TEXT,
    PRIMARY KEY (idVip1, idVip2, dateLiaison)
);

CREATE TABLE mariage (
    idVip1 INT REFERENCES VIP(idVip),
    idVip2 INT REFERENCES VIP(idVip),
    dateMariage DATE, 
    lieu VARCHAR(50), 
    dateSeparation DATE,
    PRIMARY KEY (idVip1, idVip2, dateMariage)
);

CREATE TABLE aRealise (
    idDefile INT REFERENCES defile(idDefile),
    idVip INT REFERENCES VIP(idVip),
    PRIMARY KEY (idDefile, idVip)
);

CREATE TABLE a_composer (
    idAlbum INT REFERENCES album(idAlbum) ON DELETE CASCADE,
    idArtiste INT REFERENCES musicien(idArtiste) ON DELETE CASCADE,
    PRIMARY KEY (idAlbum, idArtiste)
);


CREATE TABLE apparait_photo (
    idVip INT REFERENCES VIP(idVip) ON DELETE CASCADE,
    numPhoto INT REFERENCES photo(numPhoto) ON DELETE CASCADE,
    PRIMARY KEY (idVip, numPhoto)
);


CREATE TABLE apparait_dans_revue (
    numPhoto INT REFERENCES photo(numPhoto) ON DELETE CASCADE,
    nomRevue VARCHAR(100) REFERENCES revue(nomRevue) ON DELETE CASCADE,
    PRIMARY KEY (numPhoto, nomRevue)
);


CREATE TABLE contenu_article (
    idArticle INT REFERENCES article(idArticle) ON DELETE CASCADE,
    nomRevue VARCHAR(100) REFERENCES revue(nomRevue) ON DELETE CASCADE,
    PRIMARY KEY (idArticle, nomRevue)
);

CREATE TABLE apparait_article (
    idVip INT REFERENCES VIP(idVip) ON DELETE CASCADE,
    idArticle INT REFERENCES article(idArticle) ON DELETE CASCADE,
    PRIMARY KEY (idVip, idArticle)
);


CREATE TABLE joue (
    idActeur INT REFERENCES acteur(idActeur) ON DELETE CASCADE,
    idFilm INT REFERENCES film(numeroVisa) ON DELETE CASCADE,
    role VARCHAR(100),  
    PRIMARY KEY (idActeur, idFilm)
);

CREATE TABLE aDefile (
    idManequin INT REFERENCES manequin(idManequin),
    idDefile INT REFERENCES defile(idDefile),
    PRIMARY KEY (idManequin, idDefile)
);


CREATE OR REPLACE VIEW top_5_femmes_divorces AS
WITH divorce_count_f AS (
    SELECT
        vip.idVip,
        vip.nom,
        vip.prenom,
        vip.sexe,
        COUNT(*) AS nb_divorces
    FROM VIP
    JOIN mariage ON (vip.idVip = mariage.idVip1 OR vip.idVip = mariage.idVip2)
    WHERE mariage.dateSeparation IS NOT NULL
    GROUP BY vip.idVip, vip.nom, vip.prenom, vip.sexe
)
SELECT idVip, nom, prenom, nb_divorces
FROM divorce_count_f
WHERE sexe = 'F'
ORDER BY nb_divorces DESC
LIMIT 5;




CREATE OR REPLACE VIEW top_5_hommes_divorces AS
WITH divorce_count_m AS (
    SELECT
        vip.idVip,
        vip.nom,
        vip.prenom,
        vip.sexe,
        COUNT(*) AS nb_divorces
    FROM VIP
    JOIN mariage ON (vip.idVip = mariage.idVip1 OR vip.idVip = mariage.idVip2)
    WHERE mariage.dateSeparation IS NOT NULL
    GROUP BY vip.idVip, vip.nom, vip.prenom, vip.sexe
)
SELECT idVip, nom, prenom, nb_divorces
FROM divorce_count_m
WHERE sexe = 'M'
ORDER BY nb_divorces DESC
LIMIT 5;



CREATE OR REPLACE VIEW vip_non_apparus_article AS
SELECT idVip, nom, prenom
FROM VIP
WHERE idVip NOT IN (
    SELECT DISTINCT idVip
    FROM apparait_article
    NATURAL JOIN article
    NATURAL JOIN revue
    WHERE dateParution >= (CURRENT_DATE - INTERVAL '1 year'));



--VALEUR POUR TESTER LA DB

-- Insérer des données dans la table VIP
INSERT INTO VIP (nom, prenom, sexe, nationalite, dateNais, dateDeces) VALUES
('Dupont', 'Marie', 'F', 'Française', '1985-06-15', NULL),
('Martin', 'Jean', 'M', 'Français', '1978-11-20', '2023-04-12'),
('Lemoine', 'Claire', 'F', 'Belge', '1990-02-22', NULL),
('Durand', 'Louis', 'M', 'Français', '1965-03-30', '2020-01-10');

-- Insérer des données dans la table film
INSERT INTO film (numeroVisa, idRealisateur, titre, dateRealisation) VALUES
(1234, 1, 'Le Voyage', '2020-07-15'),
(5678, 2, 'Sous la pluie', '2022-10-03'),
(9101, 3, 'L’ombre de la nuit', '2019-11-09');

-- Insérer des données dans la table acteur
INSERT INTO acteur (idActeur, datePremierTournage, filmDejaRealise) VALUES
(1, '2005-05-10', 'Y'),
(2, '2010-09-15', 'N'),
(3, '2015-03-25', 'Y');

-- Insérer des données dans la table manequin
INSERT INTO manequin (idManequin, taille, nomAgence) VALUES
(1, 180, 'Elite Paris'),
(2, 175, 'Next Models');

-- Insérer des données dans la table defile
INSERT INTO defile (idDefile, dateDefile, lieu) VALUES
(1, defile_1, '2023-06-20', 'Paris'),
(2, defile_2, '2024-05-15', 'New York');

-- Insérer des données dans la table musicien
INSERT INTO musicien (idArtiste, specialite, nomMaisonDisque) VALUES
(1, 'Rock', 'Universal'),
(2, 'Jazz', 'Sony Music');

-- Insérer des données dans la table album
INSERT INTO album (idAlbum, nom_album, dateRealisation) VALUES
(1, 'Rock n Roll', '2023-04-12'),
(2, 'Smooth Jazz', '2024-01-01');

-- Insérer des données dans la table article
INSERT INTO article (idArticle, titre, numPageDebut, resume) VALUES
(1, 'Les nouvelles tendances du cinéma', 1, 'Un article sur les tendances actuelles du cinéma.'),
(2, 'Musique et société', 25, 'Un article analysant l’impact de la musique sur la société.');

-- Insérer des données dans la table revue
INSERT INTO revue (nomRevue, dateParution) VALUES
('Le Cinéma Moderne', '2023-11-01'),
('Jazz Magazine', '2024-01-01');

-- Insérer des données dans la table photo
INSERT INTO photo (numPhoto, imageNumerise, photographe, lieu, circonstance) VALUES
(1, 'Gru.jpg', 'Jean-Luc', 'Paris', 'Photo prise lors du festival de mode'),
(2, 'Margo.jpg', 'Marie-Claude', 'New York', 'Photo pour une couverture de revue');

-- Insérer des données dans la table liaison
INSERT INTO liaison (idVip1, idVip2, dateLiaison, dateSeparation, motifSeparation) VALUES
(1, 2, '2010-05-05', '2012-03-15', 'Rupture amicale'),
(3, 4, '2018-07-20', '2020-06-15', 'Incompatibilité de caractère');

-- Insérer des données dans la table mariage
INSERT INTO mariage (idVip1, idVip2, dateMariage, lieu, dateSeparation) VALUES
(1, 3, '2015-06-10', 'Paris', '2018-06-01'),
(2, 4, '2011-09-25', 'Lyon', NULL);

-- Insérer des données dans la table aRealise
INSERT INTO aRealise (idDefile, idVip) VALUES
(1, 1),
(2, 2);

-- Insérer des données dans la table a_composer
INSERT INTO a_composer (idAlbum, idArtiste) VALUES
(1, 1),
(2, 2);

-- Insérer des données dans la table apparait_photo
INSERT INTO apparait_photo (idVip, numPhoto) VALUES
(1, 1),
(2, 2);

-- Insérer des données dans la table apparait_dans_revue
INSERT INTO apparait_dans_revue (numPhoto, nomRevue) VALUES
(1, 'Le Cinéma Moderne'),
(2, 'Jazz Magazine');

-- Insérer des données dans la table contenu_article
INSERT INTO contenu_article (idArticle, nomRevue) VALUES
(1, 'Le Cinéma Moderne'),
(2, 'Jazz Magazine');

-- Insérer des données dans la table apparait_article
INSERT INTO apparait_article (idVip, idArticle) VALUES
(1, 1),
(2, 2);

-- Insérer des données dans la table joue
INSERT INTO joue (idActeur, idFilm, role) VALUES
(1, 1234, 'Héroïne'),
(2, 5678, 'Antagoniste');

-- Insérer des données dans la table aDefile
INSERT INTO aDefile (idManequin, idDefile) VALUES
(1, 1),
(2, 2);


