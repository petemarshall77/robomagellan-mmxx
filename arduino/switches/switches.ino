// Bump/start switch pins
const int bump_switch = 4;
const int start_switch = 5;

void setup(void) 
{
  Serial.begin(9600);
  Serial.println("CompassSwitch Started"); Serial.println("");
  
  // Set bump/switch pins
  pinMode(bump_switch, INPUT_PULLUP);
  pinMode(start_switch, INPUT_PULLUP);
}

void loop(void) 
{
  // Switch states
  int bump_state = !digitalRead(bump_switch);
  int start_state = !digitalRead(start_switch);
  
  Serial.print(bump_state);Serial.print(",");Serial.println(start_state);
  delay(500);
}
