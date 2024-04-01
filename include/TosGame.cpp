#include <iostream>
#include <string>
#include "TosGame.h"
#include "Rune.h"
#include <random>
#include <stack>
#include <vector>
#include <array>
#include <ctime>
#include <chrono>
#include <assert.h>
#include <algorithm>
#include <utility>

using namespace std;

#define MAX_DEPTH 10

TosGame::~TosGame() {
}

void TosGame::randomize_runes() {
    int type;
    for (int i = 0; i < 30; i++) {
        type = rand() % 6 + 1;
        rune_list[i] = new Rune(type);
    }
}

void TosGame::reset_indices() {
    for (int y = 0; y < 5; y++) {
        for (int x = 0; x < 6; x++) {
            rune_indices[y][x] = y * 6 + x;
        }
    }
}

TosGame::TosGame() {
    // set up board
    empty_rune = new Rune(0);
    rune_list[30] = empty_rune;
    randomize_runes();
    reset_indices();

    first_combo = 0;
    total_combos = 0;
    total_eliminated = 0;
    target_first_combo = 10;
    for (int i = 0; i < 7; i++) {
        no_first[i] = false;
        eli_color[i] = false;
        all_first[i] = false;
        same_first[i] = false;
    }

    // TODO
    
}

TosGame::TosGame(const TosGame &game) {
    for (int i = 0; i < 31; i++) {
        rune_list[i] = game.rune_list[i];
    }
    empty_rune = game.empty_rune;
    for (int y = 0; y < 5; y++) {
        for (int x = 0; x < 6; x++) {
            rune_indices[y][x] = game.rune_indices[y][x];
        }
    }
    first_combo = game.first_combo;
    total_combos = game.total_combos;
    total_eliminated = game.total_eliminated;
    target_first_combo = game.target_first_combo;
    for (int i = 0; i < 7; i++) {
        no_first[i] = game.no_first[i];
        eli_color[i] = game.eli_color[i];
        all_first[i] = game.all_first[i];
        same_first[i] = game.same_first[i];
    }

}





// void TosGame::set_board(int type[5][6], int race[5][6], int min_match[5][6], bool no_first[5][6], bool untouchable[5][6], bool must_eliminate[5][6]) {
//     for (int y = 0; y < 5; y++) {
//         for (int x = 0; x < 6; x++) {
//             rune_list[y * 6 + x] = new Rune(type[y][x], race[y][x], min_match[y][x], no_first[y][x], untouchable[y][x], must_eliminate[y][x]);
//         }
//     }
// }

void TosGame::set_rune(string rune_str) {
    string rune_type_str = " WFGLDH?";
    assert(rune_str.length() == 30);
    for (int i = 0; i < 30; i++) {
        rune_list[i]->type = rune_type_str.find(rune_str[i]);
    }
}

void TosGame::set_race(string race_str) {
    string rune_race_str = " GDHOLEM";
    assert(race_str.length() == 30);
    for (int i = 0; i < 30; i++) {
        rune_list[i]->race = rune_race_str.find(race_str[i]);
    }
}

void TosGame::set_min_match(string min_match_str) {
    assert(min_match_str.length() == 30);
    for (int i = 0; i < 30; i++) {
        rune_list[i]->min_match = min_match_str[i] - '0';
    }
}

void TosGame::set_must_eliminate(string must_eliminate_str) {
    assert(must_eliminate_str.length() == 30);
    for (int i = 0; i < 30; i++) {
        rune_list[i]->must_eliminate = (must_eliminate_str[i] == '1');
    }
}

