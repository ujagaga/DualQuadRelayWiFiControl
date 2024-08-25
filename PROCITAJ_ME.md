# DualQuadRelayWiFiControl

Korištenje 2 komada ESP8266 modula sa 4 releja za kontrolu 2 kapije.
Jedan modul se zove "primarni", a drugi "sekundarni".

Primarni obezbeđuje http server sa web interfejsom za oba modula.
Koristi UDP broadcast za slanje komande sekundarnom modulu.
Na taj način ne mora da brine o IP adresi sekundarnog modula.

Sekundarni modul takođe pruža web interfejs za pristup u slučaju da primarni ne radi.
Sekundarni modul sadrži UDP server koji sluša emitovanje naredbe za aktiviranje jednog od 4 releja na sekundu.
Oba modula imaju mehanizam za "Over The Air" ažuriranje, tj. preko mreže. Nema nikakvu sigurnost prema zadanim postavkama, ali ga možete omogućiti tako što ćete odkomentirati u "config.h": "#define ENABLE_UPDATE_PASSWORD".
Da biste pokrenuli "Over The Air" ažuriranje, samo idite na http stranicu "/update".

## Kako početi

1. Instalirajte Arduino IDE.
2. U "File/Preferences" dodajte u "Additional Boards Manager":

        https://arduino.esp8266.com/stable/package_esp8266com_index.json


2. Instalirajte dodatne biblioteke: "ArduinoJson" i "WebSockets"
3. U "config.h" podesite po potrebi:
- Ako gradite za primarni modul, odkomentarisite

        #define DEV_IS_PRIMARY

- Ako gradite za sekundarni, uvjerite se da je prethodno zakomentarisano
- Promijeni

        #define LOZINKU "abc131313"

 na nešto što ćete samo vi znati
- Odaberite želite li koristiti lozinku za korištenje OTA ažuriranja

        #define ENABLE_UPDATE_PASSWORD

 Mreža bi trebala biti zatvorena i ne bi trebalo da neovlaštene osobame imaju pristup, tako da bi trebala da bude dovoljno sigurna bez lozinke.
- Promeni

        #define AP_NAME_PREFIX "Zaric_sw_"

4. Povežite svoj modul za početno programiranje
5. Odaberite ESP-12 ploču i
6. izgradite i programirajte koristeći USB UART modul. Za sva daljnja ažuriranja firmvera, možete koristiti ažuriranje Over The Air. Za korištenje:
- Povežite se na WiFi mrežu uređaja ili kućni LAN ako ste već konfigurirali svoj uređaj da se poveže na njega.
- Koristeći svoj web pretraživač, idite na stranicu "/update" da pokrenete ažuriranje.
- Ponovo pokrenite Arduino IDE kako bi mogao otkriti novi server za ažuriranje i navesti ga u "Alati/Port" da biste odabrali.
- Kliknite na dugme program u Arduino IDE. Arduino IDE ce traziti lozinku, ali ako niste nikakvu podesili, upisite bilo sta.

## Napomena
Kada konfigurišete uređaj da koristi vašu kućnu mrežu, ili koristite postavke rutera da dodelite statičku IP adresu ili navedite statičku IP adresu u WiFi postavkama. Na taj način ćete znati adresu uređaja na koji ćete se povezati.

## Status
U funkciji, ali još uvijek na testiranju