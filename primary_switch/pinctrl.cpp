/* 
 *  Author: Rada Berar
 *  email: ujagaga@gmail.com
 *  
 *  GPIO management module
 */
#include "http.h"
#include "wifi_connection.h"
#include "config.h"

#define DEBOUNCE_TIMEOUT    200

static int currentPinVal[4] = {0}; 
static int pin_num[4] = {RELAY_1_PIN, RELAY_2_PIN, RELAY_3_PIN, RELAY_4_PIN};
static unsigned long PinWriteTimestamp = 0;


int PINCTRL_getState( int pinId ){
  if((pinId > 0) && (pinId < 4)){
    return currentPinVal[pinId];
  }

  return -1;
}

void PINCTRL_init(){
  pinMode(pin_num[0], OUTPUT);
  pinMode(pin_num[1], OUTPUT);
  pinMode(pin_num[2], OUTPUT);
  pinMode(pin_num[3], OUTPUT);
}

void PINCTRL_write(int pinId, int state)
{
  if((millis() - PinWriteTimestamp) < DEBOUNCE_TIMEOUT){
    return;
  }

  if((pinId < 0) || (pinId > 3)){
    return;
  }

  Serial.print("SW:");
  Serial.print(pinId);
  Serial.print(" = ");
  Serial.println(state);  

  digitalWrite(pin_num[pinId], state);

  PinWriteTimestamp = millis();  
}
