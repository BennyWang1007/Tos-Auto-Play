@echo off
cd include
g++ -c *.cpp -O3 -Wall
cd ..
@REM g++ -o main.exe main.cpp include\*.o -O3
g++ -o get_route.exe get_route.cpp include\*.o -O3 -Wall
@REM g++ -o bench_mark.exe bench_mark.cpp include\*.o -O3 -Wall
