all: install

install: change-login change-character apt-requirements py-requirements cron icon
	@ln -s ~/.local/opt/ymael/assets/linux/ymael.desktop ~/Bureau
	@ln -s ~/.local/opt/ymael/assets/linux/ymael-check ~/.config/cron/cron.hourly/

update: git py-requirements

git:
	@git pull

icon:
	@mkdir -p ~/.local/share/icons/
	@ln -s `pwd`/icons/ymael.png ~/.local/share/icons/

apt-requirements:
	@sudo apt install python3-pip pandoc texlive texlive-base texlive-xetex

py-requirements:
	@pip3 install --user -r requirements.txt

change-login:
	@mkdir -p ~/.local/share/ymael
	@echo "Login ?" && read LOGIN && echo \\$LOGIN > ~/.local/share/ymael/login

change-character:
	@mkdir -p ~/.local/share/ymael
	@echo "Nom du personnage ?" && read CHARNAME && echo \\$CHARNAME > ~/.local/share/ymael/character

cron:
	@mkdir -p ~/.config/cron/etc
	@mkdir -p ~/.config/cron/spool
	@mkdir -p ~/.config/cron/cron.hourly
	@crontab ~/.local/opt/ymael/assets/linux/my-crontab

clean:
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete

.PHONY: install update clean
