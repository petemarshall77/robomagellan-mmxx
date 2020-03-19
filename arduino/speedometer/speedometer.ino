// MONTY III Speedometer

// Input: hall-effect switch pin 2
// Output: rotations/second, total rotation count sent to Serial

const int sensor_pin = 2; // do not change, fixed to interrupt 0
volatile unsigned long rotation_cnt;
unsigned long last_rot_cnt;
unsigned long last_rot_time;
float counts_per_second;
 
// Set Up
void setup() {
  rotation_cnt = last_rot_cnt = 0;
  last_rot_time = micros();
  Serial.begin(9600);
  attachInterrupt(0,rotation_isr, FALLING); 
}

// Main Loop
void loop() {
  unsigned long delta_cnt;
  unsigned long delta_time;

  delay(500);
  delta_cnt = rotation_cnt - last_rot_cnt;
  last_rot_cnt = rotation_cnt;
  delta_time = micros() - last_rot_time;
  last_rot_time = micros();
  counts_per_second = delta_cnt * 1000000.0 / delta_time;
  
  Serial.print(counts_per_second);
  Serial.print(',');
  Serial.println(last_rot_cnt);
  
}
 
// Interrupt hander for rotation sensor
void rotation_isr()
{
  rotation_cnt++;
}



