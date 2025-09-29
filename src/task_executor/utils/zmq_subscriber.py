import zmq

class ZMQSubscriber:
    def __init__(self, host, port, topic):
        self.ctx = zmq.Context()
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect(f"tcp://{host}:{port}")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.topic = topic

    def recv(self, flags: int = 0, timeout: int = 1000) -> tuple[str, str] | tuple[None, None]:
        try:
            poller = zmq.Poller()
            poller.register(self.sub, zmq.POLLIN)
            socks = dict(poller.poll(timeout))
            if self.sub in socks and socks[self.sub] == zmq.POLLIN:
                raw = self.sub.recv_string(flags=flags)
                if raw is None:
                    return None, None
                topic, payload = raw.split(" ", 1)
                if topic.startswith(self.topic):
                    return topic, payload
            return None, None
        except zmq.Again:
            return None, None
        except Exception as e:
            print(f"[ZMQSubscriber] Error: {e}")
            return None, None
