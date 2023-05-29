#ifndef ROBOT_CONTROL_BRAIN_H
#define ROBOT_CONTROL_BRAIN_H

#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <fstream>
#include <cmath>
#include <deque>
#include <chrono>

#include "opencv2/opencv.hpp"

#include "../debug/debug.h"

#include "../eye/receptive_field.h"

#include "colliculus_neuron.h"
#include "log_neuron_1.h"
#include "../izhikevich_neuron/izhikevich.h"
#include "../lif_neuron/lif_neuron.h"
#include "../pons/reward_neuron.h"
#include "../pons/llbn.h"
#include "../pons/ebn.h"
#include "../pons/ibn.h"
#include "../pons/ifn.h"
#include "../pons/opn.h"
#include "../pons/tonic_neuron.h"
#include "../pons/motor_neuron.h"
#include "../pons/selective_neuron.h"
#include "../thresh_neuron/thresh_neuron.h"
#include "../sum_neuron/sum_neuron.h"
#include "../arbotix_pc_serial/position.h"
#include "../arbotix_pc_serial/arbotix_control.h"

#include "../constants.h"

#define _USE_MATH_DEFINES

using namespace std;
using namespace cv;

int threshold_value = 230;
threshold_value = 171.28378378378378;
// Equivalent of say - Superior colliculus
class NewBrain {
private:
	bool coordinated_run;
	WorkQueue<Mat> &frameQueue_Left;
	WorkQueue<Mat> &frameQueue_Right;

	// Assuming only horizontal movement to start with
	vector<ColliculusNeuron> sc_neurons_Left;
	vector<ColliculusNeuron> sc_neurons_Right;

	json inverseJson;

	int frame_count = 0;

	// status file
	fstream stat_file;
	bool at_start = true;

	// position outputs
	ofstream pos_out_left, pos_out_right, pos_out_neck;

	string folderName = Constants::instance()->outputDir;

	OPN opn;

	RewardNeuron rew_ll, rew_lr, rew_rl, rew_rr;

	//Horizontal conjugate movements
	LLBN llbn_Left;
	EBN ebn_Left;
	IBN ibn_Left;
	IFN ifn_Left;

	LLBN llbn_Right;
	EBN ebn_Right;
	IBN ibn_Right;
	IFN ifn_Right;

	TonicNeuron tn_Left;
	TonicNeuron tn_Right;

	//Horizontal vergence movements
	LLBN llbn_LR;
	EBN ebn_LR;
	IFN ifn_LR;

	LLBN llbn_RL;
	EBN ebn_RL;
	IFN ifn_RL;

	TonicNeuron tn_LR;
	TonicNeuron tn_RL;

	//Vertical Movement
	LLBN llbn_U;
	EBN ebn_U;
	IFN ifn_U;
	TonicNeuron tn_U;

	LLBN llbn_D;
	EBN ebn_D;
	IFN ifn_D;
	TonicNeuron tn_D;

	//Horizontal motor neurons
	//Selection path based
	SelectiveNeuron
		s1_r_mn_LR, s1_r_mn_RR,
		s2_r_mn_LR, s2_r_mn_RR,
		s3_r_mn_LR, s3_r_mn_RR,
		s4_r_mn_LR, s4_r_mn_RR,
		r_mn_LR, r_mn_RR;

	SelectiveNeuron
		s1_l_mn_RL, s1_l_mn_LL,
		s2_l_mn_RL, s2_l_mn_LL,
		s3_l_mn_RL, s3_l_mn_LL,
		s4_l_mn_RL, s4_l_mn_LL,
		l_mn_RL, l_mn_LL;

	SumNeuron mn_LR, mn_RL, mn_LL, mn_RR;

	//Vertical motor neurons
	//Innervates with superior and inferior rectus muscles
	MotorNeuron mn_U, mn_D;

	//Neck motor neurons
	LeakyIntegrateFireNeuron mn_NL, mn_NR, mn_NU, mn_ND;

	ExcitableIzhikevichNeuron neck_mn_u, neck_mn_d, neck_mn_l, neck_mn_r;

	// Selectivity Neurons - Horizontal movement
	ThreshNeuron s1_r, s2_r, s3_r, s4_r;
	ThreshNeuron s1_l, s2_l, s3_l, s4_l;


	// Speed control
	LogNeuron1 sn1_ll, sn1_lr, sn1_rl, sn1_rr, sn1_u, sn1_d;
	LogNeuron2 sn2_ll, sn2_lr, sn2_rl, sn2_rr, sn2_u, sn2_d;
	LogNeuron3 sn3_ll, sn3_lr, sn3_rl, sn3_rr, sn3_u, sn3_d;
	LogNeuron4 sn4_ll, sn4_lr, sn4_rl, sn4_rr, sn4_u, sn4_d;
	LogNeuron5 sn5_ll, sn5_lr, sn5_rl, sn5_rr, sn5_u, sn5_d;

	ArbotixControl *control;

	Position *leftEyePosition, *rightEyePosition, *neckPosition;

	deque<double> neck_left_inputs, neck_right_inputs;

	// VideoWriter left_video, right_video;

