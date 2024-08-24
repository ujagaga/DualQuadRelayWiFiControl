#ifndef CONFIG_H
#define CONFIG_H

// Comment this is device is secondary
//#define DEV_IS_PRIMARY

#define RELAY_1_PIN             16   
#define RELAY_2_PIN             14   
#define RELAY_3_PIN             12   
#define RELAY_4_PIN             13

#define UDP_PORT                13131

#define AP_NAME_PREFIX          "Zaric_sw_"
#ifdef DEV_IS_PRIMARY
  #define DEV_ID "primary"
#else
  #define DEV_ID "secondary"
#endif
#define AP_NAME AP_NAME_PREFIX DEV_ID

#define WIFI_PASS_EEPROM_ADDR   (0)
#define WIFI_PASS_SIZE          (32)
#define SSID_EEPROM_ADDR        (WIFI_PASS_EEPROM_ADDR + WIFI_PASS_SIZE)
#define SSID_SIZE               (32)
#define STATION_IP_ADDR         (SSID_EEPROM_ADDR + SSID_SIZE)
#define STATION_IP_SIZE         (4)
#define EEPROM_SIZE             (WIFI_PASS_SIZE + SSID_SIZE + STATION_IP_SIZE)   

#endif
