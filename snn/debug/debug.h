#ifndef ROBOT_CONTROL_DEBUG_H
#define ROBOT_CONTROL_DEBUG_H

#include <iostream>

using namespace std;

#define DEBUG_VERBOSE 0
#define DEBUG_INFO 1
#define DEBUG_WARN 2
#define DEBUG_ERROR 3

class Debug {
public:
	static int debug_level;
	static void log(string msg, int level) {
		if(level >= debug_level)
			cout << msg << endl;
	};
};

#endif