	// eye = {0, 1} = {left, right}
	void computeColliculusInput(vector<double> &colliculusInput, double x, double y, int eye) {
		// Instead of having a center min weight based approach
		// Use min
		// Vertical Movement
		double max_w = log(1 + 360.0/288.0);

		if (x > 360) { //Down
			double w = log(1 + (x - 360.0)/288.0) / max_w;
			colliculusInput[0] += w;
		}
		if (x < 360) { //Up
			double w = log(1 + (360.0 - x)/288.0) / max_w;
			colliculusInput[1] += w;
		}
		// Horizontal Movement
		if (y < 360) { //Left
			double w = log(1 + (360.0 - y)/288.0) / max_w;
			colliculusInput[2] += w;
			if(eye == 1) {
				//right eye
				double val = log(1 + (y)/288.0) / max_w;
				colliculusInput[4] += val;
			}
		}
		if (y > 360) { //Right
			double w = log(1 + (y - 360.0)/288.0) / max_w;
			colliculusInput[3] += w;
			if(eye == 0) {
				//left eye
				double val = log(1 + (720 - y)/288.0) / max_w;
				colliculusInput[4] += val;
			}
		}
	}

public:
	NewBrain(WorkQueue<Mat> &frameQueue_L, WorkQueue<Mat> &frameQueue_R) :
				frameQueue_Left(frameQueue_L), frameQueue_Right(frameQueue_R),
				//Horizontal
				llbn_Left("llbn_l", &ifn_Left), ebn_Left("ebn_l", &llbn_Left, &opn, &ibn_Right),
				ibn_Left("ibn_l", &ebn_Left, &opn, &ibn_Right), ifn_Left("ifn_l", &ebn_Left, &ibn_Right),
				llbn_Right("llbn_r", &ifn_Right), ebn_Right("ebn_r", &llbn_Right, &opn, &ibn_Left),
				ibn_Right("ibn_r", &ebn_Right, &opn, &ibn_Left), ifn_Right("ifn_r", &ebn_Right, &ibn_Left),
				opn("opn", &ibn_Left, &ibn_Right),
				tn_Left("tn_l", &ebn_Left, &ibn_Right), tn_Right("tn_r", &ebn_Right, &ibn_Left),
				//Vergence
				llbn_LR("llbn_lr", &ifn_LR), llbn_RL("llbn_rl", &ifn_RL),
				ebn_LR("ebn_lr", &llbn_LR), ebn_RL("ebn_rl", &llbn_RL),
				ifn_LR("ifn_lr", &ebn_LR), ifn_RL("ifn_rl", &ebn_RL),
				tn_LR("tn_lr", &ebn_LR, &ibn_Left), tn_RL("tn_rl", &ebn_RL, &ibn_Right),
				//Vertical
				llbn_U("llbn_u", &ifn_U), llbn_D("llbn_d", &ifn_D),
				ebn_U("ebn_u", &llbn_U), ebn_D("ebn_d", &llbn_D),
				ifn_U("ifn_u", &ebn_U), ifn_D("ifn_d", &ebn_D),
				tn_U("tn_u", &ebn_U), tn_D("tn_d", &ebn_D),
				mn_U("mn_u", &tn_U), mn_D("mn_d", &tn_D),
				//Neck - Horizontal
				mn_NL("mn_nl"), mn_NR("mn_nr"),
				mn_NU("mn_nu"), mn_ND("mn_nd"),
				//Selectivity Neurons - Eyes horizontal
				s1_r("s1_r", 30, 3), s2_r("s2_r", 30, 2), s3_r("s3_r", 30, 1), s4_r("s4_r", 30, 1),
				s1_l("s1_l", 30, 3), s2_l("s2_l", 30, 2), s3_l("s3_l", 30, 1), s4_l("s4_l", 30, 1),
				//Selectivity based motor neurons
				s1_r_mn_LR("s1_r_mn_lr", &ibn_Left, &tn_Right, 0, &tn_LR, 0.8), s1_r_mn_RR("s1_r_mn_rr", &ibn_Left, &tn_Right, 0, &tn_LR, 0),
				s2_r_mn_LR("s2_r_mn_lr", &ibn_Left, &tn_Right, 0, &tn_LR, 1.3, &tn_RL, 2.0), s2_r_mn_RR("s2_r_mn_rr", &ibn_Left, &tn_Right, 0, &tn_LR, 0),
				s3_r_mn_LR("s3_r_mn_lr", &ibn_Left, &tn_Right, 0, &tn_LR, 0.8), s3_r_mn_RR("s3_r_mn_rr", &ibn_Left, &tn_Right, 0, &tn_LR, 3.0),
				s4_r_mn_LR("s4_r_mn_lr", &ibn_Left, &tn_Right, 1.5, &tn_LR, 0), s4_r_mn_RR("s4_r_mn_rr", &ibn_Left, &tn_Right, 1.0, &tn_LR, 0),
				r_mn_LR("r_mn_lr", &ibn_Left, &tn_Right, 0, &tn_LR, 1.5), r_mn_RR("r_mn_rr", &ibn_Left, &tn_Right, 1.5, &tn_LR, 0),
				s1_l_mn_RL("s1_l_mn_rl", &ibn_Right, &tn_Left, 0, &tn_RL, 0.8), s1_l_mn_LL("s1_l_mn_ll", &ibn_Right, &tn_Left, 0, &tn_RL, 0),
				s2_l_mn_RL("s2_l_mn_rl", &ibn_Right, &tn_Left, 0, &tn_RL, 1.3, &tn_LR, 2.0), s2_l_mn_LL("s2_l_mn_ll", &ibn_Right, &tn_Left, 0, &tn_RL, 0),
				s3_l_mn_RL("s3_l_mn_rl", &ibn_Right, &tn_Left, 0, &tn_RL, 0.8), s3_l_mn_LL("s3_l_mn_ll", &ibn_Right, &tn_Left, 0, &tn_RL, 3.0),
				s4_l_mn_RL("s4_l_mn_rl", &ibn_Right, &tn_Left, 1.5, &tn_RL, 0), s4_l_mn_LL("s4_l_mn_ll", &ibn_Right, &tn_Left, 1.0, &tn_RL, 0),
				l_mn_RL("l_mn_rl", &ibn_Right, &tn_Left, 0, &tn_RL, 1.5), l_mn_LL("l_mn_ll", &ibn_Right, &tn_Left, 1.5, &tn_RL, 0),
				mn_LL("mn_ll"), mn_LR("mn_lr"), mn_RL("mn_rl"), mn_RR("mn_rr"),
				neck_mn_u("n_mn_u"), neck_mn_d("neck_mn_d"), neck_mn_l("neck_mn_l"), neck_mn_r("neck_mn_r"),
				// learning / reward neurons
				rew_ll("rew_ll", &llbn_Left, &ebn_Left), rew_lr("rew_lr", &llbn_LR, &ebn_LR),
				rew_rl("rew_rl", &llbn_RL, &ebn_RL), rew_rr("rew_rr", &llbn_Right, &ebn_Right),
				//speed - ll
				sn5_ll("sn5_ll", &sn1_ll, &sn2_ll, &sn3_ll, &sn4_ll), sn4_ll("sn4_ll", &sn1_ll, &sn2_ll, &sn3_ll), sn3_ll("sn3_ll", &sn1_ll, &sn2_ll),
				sn2_ll("sn2_ll", &sn1_ll), sn1_ll("sn1_ll"),
				//speed - lr
				sn5_lr("sn5_lr", &sn1_lr, &sn2_lr, &sn3_lr, &sn4_lr), sn4_lr("sn4_lr", &sn1_lr, &sn2_lr, &sn3_lr), sn3_lr("sn3_lr", &sn1_lr, &sn2_lr),
				sn2_lr("sn2_lr", &sn1_lr), sn1_lr("sn1_lr"),
				//speed - rl
				sn5_rl("sn5_rl", &sn1_rl, &sn2_rl, &sn3_rl, &sn4_rl), sn4_rl("sn4_rl", &sn1_rl, &sn2_rl, &sn3_rl), sn3_rl("sn3_rl", &sn1_rl, &sn2_rl),
				sn2_rl("sn2_rl", &sn1_rl), sn1_rl("sn1_rl"),
				//speed - rr
				sn5_rr("sn5_rr", &sn1_rr, &sn2_rr, &sn3_rr, &sn4_rr), sn4_rr("sn4_rr", &sn1_rr, &sn2_rr, &sn3_rr), sn3_rr("sn3_rr", &sn1_rr, &sn2_rr),
				sn2_rr("sn2_rr", &sn1_rr), sn1_rr("sn1_rr"),
				//speed - u
				sn5_u("sn5_u", &sn1_u, &sn2_u, &sn3_u, &sn4_u), sn4_u("sn4_u", &sn1_u, &sn2_u, &sn3_u), sn3_u("sn3_u", &sn1_u, &sn2_u),
				sn2_u("sn2_u", &sn1_u), sn1_u("sn1_u"),
				//speed - d
				sn5_d("sn5_d", &sn1_d, &sn2_d, &sn3_d, &sn4_d), sn4_d("sn4_d", &sn1_d, &sn2_d, &sn3_d), sn3_d("sn3_d", &sn1_d, &sn2_d),
				sn2_d("sn2_d", &sn1_d), sn1_d("sn1_d")
				{
		sc_neurons_Left = readFrontalReceptiveField(0);
		sc_neurons_Right = readFrontalReceptiveField(1);

		inverseJson = readInverseReceptiveField();

		cout << "All neuron connections established" << endl;

		leftEyePosition = new Position(1);
		rightEyePosition = new Position(2);
		neckPosition = new Position(3);

		pos_out_left.open(Constants::instance()->outputDir + "pos_out_left", ios::out);
		pos_out_right.open(Constants::instance()->outputDir + "pos_out_right", ios::out);
		pos_out_neck.open(Constants::instance()->outputDir + "pos_out_neck", ios::out);

    	//Status file
    	stat_file.open("/tmp/robot_status", ios::in | ios::out);

		coordinated_run = Constants::instance()->coordinated_run;
	}

