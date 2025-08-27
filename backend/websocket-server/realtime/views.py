import redis
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view

@api_view(['GET'])
def health_check(request):
    return JsonResponse(
        {'status': 'healthy',
         'service': 'django-websocket'
        }
    )

@api_view(['GET'])
def get_current_stats(request):
    """REST endpoint to get current stats"""""
    try:
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
        stats = r.hgetall('daily_stats')

        return JsonResponse({
            'orders': int(stats.get('orders', 0)),
            'revenue': float(stats.get('revenue', 0.0)),
            'timestamp': r.get('last_update') or 'unknown'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status = 500)