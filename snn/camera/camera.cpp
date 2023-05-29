//
// Created by praveen on 11/1/16.
//

#include <exception>
#include <string>

#include "opencv2/opencv.hpp"
#include "camera.h"
#include "../constants.h"

using namespace cv;
using namespace std;

Camera::Camera(const int device, string video_stream_filename) {
    cam = VideoCapture(device);
    int fourcc = CV_FOURCC('M','J','P','G');
    //if(Constants::instance()->saveVideo)
        //out.open(video_stream_filename, fourcc, 30, Size(width, height), true);
}

Mat Camera::getNextFrame() {//may implement our own
    if(!cam.isOpened())
        throw -1;
    Mat frame;
    Mat gray;
    cam >> frame;//Probably where matrix will come in
    Mat bgr[3];
    split(frame, bgr);
    // cvtColor(frame, gray, COLOR_RGB2GRAY, 1);
    //red channel
    resize(bgr[2], gray, Size(width, height));

    //if(Constants::instance()->saveVideo) {
       // resize(frame, frame, Size(width, height));
       // out << frame;
    //}
    return gray;
}

void Camera::release() {
    cam.release();
}
