//
// Created by praveen on 11/1/16.
//

#ifndef ROBOT_CONTROL_CAMERA_H
#define ROBOT_CONTROL_CAMERA_H

#include "opencv2/opencv.hpp"
#include <string>

using namespace std;
using namespace cv;

class Camera {
private:
    VideoCapture cam;
    string out_file;
    VideoWriter out;

public:
    static int width;
    static int height;

    Camera(const int device = 0, string video_stream_filename = "");
    Mat getNextFrame();
    void release();
};

#endif //ROBOT_CONTROL_CAMERA_H
