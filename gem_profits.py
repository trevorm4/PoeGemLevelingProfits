from argparse import ArgumentParser
import requests
from collections import defaultdict
import json
from pprint import pformat
import re

gem_url = "https://poe.ninja/api/data/itemoverview?league={0}&type=SkillGem"


def get_gem_data(league="Sentinel"):
    url = gem_url.format(league)
    r = requests.get(gem_url.format(league))
    return json.loads(r.text)


def extract_gem_info(lines: dict):
    new_dict = defaultdict(dict)
    for l in lines:
        new_dict[l["name"]][l["gemLevel"]] = {
            "quality": l.get("gemQuality", 0),
            "chaosValue": l["chaosValue"],
            "exValue": l["exaltedValue"],
            "listingCount": l.get("listingCount",0)
        }
    return new_dict


def get_level_difference(info_dict, lower_bound=1, upper_bound=21, pattern="", minimum_listed=1):
    differences = {}
    print(pattern)
    for k, v in info_dict.items():
        if len(re.findall(pattern, k)) > 0:
            if v.get(upper_bound) is None or v.get(lower_bound) is None or v[upper_bound]["listingCount"] < minimum_listed:
                continue
            differences[k] = {"profit" : v[upper_bound]["chaosValue"] - v[lower_bound]["chaosValue"], "numListed" : v[upper_bound]["listingCount"]}
    return differences

def do_calculations(league, pattern, start_level, end_level, min_listed, min_profit):
    data = get_gem_data(league)
    info_dict = extract_gem_info(data["lines"])
    diffs = get_level_difference(info_dict, lower_bound=start_level, upper_bound=end_level, pattern=pattern, minimum_listed=min_listed)
    return sorted(filter(lambda tup: tup[1]["profit"] > min_profit ,diffs.items()), key=lambda x: x[1]["profit"])
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--pattern", type=str, help="Gem regex to filter by (e.g. Awakened)", default=".*", nargs="?")
    parser.add_argument("--league", type=str, help="Name of League to filter by", default="Sentinel", nargs="?")
    parser.add_argument("--start_level", type=int, help="Gem starting level", default=1)
    parser.add_argument("--end_level", type=int, help="Gem Ending Level", nargs=1, default=20)
    parser.add_argument("--min_listed", type=int, help="Min number of gems listed to display in results", default=1)
    parser.add_argument("--min_profit", type=int, help="Min profit in chaos", default=1)
    args = parser.parse_args()
    print(pformat(do_calculations(args.league, args.pattern, args.start_level, args.end_level, args.min_listed, args.min_profit)))
