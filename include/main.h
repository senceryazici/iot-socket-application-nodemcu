#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <params.h>
#include <SFE_BMP180.h>
#include <Wire.h>

String GetJSONString(String name, String value)
{
    return "{'time':" + String(millis()) + "," + "'device':" + String(DEVICE_ID) + ",'" + name + "':" + value + "}";
}
