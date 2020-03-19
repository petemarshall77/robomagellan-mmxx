//------------------------------------------------------------------------
// MONTY2 Control Hardware Interfacing Arduino Software (CHIAS)
//
//     CHIA is the system that MONTY2 uses to interface between the main
//     controller laptop and the robot steering servo and motor
//     controller. It communicates with the controller via a serial port
//     which is used to send and recieve steering and throttle data.
//
//     The CHIA (and hence Monty's throttle/steering system) can is in
//     Juan of three states:
//      
//         1. STOPPED  - the robot is stopped and no power or steering
//                       data is sent or recieved. This is the initial
//                       state of the CHIA and the state in which the
//                       controller will use to compeletly stop the
//                       robot.
//
//         2. MANUAL   - this is used to simply drive Monty as a remote
//                       control vehicle. The CHIA simply passes the
//                       throttle and steering PWM signals from the
//                       radio receiver to the power contoller and
//                       steering servos.
//
//         3. AUTO     - Similar to MANUAL but the CHIA writes the 
//                       throttle and steering values received from the 
//                       controller. 
//                       
//     The CHIA's state is determined by a three position switch which will
//     set the value of either autoPin or manualPin to low. If both pins are
//     high it indicates stopped mode. 
//
//     Note: the CHIA expects data to be sent as newline ('\n') terminated
//     strings. Don't send it CRs/LFs or CR/LFs, just newlines please.
//     Failure to comply will void your warranty and may lead to serious
//     injury or death (or, worse still, a robot that just sits there and
//     does nothing). You have been warned.
//
#include <Servo.h>

//------------------------------------------------------------------------
// Dramatis personae
//------------------------------------------------------------------------

// Safety
#define MAX_POWER 1635

// Serial buffer
#define BUFFER_LENGTH 80
char serialBuffer[BUFFER_LENGTH];
String inputString;

// System can be in Juan of three states...
#define STOPPED  1
#define MANUAL   2
#define AUTO     3

int system_state;

// Pin declarations
const int steer_Pin = 2;  // do not change: mapped to interrupt 0
const int power_Pin = 3;  // do not change: mapped to interrupt 1
const int auto_Pin = 5;
const int manual_Pin = 6;
const int steer_Out_1 = 11;
const int steer_Out_2 = 7;
const int power_Out = 8;
const int kill_Switch = 10;
const int LED_pin = 13;

// Interrupt routine values
volatile unsigned long steer_Microseconds;
volatile unsigned long steer_Initial_Result;

volatile unsigned long power_Microseconds;
volatile unsigned long power_Initial_Result;

volatile unsigned long safety_Microseconds;
volatile unsigned long safety_Initial_Result;

//------------------------------------------------------------------------
// SETUP
//------------------------------------------------------------------------
void setup()
{
  // System start in stopped state
  system_state = STOPPED;
  
  // Set up serial communications
  Serial.begin(9600);
  Serial.println("CHIAS18a");
  
   // Pin initializations
  pinMode(steer_Pin, INPUT);
  pinMode(power_Pin, INPUT);
  pinMode(auto_Pin, INPUT);
  pinMode(manual_Pin, INPUT);
  pinMode(steer_Out_1, OUTPUT);
  pinMode(steer_Out_2, OUTPUT);
  pinMode(power_Out, OUTPUT);
  pinMode(kill_Switch, INPUT_PULLUP);
  pinMode(LED_pin, OUTPUT);

  // Ensures that the two ouput pins are set to low at the start
  digitalWrite(steer_Out_1, LOW);
  digitalWrite(steer_Out_2, LOW);
  digitalWrite(power_Out, LOW);
  digitalWrite(LED_pin, HIGH);
}

//------------------------------------------------------------------------
// Main LOOP
//------------------------------------------------------------------------
void loop()
{
  boolean isManual = digitalRead(manual_Pin);  // negate as pin is pulled-up
  boolean isAuto = digitalRead(auto_Pin);      // negate as pin is pulled-up
  
  if(isManual && isAuto){
    Serial.println("Error");
    delay(1000);
  }else if(isManual){
    Serial.println("Mode is manual");
    do_manual();
  }else if(isAuto){
    Serial.println("Mode is auto");
    do_auto();
  }else{
    Serial.println("Mode now stopped");
    do_stopped();
  }
}