void TosGame::set_setting(string setting_str) {
    // split setting_str by '/'
    // setting shoud be one of the following:
    // eli_color: no_first: all_first: eli_first: same:
    string rune_type_str = " WFGLDH?";
    string delimiter = "/";
    size_t pos = 0;
    string token;
    string str = setting_str;
    string setting_list[10];
    int count = 0;
    while ((pos = str.find(delimiter)) != string::npos) {
        token = str.substr(0, pos);
        setting_list[count] = token;
        str.erase(0, pos + delimiter.length());
        count++;
    }
    setting_list[count] = str;
    count++;
    for (int idx = 0; idx < count; idx++) {
        if (setting_list[idx].find("eli_color: ") == 0) {
            string eli_color_str = setting_list[idx].substr(11);
            // cout << "eli_color: |" << eli_color_str << "|\n";
            for (size_t i = 0; i < eli_color_str.length(); i++) {
                size_t type = rune_type_str.find(eli_color_str[i]);
                if (type < 7) eli_color[type] = true;
            }
        }
        else if (setting_list[idx].find("no_first: ") == 0) {
            string no_first_str = setting_list[idx].substr(10);
            // cout << "no_first: |" << no_first_str << "|\n";
            for (size_t i = 0; i < no_first_str.length(); i++) {
                size_t type = rune_type_str.find(no_first_str[i]);
                if (type < 7) no_first[type] = true;
            }
        }
        else if (setting_list[idx].find("all_first: ") == 0) {
            string all_first_str = setting_list[idx].substr(11);
            // cout << "all_first: |" << all_first_str << "|\n";
            for (size_t i = 0; i < all_first_str.length(); i++) {
                size_t type = rune_type_str.find(all_first_str[i]);
                if (type < 7) all_first[type] = true;
            }
        }
        else if (setting_list[idx].find("eli_first: ") == 0) {
            string eli_first_str = setting_list[idx].substr(11);
            // cout << "eli_first: |" << eli_first_str << "|\n";
            target_first_combo = stoi(eli_first_str);
        }
        else if (setting_list[idx].find("same: ") == 0) {
            string same_str = setting_list[idx].substr(6);
            // cout << "same: |" << same_str << "|\n";
            for (size_t i = 0; i < same_str.length(); i++) {
                size_t type = rune_type_str.find(same_str[i]);
                if (type < 7) same_first[type] = true;
            }
        }
    }
}

// void TosGame::set_board(string str) {
//     string rune_type_str = " WFGLDH?";
//     string rune_race_str = " GDHOLEM";
//     int type[5][6] = {0};
//     int race[5][6] = {0};
//     int min_match[5][6] = {0};
//     bool no_first[5][6] = {0};
//     bool untouchable[5][6] = {0};
//     bool must_eliminate[5][6] = {0};

//     assert(str.length() % 30 == 0);

//     for (int x = 0; x < 6; x++) {
//         for (int y = 0; y < 5; y++) {
//             type[y][x] = rune_type_str.find(str[y * 6 + x]);
//         }
//     }
//     reset_indices();
//     if (str.length() > 30) {
//         for (int x = 0; x < 6; x++) {
//             for (int y = 0; y < 5; y++) {
//                 race[y][x] = rune_race_str.find(str[y * 6 + x + 30]);
//             }
//         }
//     }
//     if (str.length() > 60) {
//         for (int x = 0; x < 6; x++) {
//             for (int y = 0; y < 5; y++) {
//                 min_match[y][x] = str[y * 6 + x + 60] - '0';
//             }
//         }
//     }
//     if (str.length() > 90) {
//         for (int x = 0; x < 6; x++) {
//             for (int y = 0; y < 5; y++) {
//                 no_first[y][x] = (str[y * 6 + x + 90] == '1');
//             }
//         }
//     }
//     if (str.length() > 120) {
//         for (int x = 0; x < 6; x++) {
//             for (int y = 0; y < 5; y++) {
//                 untouchable[y][x] = (str[y * 6 + x + 120] == '1');
//             }
//         }
//     }
//     if (str.length() > 150) {
//         for (int x = 0; x < 6; x++) {
//             for (int y = 0; y < 5; y++) {
//                 must_eliminate[y][x] = (str[y * 6 + x + 150] == '1');
//             }
//         }
//     }
//     set_board(type, race, min_match, no_first, untouchable, must_eliminate);
// }



