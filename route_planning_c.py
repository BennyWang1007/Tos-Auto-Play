import subprocess
from TosGame import TosGame
from read_board import *
from effect.read_effect import *
from route_planning import *

def route_planning_c(game: TosGame, iter: int, max_first_depth: int, max_depth: int, debug: bool) -> list[tuple[int, int]]:

    rune_str = game.rune_str()
    race_str = game.race_str()
    min_match_str = game.min_match_str()
    must_remove_str = game.must_remove_str()
    setting_str = game.setting_str()

    command = [
        "get_route.exe", '-i', str(iter), '-f', str(max_first_depth), '-d', str(max_depth),
        '-rune', rune_str,'-race', race_str, '-min_match', min_match_str,
        '-must', must_remove_str, '-setting', setting_str
    ]
    # print(f"{command=}\n")
    # Execute the command and capture the output
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check if the command was executed successfully
    if result.returncode == 0:
        # print("C++ program executed successfully")
        # print('stdout:\n', result.stdout)
        final_route_str = result.stdout
        final_route_str = final_route_str.replace("(", "").replace(")", "").replace("\n", "")
        final_route_list = final_route_str.split(", ")
        final_route = [(int(final_route_list[i]), int(final_route_list[i + 1])) for i in range(0, len(final_route_list), 2)]
        return final_route
    else:
        # If there was an error, print the error message from stderr
        print("Error executing the C++ program:")
        print(result.stderr)
        return []


if __name__ == "__main__":

    iter = 30
    max_first_depth = 6
    max_depth = 7

    test_path = 'screenshots/Screenshot_20240323-012256.png'
    game = read_board(None, test_path)

    final_route = route_planning_c(game, iter, max_first_depth, max_depth, False)
    print(f"{final_route=}")
    indices = get_indices_from_route(final_route)
    print_two_board(game.board, None, indices)

    c, eli = eliminate_once_with_indices(game.board, indices, True)
    print(f"combo: {c}, elimminated: {eli}")
    print_two_board(game.board, None, indices)
