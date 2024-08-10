# Tos Auto Play
Welcome to Tos Auto Play! This tool is designed to automate gameplay on your device or simulator. Please follow the steps below to set it up according to your device's specifications. This project is currently under construction, and contributions to improve algorithms, routing, and scoring calculations are highly welcomed.

## Step 1. Configure Screen Dimensions
Modify the `screen_width` and `screen_height` variables in `config.ini` to match your device's screen dimensions.
Then, assign the position of the top-left corner of the board to the variables `lefttop_x` and `lefttop_y`.

## Step 2: Compile the C++ Code
Compile the C++ code in the `c++` directory by running `compile.bat` in directory `c++`, which will generate the `c++/get_route.exe` file. (Or you can compile it manually by yourself.)

## Step 3: Install ADB and Required Libraries
* Install ADB on your computer by following the instructions on the [Android Developer website](https://developer.android.com/studio/command-line/adb).
* Install the required libraries by running the following command:
```bash
pip install -r requirements.txt
```

## Final Step: Run and Enjoy!
Run `auto_play.py` to start automating gameplay. Have fun!\
And this project can also be called as a library, like:
```python
import sys
sys.path.append('path/to/tos_auto_play')

from main.play_once import GamePlayer

if __name__ == "__main__":
    game_player = GamePlayer(complexity="Mid", read_effect=False)
    game_player.play_once()
```

## Contribution
This project is a work in progress, and contributions are greatly appreciated. Feel free to improve upon the algorithm, routing techniques, and score calculations to better suit your needs. If you have suggestions or improvements, please submit a pull request or open an issue.

## Note
This guide assumes a basic understanding of Python and ADB. If you're unfamiliar with these tools, we recommend looking up additional resources for guidance.