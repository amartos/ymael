NAME=ymael

all: compile

install: requirements compile
	@sudo mv dist/$(NAME) /opt/
	@cp assets/ymael.desktop ~/.local/share/applications/

compile:
	@pip3 install -q --exists-action i --user pyinstaller
	@pyinstaller --clean -y --onedir main.spec
	@cp assets/icons/ymael.png dist/$(NAME)/share/
	@ln -s /usr/share/icons dist/$(NAME)/share/

requirements:
	@sudo apt install -y python3-pip pandoc texlive texlive-latex-base texlive-latex-recommended texlive-xetex
	@sudo apt install -y python3-gi libcairo2-dev libgirepository1.0-dev gir1.2-gtk-3.0
	@sudo apt install -y python3-pip
	@pip3 install -q --exists-action i --user -r requirements.txt

clean:
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -rf build dist

.PHONY: compile requirements clean
