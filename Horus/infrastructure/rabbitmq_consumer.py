import pika
import json

from typing import List

from infrastructure.event_dispatcher import EventDispatcher
from utils.logger_interface import ILogger

class RabbitMQConsumer:

    def __init__(self, tag: str, connection_string: str, queues: List[str], event_dispatcher: EventDispatcher, logger: ILogger):
        self._tag = tag
        self._connection_string = connection_string
        self._queues = queues
        self._event_dispatcher = event_dispatcher
        self._logger = logger


    def callback_factory(self, queue_name):
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode("utf-8"))
                self._event_dispatcher.dispatch(message)
            except Exception as e:
                self._logger.error(e)
            finally:
                ch.basic_ack(delivery_tag=method.delivery_tag)
        return callback


    def start(self):
        connection = pika.BlockingConnection(pika.URLParameters(self._connection_string))
        channel = connection.channel()

        for queue in self._queues:
            channel.queue_declare(
                queue=queue,
                durable=False,
                auto_delete=True
            )

            channel.basic_consume(
                queue=queue,
                on_message_callback=self.callback_factory(queue),
                consumer_tag=f"{self._tag}-{queue}"
            )
            self._logger.info(f"[START] Consumer {queue}")

        self._logger.info(f"[START] Waiting for messages")
        channel.start_consuming()