	int frame_num = 0;

	void run() {
		cvNamedWindow("Left Eye");
		cvNamedWindow("Right Eye");
		double minPixelValue, maxPixelValue;
		Point minPixelLocation, maxPixelLocation_Left, maxPixelLocation_Right;
		char maxLocation_Left[8], maxLocation_Right[8];
		vector<int> neuronsWithFieldAtPixel_Left, neuronsWithFieldAtPixel_Right;
		int activeBipolars;

		while(true) {
			int leftQueueLength = frameQueue_Left.size(), rightQueueLength = frameQueue_Right.size();
			if(leftQueueLength == 0 || rightQueueLength == 0)
				continue;

			frame_count++;

			//Read frame from both eyes simultaneously
			Mat frame_Left = frameQueue_Left.remove_last();
			Mat frame_Right = frameQueue_Right.remove_last();

			//Invalid frame from one of the eyes
			if(frame_Left.rows == 0 || frame_Right.rows == 0 || frame_Left.cols == 0 || frame_Right.cols == 0)
				throw -1;

			threshold(frame_Left, frame_Left, threshold_value, 255, 0);
			threshold(frame_Right, frame_Right, threshold_value, 255, 0);

			imshow("Left Eye", frame_Left);
			imshow("Right Eye", frame_Right);

			if(waitKey(3) == 27)
			{
				cout << "esc key is pressed by user" << endl;
				break;
			}

			frame_num++;

			if(frame_count <= 30)
			{
				process(0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);//probably done while waiting to process the beginning
				continue;
			}

			vector<double> colliculusInput_Left = {0.0, 0.0, 0.0, 0.0, 0.0};
			vector<double> colliculusInput_Right = {0.0, 0.0, 0.0, 0.0, 0.0};

			//Process frame
			vector<Point> locations_Left, locations_Right;

			findNonZero(frame_Left, locations_Left); //input, output
			findNonZero(frame_Right, locations_Right);

			map<int, int> input_Left, input_Right;
			char loc[8];
			int left_centers = 0, right_centers = 0;

			int left_x_center = 0, left_y_center = 0;
			int right_x_center = 0, right_y_center = 0;

			for(Point pnt : locations_Left) {
				// Convert the location to the format in JSON
				snprintf(loc, sizeof(loc), "%d,%d", pnt.x, pnt.y);
				left_x_center += pnt.x;
				left_y_center += pnt.y;
				vector<int> listOfNeurons = inverseJson[loc].get<vector<int>>();
				for(int nrnIndex : listOfNeurons) {
					if(input_Left.find(nrnIndex) == input_Left.end()) {
						input_Left.insert(pair<int, int>(nrnIndex, 1));
						left_centers += 1;
					}
					else
						input_Left[nrnIndex] += 1;
				}
			}

			for(Point pnt : locations_Right) {
				// Convert the location to the format in JSON
				snprintf(loc, sizeof(loc), "%d,%d", pnt.x, pnt.y);
				right_x_center += pnt.x;
				right_y_center += pnt.y;
				vector<int> listOfNeurons = inverseJson[loc].get<vector<int>>();
				for(int nrnIndex : listOfNeurons) {
					if(input_Right.find(nrnIndex) == input_Right.end()) {
						input_Right.insert(pair<int, int>(nrnIndex, 1));
						right_centers += 1;
					}
					else
						input_Right[nrnIndex] += 1;
				}
			}

			if(locations_Left.size() > 0) {
				left_x_center /= locations_Left.size();
				left_y_center /= locations_Left.size();
			}
			if(locations_Right.size() > 0) {
				right_x_center /= locations_Right.size();
				right_y_center /= locations_Right.size();
			}

			// Send frame through all of the higher processing centers of the brain
			// to generate colliculus to LLBN/pons inputs
			double in_l, in_r;
			double left_c = 0, right_c = 0;
			double out_Left, out_Right;
			double sc_in = 0;

			//Left-right movement
			double inp_llbn_Left_Left = 0, inp_llbn_Left_Right = 0;
			double inp_llbn_Right_Left = 0, inp_llbn_Right_Right = 0;
			double inp_from_right = 0, inp_from_left = 0;

			// Up-down movement
			double inp_llbn_Left_Up = 0, inp_llbn_Left_Down = 0;
			double inp_llbn_Right_Up = 0, inp_llbn_Right_Down = 0;

			for(int cn_index = 0; cn_index < sc_neurons_Left.size(); cn_index++) {
				sc_neurons_Left[cn_index].reset();
				sc_neurons_Right[cn_index].reset();
			}

			for(int cn_index = 0; cn_index < sc_neurons_Left.size(); cn_index++) {
				if(input_Left.find(cn_index) == input_Left.end())
					in_l = 0;
				else
					in_l = input_Left[cn_index];

				if(input_Right.find(cn_index) == input_Right.end())
					in_r = 0;
				else
					in_r = input_Right[cn_index];

				out_Left = sc_neurons_Left[cn_index].process(in_l);
				out_Right = sc_neurons_Right[cn_index].process(in_r);

				if(out_Left == 25) {
					left_c += 1;
					computeColliculusInput(colliculusInput_Left, sc_neurons_Left[cn_index].getY(), sc_neurons_Left[cn_index].getX(), 0);
					// Horizontal movement - left / right - for left eye
					inp_llbn_Left_Left = colliculusInput_Left[2];
					inp_llbn_Left_Right = colliculusInput_Left[3];
					//Vertical movement - up / down - for left eye
					inp_llbn_Left_Up = colliculusInput_Left[1];
					inp_llbn_Left_Down = colliculusInput_Left[0];
					// inp for right eye from left
					inp_from_left = colliculusInput_Left[4];

				}

				if(out_Right == 25) {
					right_c += 1;
					computeColliculusInput(colliculusInput_Right, sc_neurons_Right[cn_index].getY(), sc_neurons_Right[cn_index].getX(), 1);
					// Horizontal movement - left / right - for right eye
					inp_llbn_Right_Left = colliculusInput_Right[2];
					inp_llbn_Right_Right = colliculusInput_Right[3];
					//Vertical movement - up / down - for left eye
					inp_llbn_Right_Up = colliculusInput_Right[1];
					inp_llbn_Right_Down = colliculusInput_Right[0];
					// inp for left eye from right
					inp_from_right = colliculusInput_Right[4];
				}
			}

			if(left_c > 1) {
				inp_llbn_Left_Left /= left_c;
				inp_llbn_Left_Right /= left_c;
				inp_from_left /= left_c;
				inp_llbn_Left_Up /= left_c;
				inp_llbn_Left_Down /= left_c;
			}
			if(right_c > 1) {
				inp_llbn_Right_Right /= right_c;
				inp_llbn_Right_Left /= right_c;
				inp_from_right /= right_c;
				inp_llbn_Right_Down /= right_c;
				inp_llbn_Right_Up /= right_c;
			}

			setReward(left_x_center, right_x_center, (right_y_center + left_y_center)/2);

			//NOTE: Control transfer to midbrain
			double ver_factor = 1.2;
			double opn_sc_input = (inp_llbn_Left_Left + inp_llbn_Right_Right)/1.5;
			process(
				inp_llbn_Left_Left, //LL
				inp_llbn_Right_Right, //RR
				opn_sc_input, //OPN
				(inp_llbn_Left_Right), //LR
				(inp_llbn_Right_Left), //RL,
				inp_from_left, // Fovea_in_Left
				inp_from_right, // Fovea_in_right
				(inp_llbn_Left_Up + inp_llbn_Right_Up) / ver_factor, //Up
				(inp_llbn_Left_Down + inp_llbn_Right_Down) / ver_factor, // Down
				left_x_center, left_y_center,
				right_x_center, right_y_center
				);
		}
	}

