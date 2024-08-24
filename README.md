# DualQuadRelayWiFiControl

Using 2 pieces of ESP8266 module with 4 relays to controll 2 gates.
One module is named "primary_switch" and the other "secondary_switch". 

The primary provides an http server with a web interface for both modules.
It uses a UDP broadcast to dispatch the command to the secondary module.
That way it does not have to wory about the secondary module IP address.

The secondary switch also provides a web interface to access in case the primary is not working.

The secondary module features an UDP server listening for the broadcast 
command to trigger one of 4 relays for a second.

Both modules feature an Over The Air update mecanysm. It does not have any security yet.

## How to start

Install Arduino IDE.
In FilePreferences add to Additional Boards Manager:

        https://arduino.esp8266.com/stable/package_esp8266com_index.json

Install additional libraries: "ArduinoJson" and "WebSockets"
Select ESP-12 board, build and program using a USB UART module.

Before building, make sure to go through "config.h" and select whether the device is primary (#define DEV_IS_PRIMARY).
You may also change the AP_NAME_PREFIX.

## Status
Just finished first version. Needs testing.