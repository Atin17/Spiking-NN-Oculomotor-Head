//
// Created by praveen on 11/1/16.
//

#ifndef ROBOT_CONTROL_CAMERATHREAD_H
#define ROBOT_CONTROL_CAMERATHREAD_H

#include "opencv2/opencv.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <iostream>
#include <unistd.h>
#include <chrono>
#include <time.h>

#include "../camera/camera.h"
#include "../thread/thread.h"
#include "../workqueue/workqueue.h"

using namespace std;
using namespace cv;

class CameraThread : public Thread
{
    WorkQueue<Mat>& m_queue;
    Camera cam;
    int tmp, deviceNum;
    struct timespec pause = {0};
    Mat prevFrame;

public:
    CameraThread(WorkQueue<Mat>& queue, int device = 0, string video_out = "") : m_queue(queue), cam(device, video_out) {
	    pause.tv_sec = 0;
	    pause.tv_nsec = 30 * 1000000L;
    }

    void *run() {
        // cvNamedWindow("Live Feed");
        while(true) {
            Mat frame = cam.getNextFrame();
            if(frame.rows == 0 || frame.cols == 0) {
                cout << "Error: No frame to read";
            }
            // imshow("Live Feed", frame);

            if(m_suspended == 0) {
                m_queue.add(frame);
                prevFrame = frame;
                tmp++;
            }

            // if(waitKey(10) >= 0) {
            //     cam.release();
            //     break;
            // }
        }
        return 0;
    }

    ~CameraThread() {
        cam.release();
    }

    Mat getFrame() {
        return prevFrame;
    }
};

#endif //ROBOT_CONTROL_CAMERATHREAD_H
