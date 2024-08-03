

#ifndef TOSGAME_H
#define TOSGAME_H

#include <iostream>
#include <vector>
#include "Rune.h"
using namespace std;

#define RUNE_NUM 7
#define EMPTY 0
#define WATER 1
#define FIRE 2
#define GRASS 3
#define LIGHT 4
#define DARK 5
#define HEART 6

#define COL_NUM 6
#define ROW_NUM 5

#define MAX_DEPTH 10

class TosGame {
public:
    TosGame();
    ~TosGame();

    void randomize_runes();
    void reset_indices();

public:

    Rune *rune_list[31];
    
    int rune_indices[ROW_NUM][COL_NUM]; // 5 rows, 6 columns as rune_indices[y][x]
    int first_combo;
    int total_combos;
    int total_eliminated;
    int target_first_combo;
    // void set_board(int type[5][6], int race[5][6], int min_match[5][6], bool no_first[5][6], bool untouchable[5][6], bool must_eliminate[5][6]);
    // void set_board(string str);
    void set_rune(string rune_str);
    void set_race(string race_str);
    void set_min_match(string min_match_str);
    // void set_no_first(string no_first_str);
    // void set_untouchable(string untouchable_str);
    void set_must_eliminate(string must_eliminate_str);
    void set_setting(string setting_str);
    void print_all_attributes();

    TosGame(const TosGame &game);
    // void set_all_runes();

public:
    Rune *empty_rune;
    bool no_first[7];
    bool eli_color[7];
    bool all_first[7];
    bool same_first[7];
    
};

/**
 * @brief Print the board with rune_list and rune_indices
 * 
 * @param rune_list a list of runes of size 31
 * @param rune_indices a 5x6 array of indices
 */
void show_board(Rune *rune_list[31], int rune_indices[5][6]);
void eliminate_once(Rune *rune_list[31], int rune_indices[5][6], int *combo, int *total_eliminated);

/**
 * @brief Eliminate runes once with different min_match
 * 
 * @param rune_list A list of runes of size 31
 * @param rune_indices Array of indices. Will be modified in place
 * @param combo The number of combos
 * @param total_eliminated The number of runes eliminated
 * @return std::array<std::pair<int, int>, 6> A list of [combo, eliminated] for each rune type
 */
void eliminate_once_special(Rune *rune_list[31], int rune_indices[5][6], int *combo, int *total_eliminated, int color_eliminated[], int color_combo[]);
void drop_indices(int rune_indices[5][6]);

/**
 * @brief Get the indices after route played
 * 
 * @param rune_indices Array of indices. Will be modified in place
 * @param route A vector of pairs of indices
 */
void get_indices_from_route(int rune_indices[5][6], vector<pair<int, int>> route);

std::pair<int, std::vector<std::pair<int, int>>> find_best_route(TosGame &game, int x, int y, std::vector<std::pair<int, int>> currentRoute, int current_indices[5][6], size_t max_depth);
std::pair<int, std::vector<std::pair<int, int>>> find_best_route_no_start(TosGame &game, size_t max_depth);
std::pair<int, std::vector<std::pair<int, int>>> route_planning(TosGame &game, int iter_time, int max_first_depth, size_t max_depth);

#endif
