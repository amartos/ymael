NAME=ymael

all: requirements compile

compile:
	@pip3 install -q --exists-action i --user pyinstaller
	@pyinstaller --clean -y main.spec

requirements:
	@sudo apt install -y python3-pip pandoc texlive texlive-latex-base texlive-latex-recommended texlive-xetex
	@sudo apt install -y python3-gi libcairo2-dev libgirepository1.0-dev gir1.2-gtk-3.0
	@sudo apt install -y python3-pip
	@pip3 install -q --exists-action i --user -r linux.txt

clean:
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -rf build dist

.PHONY: compile requirements clean
