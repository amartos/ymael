Ymael est un logiciel de surveillance et d'export de posts de forums de
Role-Play. Il a été développé pour compenser l'absence de notification de
nouveaux posts du site de *PBF* `Edenya.net`, ainsi que pour sauvegarder les
posts que le site supprimait après un certain temps.

## Licences

Ymael est sous license GPLv3. L'icône, elle aussi sous license GPLv3, a été
crée par Xen.

## Windows

### Prérequis

Aucun prérequis n'est nécessaire pour la surveillance de nouveaux posts.

Pour exporter les RP en formats PDF, ODT ou DOCX, il vous faudra installer
[Pandoc](https://pandoc.org/installing.html#windows) et [Miktex](https://miktex.org/download).
Les réglages par défaut pour chacun sont suffisants, excepté dans la section
`Paramètres` de Miktex où il faut régler `Installation des paquets à la volée`
sur `Oui`. L'installation de Miktex nécessite quelques réglages
supplémentaires: effectuez la mise à jour des paquets avant toute utilisation.

Une fois ces installations et réglages effectués, redémarrez votre PC.

Le premier export d'un RP sera **très** long (jusqu'à plusieurs minutes), et
**c'est normal**. Miktex installera tout d'abord tous les paquets qui lui sont
nécessaires (et ils sont nombreux).  Les exports suivants seront bien plus
rapides.

### Installation

Téléchargez la dernière version du logiciel à l'adresse
`https://gitea.com/amartos/ymael/releases`, et décompressez-la.

### Utilisation

Double-cliquez sur l'exécutable. C'est aussi simple !

L'interface en ligne de commande n'est pas disponible pour la version
exécutable de windows, seule la version graphique est accessible (les options
`--help`, `--logging-level` et `--minimized` restent disponibles). Il vous est
toujours possible de télécharger les sources, cependant, et d'utiliser le
logiciel complet via cette méthode (cf en-dessous).

### En cas de problèmes

Allez [ici](https://gitea.com/amartos/ymael/issues), cliquez sur `Nouveau ticket`, et suivez le guide.
Notez qu'il vous faudra un compte pour pouvoir remplir un ticket.

## GNU/Linux

### Prérequis

Quelques packages sont requis pour faire fonctionner l'export. Il vous faudra
les logiciels `pandoc` et le support de LaTeX et XeLaTex *via* `texlive`.

Voici la commande pour les OS type Debian:

```sh
sudo apt install -y pandoc texlive texlive-latex-base texlive-latex-recommended texlive-xetex
```

### Installation

Téléchargez la dernière version du logiciel compilé à l'adresse
`https://gitea.com/amartos/ymael/releases`, décompressez le, et lancez le script
`install.py`. Des droits sudo seront demandés lors de l'installation pour
pouvoir créer le dossier racine dans `/opt`.

```sh
tar -xzvf ymael.version.tar.gz
python3 ymael_version/install.py
```
### Utilisation

Vous pouvez maintenant lancer l'interface graphique à partir du menu du système
à l'aide du fichier `.desktop` maintenant présent dans le dossier
`~/.local/share/applications` - et donc dans votre menu, dépendant du bureau
utilisé. Il est aussi possible d'utiliser la ligne de commande:

```sh
/opt/ymael/ymael --help
```

## Installation des sources *via* le dépôt git

Une fois le dépôt git cloné sur votre pc, installez les prérequis comme indiqué
ci-dessous.

### Méthode rapide (Debian et dérivés)

Le fichier Makefile est paramétré pour installer les prérequis et compiler le
programme en un exécutable unique.

**Attention, les installations des prérequis sont basés sur un OS type debian (via apt).**

Utilisez simplement:

```sh
make
# détail:
# make requirements # installer les prérequis seulement
# make compile # créer un exécutable dans le dossier `dist`
```

### Méthode détaillée

#### Prérequis

D'autres prérequis que ceux cités précédemment sont nécessaires.

Outre `git`, vous aurez besoin d'une installation `python` version > 3, ainsi
que de `pip`.  Les librairies python requises sont toutes listées dans le
fichier `linux.txt` ou `windows.txt` et peuvent donc être installées à l'aide
de pip.

Pour Gnu/Linux, divers packages sont également nécessaires pour la libraire
pygobject, et sont listés dans la commandes ci-dessous (les noms correspondent
à un système debian, n'oubliez pas d'adapter la commande à votre distribution).

```sh
sudo apt install -y python3-gi libcairo2-dev libgirepository1.0-dev gir1.2-gtk-3.0
pip3 install --exists-action i --user -r linux.txt
# Pour Windows:
# pip install --exists-action i --user -r windows.txt
```

#### Création de l'exécutable

Pour créer un exécutable via pyinstaller, lancez les commandes ci-dessous:

```sh
pip install --exists-action i --user pyinstaller
pyinstaller --clean -y main.spec
```

L'exécutable sera alors disponible dans le sous-dossier `dist`.

### Utilisation

```sh
# directement depuis les sources
python3 main.py --help
# ou via l'exécutable
# ./dist/ymael --help
```

## À faire

  - [x] adapter le logiciel aux OS type Windows
  - [] améliorer l'interface graphique
  - [] ajouter des options de configuration de l'interface graphique
  - [] ajouter un manuel d'utilisation de l'interface graphique
  - [] intégrer un éditeur de RP avec balises et mise en forme
