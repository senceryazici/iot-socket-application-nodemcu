#include <main.h>
#include <ESP8266mDNS.h>

#define DEVICE_ID 0
SFE_BMP180 pressure_sensor;
double baseline_pressure;

double getPressure(SFE_BMP180 *sensor);
double getTemperature(SFE_BMP180 *sensor);

void setup()
{
    Serial.begin(115200);
    Serial.print("Connecting to the Wifi with ssid '");
    Serial.print(ssid);
    Serial.println("'");

    WiFi.hostname("iot-device-" + String(DEVICE_ID));
    WiFi.mode(WIFI_STA);
    WiFi.config(ip, gateway, subnet);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("Connected to the Wifi with ssid '" + String(ssid) + "'");
    Serial.print("Device IP address: ");
    Serial.println(WiFi.localIP());
    if (!MDNS.begin("iot-device-" + String(DEVICE_ID)))
    {
        Serial.println("Error setting up MDNS responder!");
    }
    else
    {
        Serial.println("mDNS responder set up correctly.");
    }
    pressure_sensor.begin();
    baseline_pressure = getPressure(&pressure_sensor);
}

WiFiClient client;

void loop()
{
    Serial.println("Attempting connection to host@" + String(host) + ":" + String(port));

    if (!client.connect(host, port))
    {
        Serial.println("Attempt failed");
        delay(500);
        return;
    }

    Serial.println("Connection successfull on the host@" + String(host) + ":" + String(port));

    while (client.connected())
    {
        double pressure = getPressure(&pressure_sensor);
        String pressure_json = GetJSONString("pressure", String(pressure));
        client.println(pressure_json);

        double altitude = pressure_sensor.altitude(pressure, baseline_pressure);
        String altitude_json = GetJSONString("altitude", String(altitude));
        client.println(altitude_json);

        double temperature = getTemperature(&pressure_sensor);
        String temp_json = GetJSONString("temperature", String(temperature));
        client.println(temp_json);

        delay(500);
    }
    Serial.println("Lost connection to the host.");
    // while(client.available())
    // {
    //
    // }
    client.stop();
    delay(1000);
}

double getTemperature(SFE_BMP180 *sensor)
{
    char status;
    double T,P;
    status = sensor->startTemperature();
    if (status != 0)
    {
        delay(status);
        status = sensor->getTemperature(T);
        if (status != 0)
        {
            return(T);
        }
        else Serial.println("error retrieving temperature measurement\n");
    }
    else Serial.println("error starting temperature measurement\n");
}

double getPressure(SFE_BMP180 *sensor)
{
    char status;
    double T,P;
    status = sensor->startTemperature();
    if (status != 0)
    {
        delay(status);
        status = sensor->getTemperature(T);
        if (status != 0)
        {
            status = sensor->startPressure(3);
            if (status != 0)
            {
                delay(status);
                status = sensor->getPressure(P,T);
                if (status != 0)
                {
                    return(P);
                }
                else Serial.println("error retrieving pressure measurement\n");
            }
            else Serial.println("error starting pressure measurement\n");
        }
        else Serial.println("error retrieving temperature measurement\n");
    }
    else Serial.println("error starting temperature measurement\n");
}
