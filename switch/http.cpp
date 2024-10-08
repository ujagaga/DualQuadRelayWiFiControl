/* 
 *  Author: Rada Berar
 *  email: ujagaga@gmail.com
 *  
 *  HTTP server which generates the web browser pages. 
 */
 
#include <ESP8266WebServer.h>
#include <ESP_EEPROM.h>
#include <ESP8266HTTPClient.h>
#include <pgmspace.h>
#include "http.h"
#include "wifi_connection.h"
#include "config.h"
#include "switch.h"
#include "pinctrl.h"
#include "ota.h"
#include "web_socket.h"
#include "udp.h"


/* If we were writing HTML files, this would be the content. Here we use char arrays. */
static const char HTML_BEGIN[] PROGMEM = R"(
<!DOCTYPE HTML>
<html>
  <head>
    <meta name = "viewport" content = "width = device-width, initial-scale = 1.0, maximum-scale = 1.0, user-scalable=0">
    <title>Zaric Gate</title>
    <style>
      body { background-color: white; font-family: Arial, Helvetica, Sans-Serif; Color: #000000; }
      .contain{width: 100%;}
      .center_div{margin:0 auto; max-width: 400px;position:relative;}
    </style>
  </head>
  <body>
)";

static const char HTML_END[] PROGMEM = "</body></html>";

static const char INDEX_HTML_0[] PROGMEM = R"(
<style>
  .btn_b{border:0;border-radius:0.3rem;color:#fff;line-height:4rem;font-size:3rem;margin:1%;height:4rem;width:4rem;background-color:#1fa3ec;flex:1;}
  .btn_cfg{border:0;border-radius:0.3rem;color:#fff;line-height:1.4rem;font-size:0.8rem;margin:1ch;height:2rem;width:10rem;background-color:#ff3300;}      
  .row{display: flex;justify-content: space-between;align-items: center;}      
</style>
<div class="contain">
  <div class="center_div">
)";

const char INDEX_HTML_1[] PROGMEM = R"(
  </div>
  <hr>
  <p id='status'></p>  
  <br>
  <button class="btn_cfg" type="button" onclick="location.href='/selectap';">Configure wifi</button>
  <button class="btn_cfg" type="button" onclick="location.href='/config';">Configure Buttons</button>
  <br/>
</div>
<script>
  function redirectTo(id) {
    const timestamp = new Date().getTime();
    location.href = `/trigger?id=${id}&t=${timestamp}`;
  }
</script>
)";

static const char APLIST_HTML_0[] PROGMEM = R"(
<style>
  .c{text-align: center;}
  div,input{padding:5px;font-size:1em;}
  input{width:95%;}
  body{text-align: left;}
  button{width:100%;border:0;border-radius:0.3rem;color:#fff;line-height:2.4rem;font-size:1.2rem;height:40px;background-color:#1fa3ec;}
  .q{float: right;width: 64px;text-align: right;}
  .radio{width:2em;}
  #vm{width:100%;height:50vh;overflow-y:auto;margin-bottom:1em;} 
</style>
</head><body>  
  <div class="contain">
    <div class="center_div">
)";    

/* Placeholder for the wifi list */
static const char APLIST_HTML_1[] PROGMEM = R"(   
      <h1 id='ttl'>Networks found:</h1>
      <div id='vm'>
)";  

static const char APLIST_HTML_2[] PROGMEM = R"( 
      </div>
      <form method='get' action='wifisave'>
        <button type='button' onclick='refresh();'>Rescan</button><br/><br/>
        <input id='s' name='s' length=32 placeholder='SSID (Leave blank for AP mode)'><br>      
        <input id='p' name='p' length=32 placeholder='password'><br>
        <input id='a' name='a' length=16 placeholder='static IP address (optional)'><br>       
        <br><button type='submit'>save</button>        
      </form>      
     </div>
  </div>
<script>
  function c(l){
    document.getElementById('s').value=l.innerText||l.textContent;
    document.getElementById('p').focus();
  }
  
  var cn=new WebSocket('ws://'+location.hostname+':81/');
  cn.onopen=function(){
    cn.send('{"APLIST":""}');
  }
  cn.onmessage=function(e){
    var data=JSON.parse(e.data);
    if(data.hasOwnProperty('APLIST')){
      rsp=data.APLIST.split('|');
      document.getElementById('vm').innerHTML='';
      for(var i=0;i<(rsp.length);i++){
        document.getElementById('vm').innerHTML+='<span>'+(i+1)+": </span><a href='#p' onclick='c(this)'>" + rsp[i] + '</a><br>';
      }
      if(!document.getElementById('vm').innerHTML.replace(/\\s/g,'').length){
        document.getElementById('ttl').innerHTML='No networks found.'
      } 
    }
  };
  function refresh(){
    document.getElementById('vm').innerHTML='Please wait...'
    cn.send('{"APLIST":""}');
  } 
</script>
)";

static const char BTN_CFG_HTML[] PROGMEM = R"( 
  <h1>Select Button Display</h1>

  <form method='get' action='config'>
    <label for="prim">Primary buttons:</label>

    <select name="prim" id="prim">
      <option value="1">1</option>
      <option value="2">2</option>
      <option value="3">3</option>
      <option value="4" selected>4</option>
    </select></br>

    <label for="sec">Secondary buttons:</label>
    <select name="sec" id="sec">
      <option value="0">0</option>
      <option value="1">1</option>
      <option value="2">2</option>
      <option value="3">3</option>
      <option value="4" selected>4</option>
    </select><br>
    <button type='submit'>save</button>        
  </form>
)";

static const char REDIRECT_HTML[] PROGMEM = R"(
<p id="tmr"></p>
<script>
  var c=6;   
  function count(){
    var tmr=document.getElementById('tmr');   
    if(c>0){
      c--;
      tmr.innerHTML="You will be redirected to home page in "+c+" seconds.";
      setTimeout('count()',1000);
    }else{
      window.location.href="/";
    }
  }
  count();
</script> 
)";

static const char OTA_HTML[] PROGMEM = R"(
<html><head> <title>OTA Update</title></head>
<body>
  <h1>OTA Update</h1>
  <p>Starting the update server.</p>
  <p>If no update starts in 5 minutes, will stop the update server and restore default functionallity.</p>
</body>
</html>
)";
/* Declaring a web server object. */
static ESP8266WebServer webServer(80);
static uint8_t maxPrimNumOfBtns = 4;
static uint8_t maxSecNumOfBtns = 4;

void showStartPage() { 
  String response = FPSTR(HTML_BEGIN);
  response += FPSTR(INDEX_HTML_0);
  response += "<div class='row'>";
  response += "<button class=\"btn_b\" type=\"button\" onclick=\"redirectTo(0)\"><</button>";
  if(maxPrimNumOfBtns > 1){
    response += "<button class=\"btn_b\" type=\"button\" onclick=\"redirectTo(1)\">></button>";
  }
  if(maxPrimNumOfBtns > 2){
    response += "<button class=\"btn_b\" type=\"button\" onclick=\"redirectTo(2)\">&frac12;</button>";
  }
  if(maxPrimNumOfBtns > 3){
    response += "<button class=\"btn_b\" type=\"button\" onclick=\"redirectTo(3)\">x</button>";
  }

  if(maxSecNumOfBtns > 0){
    response += "</div><hr>";

    response += "<div class='row'>";
    response += "<button class=\"btn_b\" type=\"button\" onclick=\"redirectTo(4)\"><</button>";
    if(maxSecNumOfBtns > 1){
      response += "<button class=\"btn_b\" type=\"button\" onclick=\"redirectTo(5)\">></button>";
    }
    if(maxSecNumOfBtns > 2){
      response += "<button class=\"btn_b\" type=\"button\" onclick=\"redirectTo(6)\">&frac12;</button>";
    }
    if(maxSecNumOfBtns > 3){
      response += "<button class=\"btn_b\" type=\"button\" onclick=\"redirectTo(7)\">x</button>";
    }
  }
  response += "</div>";

  response += FPSTR(INDEX_HTML_1); 
  response += FPSTR(HTML_END);
  webServer.send(200, "text/html", response);  
}

void buttonConfig() {   
  String response = FPSTR(HTML_BEGIN);

  if (webServer.hasArg("prim")) {
    String primNumOfButtons = webServer.arg("prim");
    int8_t primNo = primNumOfButtons.toInt();

    if((primNo > 0) && (primNo < 5)){
      maxPrimNumOfBtns = primNo;
    }        

    if (webServer.hasArg("sec")) {
      String secNumOfButtons = webServer.arg("sec");
      int8_t secNo = secNumOfButtons.toInt();

      if((secNo >= 0) && (secNo < 5)){
        maxSecNumOfBtns = secNo;
      }       
    }

    EEPROM.begin(EEPROM_SIZE);  
    EEPROM.put(BTN_NUM_ADDR, maxPrimNumOfBtns);
    EEPROM.put(BTN_NUM_ADDR+1, maxSecNumOfBtns);      
    EEPROM.commit();

    response += "<p>Successfully saved</p>";
    response += FPSTR(REDIRECT_HTML);
  }else{
    response += FPSTR(BTN_CFG_HTML);
  }  
  
  response += FPSTR(HTML_END);
  webServer.send(200, "text/html", response);  
}

static void trigger(void){
  if (webServer.hasArg("id")) {
    String idStr = webServer.arg("id");
    int id = idStr.toInt();

#ifdef DEV_IS_PRIMARY
    if(id < 4){
      PINCTRL_trigger(id);
    }else{
      UDP_send(id);
    }   
#else
    if(id > 3){
      int realId = id - 4;
      PINCTRL_trigger(realId);
    }  
#endif
  }
  showStartPage();  
}

