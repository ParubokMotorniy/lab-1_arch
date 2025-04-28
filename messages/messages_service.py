from fastapi import FastAPI
from confluent_kafka import Consumer, KafkaException
import os
import threading
from ..common import funcs


kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id':          'kafka-servitor',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit' : True
}

messenger_service = FastAPI()
kafka_consumer = Consumer(kafka_config)

messenger_service.state.local_message_map = {} 
messenger_service.state.kafka_topic = ""
messenger_service.state.polling_thread = None

def poll_messages():
    while True:
        try:
            incoming_message = kafka_consumer.poll()
            
            if incoming_message is None:
                continue
            if incoming_message.error():
                raise KafkaException(incoming_message.error())
            else:
                messenger_service.state.local_message_map[incoming_message.key().decode('utf-8')] = incoming_message.value().decode('utf-8') 
                print(f"Messenger {os.getpid()} received message: {incoming_message.key().decode('utf-8')}:{incoming_message.value().decode('utf-8')}")
                
                kafka_consumer.commit(incoming_message)
        except RuntimeError as e:
            #probably consumer was closed
            print(f"Polling on messenger {os.getpid()} stopped!")
            break
        except KafkaException as e:
            print(f"Received kafka exception: {e}")
            break
        
@messenger_service.on_event("startup")
async def start_messanger():
    messenger_service.state.kafka_topic = os.environ["MESSAGING_KAFKA_TOPIC"].strip() 
    
    kafka_consumer.subscribe([messenger_service.state.kafka_topic])
    
    port = os.environ["INSTANCE_PORT"]
    funcs.register_consul_service("messenger", port, os.environ["INSTANCE_HOST"], int(port), 30, 60, "/health" )
        
    messenger_service.state.polling_thread = threading.Thread(target=poll_messages,name="Poller",daemon=True)
    messenger_service.state.polling_thread.start()
    
    print(f"Messenger {os.getpid()} started!")
    
@messenger_service.on_event("shutdown")
async def terminate_messenger():
    kafka_consumer.close()
    print(f"Messenger {os.getpid()} terminated!")
    
@messenger_service.get("/health")
async def check():
    return f"Messenger {os.getpid()} is healthy"

@messenger_service.get("/messenger/messages", response_model=str)
def access_messenger() -> str:
    print(f"Messages stored on messenger {os.getpid()}: {messenger_service.state.local_message_map}")
    return ' ; '.join([msg_body for msg_body in messenger_service.state.local_message_map.values()])