	void setControl(ArbotixControl *arbotix_control) {
		control = arbotix_control;
	}

	void setReward(int left_x_center, int right_x_center, int vertical_center) {
		if(Constants::instance()->learning) {
			double new_reward = (-1.0 + (left_x_center <= 360) * 2.0) * (1 - (360 - left_x_center)/360.0);
			Constants::instance()->ll_reward = new_reward;
			Constants::instance()->ll_reward_avg = moving_average(Constants::instance()->ll_reward_avg, new_reward);
			Constants::instance()->ll_reward_signal = (Constants::instance()->ll_reward - Constants::instance()->ll_reward_avg);

			new_reward = (-1.0 + (left_x_center >= 360) * 2.0) * (1 - (left_x_center - 360.0)/360.0);
			Constants::instance()->lr_reward = new_reward;
			Constants::instance()->lr_reward_avg = moving_average(Constants::instance()->lr_reward_avg, new_reward);
			Constants::instance()->lr_reward_signal = (Constants::instance()->lr_reward - Constants::instance()->lr_reward_avg);

			new_reward = (-1.0 + (right_x_center <= 360) * 2.0) * (1 - (360 - right_x_center)/360.0);
			Constants::instance()->rl_reward = new_reward;
			Constants::instance()->rl_reward_avg = moving_average(Constants::instance()->rl_reward_avg, new_reward);
			Constants::instance()->rl_reward_signal = (Constants::instance()->rl_reward - Constants::instance()->rl_reward_avg);

			new_reward = (-1.0 + (right_x_center >= 360) * 2.0) * (1 - (right_x_center - 360.0)/360.0);
			Constants::instance()->rr_reward = new_reward;
			Constants::instance()->rr_reward_avg = moving_average(Constants::instance()->rr_reward_avg, new_reward);
			Constants::instance()->rr_reward_signal = (Constants::instance()->rr_reward - Constants::instance()->rr_reward_avg);

			new_reward = (-1.0 + (vertical_center <= 360) * 2.0) * (1 - (360 - vertical_center)/360.0);
			Constants::instance()->u_reward = new_reward;
			Constants::instance()->u_reward_avg = moving_average(Constants::instance()->u_reward_avg, new_reward);
			Constants::instance()->u_reward_signal = (Constants::instance()->u_reward - Constants::instance()->u_reward_avg);

			new_reward = (-1.0 + (vertical_center >= 360) * 2.0) * (1 - (vertical_center - vertical_center)/360.0);
			Constants::instance()->d_reward = new_reward;
			Constants::instance()->d_reward_avg = moving_average(Constants::instance()->d_reward_avg, new_reward);
			Constants::instance()->d_reward_signal = (Constants::instance()->d_reward - Constants::instance()->d_reward_avg);
		}
	}

