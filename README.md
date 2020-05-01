Ymael est un logiciel de surveillance et d'export de posts de forums de
Role-Play. Il a été développé pour compenser l'absence de notification de
nouveaux posts du site de *PBF* `Edenya.net`, ainsi que pour sauvegarder les
posts que le site supprimait après un certain temps.

## Installation

Pour le moment, seuls les OS type linux sont supportés.

### Prérequis

Quelques packages sont requis pour faire fonctionner correctement le logiciel
dans tous les cas. Il vous faudra les logiciels `pandoc` et le support de LaTeX
et XeLaTex, typiquement *via* `texlive` pour les distributions linux et MikTex
pour Windows.

Pour les distributions linux, une installation via les dépôts est recommandée.
Par exemple, pour un système type Debian:

```sh
sudo apt install -y pandoc texlive texlive-latex-base texlive-latex-recommended texlive-xetex
```

### Installation des sources *via* le dépôt git

D'autres prérequis sont nécessaires. Vous aurez besoin d'une installation
python > 3 (normalement déjà présente dans la majorité des systèmes), ainsi que
du logiciel pip. Les librairies python requises sont toutes listées dans le
fichier `requirements.txt` et peuvent donc être installées à l'aide de pip.

Divers packages sont nécessaires pour la libraire pygobject, et sont listés
dans les commandes ci-dessous (les noms correspondent à un système debian,
n'oubliez pas d'adapter la commande à votre distribution).

#### Méthode rapide

Le fichier Makefile est paramétré pour installer les prérequis, compiler le
programme en un exécutable et l'installer dans le dossier `/opt`.  Attention, les
installations des prérequis sont basés sur un OS type debian (via apt).

Utilisez simplement:

```sh
make install
```

Le prgramme sera disponible dans le dossier `/opt`:

```sh
/opt/ymael/ymael --help
```

#### Détaillée

Installez les prérequis:

```sh
# toute cette suite de commande est incluse dans le Makefile
# make requirements

# prérequis pour PyGObject
sudo apt install -y python3-gi libcairo2-dev libgirepository1.0-dev gir1.2-gtk-3.0
# prérequis pour l'installation des librairies avec requirements.txt
sudo apt install -y python3-pip
# installation du logiciel
git clone https://gitea.com/amartos/ymael
cd ymael
pip3 install --exists-action i --user -r requirements.txt
```

Vous pouvez maintenant utiliser le programme via le fichier `main.py`. Lancez
cette commande pour afficher les options disponibles:

```sh
python3 main.py --help
```

Vous pouvez aussi compiler le programme en un exécutable via cette suite de
commandes:

```sh
# le Makefile résume ces commandes en une:
# make compile

# installation prérequise de pyinstaller
pip3 install --exists-action i --user pyinstaller
# compilation
pyinstaller --clean -y --onedir main.spec
# installation des icones
cp assets/icons/ymael.png dist/ymael/share/
ln -s /usr/share/icons dist/ymael/share/
```

Le dossier `./dist/ymael` contiendra alors tout le programme, et l'exécutable
est le fichier `./dist/ymael/ymael`

### Installation *via* l'archive tarball

Téléchargez la dernière version du logiciel compilé à l'adresse
`https://gitea.com/amartos/ymael/releases`, décompressez le, et lancez le script
`install.py`. Des droits sudo seront demandés lors de l'installation pour
pouvoir créer le dossier racine dans `/opt`.

```sh
tar -xzvf ymael.version.tar.gz
python3 ymael_version/install.py
```

Vous pouvez ensuite lancer l'interface graphique à partir du menu du système à
l'aide du fichier `.desktop` maintenant présent dans le dossier
`~/.local/share/applications`. Il vous est toujours possible d'utiliser la ligne
de commande:

```sh
/opt/ymael/ymael --help
```

## Utilisation

Pour une utilisation en ligne de commande, voir l'aide en lançant:

```sh
/opt/ymael/ymael --help
```

## À faire

  - [] adapter le logiciel aux OS type Windows
  - [] améliorer l'interface graphique
  - [] ajouter des options de configuration de l'interface graphique
  - [] ajouter un manuel d'utilisation de l'interface graphique
  - [] intégrer un éditeur de RP avec balises et mise en forme
