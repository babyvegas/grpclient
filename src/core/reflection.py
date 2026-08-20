import argparse

import grpc
from grpc_reflection.v1alpha import reflection_pb2
from grpc_reflection.v1alpha import reflection_pb2_grpc


def list_services(host="localhost", port=50051):
    target = f"{host}:{port}"

    with grpc.insecure_channel(target) as channel:
        reflection_stub = reflection_pb2_grpc.ServerReflectionStub(channel)
        requests = iter(
            [reflection_pb2.ServerReflectionRequest(list_services="")]
        )

        for response in reflection_stub.ServerReflectionInfo(requests):
            if response.HasField("list_services_response"):
                return [
                    service.name
                    for service in response.list_services_response.service
                ]
            if response.HasField("error_response"):
                error = response.error_response
                raise RuntimeError(
                    f"Reflection error {error.error_code}: {error.error_message}"
                )

    return []


def main():
    parser = argparse.ArgumentParser(
        description="List services exposed through gRPC server reflection."
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=50051)
    args = parser.parse_args()

    for service_name in list_services(args.host, args.port):
        print(service_name)


if __name__ == "__main__":
    main()