	void setReward_sc_input_based(double ll_in, double lr_in, double rl_in, double rr_in, double u_in, double d_in) {
		// set reward values
		if(Constants::instance()->learning) {
			double new_reward = (ll_in - lr_in);
			Constants::instance()->ll_reward = new_reward;
			Constants::instance()->ll_reward_avg = moving_average(Constants::instance()->ll_reward_avg, new_reward);
			Constants::instance()->ll_reward_signal = (Constants::instance()->ll_reward - Constants::instance()->ll_reward_avg);

			new_reward = (lr_in - ll_in);
			Constants::instance()->lr_reward = new_reward;
			Constants::instance()->lr_reward_avg = moving_average(Constants::instance()->lr_reward_avg, new_reward);
			Constants::instance()->lr_reward_signal = (Constants::instance()->lr_reward - Constants::instance()->lr_reward_avg);

			new_reward = (rl_in - rr_in);
			Constants::instance()->rl_reward = new_reward;
			Constants::instance()->rl_reward_avg = moving_average(Constants::instance()->rl_reward_avg, new_reward);
			Constants::instance()->rl_reward_signal = (Constants::instance()->rl_reward - Constants::instance()->rl_reward_avg);

			new_reward = (rr_in - rl_in);
			Constants::instance()->rr_reward = new_reward;
			Constants::instance()->rr_reward_avg = moving_average(Constants::instance()->rr_reward_avg, new_reward);
			Constants::instance()->rr_reward_signal = (Constants::instance()->rr_reward - Constants::instance()->rr_reward_avg);

			new_reward = (u_in - d_in);
			Constants::instance()->u_reward = new_reward;
			Constants::instance()->u_reward_avg = moving_average(Constants::instance()->u_reward_avg, new_reward);
			Constants::instance()->u_reward_signal = (Constants::instance()->u_reward - Constants::instance()->u_reward_avg);

			new_reward = (d_in - u_in);
			Constants::instance()->d_reward = new_reward;
			Constants::instance()->d_reward_avg = moving_average(Constants::instance()->d_reward_avg, new_reward);
			Constants::instance()->d_reward_signal = (Constants::instance()->d_reward - Constants::instance()->d_reward_avg);
		}
	}