void drop_indices(int rune_indices[5][6]) {
    for (int x = 0; x < 6; x++) {
        int cur_y = 4;
        for (int y = 4; y >= 0; y--) {
            if (rune_indices[y][x] != 30) {
                rune_indices[cur_y][x] = rune_indices[y][x];
                cur_y--;
            }
        }
        for (int y = cur_y; y >= 0; y--) {
            rune_indices[y][x] = 30;
        }
    }
}


void eliminate_once_special(Rune *rune_list[31], int rune_indices[5][6], int *combo, int *total_eliminated, int *color_eliminated, int *color_combo) {

    // array<pair<int, int>, 7> result;
    // for (int i = 0; i < 7; i++) {
    //     result[i] = {0, 0};
    // }
    int to_eliminate[5][6] = {0};
    for (int y = 0; y < 5; y++) {
        for (int x = 0; x < 6; x++) {
            int min_match = rune_list[rune_indices[y][x]]->min_match;
            int type = rune_list[rune_indices[y][x]]->type;
            if (min_match == 1) {
                to_eliminate[y][x] = type;
                min_match = 2;
            }
            if (min_match == 2) {
                if (!to_eliminate[y][x] && !to_eliminate[y][x-1] && x > 0 && rune_list[rune_indices[y][x-1]]->type == type) {
                    to_eliminate[y][x-1] = type;
                    to_eliminate[y][x] = type;
                }
                if (!to_eliminate[y][x] && !to_eliminate[y][x+1] && x < 5 && rune_list[rune_indices[y][x+1]]->type == type) {
                    to_eliminate[y][x] = type;
                    to_eliminate[y][x+1] = type;
                }
                if (!to_eliminate[y][x] && !to_eliminate[y-1][x] && y > 0 && rune_list[rune_indices[y-1][x]]->type == type) {
                    to_eliminate[y-1][x] = type;
                    to_eliminate[y][x] = type;
                }
                if (!to_eliminate[y][x] && !to_eliminate[y+1][x] && y < 4 && rune_list[rune_indices[y+1][x]]->type == type) {
                    to_eliminate[y][x] = type;
                    to_eliminate[y+1][x] = type;
                }
            }
            else {
                // if (x > 1 && rune_list[rune_indices[y][x-2]]->type == type && rune_list[rune_indices[y][x-1]]->type == type) {
                //     to_eliminate[y][x-2] = type;
                //     to_eliminate[y][x-1] = type;
                //     to_eliminate[y][x] = type;
                // }
                if (x < 4 && rune_list[rune_indices[y][x+1]]->type == type && rune_list[rune_indices[y][x+2]]->type == type) {
                    to_eliminate[y][x] = type;
                    to_eliminate[y][x+1] = type;
                    to_eliminate[y][x+2] = type;
                }
                // if (y > 1 && rune_list[rune_indices[y-2][x]]->type == type && rune_list[rune_indices[y-1][x]]->type == type) {
                //     to_eliminate[y-2][x] = type;
                //     to_eliminate[y-1][x] = type;
                //     to_eliminate[y][x] = type;
                // }
                if (y < 3 && rune_list[rune_indices[y+1][x]]->type == type && rune_list[rune_indices[y+2][x]]->type == type) {
                    to_eliminate[y][x] = type;
                    to_eliminate[y+1][x] = type;
                    to_eliminate[y+2][x] = type;
                }
            }
        }
    }
    
    (*combo) = 0;
    // (*total_eliminated) = 0;
    bool isZero = false;
    int cur_y = 0;
    int cur_x = 0;
    int target = 0;
    int last_y = 0;
    while (!isZero) {
        isZero = true;
        for (int y = last_y; y < 5; y++) {
            for (int x = 0; x < 6; x++) {
                if (to_eliminate[y][x] != 0) {
                    isZero = false;
                    last_y = y;
                    cur_y = y;
                    cur_x = x;
                    target = to_eliminate[y][x];
                    break;
                }
            }
            if (!isZero) break;
        }
        if (isZero) break;
        (*combo)++;
        // cur_combo++;
        stack<int> to_eliminate_stack;
        to_eliminate_stack.push(cur_y);
        to_eliminate_stack.push(cur_x);
        bool visited[5][6] = {0};

        while (!to_eliminate_stack.empty()) {
            int x = to_eliminate_stack.top();
            to_eliminate_stack.pop();
            int y = to_eliminate_stack.top();
            to_eliminate_stack.pop();
            if (visited[y][x]) continue;
            visited[y][x] = true;
            if (x > 0 && to_eliminate[y][x-1] == target) {
                to_eliminate_stack.push(y);
                to_eliminate_stack.push(x-1);
            }
            if (x < 5 && to_eliminate[y][x+1] == target) {
                to_eliminate_stack.push(y);
                to_eliminate_stack.push(x+1);
            }
            if (y > 0 && to_eliminate[y-1][x] == target) {
                to_eliminate_stack.push(y-1);
                to_eliminate_stack.push(x);
            }
            if (y < 4 && to_eliminate[y+1][x] == target) {
                to_eliminate_stack.push(y+1);
                to_eliminate_stack.push(x);
            }
        }
        int cur_eliminated = 0;
        for (int y = 0; y < 5; y++) {
            for (int x = 0; x < 6; x++) {
                if (visited[y][x]) {
                    cur_eliminated++;
                    to_eliminate[y][x] = 0;
                    rune_indices[y][x] = 30;
                }
            }
        }
        // result[target].first += cur_eliminated;
        // result[target].second++;
        color_combo[target]++;
        color_eliminated[target] += cur_eliminated;
        (*total_eliminated) += cur_eliminated;
    }
    // return result;
}

