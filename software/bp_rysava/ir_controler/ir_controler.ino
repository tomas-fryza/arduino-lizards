  int pinOut [11] = {2, 3, 4, 5, 6, 7, 19, 18, 17, 16, 15}; //vzdy 5. pin od shora

  //int time_measured [11]; //matice pro vysledne casy
  int sensor = 0;
  bool run_direction = 0;
  bool experiment_run = 0;
  bool stav;
  bool eneable = 0;
  int input_string = 0;
  unsigned long time1 = 0;
  unsigned long time2 = 0;
  unsigned long measured_time = 0;
  int last = 10;
  int first = 0;
  int err_count = 0;
  int err_pin [3] = {-1, -1, -1};
  
void setup() {
  Serial.begin(9600);
  for (int i=0; i < last+1; i++){
    pinMode(pinOut[i], INPUT_PULLUP);
  }
  
  //pokud je brana difoltne prerusena, nahlasi se chyba a cislo brany
  for (int i=0; i < last+1; i++){
      stav = !(digitalRead(pinOut[i]));
      if (not stav) {
        Serial.print("ERR");
        Serial.print(" ");
        Serial.print(i);
        Serial.println();
        if (err_count<3){
          err_pin[err_count]=i;
          err_count++;
        }
        else{
          Serial.print("SER_ERR");  //pokud jsou preruseny vice nez 3 chyby, nahlasi se severe error
          Serial.print(" ");
          Serial.print(i);
          Serial.println();
        }
        //reseni nefunkcnich koncovych bran
        if (i == first){ 
          first = first+1;
        }
        else if (i==last){
          if (last-1 != err_pin[0] and last-1 != err_pin[1] and last-1 != err_pin[2]){
            last = last-1;
          }
          else if(last-2 != err_pin[0] and last-2 != err_pin[1] and last-2 != err_pin[2]){
            last = last-2;
          }
          else{
            last = last-3;
          }
        }
      }
  }
}


//hlavní program
void loop() {
//čtení eneable
  if (Serial.available() > 0){
    input_string = Serial.read();
    if (input_string == 48){
      eneable = 0;
    }
    else if (input_string == 49){
      eneable = 1;
    }
    //pokud je pokus zastaven externě, program vrátí poslední čas
    if (eneable == 0 & experiment_run == 1){
      time2 = millis();
      measured_time = time2-time1;
      time1 = time2;
      Serial.print("x");
      Serial.print(" ");
      Serial.print(measured_time);
      Serial.println();
      experiment_run = 0;
    }
  }  
  
  //povolení pokusu
  if (eneable){

    //pokus ještě nezačal, hlídá se první přerušení brány
    if (not experiment_run){
      for (int i=0; i < last+1; i++){
        stav = !(digitalRead(pinOut[i]));
        //pokud je přerušena první nebo poslední brána, určí se směr měření a zahájí se pokus
        if (not stav and i != err_pin[0] and i != err_pin[1] and i != err_pin[2]) {
          if (i==first){
            run_direction = 0;
          }else if (i==last){
            run_direction = 1;
          }else {
            //send warning
            Serial.print("WAR ");
            Serial.print(i);
            Serial.println();

            if (i>5){
              run_direction = 1;
            }else{
              run_direction = 0;
            }
          }
          experiment_run=1;
          sensor = i;
          //set timer
          time1 = millis(); 
          Serial.print(i);
          Serial.print(" 0");
          Serial.println();
        }
      }
      
    }else {
      for (int i=0; i < last+1; i++){
        stav = !(digitalRead(pinOut[i]));
         if (not stav and i != err_pin[0] and i != err_pin[1] and i != err_pin[2]){             //pokud byla prerusena nejaka brana
          if (not run_direction){   //pokud je smer 0-11
            if (sensor<i){          //pokud byla prerusena nektera dalsi brana v poradi
              //write time
              time2 = millis();
              measured_time = time2-time1;
              time1 = time2;
              Serial.print(i);
              Serial.print(" ");
              Serial.print(measured_time);
              Serial.println();
              sensor = i;
            }
            if (i==last){
              eneable=0;
              Serial.print("END");
              experiment_run = 0;
            }
          }else{                    //pokud je smer v opacnem poradi
            if (sensor>i){          //pokud byla prerusena nektera dalsi brana v poradi
              //write time
              time2 = millis();
              measured_time = time2-time1;
              time1 = time2;
              Serial.print(i);
              Serial.print(" ");
              Serial.print(measured_time);
              Serial.println();
              sensor = i;
            }
            if (i==first){
              eneable=0;
              Serial.print("END");
              experiment_run = 0;
            }
          }
        }
      }
    }
  }
}