	// Inputs from higher centers / superior colliculus
	// Currently handles only - horizontal movement of the eyes
	void process(
		double sc_left_in, double sc_right_in,
		double sc_weak_in,
		double sc_LR, double sc_RL,
		double fovea_in_l, double fovea_in_r,
		double sc_U, double sc_D,
		int left_x_center, int left_y_center, // Only for outputs
		int right_x_center, int right_y_center) {

		// learning - set reward - based on sc input
		// setReward(sc_left_in, sc_LR, sc_RL, sc_right_in, sc_U, sc_D);
		
		double out_mn_u, out_mn_d;
		double out_mn_nl, out_mn_nr;

		double out_tn_ll, out_tn_rl, out_tn_lr, out_tn_rr;

		int left_LR = 0, right_RL = 0, left_LL = 0, right_RR = 0; // Horizontal movement only
		int max_left_LR = 0, max_left_LL = 0, max_right_RL = 0, max_right_RR = 0;
		int out_mn_LR = 0, out_mn_RL = 0, out_mn_LL = 0, out_mn_RR = 0;
		int up = 0, down = 0; // Vertical movement only
		int neck_l = 0, neck_r = 0; // Horizontal - neck movement only
		int neck_u = 0, neck_d = 0; // Vertical - neck movement only

		deque<double> mem_tn_ll, mem_tn_lr, mem_tn_rl, mem_tn_rr;
		double sum_tn_ll = 0, sum_tn_lr = 0, sum_tn_rl = 0, sum_tn_rr = 0;

		double out_s1_r, out_s2_r, out_s3_r, out_s4_r;
		double out_s1_l, out_s2_l, out_s3_l, out_s4_l;

		int s1_r_c = 0, s2_r_c = 0, s3_r_c = 0, s4_r_c = 0;
		int s1_l_c = 0, s2_l_c = 0, s3_l_c = 0, s4_l_c = 0;

		int count_tn_l = 0, count_tn_r = 0, count_tn_lr = 0, count_tn_rl = 0;

		int sp_count_ll = 0, sp_count_lr = 0, sp_count_rl = 0, sp_count_rr = 0;
		int sp_count_u = 0, sp_count_d = 0;

		mn_NU.reset(); mn_ND.reset();
		mn_NL.reset(); mn_NR.reset();

		// reset speed neurons
		sn1_ll.reset();
		sn2_ll.reset();
		sn3_ll.reset();
		sn4_ll.reset();
		sn5_ll.reset();

		sn1_lr.reset();
		sn2_lr.reset();
		sn3_lr.reset();
		sn4_lr.reset();
		sn5_lr.reset();

		sn1_rl.reset();
		sn2_rl.reset();
		sn3_rl.reset();
		sn4_rl.reset();
		sn5_rl.reset();

		sn1_rr.reset();
		sn2_rr.reset();
		sn3_rr.reset();
		sn4_rr.reset();
		sn5_rr.reset();

		sn1_u.reset();
		sn2_u.reset();
		sn3_u.reset();
		sn4_u.reset();
		sn5_u.reset();

		sn1_d.reset();
		sn2_d.reset();
		sn3_d.reset();
		sn4_d.reset();
		sn5_d.reset();

		for(int i = 0; i < Constants::instance()->window_size; i++) {
			//Horizontal
			llbn_Left.process(sc_left_in, Constants::instance()->ll_reward_signal);
			llbn_Right.process(sc_right_in, Constants::instance()->rr_reward_signal);
			llbn_LR.process(sc_LR, Constants::instance()->lr_reward_signal);
			llbn_RL.process(sc_RL, Constants::instance()->rl_reward_signal);

			ebn_Left.process(sc_left_in, Constants::instance()->ll_reward_signal);
			ebn_Right.process(sc_right_in, Constants::instance()->rr_reward_signal);
			ebn_LR.process(sc_LR, Constants::instance()->lr_reward_signal);
			ebn_RL.process(sc_RL, Constants::instance()->rl_reward_signal);

			rew_ll.process(sc_left_in);
			rew_lr.process(sc_LR);
			rew_rl.process(sc_RL);
			rew_rr.process(sc_right_in);

			ibn_Left.process(sc_left_in, Constants::instance()->ll_reward_signal);
			ibn_Right.process(sc_right_in, Constants::instance()->rr_reward_signal);

			ifn_Left.process(0, Constants::instance()->ll_reward_signal);
			ifn_Right.process(0, Constants::instance()->rr_reward_signal);
			ifn_LR.process(0, Constants::instance()->lr_reward_signal);
			ifn_RL.process(0, Constants::instance()->rl_reward_signal);

			opn.process(sc_weak_in, (
				Constants::instance()->ll_reward_signal + Constants::instance()->lr_reward_signal +
				Constants::instance()->rl_reward_signal + Constants::instance()->rr_reward_signal) / 4.0);

			out_tn_ll = tn_Left.process(0, Constants::instance()->ll_reward_signal);
			mem_tn_ll.push_back(out_tn_ll == 25);
			sum_tn_ll += (out_tn_ll == 25);
			count_tn_l += (out_tn_ll == 25);
			if(mem_tn_ll.size() > 10) {
				sum_tn_ll -= mem_tn_ll.front();
				mem_tn_ll.pop_front();
			}

			out_tn_rr = tn_Right.process(0, Constants::instance()->rr_reward_signal);
			mem_tn_rr.push_back(out_tn_rr == 25);
			sum_tn_rr += (out_tn_rr == 25);
			count_tn_r += (out_tn_rr == 25);
			if(mem_tn_rr.size() > 10) {
				sum_tn_rr -= mem_tn_rr.front();
				mem_tn_rr.pop_front();
			}

			out_tn_lr = tn_LR.process(0, Constants::instance()->lr_reward_signal);
			mem_tn_lr.push_back(out_tn_lr == 25);
			sum_tn_lr += (out_tn_lr == 25);
			count_tn_lr += (out_tn_lr == 25);
			if(mem_tn_lr.size() > 10) {
				sum_tn_lr -= mem_tn_lr.front();
				mem_tn_lr.pop_front();
			}

			out_tn_rl = tn_RL.process(0, Constants::instance()->rl_reward_signal);
			mem_tn_rl.push_back(out_tn_rl == 25);
			sum_tn_rl += (out_tn_rl == 25);
			count_tn_rl += (out_tn_rl == 25);
			if(mem_tn_rl.size() > 10) {
				sum_tn_rl -= mem_tn_rl.front();
				mem_tn_rl.pop_front();
			}

			//Eyes - right side - direction selection
			out_s1_r = s1_r.process((out_tn_lr == 25) - sum_tn_rr * 10 - s4_r.out_3 * 20);
			out_s1_r = (out_s1_r == 25);
			s1_r_c += out_s1_r;
			out_s2_r = s2_r.process((out_tn_lr == 25) - sum_tn_rr * 10 - s1_r.out_3 * 10 - s4_r.out_3 * 20);
			out_s2_r = (out_s2_r == 25);
			s2_r_c += out_s2_r;
			out_s3_r = s3_r.process((out_tn_lr == 25) - sum_tn_rr * 10 - s1_r.out_3 * 10 - s2_r.out_3 * 10 - s4_r.out_3 * 20);
			out_s3_r = (out_s3_r == 25);
			s3_r_c += out_s3_r;
			out_s4_r = s4_r.process((out_tn_rr == 25) - sum_tn_lr * 10);
			out_s4_r = (out_s4_r == 25);
			s4_r_c += out_s4_r;

			left_LR += s1_r_mn_LR.process((out_s2_r + out_s3_r + out_s4_r) * (-100.0), Constants::instance()->lr_reward_signal) == 25;
			right_RR += s1_r_mn_RR.process((out_s2_r + out_s3_r + out_s4_r) * (-100.0), Constants::instance()->rr_reward_signal) == 25;

			left_LR += s2_r_mn_LR.process((out_s1_r + out_s3_r + out_s4_r) * (-100.0), Constants::instance()->lr_reward_signal) == 25;
			right_RR += s2_r_mn_RR.process((out_s1_r + out_s3_r + out_s4_r) * (-100.0), Constants::instance()->rr_reward_signal) == 25;

			left_LR += s3_r_mn_LR.process((out_s2_r + out_s1_r + out_s4_r) * (-100.0), Constants::instance()->lr_reward_signal) == 25;
			right_RR += s3_r_mn_RR.process((out_s2_r + out_s1_r + out_s4_r) * (-100.0), Constants::instance()->rr_reward_signal) == 25;

			left_LR += s4_r_mn_LR.process((out_s2_r + out_s3_r + out_s1_r) * (-100.0), Constants::instance()->lr_reward_signal) == 25;
			right_RR += s4_r_mn_RR.process((out_s2_r + out_s3_r + out_s1_r) * (-100.0), Constants::instance()->rr_reward_signal) == 25;

			left_LR += r_mn_LR.process((out_s1_r + out_s2_r + out_s3_r + out_s4_r) * (-100.0), Constants::instance()->lr_reward_signal) == 25;
			right_RR += r_mn_RR.process((out_s1_r + out_s2_r + out_s3_r + out_s4_r) * (-100.0), Constants::instance()->rr_reward_signal) == 25;

			// Eyes - left side - direction selection
			out_s1_l = s1_l.process((out_tn_rl == 25) - sum_tn_ll * 10 - s4_l.out_3 * 20);
			out_s1_l = (out_s1_l == 25);
			s1_l_c += out_s1_l;
			out_s2_l = s2_l.process((out_tn_rl == 25) - sum_tn_ll * 10 - s1_l.out_3 * 10 - s4_l.out_3 * 20);
			out_s2_l = (out_s2_l == 25);
			s2_l_c += out_s2_l;
			out_s3_l = s3_l.process((out_tn_rl == 25) - sum_tn_ll * 10 - s1_l.out_3 * 10 - s2_l.out_3 * 10 - s4_l.out_3 * 20);
			out_s3_l = (out_s3_l == 25);
			s3_l_c += out_s3_l;
			out_s4_l = s4_l.process((out_tn_ll == 25) - sum_tn_rl * 10);
			out_s4_l = (out_s4_l == 25);
			s4_l_c += out_s4_l;

			right_RL += s1_l_mn_RL.process((out_s2_l + out_s3_l + out_s4_l) * (-100.0), Constants::instance()->rl_reward_signal) == 25;
			left_LL += s1_l_mn_LL.process((out_s2_l + out_s3_l + out_s4_l) * (-100.0), Constants::instance()->ll_reward_signal) == 25;

			right_RL += s2_l_mn_RL.process((out_s1_l + out_s3_l + out_s4_l) * (-100.0), Constants::instance()->rl_reward_signal) == 25;
			left_LL += s2_l_mn_LL.process((out_s1_l + out_s3_l + out_s4_l) * (-100.0), Constants::instance()->ll_reward_signal) == 25;

			right_RL += s3_l_mn_RL.process((out_s2_l + out_s1_l + out_s4_l) * (-100.0), Constants::instance()->rl_reward_signal) == 25;
			left_LL += s3_l_mn_LL.process((out_s2_l + out_s1_l + out_s4_l) * (-100.0), Constants::instance()->ll_reward_signal) == 25;

			right_RL += s4_l_mn_RL.process((out_s2_l + out_s3_l + out_s1_l) * (-100.0), Constants::instance()->rl_reward_signal) == 25;
			left_LL += s4_l_mn_LL.process((out_s2_l + out_s3_l + out_s1_l) * (-100.0), Constants::instance()->ll_reward_signal) == 25;

			right_RL += l_mn_RL.process((out_s1_l + out_s2_l + out_s3_l + out_s4_l) * (-100.0), Constants::instance()->rl_reward_signal) == 25;
			left_LL += l_mn_LL.process((out_s1_l + out_s2_l + out_s3_l + out_s4_l) * (-100.0), Constants::instance()->ll_reward_signal) == 25;

			out_mn_LL += mn_LL.process(left_LL - left_LR) == 25;
			out_mn_RR += mn_RR.process(right_RR - right_RL) == 25;
			out_mn_LR += mn_LR.process(left_LR - left_LL) == 25;
			out_mn_RL += mn_RL.process(right_RL - right_RR) == 25;

			//Vertical
			llbn_U.process(sc_U, Constants::instance()->u_reward_signal);
			llbn_D.process(sc_D, Constants::instance()->d_reward_signal);

			ebn_U.process(sc_U, Constants::instance()->u_reward_signal);
			ebn_D.process(sc_D, Constants::instance()->d_reward_signal);

			ifn_U.process(0, Constants::instance()->u_reward_signal);
			ifn_D.process(0, Constants::instance()->d_reward_signal);

			tn_U.process(0, Constants::instance()->u_reward_signal);
			tn_D.process(0, Constants::instance()->d_reward_signal);

			out_mn_u = mn_U.process(0, Constants::instance()->u_reward_signal) == 25;
			out_mn_d = mn_D.process(0, Constants::instance()->d_reward_signal) == 25;

			up += out_mn_u;
			down += out_mn_d;

			//Horizontal - Neck
			double nl_in = 0, nr_in = 0;
			nl_in = (sc_left_in * 10.0 + sc_RL * 1.5) * 10.0;
			nr_in = (sc_right_in * 10.0 + sc_LR * 1.5) * 10.0;

			//Vertical - Neck
			double nu_in = 0, nd_in = 0;
			nu_in = (sc_U) * 5.0 + out_mn_u * 5.0;
			nd_in = (sc_D) * 5.0 + out_mn_d * 5.0;

			// Write positions to output
			chrono::milliseconds ms = chrono::duration_cast<chrono::milliseconds >(chrono::system_clock::now().time_since_epoch());
			pos_out_left << ms.count() << " " << leftEyePosition->pan << " " << leftEyePosition->tilt << endl;
			pos_out_right << ms.count() << " " << rightEyePosition->pan << " " << rightEyePosition->tilt << endl;
			pos_out_neck << ms.count() << " " << neckPosition->pan << " " << neckPosition->tilt << endl;

			if(coordinated_run) {
				if(at_start) {
					cout << "At start" << endl;
					stat_file << "START" << endl;
					stat_file.flush();
					at_start = false;
				} else {
					string status;
					stat_file.seekg(0, stat_file.beg); // Go to beginning
					getline(stat_file, status);
					if(status.compare("START") != 0) {
						cout << "End?: " << status << endl;
						exit(0);
					}
				}
			}

			double out_mn_nl = mn_NL.process(nl_in);
			double out_mn_nr = mn_NR.process(nr_in);

			double out_mn_nu = mn_NU.process(nu_in);
			double out_mn_nd = mn_ND.process(nd_in);

			neck_l += neck_mn_l.process((out_mn_nl == 25) * 20.0) == 25;
			neck_r += neck_mn_r.process((out_mn_nr == 25) * 20.0) == 25;
			neck_u += neck_mn_u.process((out_mn_nu == 25) * 25.0) == 25;
			neck_d += neck_mn_d.process((out_mn_nd == 25) * 25.0) == 25;

			// speed control
			//sc_left_in, sc_right_in, sc_LR, sc_RL
			sn1_ll.process(sc_left_in);
			sn2_ll.process(sc_left_in);
			sn3_ll.process(sc_left_in);
			sn4_ll.process(sc_left_in);
			sp_count_ll += sn5_ll.process(sc_left_in) == 25;

			sn1_lr.process(sc_LR);
			sn2_lr.process(sc_LR);
			sn3_lr.process(sc_LR);
			sn4_lr.process(sc_LR);
			sp_count_lr += sn5_lr.process(sc_LR) == 25;

			sn1_rl.process(sc_RL);
			sn2_rl.process(sc_RL);
			sn3_rl.process(sc_RL);
			sn4_rl.process(sc_RL);
			sp_count_rl += sn5_rl.process(sc_RL) == 25;

			sn1_rr.process(sc_right_in);
			sn2_rr.process(sc_right_in);
			sn3_rr.process(sc_right_in);
			sn4_rr.process(sc_right_in);
			sp_count_rr += sn5_rr.process(sc_right_in) == 25;

			sn1_u.process(sc_U);
			sn2_u.process(sc_U);
			sn3_u.process(sc_U);
			sn4_u.process(sc_U);
			sp_count_u += sn5_u.process(sc_U) == 25;

			sn1_d.process(sc_D);
			sn2_d.process(sc_D);
			sn3_d.process(sc_D);
			sn4_d.process(sc_D);
			sp_count_d += sn5_d.process(sc_D) == 25;
		}

		if(!(sc_left_in == 0 && sc_right_in == 0 && sc_LR == 0 && sc_RL == 0 && sc_U == 0 && sc_D == 0)) {
			// cout << sc_left_in << " " << sc_LR << " " << sc_RL << " " << sc_right_in 
			// 	<< " gives " << sp_count_ll << " " << sp_count_lr << " " << sp_count_rl << " " << sp_count_rr << endl;
			executeMotorCommand(
				out_mn_LL, out_mn_RR, out_mn_LR, out_mn_RL, up, down, neck_l, neck_r, neck_u, neck_d,
				sp_count_ll, sp_count_lr, sp_count_rl, sp_count_rr, sp_count_u, sp_count_d);
		}
	}


