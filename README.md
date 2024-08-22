# DualQuadRelayWiFiControl

Using 2 pieces of ESP8266 module with 4 relays to controll 2 gates.
One module is named "primary_switch" and the other "secondary_switch". 
The primary provides an http server with a web interface for both modules.
It uses a UDP broadcast to dispatch the command to the secondary module.
That way it does not have to wory about the secondary module IP address.

The secondary module features an UDP server listening for the broadcast 
command to trigger one of 4 relays for a couple of seconds.

## Status
In development and not yet usable