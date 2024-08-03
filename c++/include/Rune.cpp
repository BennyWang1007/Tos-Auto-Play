#include "Rune.h"

Rune::Rune(int type, int race, int min_match, bool no_first, bool untouchable, bool must_eliminate) : type(type), race(race), min_match(min_match), no_first(no_first), untouchable(untouchable), must_eliminate(must_eliminate) {
}

Rune::Rune() : type(0), race(0), min_match(3), no_first(false), untouchable(false), must_eliminate(false) {
}

Rune::~Rune() {
}

Rune::Rune(const Rune &rune) : type(rune.type), race(rune.race), min_match(rune.min_match), no_first(rune.no_first), untouchable(rune.untouchable), must_eliminate(rune.must_eliminate) {
}