	void executeMotorCommand(
		int left_LR, int right_LR, int left_MR, int right_MR, //Horizontal - muscles (lateral/medial rectus)
		int up, int down, //Vertical
		int neck_left, int neck_right, // Neck - horizontal
		int neck_up, int neck_down, // Neck -vertical
		int speed_ll, int speed_lr, int speed_rl, int speed_rr,
		int speed_u, int speed_d) {

		//Down-Up-Left-Right
		vector<int> leftEyeSpikes = {down, up, left_LR, left_MR};
		vector<int> rightEyeSpikes = {down, up, right_MR, right_LR};
		vector<int> neckSpikes {neck_down, neck_up, neck_left, neck_right};

		convertSpikesToPosition(leftEyeSpikes, leftEyePosition, speed_ll, speed_lr, speed_u, speed_d);
		convertSpikesToPosition(rightEyeSpikes, rightEyePosition, speed_rl, speed_rr, speed_u, speed_d);
		convertSpikesToNeckPosition(neckSpikes, neckPosition);
		//Neck (p,t), left (p,t), right(p,t)

		/*if(Constants::instance()->learning) {
			neckPosition->pan = 512;
			neckPosition->tilt = 512;
			neckPosition->changed = false;
		}*/
                //put back in to disable neck movement, because it currently seems that the neck cannot learn

		if(leftEyePosition->changed || rightEyePosition->changed || neckPosition->changed)
			control->move({neckPosition->pan, neckPosition->tilt, leftEyePosition->pan, leftEyePosition->tilt, rightEyePosition->pan, rightEyePosition->tilt});
	}

