/**********************************************************************
 * 
 * Measuring the speed of lizards using optical gates.
 * ATmega328P (Arduino Nano), 16 MHz, PlatformIO
 *
 * Copyright (c) 2023 Tomas Fryza
 * Dept. of Radio Electronics, Brno University of Technology, Czechia
 * This work is licensed under the terms of the MIT license.
 *
 **********************************************************************/


/* Defines -----------------------------------------------------------*/
#define NGATES 11
#define PIN_LED 13    // SCK
#define PIN_DHT11 11  // MOSI
#define TIMEOUT_MILLIS 5000  // 5 seconds

/* Includes ----------------------------------------------------------*/
#include "Arduino.h"
#include <dht.h>


/* Global variables --------------------------------------------------*/
// Pin ID for optical gates
uint8_t gates[NGATES] = {
        7, 6, 5, 4, 3, 2, 16, 17, 18, 19, 15
    };

// Temperature and humidity sensor DHT11
dht DHT;

uint8_t measure_en = 0;
uint8_t measure_id = 0;
uint8_t measured_num = 0;


/* Function definitions ----------------------------------------------*/
/**********************************************************************
 * Function: setup()
 * Purpose:  Setup function where the program execution begins. Init 
 *           serial communications, GPIO pins, and perform functionality
 *           tests of optical gates.
 * Returns:  none
 **********************************************************************/
void setup()
{
    // Setup UART communication with Serial monitor in Arduino IDE
    Serial.begin(9600);

    // Setup input pins for optical gates
    for (uint8_t i = 0; i < NGATES; i++) {
        pinMode(gates[i], INPUT_PULLUP);
    }

    // Setup output pin for status LED
    pinMode(PIN_LED, OUTPUT);

    // Setup input pin for DHT11 sensor
    pinMode(PIN_DHT11, INPUT_PULLUP);

    // Test signals from all gates
    Serial.print("\r\nTest of optical gates ");
    for (uint8_t i = 0; i < NGATES; i++) {
        uint8_t state = digitalRead(gates[i]);
        if (state == 0) {  // Signal OK
            Serial.print(".");
        }
        else {
            Serial.print("#");
            Serial.print(i, DEC);
            Serial.print(" Error ");
        }
        delay(100);
    }
    Serial.println(" done");

    Serial.println("Press 'S' to start");
    Serial.println("id;time0;time1;time2;time3;time4;time5;time6;time77;time8;time9;time10;humid;temp");
}


/**********************************************************************
 * Function: loop()
 * Purpose:  Infinite loop. This function is executed over and over 
 *           again. Check values from optical gates, measure the time
 *           and send it to the UART. Use Serial Monitor to view it.
 * Returns:  none
 **********************************************************************/
void loop()
{
    uint8_t ch;

    uint8_t measured_status[NGATES] = {0};
    unsigned long measured_time[NGATES] = {0};
    unsigned long start_millis;
    unsigned long current_millis;

    // Wait for Start from UART: key "S"
    if (Serial.available() > 0) {
        ch = Serial.read();
        if ((ch == 'S') || (ch == 's')) {
            measure_en = 1;
        }
    }

    // Start measurement
    if (measure_en == 1) {
        // Turn Status LED on
        digitalWrite(PIN_LED, 1);

        // Wait for the first optical gate
        uint8_t i = 0;
        uint8_t state;
        do {
            i++;
            if (i >= NGATES)
                i = 0;
            state = digitalRead(gates[i]);
        } while (state == 0);

        // Reference time of the first gate
        start_millis = millis();

        // Store measured values
        measured_status[i] = 1;
        measured_time[i] = 0;
        measured_num = 1;
        Serial.println(i);

        // Read all other optical gates
        do {
            i++;
            if (i >= NGATES)
                i = 0;
            state = digitalRead(gates[i]);
            current_millis = millis();
            if (state == 1) {
                if (measured_status[i] == 0) {
                    measured_status[i] = 1;
                    measured_time[i] = current_millis - start_millis;
                    measured_num++;
                    Serial.println(i);
                }
            }
        } while ((measured_num < NGATES) && (current_millis - start_millis <= TIMEOUT_MILLIS));

        // Display measurement ID
        Serial.print(measure_id++);

        // Display measured times
        for (uint8_t i = 0; i < (NGATES); i++) {
            Serial.print(";");
            if (measured_status[i] == 1)
                Serial.print(measured_time[i]);
            else
                Serial.print("-");
        }

        // Read and display DHT11 data
        DHT.read11(PIN_DHT11);
        Serial.print(";");
        Serial.print(DHT.humidity, 0);
        Serial.print(";");
        Serial.println(DHT.temperature, 0);

        // Clear measured values
        for (uint8_t i = 0; i < (NGATES); i++) {
            measured_status[i] = 0;
            measured_time[i] = 0;
        }

        // Turn Status LED off
        digitalWrite(PIN_LED, 0);

        // Measurement is over
        measure_en = 0;
    }
}
