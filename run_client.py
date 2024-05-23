import argparse, threading
from src.client import Client


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--name', type=str, required=True,
        help='The identifier of the user.'
    )
    parser.add_argument(
        '--port', type=int, required=True,
        help='Port of the server to connect to.'
    )
    parser.add_argument(
        '--logs', action='store_true'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    client = Client(name=args.name, port=args.port, logs=args.logs)
    input_thread = threading.Thread(
        target=client.try_send_message_forever
    )
    input_thread.start()
    client.try_commucate_forever()
    