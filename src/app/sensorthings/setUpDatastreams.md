# Create SensorThings instances

for each using the POST method

## Thing

http://il081:8084/v1.0/Things

```
{
   "name": "Prusa i3",
   "description": "3D Printer Prusa i3 MK3 in the Iot Lab Salzburg on the central desk",
   "properties": {
      "kafka": {
         "hosts": [
            "il081:9093",
            "il082:9094",
            "il083:9095"
         ],
         "topics": {
            "logs": "dtz-logging",
            "metrics": "dtz-sensorthings"
         },
      "specification": "https://www.prusa3d.com/downloads/manual/prusa3d_manual_175_en.pdf"
      }
}

{
  "name": "Panda",
  "description": "Franka Emika Panda robot in the Iot Lab Salzburg on the central desk",
  "properties": {
    "specification": "https://s3-eu-central-1.amazonaws.com/franka-de-uploads-staging/uploads/2018/05/2018-05-datasheet-panda.pdf"
  }
}
```

## Location

for each Thing:

http://il081:8084/v1.0/Things(1)/Locations

http://il081:8084/v1.0/Things(2)/Locations

```
{
  "name": "IoT Labor Salzburg",
  "description": "IoT Labor of Salzburg Research",
  "encodingType": "application/vnd.geo+json",
  "location": {
    "type": "Point",
    "coordinates": [13.040670, 47.822784]
  }
}
```



## Sensor

http://il081:8084/v1.0/Sensors
```
{
  "name": "operator input on the operator dashboard",
  "description": "Input from the Prusa i3 3D Printer's operator Dashboard is streamed.",
  "encodingType": "application/pdf",
  "metadata": "https://github.com/iot-salzburg/dtz_operator-dashboard"
}
```


## Datastreams with Observed Properties

http://il081:8084/v1.0/Datastreams


```
{
  "name": "Filament Change",
  "description": "New Filament inserted into the Prusa 3D printer will be logged.",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
  "unitOfMeasurement": {
    "name": "filament",
    "symbol": "srfg.prusa3d.filament",
    "definition": "string"
      },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
      {
      "name": "Prusa i3 Filament Change",
      "description": "The Filament color and type of the Prusa i3 3D printer",
      "definition": "http://il081:6789/edit_filaments"
        },
  "Sensor":{"@iot.id":6}
}


{
  "name": "3D Print Annotations",
  "description": "Annotations of the print and printing process",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
  "unitOfMeasurement": {
    "name": "print annotation",
    "symbol": "srfg.prusa3d.annotation",
    "definition": "string"
  },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
    {
      "name": "Prusa i3 print annotation",
      "description": "Observations of the printing result of the Prusa i3.",
      "definition": "srfg.prusa3d.annotaion"
    },
  "Sensor":{"@iot.id":6}
}

{
  "name": "3D Print Nozzle Cleaning",
  "description": "Nozzle cleaning event of the Prusa i3",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
  "unitOfMeasurement": {
    "name": "nozzle cleaning",
    "symbol": "srfg.prusa3d.nozzle-cleaning",
    "definition": "string"
  },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
    {
      "name": "Prusa i3 nozzle cleaning event",
      "description": "Reported nozzle cleaning of the Prusa i3.",
      "definition": "srfg.prusa3d.nozzle-cleaning"
    },
  "Sensor":{"@iot.id":6}
}
```



# Getting corresponding datastreams:

http://il081:8084/v1.0/Datastreams(10)?$expand=ObservedProperty