void eliminate_once(Rune *rune_list[31], int rune_indices[5][6], int *combo, int *total_eliminated) {
    int to_eliminate[5][6] = {0};
    for (int y = 0; y < 5; y++) {
        for (int x = 1; x < 5; x++) {
            int type = rune_list[rune_indices[y][x]]->type;
            // cout << "rune: " << rune << ", x-1: " << rune_list[rune_indices[y][x-1]] << ", x+1: " << rune_list[rune_indices[y][x+1]] << endl;
            if (rune_list[rune_indices[y][x-1]]->type == type && rune_list[rune_indices[y][x+1]]->type == type) {
                to_eliminate[y][x-1] = type;
                to_eliminate[y][x] = type;
                to_eliminate[y][x+1] = type;

            }
        }
    }
    for (int x = 0; x < 6; x++) {
        for (int y = 1; y < 4; y++) {
            int type = rune_list[rune_indices[y][x]]->type;
            if (rune_list[rune_indices[y-1][x]]->type == type && rune_list[rune_indices[y+1][x]]->type == type) {
                to_eliminate[y-1][x] = type;
                to_eliminate[y][x] = type;
                to_eliminate[y+1][x] = type;
            }
        }
    }

    // cout << "to_eliminate: " << endl;
    // for (int y = 0; y < 5; y++) {
    //     for (int x = 0; x < 6; x++) {
    //         cout << to_eliminate[y][x] << " ";
    //     }
    //     cout << endl;
    // }
    // return;

    (*combo) = 0;
    // (*total_eliminated) = 0;
    bool isZero = false;
    int cur_y = 0;
    int cur_x = 0;
    int target = 0;
    int last_y = 0;
    while (!isZero) {
        isZero = true;
        for (int y = last_y; y < 5; y++) {
            for (int x = 0; x < 6; x++) {
                if (to_eliminate[y][x] != 0) {
                    isZero = false;
                    last_y = y;
                    cur_y = y;
                    cur_x = x;
                    target = to_eliminate[y][x];
                    break;
                }
            }
            if (!isZero) break;
        }
        if (isZero) break;
        (*combo)++;
        stack<int> to_eliminate_stack;
        to_eliminate_stack.push(cur_y);
        to_eliminate_stack.push(cur_x);
        bool visited[5][6] = {0};

        while (!to_eliminate_stack.empty()) {
            int x = to_eliminate_stack.top();
            to_eliminate_stack.pop();
            int y = to_eliminate_stack.top();
            to_eliminate_stack.pop();
            if (visited[y][x]) continue;
            visited[y][x] = true;
            if (x > 0 && to_eliminate[y][x-1] == target) {
                to_eliminate_stack.push(y);
                to_eliminate_stack.push(x-1);
            }
            if (x < 5 && to_eliminate[y][x+1] == target) {
                to_eliminate_stack.push(y);
                to_eliminate_stack.push(x+1);
            }
            if (y > 0 && to_eliminate[y-1][x] == target) {
                to_eliminate_stack.push(y-1);
                to_eliminate_stack.push(x);
            }
            if (y < 4 && to_eliminate[y+1][x] == target) {
                to_eliminate_stack.push(y+1);
                to_eliminate_stack.push(x);
            }
        }
        for (int y = 0; y < 5; y++) {
            for (int x = 0; x < 6; x++) {
                if (visited[y][x]) {
                    // cout << "eliminate: " << y << " " << x << endl;
                    to_eliminate[y][x] = 0;
                    rune_indices[y][x] = 30;
                    (*total_eliminated)++;
                }
            }
        }
    }
}

