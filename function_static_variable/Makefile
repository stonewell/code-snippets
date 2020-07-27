.PHONY: all clean

DIRS = lib lib_2 lib_3 prog

all:
	$(foreach var, $(DIRS), make -C $(var);)

clean:
	$(foreach var, $(DIRS), make -C $(var) clean;)
