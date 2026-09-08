# @quantlab/output: 6aa053af
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('market_data', value=tick_data)
