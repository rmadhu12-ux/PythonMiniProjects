import argparse
import logging
import sys
import httpx
from .pipeline import run

#run the below in cmd
"""python -m MiniProject.main --user-id 1
python -m MiniProject.main --help
python -m MiniProject.main
python -m MiniProject.main --user-id abc
python -m MiniProject.main --user-id 1 --out-dir out"""

def main():
    """parser = argparse.ArgumentParser(description="Fetch and summarize todos.")
    parser.add_argument("--user-id", type=int, required=True)
    parser.add_argument("--out-dir", default="data")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()"""

    #logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        #summary = run(args.user_id, args.out_dir)           # call run with args.user_id and args.out_dir
        summary = run(1, "out")
    except httpx.HTTPError as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    print(summary)


if __name__ == "__main__":
    main()