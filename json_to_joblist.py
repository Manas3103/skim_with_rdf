import json
import argparse

def json_to_joblist(json_file, output_txt):
    with open(json_file, "r") as f:
        data = json.load(f)

    with open(output_txt, "w") as out:
        for process, content in data.items():
            parts = content.get("files", {})

            # sort parts numerically (part1, part2, ...)
            sorted_parts = sorted(parts.keys(), key=lambda x: int(x.replace("part","")))

            for part in sorted_parts:
                out.write(f"{process} {part}\n")

    print(f"Job list written to {output_txt}")


def main():
    parser = argparse.ArgumentParser(description="Convert dataset JSON to HTCondor job list")
    parser.add_argument("json_file", help="Input JSON dataset file")
    parser.add_argument("-o", "--output", default="jobs.txt", help="Output txt file (default: jobs.txt)")

    args = parser.parse_args()

    json_to_joblist(args.json_file, args.output)


if __name__ == "__main__":
    main()
