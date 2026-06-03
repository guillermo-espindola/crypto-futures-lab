import json


class KafkaUtils:

    # =====================================================
    # JSON LOADS
    # =====================================================

    @staticmethod
    def deserialize(message):

        if isinstance(message, bytes):

            message = message.decode(
                "utf-8"
            )

        return json.loads(message)

    # =====================================================
    # JSON DUMPS
    # =====================================================

    @staticmethod
    def serialize(data):

        return json.dumps(data).encode(
            "utf-8"
        )