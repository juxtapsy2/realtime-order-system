import json
import asyncio
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

class OrderdashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get API key
        api_key = self.scope['query_string'].decode().split('api_key=')[-1]

        if api_key not in settings.API_KEYS:
            await self.close(code=4001)
            return
        await self.accept()

        # Redis connect
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_response=True
        )

        # Start senmding updates
        self.send_updates = True
        asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        self.send_updates = False
        if hasattr(self, 'redis_client'):
            await self.redis_client.close()
    
    async def send_periodic_updates(self):
        while self.send_updates:
            try:
                # Get stats from Redis
                stats = await self.redis_client.hgetall('daily_stats')
                
                update_data = {
                    'type': 'order_update',
                    'data': {
                        'orders': int(stats.get('orders', 0)),
                        'revenue': float(stats.get('revenue', 0.0)),
                        'timestamp': asyncio.get_event_loop().time()
                    }
                }

                await self.send(text_daa=json.dumps(update_data))
                await asyncio.sleep(3) # Send updates every 3 secs

            except Exception as e:
                print(f"Error sending update: {e}")
                await asyncio.sleep(5)