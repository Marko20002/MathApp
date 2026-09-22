import argparse
import csv
import json
import sys

from .data import load_csv


def main():
    parser = argparse.ArgumentParser(description="MathApp offline ML tools")
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("csv")
    training = commands.add_parser("train")
    training.add_argument("csv")
    training.add_argument("--output", required=True)
    training.add_argument("--include-pending", action="store_true")
    prediction = commands.add_parser("predict")
    prediction.add_argument("question")
    prediction.add_argument("--model", required=True)
    args = parser.parse_args()
    try:
        if args.command == "audit":
            _, result = load_csv(args.csv)
        elif args.command == "train":
            from .training import train
            result = train(args.csv, args.output, args.include_pending)
        else:
            from .inference import predict
            result = predict(args.question, args.model)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, csv.Error) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