static void showNotFound(void){
  webServer.send(404, "text/html; charset=iso-8859-1","<html><head> <title>404 Not Found</title></head><body><h1>Not Found</h1></body></html>"); 
}

void showID( void ) {    
  webServer.send(200, "text/plain", DEV_ID);  
}

static void showStatusPage(bool goToHome = false) {    
  Serial.println("showStatusPage");
  String response = FPSTR(HTML_BEGIN);
  response += "<h1>Connection Status</h1><p>";
  response += MAIN_getStatusMsg() + "</p>";
  if(goToHome){
    /* Add redirect timer. */
    response += FPSTR(REDIRECT_HTML);
  }
  response += FPSTR(HTML_END);
  webServer.send(200, "text/html", response);   
}

static void startOtaUpdate(void){
  String response = FPSTR(OTA_HTML);
  webServer.send(200, "text/html; charset=iso-8859-1", response); 
  webServer.handleClient(); 
  OTA_init();    
}

static void showRedirectPage(void){  
  showNotFound();
}

static void selectAP(void) {   
  Serial.println("selectAP");
  String response = FPSTR(HTML_BEGIN);
  response += FPSTR(APLIST_HTML_0);  
  response += FPSTR(APLIST_HTML_1);
  response += "Please wait...";  
  response += FPSTR(APLIST_HTML_2);   
  response += FPSTR(HTML_END);
  webServer.send(200, "text/html", response);  
}

/* Saves wifi settings to EEPROM */
static void saveWiFi(void){
  String ssid = webServer.arg("s");
  String pass = webServer.arg("p");
  String ipaddr = webServer.arg("a");
  
  if((ssid.length() > 63) || (pass.length() > 63)){
      MAIN_setStatusMsg("Sorry, this module can only remember SSID and a PASSWORD up to 63 bytes long.");
      showRedirectPage(); 
      return;
  } 

  IPAddress newStationIP;
  newStationIP.fromString(ipaddr);

  String st_ssid = "";
  String st_pass = "";
  IPAddress stationIP;

  if(ssid.length() > 0){
    bool cmpFlag = true;

    st_ssid = WIFIC_getStSSID();
    st_pass = WIFIC_getStPass();
    stationIP = WIFIC_getStIP();    

    if(!st_ssid.equals(ssid) || !st_pass.equals(pass)){
      cmpFlag = false;
    }
      
    if(cmpFlag){
       if((newStationIP[0] != stationIP[0]) || (newStationIP[1] != stationIP[1]) || (newStationIP[2] != stationIP[2]) || (newStationIP[3] != stationIP[3])){
          cmpFlag = false;
       }
    }
  
    if(cmpFlag){
      MAIN_setStatusMsg("All parameters are already set as requested.");
      showRedirectPage();      
      return;
    }   
  }
  
  WIFIC_setStSSID(ssid);
  WIFIC_setStPass(pass);
  WIFIC_setStIP(newStationIP); 

  String http_statusMessage;
  
  if(ssid.length() > 3){    
    http_statusMessage = "Saving settings and connecting to SSID: ";
    http_statusMessage += ssid; 
    http_statusMessage += " ,IP: ";
    
    http_statusMessage += ipaddr;   
    
  }else{       
    http_statusMessage = "Saving settings and switching to AP mode only.";    
  }
  http_statusMessage += "<br>If you can not connect to this device 20 seconds from now, please, reset it.";

  MAIN_setStatusMsg(http_statusMessage);
  showStatusPage();

  volatile int i;

  /* Keep serving http to display the status page*/
  for(i = 0; i < 100000; i++){
    webServer.handleClient(); 
    ESP.wdtFeed();
  } 

  /* WiFI config changed. Restart to apply. 
   Note: ESP.restart is buggy after programming the chip. 
   Just reset once after programming to get stable results. */

  ESP.restart();
}

void HTTP_process(void){
  webServer.handleClient(); 
}

void HTTP_init(void){ 
  EEPROM.begin(EEPROM_SIZE);

  uint8_t maxBtnCount;
  EEPROM.get(BTN_NUM_ADDR, maxBtnCount); 

  if((maxBtnCount > 0) && (maxBtnCount < 5)){
    maxPrimNumOfBtns = maxBtnCount;
  }

  EEPROM.get(BTN_NUM_ADDR+1, maxBtnCount);
  if((maxBtnCount >= 0) && (maxBtnCount < 5)){
    maxSecNumOfBtns = maxBtnCount;
  }

  webServer.on("/", showStartPage);
  webServer.on("/config", buttonConfig);
  webServer.on("/id", showID);
  webServer.on("/favicon.ico", showNotFound);
  webServer.on("/selectap", selectAP);
  webServer.on("/trigger", trigger);
  webServer.on("/wifisave", saveWiFi);
  webServer.on("/update", startOtaUpdate);  
  webServer.onNotFound(showStartPage);
  
  webServer.begin();
}
