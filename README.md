# Operator Dashboard

This Software provides a dashboard for operational 3d printer data.

## Start

```bash
./src/operator_dashboard.py
```

Visit:
[http://hostname:6789/dashboard](http://hostname:6789/dashboard)

Here you can submit a filament change and annotate
 information to a print.


To view the status:
[http://hostname:6789/status](http://hostname:6789/status)


## Docker deployment

Build local Docker image:
```bash
sudo docker-compose up --build
```


## Add, edit or delete a filament

You can edit the filament list on
[http://hostname:6789/edit_filaments](http://hostname:6789/edit_filaments)

Be sure that you submit a valid json file.
If everything works well, you will be redirected to the valid json file.


# Connect to the i-Maintenance Messaging System:

1)  Logging messages to Logstash:
    Set LOGSTASH_HOST (here: il060)

2) Install librdkafka and pip confluent-kafka in Dockerfile

3)  Create a new Kafka Topic in Kafka Broker:
    ```bash
    kafka-topics --create --zookeeper localhost:2181 --replication-factor 3 --partitions 3 --topic OperatorData
    ```

    View the entries with
    ```bash
    kafka-console-consumer --bootstrap-server localhost:9092 \
    --topic OperatorData \
    --from-beginning \
    --formatter kafka.tools.DefaultMessageFormatter \
    --property print.key=true \
    --property print.value=true \
    --property key.deserializer=org.apache.kafka.common.serialization.StringDeserializer \
    --property value.deserializer=org.apache.kafka.common.serialization.StringDeserializer
    ```

4) Create the SensorThings topics:
