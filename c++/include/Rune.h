
#ifndef RUNE_H
#define RUNE_H

#include <iostream>
using namespace std;

#define RUNE_NUM 7

class Rune {
public:
    Rune(int type, int race=0, int min_match=3, bool no_first=false, bool untouchable=false, bool must_eliminate=false);
    Rune(int type);
    Rune();
    ~Rune();

    int type;
    int race;
    // const int min_match;
    int min_match;
    bool no_first;
    bool untouchable;
    bool must_eliminate;

    // copy constructor
    Rune(const Rune &rune);

    int static str2int(string str);
};

#endif

