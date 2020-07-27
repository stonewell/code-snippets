.PHONY:all clean foo

SRC_DIR = ../shared
all: clean foo

foo: $(SRC_DIR)/foo.cpp $(SRC_DIR)/foo.h
	g++ -fvisibility-inlines-hidden -Wl,--build-id -Wl,--gc-sections -std=c++11 -shared -g -O0 -fPIC $(SRC_DIR)/foo.cpp -o libfoo_global.so -Wl,--version-script=./foo.exp
	g++ -fvisibility-inlines-hidden -Wl,--build-id -Wl,--gc-sections -std=c++11 -shared -g -O0 -fPIC $(SRC_DIR)/foo.cpp -o libfoo_global_2.so -Wl,--version-script=./foo.exp

clean:
	rm -f *.o *.so *.out
