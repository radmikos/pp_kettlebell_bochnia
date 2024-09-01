import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ResultsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'results_amator_kobiety_do_65kg'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'results_update',
                'message': message
            }
        )

    # Receive message from room group
    async def results_update(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))