/**
 * @brief Evaluate the score of the current board
 * 
 * @param game The game object
 * @param rune_indices Indices of current board, will not be modified
 * @return int : Evaluated score
 */
int evaluate_score(TosGame game, int rune_indices[5][6]) {
    int new_rune_indices[5][6];
    for (int y = 0; y < 5; y++) {
        for (int x = 0; x < 6; x++) {
            new_rune_indices[y][x] = rune_indices[y][x];
        }
    }
    int combo = 0;
    int first_combo = 0;
    int total_combos = 0;
    int total_eliminated = 0;
    // eliminate_once(rune_list, new_rune_indices, &combo, &total_eliminated);
    int color_eliminated[7] = {0};
    int color_combo[7] = {0};
    eliminate_once_special(game.rune_list, new_rune_indices, &combo, &total_eliminated, color_eliminated, color_combo);

    int score = 0;
    for (int i = 1; i < 7; i++) {
        // eliminate the color that shouldn't be eliminated first
        if (game.no_first[i] && color_combo[i] > 0) {
            // cout << "eliminate color: " << i << "\n";
            score -= 100;
        }
    }

    if (new_rune_indices[0][0] == 30) score += 10;
    if (new_rune_indices[0][5] == 30) score += 10;
    if (new_rune_indices[4][0] == 30) score += 10;
    if (new_rune_indices[4][5] == 30) score += 10;
    // for (int x = 0; x < 6; x++){
    //     if (new_rune_indices[0][x] == 30) score += 10;
    //     if (new_rune_indices[4][x] == 30) score += 10;
    // }
    // for (int y = 0; y < 5; y++){
    //     if (new_rune_indices[y][0] == 30) score += 10;
    //     if (new_rune_indices[y][5] == 30) score += 10;
    // }
        
    drop_indices(new_rune_indices);
    first_combo = combo;
    while (combo > 0) {
        total_combos += combo;
        // eliminate_once(rune_list, new_rune_indices, &combo, &total_eliminated);
        eliminate_once_special(game.rune_list, new_rune_indices, &combo, &total_eliminated, color_eliminated, color_combo);
        drop_indices(new_rune_indices);
    }

    for (int i = 1; i < 7; i++) {
        // not eliminate the color needed to eliminate
        if (game.eli_color[i] && color_combo[i] == 0) {
            // cout << "missing color: " << i << "\n";
            score -= 100;
        }
    }

    // 100 for first combo, 40 for each additional combo, 1 for each eliminated rune
    score += 60 * first_combo + 40 * total_combos + total_eliminated;

    return score;
}


