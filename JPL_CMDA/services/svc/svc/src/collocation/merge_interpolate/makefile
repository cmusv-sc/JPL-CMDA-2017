mergein.so: mergein.o distance.o
	gcc -shared -O3 -lm mergein.o distance.o -o _mergein.so
mergein.o: mergein.c distance.h
	gcc -c -fPIC -O3 mergein.c
distance.o: distance.c distance.h
	gcc -c -fPIC -O3 distance.c
clean:
	rm -f mergein.o distance.o _mergein.so
