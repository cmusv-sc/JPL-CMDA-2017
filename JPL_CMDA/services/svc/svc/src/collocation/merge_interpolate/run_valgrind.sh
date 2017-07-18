#!/bin/env sh

valgrind --tool=memcheck --leak-check=yes --show-reachable=yes -v ./a.out
