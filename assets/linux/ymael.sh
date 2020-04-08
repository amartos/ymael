#!/usr/bin/env bash

DIR=$HOME/.local/opt/ymael
LINK=$(zenity --entry --title "Lien ?" --text "Lien du site :")
LOGIN=$(cat ~/.local/share/ymael/login)

if [ ! -z "$LINK" ]
then
	if zenity --question --title "Action ?" --text "Que voulez-vous faire ?" --ok-label "PDF" --cancel-label "Surveiller"
	then 
		FILE=$(zenity --file-selection --save --title "Nom du fichier" --text "Où souhaitez-vous l'exporter :")
		if [ ! ${FILE: -4} == ".pdf" ]
		then
			FILE=$FILE.pdf
		fi
		python3 $DIR/main.py $LOGIN -f "$FILE" -u "$LINK"
	else 
		python3 $DIR/main.py $LOGIN -u "$LINK"
	fi
	
fi
