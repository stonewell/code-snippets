.PHONY: prog all clean

all: prog

prog: main.cpp ../shared/foo.h
	$(CXX) -o prog -g -O0 -I../shared main.cpp -ldl -Wl,--version-script=./prog.exp

clean:
	$(RM) prog
