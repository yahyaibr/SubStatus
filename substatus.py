#!/usr/bin/env python3

import argparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import requests


from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_subdomain(subdomain):
    subdomain = subdomain.strip()
    if not subdomain:
        return None


    protocols = ["https", "http"]
    
    for proto in protocols:
        url = f"{proto}://{subdomain}"
        try:
            res = requests.get(
                url,
                timeout=5,
                allow_redirects=True,
                verify=False, 
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            return {
                "url": url,
                "status": res.status_code,
                "time": f"{res.elapsed.total_seconds():.3f}s"
            }
        except requests.RequestException:
            continue


    return {
        "url": subdomain,
        "status": "DOWN",
        "time": "-"
    }


def main():
    parser = argparse.ArgumentParser(description="Fast concurrent subdomain status checker")
    
    parser.add_argument("-f", "--file", help="Path to text file containing subdomains")
    parser.add_argument("-s", "--subdomains", nargs="+", help="List of subdomains separated by spaces")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Number of concurrent threads (default: 20)")

    args = parser.parse_args()


    if args.file:
        try:
            with open(args.file, "r") as f:
                subdomains = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            parser.error(f"Could not find or open file: {args.file}")
    elif args.subdomains:
        subdomains = args.subdomains
    else:
        parser.error("You must provide either a file (-f) or a list of subdomains (-s)")

    print(f"\n[*] Scanning {len(subdomains)} targets using {args.threads} threads...\n")
    print(f"{'URL':<45} {'STATUS':<10} {'RESPONSE TIME'}")
    print("-" * 70)

    results = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:

        raw_results = list(tqdm(
            executor.map(check_subdomain, subdomains), 
            total=len(subdomains), 
            desc="Progress", 
            leave=False
        ))
        

        results = [r for r in raw_results if r]


    print("\n" + "="*70)
    for res in results:
        print(f"{res['url']:<45} {res['status']:<10} {res['time']}")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Scan aborted by user.")
