. To run with Valgrind:
  G_SLICE=always-malloc G_DEBUG=gc-friendly  valgrind -v --tool=memcheck --leak-check=full --num-callers=40 --log-file=valgrind.log --track-origins=yes --leak-check=full --show-reachable=yes a.out
