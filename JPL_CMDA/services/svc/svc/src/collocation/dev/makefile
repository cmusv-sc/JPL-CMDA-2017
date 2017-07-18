_distance.so: distance.o distance_wrap.o
	ld -shared -O3 distance.o distance_wrap.o -o _distance.so
distancy.py distance_wrap.c: distance.i
	swig -python distance.i
distance.o distance_wrap.o: distance.c distance_wrap.c
	gcc -c -fPIC -O3 distance.c distance_wrap.c -I/opt/sciflo/include/python2.5
clean:
	rm -f distance.o distance.py distance_wrap.c distance_wrap.o
