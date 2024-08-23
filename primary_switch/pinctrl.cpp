/* 
 *  Author: Rada Berar
 *  email: ujagaga@gmail.com
 *  
 *  GPIO management module
 */
#include "http.h"
#include "wifi_connection.h"
#include "config.h"

#define DEBOUNCE_TIMEOUT    800

static int currentPinVal[4] = {0}; 
static int pin_num[4] = {RELAY_1_PIN, RELAY_2_PIN, RELAY_3_PIN, RELAY_4_PIN};
static uint32_t PinWriteTimestamp[4] = {0};

void PINCTRL_init(){
  pinMode(pin_num[0], OUTPUT);
  pinMode(pin_num[1], OUTPUT);
  pinMode(pin_num[2], OUTPUT);
  pinMode(pin_num[3], OUTPUT);
}

void PINCTRL_trigger(int pinId)
{
  if((pinId < 0) || (pinId > 3)){
    return;
  }

  if((millis() - PinWriteTimestamp[pinId]) < DEBOUNCE_TIMEOUT){
    return;
  }  

  Serial.print("SW:");
  Serial.println(pinId); 

  digitalWrite(pin_num[pinId], HIGH);

  PinWriteTimestamp[pinId] = millis();
}

void PINCTRL_process(){
  for(int i = 0; i < 4; ++i){
    if((millis() - PinWriteTimestamp[i]) > DEBOUNCE_TIMEOUT){
      digitalWrite(pin_num[i], LOW);
    }
  }
}
