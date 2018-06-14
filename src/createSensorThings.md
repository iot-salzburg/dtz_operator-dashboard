# RESTful API to create SensorThings instances

**Universal Sensor**

POST, http://il060:8082/v1.0/Sensors
```
{
  "name": "3DPrintOperatorDashboard",
  "description": "Interactions from the Operator Dashboard made by the operator.",
  "encodingType": "application/pdf",
  "metadata": "http://il050:6789/dashboard"
}
```

## Filament Changes

**Observed Properties**

POST, http://il060:8082/v1.0/ObservedProperties
```
{
  "name": "3D Printer Filament Type",
  "description": "The type of filament used by the printer",
  "encodingType": "application/pdf",
  "definition": "http://il050:6789/edit_filaments"
}
```

**Datastream**

POST, http://il060:8082/v1.0/Datastreams
```
{
	"name": "3DPrinterFilamentChange",
	"description": "The type and color of filament which is used by the 3D printer",
	"observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
	"unitOfMeasurement": {
		"defitintion": "filament string",
		"name": "3D Printer Filament",
		"symbol": "srfg.3DPrinterFilament" },
    "Thing":{"@iot.id":1},
    "ObservedProperty":{"@iot.id":35},
    "Sensor":{"@iot.id":10}
}
```


## Printing Annotations

**Observed Properties**

POST, http://il060:8082/v1.0/ObservedProperties
```
{
  "name": "3D Prints annotation",
  "description": "Annotations of the latest prints",
  "encodingType": "application/pdf",
  "definition": "http://il050:6789/definition_annotation"
}
```



**Datastream**

POST, http://il060:8082/v1.0/Datastreams
```
{
	"name": "3DPrintAnnotations",
	"description": "Annotations of the latest print.",
	"observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
	"unitOfMeasurement": {
		"defitintion": "annotation string",
		"name": "3D Print Annotation",
		"symbol": "srfg.3DPrintAnnotations" },
    "Thing":{"@iot.id":1},
    "ObservedProperty":{"@iot.id":36},
    "Sensor":{"@iot.id":10}
}
```


## Nozzle Cleansing

**Observed Properties**

POST, http://il060:8082/v1.0/ObservedProperties
```
{
  "name": "3D Printer Nozzle Cleansing",
  "description": "A cleaning of the nozzle occured",
  "encodingType": "application/pdf",
  "definition": "http://il050:6789/nozzle_cleanings"
}
```

**Datastream**

POST, http://il060:8082/v1.0/Datastreams
```
{
	"name": "3DPrinterNozzleCleansing",
	"description": "The nozzle of the 3D printer was cleaned",
	"observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
	"unitOfMeasurement": {
		"defitintion": "the event triggers a 1 flag",
		"name": "eventFlag",
		"symbol": "srfg.3DPrinterNozzleCleansing" },
    "Thing":{"@iot.id":1},
    "ObservedProperty":{"@iot.id":37},
    "Sensor":{"@iot.id":10}
}
```
