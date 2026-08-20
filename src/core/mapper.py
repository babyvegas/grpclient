import logging

import grpc
from .protos import helloworld_pb2
from .protos import helloworld_pb2_grpc


def map():
    names = {"name":"Donovan"}
    print("Mapping request")
    request = helloworld_pb2.HelloRequest
    for _ in names:
        name = names.name
        request.name = name
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(request)
    print("Greeter client received: " + response.message)


if __name__ == "__main__":
    logging.basicConfig()
    map()