	void convertSpikesToNeckPosition(vector<int> oculoMotorSpikes, Position *pos) {
		double horizontalRange = 20.0;
		double verticalRange = 20.0;
		int ignore = 1; //No. of spikes to ignore as no input
		pos->changed = false;
		double maxSpikes_Hor = 25.0;
		double maxSpikes_Ver = 20.0;

		if(oculoMotorSpikes[1] > oculoMotorSpikes[0]) {
			//Move the tilt motor up
			int position = verticalRange * log(1.0 + (oculoMotorSpikes[1] - ignore) / maxSpikes_Ver) / 0.6690496289808848;
			pos->tilt += position;
			if(position > 0)
				pos->changed = true;
		} else if(oculoMotorSpikes[0] > oculoMotorSpikes[1]) {
			//Move tilt motor down
			int position = verticalRange * log(1.0 + (oculoMotorSpikes[0] - ignore) / maxSpikes_Ver) / 0.6690496289808848;
			pos->tilt -= position;
			if(position > 0)
				pos->changed = true;
		}
		if(oculoMotorSpikes[2] > oculoMotorSpikes[3]) {
			//Move pan motor left
			int position = horizontalRange * log(1.0 + (oculoMotorSpikes[2] - ignore) / maxSpikes_Hor) / 0.6690496289808848;
			pos->pan += position;
			if(position > 0)
				pos->changed = true;
		} else if(oculoMotorSpikes[3] > oculoMotorSpikes[2]) {
			//move pan motor right
			int position = horizontalRange * log(1.0 + (oculoMotorSpikes[3] - ignore) / maxSpikes_Hor) / 0.6690496289808848;
			pos->pan -= position;
			if(position > 0)
				pos->changed = true;
		}

		//Max pan / tilt positions of eye determine when the neck should move
		if(pos->pan > 512 + 110)
			pos->pan = 622;
		if(pos->pan < 512 - 110)
			pos->pan = 402;
		if(pos->tilt > 512 + 100)
			pos->tilt = 612;
		if(pos->tilt < 512 - 100)
			pos->tilt = 412;
	}

	void convertSpikesToPosition(vector<int> oculoMotorSpikes, Position *pos,
		int speed_left, int speed_right,
		int speed_up, int speed_down) {
		double horizontalRange = 2.0;
		double verticalRange = 5.0;
		int ignore = 1; //No. of spikes to ignore as no input
		pos->changed = false;
		double maxSpikes_Hor = 20.0;
		double maxSpikes_Ver = 20.0;

		if(oculoMotorSpikes[1] > oculoMotorSpikes[0]) {
			//Move the tilt motor up
			int position = verticalRange * speed_up * log(1.0 + (oculoMotorSpikes[1] - ignore) / maxSpikes_Ver) / 0.6690496289808848;
			pos->tilt -= position;
			if(position > 0)
				pos->changed = true;
		} else if(oculoMotorSpikes[0] > oculoMotorSpikes[1]) {
			//Move tilt motor down
			int position = verticalRange * speed_down * log(1.0 + (oculoMotorSpikes[0] - ignore) / maxSpikes_Ver) / 0.6690496289808848;
			pos->tilt += position;
			if(position > 0)
				pos->changed = true;
		}
		if(oculoMotorSpikes[2] > oculoMotorSpikes[3]) {
			//Move pan motor left
			int position = horizontalRange * speed_left * log(1.0 + (oculoMotorSpikes[2] - ignore) / maxSpikes_Hor) / 0.6690496289808848;
			pos->pan += position;
			if(position > 0)
				pos->changed = true;
		} else if(oculoMotorSpikes[3] > oculoMotorSpikes[2]) {
			//move pan motor right
			int position = horizontalRange * speed_right * log(1.0 + (oculoMotorSpikes[3] - ignore) / maxSpikes_Hor) / 0.6690496289808848;
			pos->pan -= position;
			if(position > 0)
				pos->changed = true;
		}

		//Max pan / tilt positions of eye determine when the neck should move
		if(pos->_type == 1) {
			if(pos->pan > 512 + pos->lateral_range)
				pos->pan = (512 + pos->lateral_range);
			if(pos->pan < 512 - pos->medial_range)
				pos->pan = (512 - pos->medial_range);
		}
		else {
			if(pos->pan > 512 + pos->medial_range)
				pos->pan = (512 + pos->medial_range);
			if(pos->pan < 512 - pos->lateral_range)
				pos->pan = (512 - pos->lateral_range);
		}

		if(pos->tilt > 512 + 60)
			pos->tilt = 512 + 60;
		if(pos->tilt < 512 - 60)
			pos->tilt = 512 - 60;
	}
};

#endif //ROBOT_CONTROL_BRAIN_H
