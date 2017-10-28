#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import json
from time import time, sleep
from random import randint, choice

from kafka import KafkaProducer

KAFKA_IP_ADDRESS = '10.10.10.66:9092'
step = 5

def norm(x, sigma, mu):
    return (1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - ((x - mu)**2 / (2 * sigma**2) )))

def main ():
    sigma = 0.1
    mu = 0.7
    input_array = np.arange(0.0, 1.01, 0.01)
    vfunc = np.vectorize(norm)
    output_array = vfunc(input_array, sigma, mu)
    max_array = max(output_array)
    output = [round(1+(99*i/max_array), 2) for i in output_array]

    input_topic="alarms"
    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_IP_ADDRESS)
        pass
    except Exception as e:
        print "Kafka not found. Shutting down"
        exit(0)

    while True:
        for share in output:
            now = int(round(time()))
            item = {"date": now, "total": 100, "congested": round(share, 0)}
            message = json.dumps(item)
            print message
            producer.send(input_topic, bytes(message))
            sleep(step)

if __name__ == "__main__":
    main()
