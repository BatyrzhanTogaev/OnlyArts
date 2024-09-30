from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Artwork, Comment
from django.core.exceptions import ObjectDoesNotExist
import json

class ArtworkConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.artwork_id = self.scope['url_route']['kwargs']['artwork_id']
        self.artwork_group_name = f'artwork_{self.artwork_id}'

        # Присоединение к группе
        await self.channel_layer.group_add(
            self.artwork_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.artwork_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data['action']

        if action == 'like':
            artwork = await self.like_artwork()
            await self.channel_layer.group_send(
                self.artwork_group_name,
                {
                    'type': 'artwork_update',
                    'likes': artwork.likes,
                }
            )
        
        elif action == 'comment':
            comment_text = data['comment']
            comment = await self.save_comment(comment_text)
            await self.channel_layer.group_send(
                self.artwork_group_name,
                {
                    'type': 'comment_update',
                    'comment': comment.text,
                    'author': comment.author.username,
                }
            )

    async def artwork_update(self, event):
        await self.send(text_data=json.dumps({
            'likes': event['likes'],
        }))

    async def comment_update(self, event):
        await self.send(text_data=json.dumps({
            'comment': event['comment'],
            'author': event['author'],
        }))

    @sync_to_async
    def like_artwork(self):
        try:
            artwork = Artwork.objects.get(id=self.artwork_id)
            artwork.likes += 1
            artwork.save()
            return artwork
        except ObjectDoesNotExist:
            return None

    @sync_to_async
    def save_comment(self, text):
        try:
            artwork = Artwork.objects.get(id=self.artwork_id)
            comment = Comment.objects.create(
                artwork=artwork,
                author=self.scope['user'],
                text=text
            )
            return comment
        except ObjectDoesNotExist:
            return None
