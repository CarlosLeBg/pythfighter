@echo off
title Lancement de l'application
color 0B

:: Header esthétique
echo ============================================================
echo                Bienvenue dans l'application NSI
echo          Créée par les développeurs et designers de
echo              Première NSI : un travail d'équipe !
echo ============================================================
echo.

:: Vérification du fichier
if not exist "src\core\main.py" (
    echo [Erreur] Le fichier src\core\main.py est introuvable.
    echo Veuillez vérifier le chemin ou contacter l'équipe NSI.
    pause
    exit /B 1
)

:: Lancement du fichier Python dans la même fenêtre
echo.
echo Lancement de l'application, merci de patienter...
python src\core\main.py

:: Footer et crédits
echo.
echo ============================================================
echo        Merci d'utiliser notre application développée par :
echo        • Carl-Albert LIEVAL (Développeur)
echo        • Timothé PICHOT (Développeur et reviewer)
echo        • Moinécha SCHULTZE (Designer)
echo        • Benjamin COURAM (Designer)
echo        • Rémi POLVERINI (Développeur et coordinateur)
echo ============================================================
pause
exit
