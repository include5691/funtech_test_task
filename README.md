# funtech_test_task
Funtech test task

### Create Kafka topic
In this example we use bin files from [kafka download page](https://www.apache.org/dyn/closer.cgi?path=/kafka/4.0.0/kafka_2.13-4.0.0.tgz)

```shell
bin/kafka-topics.sh --create --topic new-orders --bootstrap-server localhost:9092
```