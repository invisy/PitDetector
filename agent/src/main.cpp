#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <Ethernet.h>
#include <PubSubClient.h>


Adafruit_MPU6050 mpu;

void setup()
{
	Serial.begin(9600);

	if (!mpu.begin())
	{
		Serial.println("MPU-6050 sensor init failed");
		while (1)
			yield();
	}
	Serial.println("Found a MPU-6050 sensor");
}

void loop()
{
	sensors_event_t a, g, temp;
  	mpu.getEvent(&a, &g, &temp);

	Serial.print("Accelerometer ");
	Serial.print("X: ");
	Serial.print(a.acceleration.x, 1);
	Serial.print(" m/s^2, ");
	Serial.print("Y: ");
	Serial.print(a.acceleration.y, 1);
	Serial.print(" m/s^2, ");
	Serial.print("Z: ");
	Serial.print(a.acceleration.z, 1);
	Serial.println(" m/s^2");

	Serial.print("Gyroscope ");
	Serial.print("X: ");
	Serial.print(g.gyro.x, 1);
	Serial.print(" rps, ");
	Serial.print("Y: ");
	Serial.print(g.gyro.y, 1);
	Serial.print(" rps, ");
	Serial.print("Z: ");
	Serial.print(g.gyro.z, 1);
	Serial.println(" rps");
}