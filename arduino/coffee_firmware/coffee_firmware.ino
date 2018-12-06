#include <Wire.h>
#include <Stepper.h>

#define STEPS 64
#define REVOLUTION 2048
#define SLAVE_ADDRESS 0x04

//naming Arduino pin
int ONOFF = 2;
int x1short = 3; // button for 1 short coffee
int x2short = 4; // button for 1 short coffee
int clean = 5; // button clean
int vape = 6; // button vape
int x1long = 7; // button for 1 long coffee
int x2long = 8; // button for 2 long coffee
int buttons[] = {ONOFF, x1short, x2short, clean, vape, x1long, x2long, -1};
int count = 0;
int number = 0;
int state = 0;
int steps = 0;
int max_step = (int)(250.0 / 180.0 * (float)REVOLUTION / 2.0);
int nb_step = 330;
Stepper stepper(STEPS, 9, 11, 10, 12);

int servo_pos = 0;

bool coffee_has_started = false;

void setup() {
  // start serial for output
  Serial.begin(9600);
  Serial.println("Ready!");

  // setup pin Mode and set default status
  int i = 0;
  while (buttons[i] != -1) {
    pinMode(buttons[i], OUTPUT);
    digitalWrite(buttons[i], HIGH);
    ++i;
  }
  stepper.setSpeed(200);
  stepper.step(0);
  turn_right(1);
  turn_left(1);
  default_value();
}

void default_value() {
  number = 0;
  count = 0;
}
/*
   Run undefinitly
*/
void loop() {
  if (Serial.available() > 0) {
    // read the incoming byte:
    int incomingByte = Serial.read();
    if (incomingByte == 'B') {
      // command have to start with 'B'
      default_value();
    } else if (incomingByte == 'E') {
      // command have to end with 'E'
      start_coffee(number);
      default_value();
    } else if (incomingByte == 'S') {
      stop_coffee();
      default_value();
    } else if (incomingByte == 'T') {
      onoff();
      default_value();
    }
    else if (incomingByte == 'V') {
      touch_vape();
      default_value();
    }
    else if (incomingByte == 'C') {
      touch_clean();
      default_value();
    }
    else if (incomingByte >= '0' && incomingByte <= '9') {
      // save as an int all the character coming from Serial
      int tmp = incomingByte - '0';
      number *= 10;
      number += tmp;
      count++;
    }
  }
}

/*
   Utils
*/

/*
   turn the stepper motor to the left
*/
void turn_left(int v) {
  Serial.println("turn left\n");
  if (v == 1)
    stepper.step(400);
  else if (v == 2)
    stepper.step(800);
  else if (v == 3)
    stepper.step(1300);
}
/*
   turn the stepper motor to the right
*/
void turn_right(int v) {
  Serial.println("turn right\n");
  if (v == 1)
    stepper.step(-400);
  else if (v == 2)
    stepper.step(-800);
  else if (v == 3)
    stepper.step(-1300);
}

/*
   simulate push a button
*/
void touch_button(int pin) {
  digitalWrite(pin, LOW);
  Serial.print(" touchdown\n");
  delay(500);
  digitalWrite(pin, HIGH);
}

/*
   simulate push button for 2 short coffees
*/
void touch_x2() {
  Serial.println("touch x2\n");
  touch_button(x2short);
}
/*
   simulate push button for 2 long coffees
*/
void touch_x2_long() {
  Serial.println("touch x2 long\n");
  touch_button(x2long);
}
/*
   simulate push button for 1 short coffee
*/
void touch_x1() {
  Serial.println("touch x1\n");
  touch_button(x1short);
}
/*
   simulate push button for 1 long coffee
*/
void touch_x1_long() {
  Serial.println("touch x1 long\n");
  touch_button(x1long);
}

/*
   simulate push button for cleaning
*/
void touch_clean() {
  Serial.println("touch clean\n");
  touch_button(clean);
}
/*
   simulate push button for cleaning
*/
void touch_vape() {
  Serial.println("touch vape\n");
  touch_button(vape);
}

/*
   simulate push button for on and off
*/
void onoff() {
  Serial.println("turn on/off\n");
  touch_button(ONOFF);
}

/*
   Select the intensity fort the coffee by moving the stepper motor
   0 -> mild
   1 -> standard
   2 -> strong
   3 -> extra strong
*/
void select_intensity(int intensity) {
  turn_right(intensity);
}

/*
   Set the stepper motor to its default position
*/
void default_intensity(int intensity) {
  turn_left(intensity);
}

/*
   compute int into order
*/

void stop_coffee() {
  if (coffee_has_started) {
    touch_x1();
    coffee_has_started = false;
  }
}

void start_coffee(unsigned int type) {

  int number = type % 10;
  int coffee_type = type / 10 % 10;
  int coffee_size = type / 100 % 10;
  int intensity = type / 1000 % 10;
  int special = type / 10000 % 10;
  Serial.print(type);
  if (coffee_type == 9) {
    coffee_has_started = true;
    select_intensity(intensity);
    if (number == 1)
      if (coffee_size == 1)
        touch_x1();
      else
        touch_x1_long();
    else if (coffee_size == 1)
      touch_x2();
    else
      touch_x2_long();
    int delay_ = 0;
    while (delay_ <= 20000 && coffee_has_started) {
      if (Serial.available() > 0 && Serial.read() == 'S')
        stop_coffee();
      delay_++;
      delay(1);
    }
    Serial.println("default intensity\n");
    default_intensity(intensity);
    coffee_has_started = false;
  }
}
