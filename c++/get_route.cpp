#include <iostream>
#include "include\Rune.h"
#include "include\TosGame.h"
#include <algorithm>
#include <utility>

// #define TEST_ROUTE

using namespace std;

char* getCmdOption(char **begin, char **end, const std::string &option) {
    char ** itr = std::find(begin, end, option);
    if (itr != end && ++itr != end) {
        return *itr;
    }
    return 0;
}

bool cmdOptionExists(char **begin, char **end, const std::string &option) {
    return std::find(begin, end, option) != end;
}



int main(int argc, char *argv[]) {

    ios::sync_with_stdio(false);
    cin.tie(0);
    cout.tie(0);

    srand(time(NULL));

    TosGame game;
    

    // for testing
    int iter_time = 30;
    int max_first_depth = 7;
    int max_depth = 9;
    
    game.randomize_runes();

    if (cmdOptionExists(argv, argv+argc, "-i")) {
        iter_time = atoi(getCmdOption(argv, argv+argc, "-i"));
    }
    if (cmdOptionExists(argv, argv+argc, "-f")) {
        max_first_depth = atoi(getCmdOption(argv, argv+argc, "-f"));
    }
    if (cmdOptionExists(argv, argv+argc, "-d")) {
        max_depth = atoi(getCmdOption(argv, argv+argc, "-d"));
    }
    if (cmdOptionExists(argv, argv+argc, "-rune")) {
        game.set_rune(getCmdOption(argv, argv+argc, "-rune"));
    }
    if (cmdOptionExists(argv, argv+argc, "-race")) {
        game.set_race(getCmdOption(argv, argv + argc, "-race"));
    }
    if (cmdOptionExists(argv, argv+argc, "-min_match")) {
        game.set_min_match(getCmdOption(argv, argv + argc, "-min_match"));
    }
    if (cmdOptionExists(argv, argv+argc, "-must")) {
        game.set_must_eliminate(getCmdOption(argv, argv + argc, "-must"));
    }
    if (cmdOptionExists(argv, argv+argc, "-setting")) {
        game.set_setting(getCmdOption(argv, argv + argc, "-setting"));
    }
    // game.print_all_attributes();

#ifdef TEST_ROUTE
    clock_t start = clock();
    show_board(game.rune_list, game.rune_indices);
#endif

    auto [bestScore, bestRoute] = route_planning(game, iter_time, max_first_depth, max_depth);
    // cout << "Best score: " << bestScore << "\n";
    string route_str = "";
    for (auto [x, y] : bestRoute) {
        route_str += "(" + to_string(x) + ", " + to_string(y) + "), ";
    }
    route_str = route_str.substr(0, route_str.size() - 2);
    cout << route_str << endl;
    game.reset_indices();
    get_indices_from_route(game.rune_indices, bestRoute);

    // show_board(game.rune_list, game.rune_indices);
    int combo = 0;
    eliminate_once(game.rune_list, game.rune_indices, &combo, &game.total_eliminated);
    game.first_combo = combo;
    drop_indices(game.rune_indices);
    while (combo > 0) {
        game.total_combos += combo;
        eliminate_once(game.rune_list, game.rune_indices, &combo, &game.total_eliminated);
        drop_indices(game.rune_indices);
    }
#ifdef TEST_ROUTE
    show_board(game.rune_list, game.rune_indices);
    cout << "Move length: " << bestRoute.size() << "\n";
    cout << "First combo: " << game.first_combo << ", Total combos: " << game.total_combos << ", Total eliminated: " << game.total_eliminated << endl;
    cout << "elapsed time: " << (clock() - start) / (double) CLOCKS_PER_SEC << "s\n";
#endif
    return 0;
}