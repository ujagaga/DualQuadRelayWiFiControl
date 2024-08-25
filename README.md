# DualQuadRelayWiFiControl

Using 2 pieces of ESP8266 module with 4 relays to controll 2 gates.
One module is named "primary" and the other "secondary". 

The primary provides an http server with a web interface for both modules.
It uses a UDP broadcast to dispatch the command to the secondary module.
That way it does not have to wory about the secondary module IP address.

The secondary switch also provides a web interface to access it in case the primary is not working.

The secondary module features an UDP server listening for the broadcast 
command to trigger one of 4 relays for a second.

Both modules feature an Over The Air update mecanysm. It does not have any security by default, but you can enable it by uncommenting the define in config: "#define ENABLE_UPDATE_PASSWORD".

To trigger the Over The Air update, just go to http page "/update".

## How to start

1. Install Arduino IDE.
2. In "File/Preferences" add to "Additional Boards Manager":

        https://arduino.esp8266.com/stable/package_esp8266com_index.json


2. Install additional libraries: "ArduinoJson", "WebSockets" and "ESP_EEPROM"
3. In "config.h" adjust as needed:
- If building for the primary module, uncomment

        #define DEV_IS_PRIMARY

- If building for the secondary, make sure previous is commented out
- Change default 

        #define PASSWORD "abc131313" 
        
  to something only you will know
- Choose whether to use password for OTA update using 

        #define ENABLE_UPDATE_PASSWORD
        
  The network should be closed and no unauthorized people should have access, so it should be safe enough without password.
- Change the 

        #define AP_NAME_PREFIX "Zaric_sw_"

4. Connect your module for initial programming
5. Select ESP-12 board and  
6. build and program using a USB UART module. For any further firmware updates, you can use the Over The Air update. To use it:
- Connect to device's WiFi network or your home LAN if you have already configured your device to connect to it.
- Using your web browser, go to "/update" page to trigger the update.
- It takes a while, up to 30 seconds for Arduino IDE to detect the new update server and list it in "Tools/Port" for you to select. 
- Click on the program button in Arduino IDE. The Arduino IDE will ask for password. If you have not set any, just use what ever.

## Note
When configuring the device to use your home network, either use your router settings to assign a static IP address, or specify a static IP address in the WiFi settings. That way you will know the device address to connect to. 

## Status
Finished