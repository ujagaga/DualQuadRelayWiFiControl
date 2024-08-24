#include <WiFiUdp.h>
#include "config.h"


void UDP_send(int id){
  WiFiUDP Udp;
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