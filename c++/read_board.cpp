#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <tuple>
#include <unordered_map>
#include <vector>
#include <string>
#include <algorithm>
#include <iostream>

#include "include/Rune.h"

using namespace cv;

using RuneTemplate = std::vector<cv::Mat>;

// Define the type for attributes (untouchable, eliminable, must_remove)
using RuneAttribute = std::tuple<bool, bool, bool>;

// Define the type for rune attributes
using RuneAttributes = std::unordered_map<int, RuneAttribute>;

// Define the type for rune names
using RuneNames = std::vector<std::string>;

// Define the type for race templates
using RaceTemplates = std::unordered_map<std::string, cv::Mat>;

RaceTemplates race_template = {
    {"race1", cv::Mat::zeros(10, 10, CV_8UC4)},  // Example template, replace with actual templates
    {"race2", cv::Mat::zeros(10, 10, CV_8UC4)}
    // Add more race templates as needed
};

// Rune templates
std::unordered_map<std::string, RuneTemplate> rune_templates = {
    {"water", {}},   // List of templates for the water rune
    {"fire", {}},    // List of templates for the fire rune
    {"grass", {}},   // List of templates for the grass rune
    {"light", {}},   // List of templates for the light rune
    {"dark", {}},    // List of templates for the dark rune
    {"heart", {}},   // List of templates for the heart rune
    {"hidden", {}}   // List of templates for the hidden rune
    // Add more rune types as needed
};

// Rune attributes
std::unordered_map<std::string, RuneAttributes> rune_attributes = {
    {"water", {}},   // Dictionary of attributes for the water rune
    {"fire", {}},    // Dictionary of attributes for the fire rune
    {"grass", {}},   // Dictionary of attributes for the grass rune
    {"light", {}},   // Dictionary of attributes for the light rune
    {"dark", {}},    // Dictionary of attributes for the dark rune
    {"heart", {}},   // Dictionary of attributes for the heart rune
    {"hidden", {}}   // Dictionary of attributes for the hidden rune
    // Add more rune types as needed
};

// Rune names
std::unordered_map<std::string, RuneNames> rune_names = {
    {"water", {}},   // List of names for the water rune
    {"fire", {}},    // List of names for the fire rune
    {"grass", {}},   // List of names for the grass rune
    {"light", {}},   // List of names for the light rune
    {"dark", {}},    // List of names for the dark rune````
    {"heart", {}},   // List of names for the heart rune
    {"hidden", {}}   // List of names for the hidden rune
    // Add more rune types as needed
};


int typestr2int(std::string str) {
    if (str == "water") {
        return 1;
    } else if (str == "fire") {
        return 2;
    } else if (str == "grass") {
        return 3;
    } else if (str == "light") {
        return 4;
    } else if (str == "dark") {
        return 5;
    } else if (str == "heart") {
        return 6;
    } else if (str == "hidden") {
        return 7;
    } else {
        return 0;
    }
}

int racestr2int(std::string str) {
    if (str == "race1") {
        return 1;
    } else if (str == "race2") {
        return 2;
    } else {
        return 0;
    }
}

std::pair<Rune, float> match_rune(cv::Mat image, std::pair<int, int> grid, float threshold = 0.8) {
    // Convert to BGRA if not
    if (image.channels() != 4) {
        cv::cvtColor(image, image, cv::COLOR_BGR2BGRA);
    }

    int width = image.cols;
    int height = image.rows;
    const int margin = 2;

    int x = grid.first;
    int y = grid.second;

    const int RUNE_SIZE = 50;  // Assuming this value
    const int SCALE = 2;  // Assuming this value
    const int OFFSET[2] = {0, 0};  // Assuming this value
    const int OFFSET2[2] = {0, 0};  // Assuming this value
    const int RACE_OFFSET[2] = {0, 0};  // Assuming this value
    const int RACE_OFFSET2[2] = {0, 0};  // Assuming this value

    auto clamp = [](int x, int l, int r) -> int { return std::max(l, std::min(r, x)); };

    int s_x = (x * RUNE_SIZE + OFFSET[0]) / SCALE - margin;
    int s_y = (y * RUNE_SIZE + OFFSET[1]) / SCALE - margin;
    int e_x = (x * RUNE_SIZE + OFFSET2[0]) / SCALE + margin;
    int e_y = (y * RUNE_SIZE + OFFSET2[1]) / SCALE + margin;

    s_x = clamp(s_x, 0, width);
    e_x = clamp(e_x, 0, width);
    s_y = clamp(s_y, 0, height);
    e_y = clamp(e_y, 0, height);

    int race_s_x = (x * RUNE_SIZE + RACE_OFFSET[0]) / SCALE - margin;
    int race_s_y = (y * RUNE_SIZE + RACE_OFFSET[1]) / SCALE - margin;
    int race_e_x = (x * RUNE_SIZE + RACE_OFFSET2[0]) / SCALE + margin;
    int race_e_y = (y * RUNE_SIZE + RACE_OFFSET2[1]) / SCALE + margin;

    race_s_x = clamp(race_s_x, 0, width);
    race_e_x = clamp(race_e_x, 0, width);
    race_s_y = clamp(race_s_y, 0, width);
    race_e_y = clamp(race_e_y, 0, width);

    cv::Mat rune_image = image(cv::Range(s_y, e_y), cv::Range(s_x, e_x));
    cv::Mat race_image = image(cv::Range(race_s_y, race_e_y), cv::Range(race_s_x, race_e_x));

    float max_res = 0.0;
    std::string result = "None";
    std::tuple<bool, bool, bool> attr = {false, false, false};
    std::string name = "None";

    for (auto const& [rune, templates] : rune_templates) {
        for (size_t i = 0; i < templates.size(); ++i) {
            cv::Mat template_img = templates[i];
            cv::Mat res;
            cv::matchTemplate(rune_image, template_img, res, cv::TM_CCOEFF_NORMED);
            double minVal, maxVal;
            cv::Point minLoc, maxLoc;
            cv::minMaxLoc(res, &minVal, &maxVal, &minLoc, &maxLoc);
            float m_res = maxVal;
            if (m_res > max_res) {
                max_res = m_res;
                result = rune;
                attr = rune_attributes[rune][i];
                name = rune_names[rune][i];
            }
        }
    }

    if (max_res < threshold) {
        result = "unknown";
    }

    float max_race_res = 0.0;
    std::string race_str = "";

    for (auto const& [race, template_img] : race_template) {
        cv::Mat small_template;
        cv::resize(template_img, small_template, cv::Size(template_img.cols / SCALE, template_img.rows / SCALE));
        if (small_template.cols > race_image.cols) {
            small_template = small_template(cv::Range::all(), cv::Range(0, race_image.cols));
        }

        cv::Mat mask = small_template(cv::Range::all(), cv::Range::all());
        cv::Mat res;
        cv::matchTemplate(race_image, small_template, res, cv::TM_CCORR_NORMED, mask);
        double minVal, maxVal;
        cv::Point minLoc, maxLoc;
        cv::minMaxLoc(res, &minVal, &maxVal, &minLoc, &maxLoc);
        float m_res = maxVal;

        if (m_res > max_race_res && m_res > 0.85) {
            race_str = race;
            max_race_res = m_res;
        }
    }

    Rune result_rune;
    // result_rune.type = Runes::str2int(result);
    result_rune.type = typestr2int(result);
    result_rune.race = racestr2int(race_str);
    result_rune.untouchable = std::get<0>(attr);
    result_rune.must_eliminate = std::get<2>(attr);

    return std::make_pair(result_rune, max_res);
}
