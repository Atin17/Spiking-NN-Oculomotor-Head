/*
 * SerialReceiveMultipleFields sketch
 * This code expects a message in the format: 12,345,678
 * This code requires a newline character to indicate the end of the data
 * Set the serial monitor to send newline characters
 */

#include <ax12.h>          // ax12 servo control
#include <TextFinder.h>

TextFinder finder(Serial);

// Serial interface
#define BAUD_RATE 57600

// Dynamixel AX-12A servo IDs
#define NECK_PAN 1
#define NECK_TILT 2
#define LEFT_EYE_PAN 3
#define LEFT_EYE_TILT 4
#define RIGHT_EYE_PAN 5
#define RIGHT_EYE_TILT 6

const int NUMBER_OF_FIELDS = 6; // how many comma separated fields we expect
int fieldIndex = 0;            // the current field being received
int positions[6], newPositions[6];

void sendCurrentPosition() {
  Serial.print(positions[0]);
  Serial.print(',');
  Serial.print(positions[1]);
  Serial.print(',');
  Serial.print(positions[2]);
  Serial.print(',');
  Serial.print(positions[3]);
  Serial.print(',');
  Serial.print(positions[4]);
  Serial.print(',');
  Serial.print(positions[5]);
  Serial.println('\n');
}

bool positionsNotEqual() {
  return positions[0] != newPositions[0] || positions[1] != newPositions[1];
}

void setPosition() {
  int i;
  while(positionsNotEqual()) {
    for(i = 0; i < 2; i++) {
      if(newPositions[i] > 340 && newPositions[i] < 700) {
        if(positions[i] < newPositions[i])
          positions[i] += 1;
        else if(positions[i] > newPositions[i])
          positions[i] -= 1;
        SetPosition(i+1, positions[i]);
      }
    }
    delay(1);
  }
  for(i = 2; i < 6; i++) {
    if(newPositions[i] > 340 && newPositions[i] < 700) {
      SetPosition(i+1, newPositions[i]);
      positions[i] = newPositions[i];
    }
  }
}

// Setup function
void setup() {
  // Set initial positions
  SetPosition(NECK_PAN, 512);
  SetPosition(NECK_TILT, 512);
  SetPosition(LEFT_EYE_PAN, 512);
  SetPosition(LEFT_EYE_TILT, 512);
  SetPosition(RIGHT_EYE_PAN, 512);
  SetPosition(RIGHT_EYE_TILT, 512);

  // Listen on serial connection for messages from the pc
  Serial.begin(BAUD_RATE);

  for(int i = 0; i < 6; i++)
    positions[i] = 512;
}

void loop()
{
  for(fieldIndex = 0; fieldIndex  < NUMBER_OF_FIELDS; fieldIndex ++)
  {
    newPositions[fieldIndex] = finder.getValue(); // get a numeric value
  }
  setPosition();
  sendCurrentPosition();
  fieldIndex = 0;  // ready to start over
  delay(5);
}
