import functools
import time
import pika
import json
import threading
from logical_module import get_data_and_process

class Rabbit_Consumer(object):
    """This is a main consumer class which is always in listening mode and it has the ability
    to reaconnect on failure connections .
    """
    EXCHANGE = None
    EXCHANGE_TYPE = 'fanout'
    QUEUE = ''
    ROUTING_KEY = ''
    CREDENTIALS = None
    HOSTNAME = None
    THREAD_LIST = []
    def __init__(self,host,username,password,exchange):

        self.should_reconnect = False
        self.was_consuming = False

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = ''
        self._consuming = False
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self._prefetch_count = 1
        self.HOSTNAME = host
        self.EXCHANGE = exchange
        self.CREDENTIALS = pika.credentials.PlainCredentials(username, password)


    def connect(self):



        return pika.SelectConnection(
            parameters=pika.ConnectionParameters(host=self.HOSTNAME, credentials=self.CREDENTIALS),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

        #return pika.BlockingConnection(pika.ConnectionParameters(host='192.168.18.27', credentials=self.CREDENTIALS))

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            #LOGGER.info('Connection is closing or already closed')
            print('Connection is closing or already closed')
        else:
            print('Closing connection')
            self._connection.close()

    def on_connection_open(self, _unused_connection):

        print('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):

        print('Connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):


        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            print('Connection closed, reconnect necessary: %s', reason)
            self.reconnect()

    def reconnect(self):

        self.should_reconnect = True
        self.stop()

    def open_channel(self):

        print('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):

        print('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):

        print('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):

        print('Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def setup_exchange(self, exchange_name):

        print('Declaring exchange: %s', exchange_name)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(
            self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=self.EXCHANGE_TYPE,
            callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):

        print('Exchange declared: %s', userdata)
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):

        print('Declaring queue %s', queue_name)
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name, callback=cb)

    def on_queue_declareok(self, _unused_frame, userdata):

        queue_name = userdata
        print('Binding %s to %s with %s', self.EXCHANGE, queue_name,self.ROUTING_KEY)
        cb = functools.partial(self.on_bindok, userdata=queue_name)
        self._channel.queue_bind(
            queue_name,
            self.EXCHANGE,
            routing_key=self.ROUTING_KEY,
            callback=cb)

    def on_bindok(self, _unused_frame, userdata):

        print('Queue bound: %s', userdata)
        self.set_qos()

    def set_qos(self):

        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):

        print('QOS set to: %d', self._prefetch_count)
        self.start_consuming()

    def start_consuming(self):

        print('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            self.QUEUE, self.on_message)
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):

        print('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):

        print('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()



    def acknowledge_message(self, delivery_tag):

        print('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):

        if self._channel:
            print('Sending a Basic.Cancel RPC command to RabbitMQ')
            cb = functools.partial(
                self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):

        self._consuming = False
        print('RabbitMQ acknowledged the cancellation of the consumer: %s',userdata)
        self.close_channel()

    def close_channel(self):

        print('Closing the channel')
        self._channel.close()

    def run(self):

        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):

        if not self._closing:
            self._closing = True
            print('Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            print('Stopped')

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        self.acknowledge_message(basic_deliver.delivery_tag)
        #print('Received message # %s from %s: %s',basic_deliver.delivery_tag, properties.app_id, body)
        data = json.loads(body)
        print(data)

        th = threading.Thread(target=get_data_and_process,args=(2,len(self.THREAD_LIST))).start()
        self.THREAD_LIST.append(th)
        #print(data['messege_type'])

class Reconnecting_Rabbit_Consumner(object):
    """This is reconnecting consumer that will reconnect if the nested
    Rabbit_Consumer indicates that a reconnect is necessary.
    """

    def __init__(self,host,username,password,exchange):
        self._reconnect_delay = 0
        self._consumer = Rabbit_Consumer(host,username,password,exchange)

    def run(self):
        while True:
            try:
                self._consumer.run()
            except KeyboardInterrupt:
                self._consumer.stop()
                break
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._consumer.should_reconnect:
            self._consumer.stop()
            reconnect_delay = self._get_reconnect_delay()
            print('Reconnecting after %d seconds', reconnect_delay)
            time.sleep(reconnect_delay)
            self._consumer = Rabbit_Consumer()

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay


def main():
    consumer = Reconnecting_Rabbit_Consumner(host='192.168.18.27',username='ocs',password='rapidev',exchange='control_exchange')
    consumer.run()


if __name__ == '__main__':
    main()