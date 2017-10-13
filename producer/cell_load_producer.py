#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from time import time, sleep
from random import randint

from kafka import KafkaProducer

KAFKA_IP_ADDRESS = '10.10.10.66:9092'
cells = ['23', '3456', '522', '10', '444', '10456', '23', '24', '25', '33', '99', '105', '1']
step = 5

def main ():
    input_topic="load"
    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_IP_ADDRESS)
        pass
    except Exception as e:
        print "Kafka not found. Shutting down"
        exit(0)

    while True:
        now = int(round(time()))
        for cell in cells :
            item = {"cell": cell, "date": now, "load": randint(0, 60)}
            message = json.dumps(item)
            print message
            producer.send(input_topic, bytes(message))
        sleep(step)

if __name__ == "__main__":
    main()