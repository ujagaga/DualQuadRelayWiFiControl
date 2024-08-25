#include <WiFiUdp.h>
#include "config.h"
#include "pinctrl.h"
#include <Arduino.h>

static WiFiUDP Udp;                             /* UDP object used for receiving the ping message. */
static char incomingPacket[255];                /* buffer for incoming packets */

void UDP_init(){
  Udp.begin(UDP_PORT);
}

void UDP_process(){
  int packetSize = Udp.parsePacket();
  String expectedMsg = "relay:";
  
  if (packetSize > String(expectedMsg).length())
  {
    // receive incoming UDP packets
    int len = Udp.read(incomingPacket, String(expectedMsg).length() + 1);
    incomingPacket[len] = 0;

    Serial.print("UDP RX:");
    Serial.println(incomingPacket);
    
    if(String(incomingPacket).startsWith(expectedMsg)){
      int id = ((int)incomingPacket[len -1]) - '0';
      if(id > 3){
        id -= 4;
      }
      PINCTRL_trigger(id);
    }    
  }
}

void UDP_send(int id){
  IPAddress SendIP(192,168,1,255);

  String broacastMsg = "relay:" + String(id);
  char buf[255] = {0};
  broacastMsg.toCharArray(buf, 255);

  // Reppeat 3 times as UDP is not guaranteed to arrive
  Udp.beginPacket(SendIP, UDP_PORT);
  Udp.write(buf);
  Udp.endPacket();

  delay(10);

  Udp.beginPacket(SendIP, UDP_PORT);
  Udp.write(buf);
  Udp.endPacket();

  delay(10);

  Udp.beginPacket(SendIP, UDP_PORT);
  Udp.write(buf);
  Udp.endPacket();
}