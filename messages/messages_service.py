from fastapi import FastAPI
from confluent_kafka import Consumer, KafkaException
import os
import threading
from ..common import funcs

messenger_service = FastAPI()

messenger_service.state.kafka_consumer = None
messenger_service.state.local_message_map = {} 
messenger_service.state.kafka_topic = ""
messenger_service.state.polling_thread = None

def poll_messages():
    while True:
        try:
            incoming_message = messenger_service.state.kafka_consumer.poll()
            
            if incoming_message is None:
                continue
            if incoming_message.error():
                raise KafkaException(incoming_message.error())
            else:
                messenger_service.state.local_message_map[incoming_message.key().decode('utf-8')] = incoming_message.value().decode('utf-8') 
                print(f"Messenger {os.getpid()} received message: {incoming_message.key().decode('utf-8')}:{incoming_message.value().decode('utf-8')}")
                
                messenger_service.state.kafka_consumer.commit(incoming_message)
        except RuntimeError as e:
            #probably consumer was closed
            print(f"Polling on messenger {os.getpid()} stopped!")
            break
        except KafkaException as e:
            print(f"Received kafka exception: {e}")
            break
        
@messenger_service.on_event("startup")
async def start_messanger():
    messenger_config = funcs.read_value_for_key("messenger_config")
    
    messenger_service.state.kafka_topic = messenger_config['topic_name']
    messenger_service.state.kafka_consumer = Consumer(messenger_config['kafka_config'])

    messenger_service.state.kafka_consumer.subscribe([messenger_service.state.kafka_topic])
    
    port = os.environ["INSTANCE_PORT"]
    funcs.register_consul_service("messenger", port, os.environ["INSTANCE_HOST"], int(port), 30, 60, "/health" )
        
    messenger_service.state.polling_thread = threading.Thread(target=poll_messages,name="Poller",daemon=True)
    messenger_service.state.polling_thread.start()
    
    print(f"Messenger {os.getpid()} started!")
    
@messenger_service.on_event("shutdown")
async def terminate_messenger():
    messenger_service.state.kafka_consumer.close()
    print(f"Messenger {os.getpid()} terminated!")
    
@messenger_service.get("/health")
async def check():
    return f"Messenger {os.getpid()} is healthy"

@messenger_service.get("/messenger/messages", response_model=str)
def access_messenger() -> str:
    print(f"Messages stored on messenger {os.getpid()}: {messenger_service.state.local_message_map}")
    return ' ; '.join([msg_body for msg_body in messenger_service.state.local_message_map.values()])
