# Tos Auto Play
Welcome to Tos Auto Play! This tool is designed to automate gameplay on your device or simulator. Please follow the steps below to set it up according to your device's specifications. This project is currently under construction, and contributions to improve algorithms, routing, and scoring calculations are highly welcomed.

## Step 1. Configure Screen Dimensions
Modify the `SCREEN_WIDTH` and `SCREEN_HEIGHT` variables in `constants.py` to match your device's screen dimensions.
Then, assign the position of the top-left corner of the board to the variable `LEFT_TOP`.

## Step 2. Generate Templates
Run `gen_templates.py` once after modifying the `SCREEN_WIDTH` and `SCREEN_HEIGHT` to generate the necessary templates for your device.

## Step 3. Connect Your Device
Use ADB to connect your physical device or simulator. Ensure that your device is recognized by running `adb devices` from your terminal.

## Step 4: Adjust Event Constants
Depending on your device, you may need to test and adjust the constants for the send event functions in `auto_play.py` to ensure proper functionality.

## Final Step: Run and Enjoy!
Once you have completed the setup, run `auto_play.py` to start automating gameplay. Have fun!

## Contribution
This project is a work in progress, and contributions are greatly appreciated. Feel free to improve upon the algorithm, routing techniques, and score calculations to better suit your needs. If you have suggestions or improvements, please submit a pull request or open an issue.

## Note
This guide assumes a basic understanding of Python and ADB. If you're unfamiliar with these tools, we recommend looking up additional resources for guidance.