all: r
# all: e
# all: raii

raii:
	python bla.py

r:
	python main.py
	
t:
	python test.py
	
res: clean

c: clean

clean:
	rm token.pickle
	
b: 
	pyinstaller --onefile main.py

e:
	./dist/main