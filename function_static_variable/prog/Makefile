.PHONY: prog

all: prog

prog: main.cpp ../shared/foo.h
	g++ -o prog -g -O0 -I../shared main.cpp -ldl -Wl,--version-script=./prog.exp
