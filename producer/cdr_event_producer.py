#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from time import time, sleep
from random import randint, choice

from kafka import KafkaProducer

KAFKA_IP_ADDRESS = '10.10.10.66:9092'
cells = ['23', '3456', '522', '10', '444', '10456', '23', '24', '25', '33', '99', '105', '1']

def main ():
    input_topic="cdr"
    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_IP_ADDRESS)
        pass
    except Exception as e:
        print "Kafka not found. Shutting down"
        exit(0)

    while True:
        cdr_queue = []
        for i in range (100):
            now = int(round(time()))
            start = now + randint(0, 30)
            end = start + randint(0, 60)
            cell = choice(cells)
            start_time = [start, cell, 'start']
            end_time = [end, cell, 'end']
            cdr_queue.append(start_time)
            cdr_queue.append(end_time)
        cdr_queue.sort(key=lambda x: x[0])
        start_tick = now = int(round(time()))
        for item in cdr_queue:
            message = ';'.join([str(token) for token in item])
            sleep(item[0]-start_tick)
            print message
            start_tick = item[0]
            producer.send(input_topic, bytes(message))

if __name__ == "__main__":
    main()