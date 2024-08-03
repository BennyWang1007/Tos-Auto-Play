# Tos Auto Play
Welcome to Tos Auto Play! This tool is designed to automate gameplay on your device or simulator. Please follow the steps below to set it up according to your device's specifications. This project is currently under construction, and contributions to improve algorithms, routing, and scoring calculations are highly welcomed.

## Step 1. Configure Screen Dimensions
Modify the `screen_width` and `screen_height` variables in `config.ini` to match your device's screen dimensions.
Then, assign the position of the top-left corner of the board to the variables `lefttop_x` and `lefttop_y`.

## Step 2: Adjust Event Constants
Depending on your device, you may need to test and adjust the constants for the send event functions in `util/events.py` to ensure proper functionality.

## Step 3: Compile the C++ Code
Compile the C++ code in the `c++` directory by running `compile.bat` in directory `c++`, which will generate the `c++/get_route.exe` file.

## Final Step: Run and Enjoy!
Once you have completed the setup, run `auto_play.py` to start automating gameplay. Have fun!

## Contribution
This project is a work in progress, and contributions are greatly appreciated. Feel free to improve upon the algorithm, routing techniques, and score calculations to better suit your needs. If you have suggestions or improvements, please submit a pull request or open an issue.

## Note
This guide assumes a basic understanding of Python and ADB. If you're unfamiliar with these tools, we recommend looking up additional resources for guidance.