//-------------------------------------------------------------------------
// STOPPED Mode - robot does nothing but wait for switch to manual or auto
//-------------------------------------------------------------------------
void do_stopped()
{
  boolean isManual; 
  boolean isAuto;

  while (true) {
    isManual = digitalRead(manual_Pin); 
    isAuto = digitalRead(auto_Pin); 
    if(isManual || isAuto) {
      break;
    }
  }
}


 
//------------------------------------------------------------------------
// MANUAL Mode - drive the robot as a remote control car
//
//      In manual mode, a pair of interrupt handlers service changes to 
//      the steering and throttle output pins of the radio reciever.
//      These pins present PWM signals that the interrupt handlers simply
//      pass on to the steering servo(s) and motor controller.
//------------------------------------------------------------------------
void do_manual()
{
  // Attach interrupt handlers to pins 2 and 3 to capture the output
  // from the radio reciever.
  attachInterrupt(0, steerInterrupt, CHANGE); // interrupt 0 is pin 2
  attachInterrupt(1, powerInterrupt, CHANGE); // interrupt 1 is pin 3

  while (true) {
    if (!digitalRead(manual_Pin)) {
      delay(250);
      if(!digitalRead(manual_Pin)) {
        detachInterrupt(0);
        detachInterrupt(1);
        break;
      }
    }
    delay(250);
  }  
}

 

//------------------------------------------------------------------------
// AUTO mode
//------------------------------------------------------------------------
void do_auto()
{
  boolean isAuto;
  int counter = 0;

  unsigned long last_data_time = millis();
  unsigned long steer_value, power_value;
  unsigned long current_power = 1500;
  
  Servo steer_servo_1;
  Servo steer_servo_2;
  Servo power_servo;
  
  Serial.println("System state is now AUTO");
  
  // Attach servo outputs
  steer_servo_1.attach(steer_Out_1);
  steer_servo_2.attach(steer_Out_2);
  power_servo.attach(power_Out);

  while (true) {
    // Check we are still in auto mode
    isAuto = digitalRead(auto_Pin);  //negate as pin is pulled up
    if(!isAuto) {
      power_servo.writeMicroseconds(1500);
      steer_servo_1.detach();
      steer_servo_2.detach();
      power_servo.detach();
      break;
    }  

    // If no command recived in 5 seconds, stop the robot
  //  if (millis() - last_data_time > 30000) {
  //    power_servo.writeMicroseconds(1500);
  //    current_power = 1500;
  //    Serial.println("Timed out");
  //    continue;
  //  }

    // If killswitch is LOW, stop the robot
    if (digitalRead(kill_Switch) == HIGH) {
      power_servo.writeMicroseconds(1500);
      current_power = 1500;
      Serial.println("Killswitch!");
      continue;
    }
    
    // Process line of data if available
    if (readLine(serialBuffer) != 0) {
      Serial.print("readLine returned: ");
      Serial.println(serialBuffer);
      last_data_time = millis();
      inputString = String(serialBuffer);           
        
      // Process the data string, should be nnnn,nnnn (steer,power)
      steer_value = inputString.substring(0,4).toInt();
      power_value = inputString.substring(5,9).toInt();
      //Serial.println(steer_value);
      //Serial.println(power_value);
      //Serial.println("Power and Steer set");
      if (steer_value < 1000 || steer_value > 2000 || power_value < 1000 || power_value > 2000) {
        //Serial.println("Bad data from laptop. PANIC");
        //Serial.println(steer_value + " " + power_value);
        //Serial.flush();
        panic();  // bad data, assume communication error, panic
      }
      
      // Enforce maximum power value
      if (power_value > MAX_POWER) {
        power_value = MAX_POWER;
      }
    }
    else {
      // DEBUG Serial.println("No data");
      continue;
    }
    
    // Got good values, kill switch is good, set steering and slew power to demand value
    steer_servo_1.writeMicroseconds(steer_value);
    steer_servo_2.writeMicroseconds(steer_value);
    //Serial.println(steer_value);
    if (power_value > current_power) {
      while (current_power < power_value) {
        current_power++;
        power_servo.writeMicroseconds(current_power);
        delay(1);
      }
    }
    else if (current_power > power_value) {
      while (current_power > power_value) {
        current_power--;
        power_servo.writeMicroseconds(current_power);
        delay(1);
      }
    }
  }
}

