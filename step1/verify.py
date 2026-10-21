import argparse
import sys

from schema import DATA_DIR, Paper, normalize, read_jsonl

# extra_url is reported but does not count towards the summary or pass/fail
SCORED_FIELDS = (
    "title",
    "paper_id",
    "author",
    "affiliation",
    "country",
    "abstract_url",
    "category",
)
FIELDS = (*SCORED_FIELDS, "extra_url")


def compare_field(expected: str | None, got: str | None) -> str:
    if expected is None:
        return "match" if got is None else "HALLUCINATION (expected null)"
    return "match" if normalize(expected) == normalize(got) else "mismatch"


def verify(short_name: str) -> int:
    truth = read_jsonl(DATA_DIR / "ground_truth" / f"{short_name}.jsonl")
    output = read_jsonl(DATA_DIR / "output" / f"{short_name}.jsonl")
    by_title: dict[str, Paper] = {normalize(p.title): p for p in output}

    found = matched = total = 0
    for expected in truth:
        got = by_title.get(normalize(expected.title))
        print(f"\n{expected.title}: {'found' if got else 'NOT FOUND'}")
        if got is None:
            continue
        found += 1
        for field in FIELDS:
            status = compare_field(getattr(expected, field), getattr(got, field))
            scored = field in SCORED_FIELDS
            if scored:
                total += 1
                matched += status == "match"
            print(f"  {field}{'' if scored else ' (not scored)'}: {status}")
            if status != "match":
                print(f"    expected={getattr(expected, field)!r}")
                print(f"    got     ={getattr(got, field)!r}")

    print(
        f"\nSummary: {found}/{len(truth)} papers found, "
        f"{matched}/{total} scored fields matched"
    )
    return 0 if found == len(truth) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("short_name", help="e.g. eacr-2026")
    sys.exit(verify(parser.parse_args().short_name))