std::pair<int, std::vector<std::pair<int, int>>> find_best_first_route(
        TosGame &game, int x, int y, std::vector<std::pair<int, int>> currentRoute,
        int current_indices[5][6], size_t max_depth=MAX_DEPTH) {

    if (currentRoute.size() == max_depth) {
        if (x == 0 || x == 5 || y == 0 || y == 4) {
            return {-1, currentRoute};
        }
        return {evaluate_score(game, current_indices), currentRoute};
    }
    std::pair<int, std::vector<std::pair<int, int>>> bestScore = {-2147483647, {}};
    for (int dx = -1; dx < 2; dx++) {
        for (int dy = -1; dy < 2; dy++) {
            // if (dx != 0 && dy != 0) continue;
            if ((dx == 0 && dy == 0)) {
                // cout << bestScore.second.size() << "\n";
                int score = 0;
                if (x == 0 || x == 5 || y == 0 || y == 4) {
                    score = -1;
                }
                else {
                    // int new_indices[5][6];
                    // for (int i = 0; i < 5; i++) {
                    //     for (int j = 0; j < 6; j++) {
                    //         new_indices[i][j] = current_indices[i][j];
                    //     }
                    // }
                    // int temp, temp2;
                    // eliminate_once_special(game.rune_list, new_indices, &temp, &temp2);
                    // if (new_indices[y][x] == 30) {
                    //     score = -1;
                    // }
                    // else{
                        score = evaluate_score(game, current_indices);
                    // }
                }
                // auto score = evaluate_score(game.rune_list, current_indices);
                if (score > bestScore.first) {
                    bestScore = {score, currentRoute};
                }
                else if (score == bestScore.first && currentRoute.size() < bestScore.second.size()) {
                    bestScore = {score, currentRoute};
                }
            }
            else{
                int new_x = x + dx;
                int new_y = y + dy;
                // cout << "move: (" << dx << ", " << dy << "), from: (" << x << ", " << y << ") to (" << x + dx << ", " << y + dy << ")\n";
                if (new_x < 0 || new_x >= 6 || new_y < 0 || new_y >= 5 || game.rune_list[current_indices[new_y][new_x]]->untouchable) continue;
                // if new_x, new_y is already in the route, skip
                if (find(currentRoute.begin(), currentRoute.end(), make_pair(new_x, new_y)) != currentRoute.end()) continue;
                // bool skip = false;
                // for (auto [x, y] : currentRoute) {
                //     if (x == new_x && y == new_y) {
                //         skip = true;
                //         continue;
                //     }
                // }
                // if (skip) continue;
                std::vector<std::pair<int, int>> newRoute = currentRoute;
                newRoute.emplace_back(x + dx, y + dy);
                int new_indices[5][6];
                for (int i = 0; i < 5; i++) {
                    for (int j = 0; j < 6; j++) {
                        new_indices[i][j] = current_indices[i][j];
                    }
                }
                std::swap(new_indices[y][x], new_indices[new_y][new_x]);
                auto [score, route] = find_best_route(game, new_x, new_y, newRoute, new_indices, max_depth);
                if (score > bestScore.first) {
                    // cout << "score: " << score << ", route: " << route.size() << endl;
                    bestScore = {score, route};
                }
            }
            
        }
    }
    return bestScore;
}


