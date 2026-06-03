import json
from typing import List, Dict
from aiokafka import AIOKafkaConsumer
from infrastructure.event_dispatcher import EventDispatcher
from utils.logger_interface import ILogger

class KafkaConsumer:
    def __init__(self, topics: List[str], 
                bootstrap_server: str, 
                group_id: str,
                event_dispatcher: EventDispatcher,
                logger: ILogger):
        self.topics = topics
        self.bootstrap_server = bootstrap_server
        self.group_id = group_id
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self.dispatcher= event_dispatcher
        self.logger = logger

    async def start(self):

        for topic in self.topics:
            self.logger.info(f"Initializing consumer for topic: {topic}")
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_server,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                group_id=self.group_id
            )
            await consumer.start()
            self.consumers[topic] = consumer

    async def stop(self):
        for consumer in self.consumers.values():
            await consumer.stop()
        self.consumers.clear()

    async def poll_events(self):
        """
        Polls one batch of messages from all consumers.
        """
        if not self.consumers:
            return

        for topic, consumer in self.consumers.items():
            # Poll for a small batch to avoid blocking the loop too long
            batch = await consumer.getmany(timeout_ms=10, max_records=100)

            for tp, messages in batch.items():
                for msg in messages:
                    self.dispatcher.dispatch(msg.value)
