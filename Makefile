osx::
	gcc -bundle -undefined dynamic_lookup gonert.c -o gonert.so

linux::
	gcc -shared gonert.c -o gonert.so -fPIC
