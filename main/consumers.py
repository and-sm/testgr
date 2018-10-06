from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class Consumer(WebsocketConsumer):

    def connect(self):

        self.groups = self.scope['url_route']['kwargs']['route']

        async_to_sync(self.channel_layer.group_add)(
            self.groups,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.groups,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to group of channel
        async_to_sync(self.channel_layer.group_send)(
            self.groups,
            {
                'type': 'message',
                'message': message
            }
        )

    # Receive message from channel
    def message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

