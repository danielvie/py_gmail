all: r
# all: e
# all: play

play:
	python play.py

r:
	. .venv/bin/activate && python main.py
	
t:
	. .venv/bin/activate && python main.py --test
	
res: clean

c: clean

clear: clean

clean:
	rm token.pickle
	
b: 
	pyinstaller --onefile main.py

e:
	./dist/main

