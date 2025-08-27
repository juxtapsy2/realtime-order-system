from confluent_kafka import Producer
import json
import time
import random

# Kafka configuration
config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'order-producer'
}

# Create producer
producer = Producer(config)

def delivery_callback(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'✅ Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

print("🚀 Starting order producer...")
print("Press Ctrl+C to stop")
print("-" * 50)

try:
    for i in range(100):
        order = {
            "orderId": f"ORD-{i:03d}",
            "customerId": f"CUST-{random.randint(100, 999)}",
            "amount": round(random.uniform(10, 500), 2),
            "timestamp": time.time(),
            "status": "pending",
            "products": [
                {
                    "productId": f"PROD-{random.randint(1, 50)}",
                    "quantity": random.randint(1, 5),
                    "price": round(random.uniform(5, 100), 2)
                }
            ]
        }
        
        # Convert to JSON string
        message_value = json.dumps(order)
        
        # Send message
        producer.produce(
            'orders-stream', 
            key=order['orderId'],
            value=message_value,
            callback=delivery_callback
        )
        
        print(f"📦 Sent order {order['orderId']} - ${order['amount']} - Customer: {order['customerId']}")
        
        # Trigger delivery callbacks
        producer.poll(0)
        
        time.sleep(2)  # Send every 2 seconds
        
except KeyboardInterrupt:
    print("\n⏹️  Stopping producer...")
finally:
    # Wait for any outstanding messages to be delivered
    print("🔄 Flushing remaining messages...")
    producer.flush()
    print("✅ Producer stopped successfully!")