// return best score and best route
std::pair<int, std::vector<std::pair<int, int>>> find_best_route(
        TosGame &game, int x, int y, std::vector<std::pair<int, int>> currentRoute,
        int current_indices[5][6], size_t max_depth=MAX_DEPTH) {

    if (currentRoute.size() == max_depth) {
        return {evaluate_score(game, current_indices), currentRoute};
    }
    std::pair<int, std::vector<std::pair<int, int>>> bestScore = {-2147483647, {}};
    for (int dx = -1; dx < 2; dx++) {
        for (int dy = -1; dy < 2; dy++) {
            // if (dx != 0 && dy != 0) continue;
            if ((dx == 0 && dy == 0)) {
                // cout << bestScore.second.size() << "\n";
                auto score = evaluate_score(game, current_indices);
                if (score > bestScore.first) {
                    bestScore = {score, currentRoute};
                }
                else if (score == bestScore.first && currentRoute.size() < bestScore.second.size()) {
                    bestScore = {score, currentRoute};
                }
            }
            else{
                int new_x = x + dx;
                int new_y = y + dy;
                // cout << "move: (" << dx << ", " << dy << "), from: (" << x << ", " << y << ") to (" << x + dx << ", " << y + dy << ")\n";
                if (new_x < 0 || new_x >= 6 || new_y < 0 || new_y >= 5 || game.rune_list[current_indices[new_y][new_x]]->untouchable) continue;
                // if new_x, new_y is already in the route, skip
                bool skip = false;
                for (auto [x, y] : currentRoute) {
                    if (x == new_x && y == new_y) {
                        skip = true;
                        continue;
                    }
                }
                if (skip) continue;
                std::vector<std::pair<int, int>> newRoute = currentRoute;
                newRoute.emplace_back(x + dx, y + dy);
                int new_indices[5][6];
                for (int i = 0; i < 5; i++) {
                    for (int j = 0; j < 6; j++) {
                        new_indices[i][j] = current_indices[i][j];
                    }
                }
                std::swap(new_indices[y][x], new_indices[new_y][new_x]);
                auto [score, route] = find_best_route(game, new_x, new_y, newRoute, new_indices, max_depth);
                if (score > bestScore.first) {
                    // cout << "score: " << score << ", route: " << route.size() << endl;
                    bestScore = {score, route};
                }
            }
            
        }
    }
    return bestScore;
}

void get_indices_from_route(int indices[5][6], std::vector<std::pair<int, int>> route) {
    
    int start_indices = indices[route[0].second][route[0].first];
    int size = route.size();
    for (int i = 0; i < size - 1; i++) {
        indices[route[i].second][route[i].first] = indices[route[i + 1].second][route[i + 1].first];
    }
    indices[route[route.size() - 1].second][route[route.size() - 1].first] = start_indices;

}

std::pair<int, std::vector<std::pair<int, int>>> find_best_route_no_start(
        TosGame &game, size_t max_depth=MAX_DEPTH) {
    std::pair<int, std::vector<std::pair<int, int>>> bestScore = {-2147483647, {}};
    for (int x = 0; x < 6; x++) {
        for (int y = 0; y < 5; y++) {
            std::vector<std::pair<int, int>> currentRoute = {{x, y}};
            currentRoute.reserve(max_depth);
            int current_indices[5][6];
            for (int i = 0; i < 5; i++) {
                for (int j = 0; j < 6; j++) {
                    current_indices[i][j] = game.rune_indices[i][j];
                }
            }
            // auto [score, route] = find_best_route(game, x, y, currentRoute, current_indices, max_depth);
            auto [score, route] = find_best_first_route(game, x, y, currentRoute, current_indices, max_depth);
            if (score > bestScore.first) {
                bestScore = {score, route};
            }
        }
    }
    return bestScore;
}

void simplify_route(std::vector<std::pair<int, int>> &route) {
    for (size_t i = 0; i < route.size() - 1; i++) {
        if (route[i].first == route[i + 1].first && route[i].second == route[i + 1].second) {
            route.erase(route.begin() + i);
            i--;
        }
    }
    size_t cur_size = route.size();
    while (true) {
        for (size_t i = 1; i < route.size() - 1; i++) {
            if (route[i + 1].first == route[i - 1].first && route[i + 1].second == route[i - 1].second) {
                route.erase(route.begin() + i + 1);
                route.erase(route.begin() + i);
                i -= 2;
            }
        }
        if (cur_size == route.size()) break;
        cur_size = route.size();
    }
}

