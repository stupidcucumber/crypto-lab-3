import argparse
from src.server import Server


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', type=int, default=5451,
        help='Port on which server will be listening.'
    )
    parser.add_argument(
        '-p', type=int, required=True,
        help='Primary number p.'
    )
    parser.add_argument(
        '-g', type=int, required=True,
        help='Primary number g.'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    server = Server(
        port=args.port, p=args.p, g=args.g
    )
    server.serve_forever()