// PANIC Function.
void panic()
{
    //noInterrupts();                  // stop servicing interrupts
    digitalWrite(power_Out, LOW);    // stop the robot's power
    Serial.println("CHIAS PANIC!!!");
    while (true) {                   // blink the LED
      digitalWrite(LED_pin, HIGH);
      delay(200);
      digitalWrite(LED_pin, LOW);
      delay(200);
    }
}
      

//------------------------------------------------------------------------
// Miscellaneous functions
//------------------------------------------------------------------------

// Read a line of data from the serial port, placing the data as a well-
// formed, null-delimited string in buffer and returning the length of
// the input. Return 0 if no data is available.
int readLine(char* buffer)
{
  int byteCount = 0;
  int inputByte;
  
  // DEBUGSerial.println("Called readLine");
  
  if (Serial.available()) {
    // data is available: keep reeading until newline is recieved
    while ((inputByte = Serial.read()) != '\n') {
      if (inputByte != -1) {
        buffer[byteCount] = inputByte;
        byteCount++;
      }
    }
    buffer[byteCount] = 0;  // make end of string
    return byteCount;       // note: if no data is available, will return 0
  }
  else {
    // DEBUG: Serial.println("No data available");
    return 0;
  }
}


//------------------------------------------------------------------------
// INTERRUPT Handlers
//
//     The steering and power interrupt handlers are used in both MANUAL
//     and RECORD mode. They are called whenever the output of the radio
//     control receiver changes state. The signals they are handling are
//     standard servo PWM signals and these routines do two things:
//
//       1 - mirror the input signals to an output attached to the
//           vehicle steering servo and motor controller, essentially
//           just passing the PWM signal through the arduino.
//
//       2 - calculate the pulse width in microseconds. These routines
//           are called on change of signal state so they don't know
//           if the current state is high or low. However, as standard
//           servo pulses last from 1000 to 2000 microseconds and the
//           overall cycle time is 10000 microseconds (i.e. the signal
//           is low for between 9000 and 8000 microseconds) then only
//           times between calls in the 1000 - 2000 range are the Juans
//           that represent PWM pulse widths.
//
//       The safety interrupt handler measures the throttle signal, just
//       like the powerinterrupt but does not mirror the signal to the
//       powercontrol. This is used in PLAYBACK/SLAVE mode to use the
//       throttle trigger as a fail-safe switch.
//
//------------------------------------------------------------------------

// STEERING interrupt handler
void steerInterrupt()
{
  // Get the time since the last interrupt
  steer_Initial_Result = micros() - steer_Microseconds;

  // If this time represents a pulse the signal has just gone low:
  // set the output low and update the steering value in steer result.
  // Note that real-world PWM values go down into 900's so we reflect
  // this here.
  if (steer_Initial_Result <= 2000 && steer_Initial_Result >= 900){
    digitalWrite(steer_Out_1, LOW);
    digitalWrite(steer_Out_2, LOW);
  }
  else {
    // this is the begining of a new pulse: set the output high but
    // don't update the pulse width value
    digitalWrite(steer_Out_1, HIGH);  // See above comment
    digitalWrite(steer_Out_2, HIGH);  // See above comment
  }

  // Reset time for next interrupt
  steer_Microseconds = micros();
}


// POWER interrupt handler
//
//     This is a mirror of the steering handler above. Refer to the code
//     comments there.
//
void powerInterrupt()                                                             
{                                                                               
  power_Initial_Result = micros() - power_Microseconds;                         
                                                                                
  if (power_Initial_Result <= 2000 && power_Initial_Result >= 900){                                                    
    digitalWrite(power_Out, LOW);                                                                                                                               
  }
  else {
    digitalWrite(power_Out, HIGH);  // See above comment
  }

  // Reset time for next interrupt
  power_Microseconds = micros();
}


// SAFETY interrupt handler
//
//     This is a mirror of the power handler above but does not mirror
//     the output signal, just records the throttle value.
//
void safetyInterrupt()                                                             
{                                                                               
  safety_Initial_Result = micros() - safety_Microseconds;                         
                                                                                
  if (safety_Initial_Result <= 2000 && safety_Initial_Result >= 900){                                                                                                                                                                                  
  }
  else {
    // do nothing
  }

  // Reset time for next interrupt
  safety_Microseconds = micros();
}

