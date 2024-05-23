import argparse
from src.server import Server


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', type=int, default=5451,
        help='Port on which server will be listening.'
    )
    parser.add_argument(
        '--nbits', type=int, default=512,
        help='The length of the primary number in the binary form.'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    server = Server(
        port=args.port, n_bits=args.nbits
    )
    server.serve_forever()