std::pair<int, std::vector<std::pair<int, int>>> route_planning(TosGame &game, int iter_time, int max_first_depth=MAX_DEPTH, size_t max_depth=MAX_DEPTH) {
    std::vector<std::pair<int, int>> totol_route;
    TosGame game_copy = game;
    int cur_indices[5][6];
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 6; j++) {
            cur_indices[i][j] = game.rune_indices[i][j];
        }
    }
    auto [bestScore, bestRoute] = find_best_route_no_start(game, max_first_depth);
    // update indices
    get_indices_from_route(game.rune_indices, bestRoute);
    totol_route.insert(totol_route.end(), bestRoute.begin(), bestRoute.end());
    int i = 0;
    for (i = 0; i < iter_time; i++) {
        // copy current indices
        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 6; j++) {
                cur_indices[i][j] = game.rune_indices[i][j];
            }
        }
        auto [last_x, last_y] = bestRoute.back();
        auto [score, route] = find_best_route(game, last_x, last_y, {make_pair(last_x, last_y)}, cur_indices, max_depth);
        if (score > bestScore) {
            // if route go backward, remove those backwards and recalculate the route
            int go_back = 0;
            while (totol_route[totol_route.size()-2-go_back].first == route[1+go_back].first && totol_route[totol_route.size()-2-go_back].second == route[1+go_back].second) {
                go_back++;
            }
            if (true || go_back == 0){
                bestScore = score;
                bestRoute = route;
                totol_route.insert(totol_route.end(), route.begin(), route.end());
                simplify_route(totol_route);
                get_indices_from_route(game.rune_indices, route);
            }
            else {
                // print totoal route, route, go_back
                // cout << "totol_route: \n";
                // for (auto [x, y] : totol_route) {
                //     cout << "(" << x << ", " << y << "), ";
                // }
                // cout << endl;
                // cout << "route: \n";
                // for (auto [x, y] : route) {
                //     cout << "(" << x << ", " << y << "), ";
                // }
                // cout << endl;
                // cout << "go_back: " << go_back << endl;

                totol_route.erase(totol_route.end() - go_back, totol_route.end());
                get_indices_from_route(game.rune_indices, totol_route);
                auto [last_x, last_y] = totol_route.back();
                auto [score, route] = find_best_route(game, last_x, last_y, {make_pair(last_x, last_y)}, cur_indices, max_depth);
                bestScore = score;
                bestRoute = route;
                totol_route.insert(totol_route.end(), route.begin(), route.end());
                simplify_route(totol_route);
            }

            
        }
        else {
            break;
        }
    }
    
    simplify_route(totol_route);

    return {bestScore, totol_route};
}


void show_board(Rune *rune_list[31], int rune_indices[5][6]) {
    string rune_type_str = " WFGLDH?";
    for (int y = 0; y < 5; y++) {
        cout << "| ";
        for (int x = 0; x < 6; x++) {
            cout << rune_type_str[rune_list[rune_indices[y][x]]->type] << " ";
        }
        cout << "|" << endl;
    }
    cout << "-----------------" << endl;
}


void TosGame::print_all_attributes() {
    string rune_type_str = "_WFGLDH?";
    string rune_race_str = "_GDHOLEM";
    string sep_str = "          ";
    cout << "rune_list:    race:         min_match:     no_first:      untouchable:   must_eliminate: " << endl;
    for (int y = 0; y < 5; y++) {
        cout << "| ";
        for (int x = 0; x < 6; x++) {
            cout << rune_type_str[rune_list[rune_indices[y][x]]->type] << " ";
        }
        cout << "| ";
        for (int x = 0; x < 6; x++) {
            cout << rune_race_str[rune_list[rune_indices[y][x]]->race] << " ";
        }
        cout << "| ";
        for (int x = 0; x < 6; x++) {
            cout << rune_list[rune_indices[y][x]]->min_match << " ";
        }
        cout << " | ";
        for (int x = 0; x < 6; x++) {
            cout << rune_list[rune_indices[y][x]]->no_first << " ";
        }
        cout << " | ";
        for (int x = 0; x < 6; x++) {
            cout << rune_list[rune_indices[y][x]]->untouchable << " ";
        }
        cout << " | ";
        for (int x = 0; x < 6; x++) {
            cout << rune_list[rune_indices[y][x]]->must_eliminate << " ";
        }
        cout << " |" << endl;
    }
        
}



