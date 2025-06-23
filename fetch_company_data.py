import requests
import json
import re
import os
import sys
import shutil

platforms = {
    'H': "hackerone",
}


def show_help():
    print("""
    Usage: 
      python fetch_company_data.py <company_name> <platform_code>

    Arguments:
      <company_name>   Name of the company (e.g., oppo)
      <platform_code>  Platform short code:
                       H - HackerOne
                       Planning to support more platforms in the future

    Example:
      python fetch_company_data.py oppo H
    """)


def clean_domain(raw):
    raw = raw.strip()
    raw = re.sub(r'^https?://', '', raw)
    raw = raw.lstrip('*.')
    return raw


def main():
    if "--h" in sys.argv or len(sys.argv) != 3:
        show_help()
        return
    company_name = sys.argv[1].strip()
    platform = sys.argv[2].strip()

    if platform not in platforms:
        print("[!] Invalid platform code. Use --h to see help.")
        return
    platform = platforms[platform]
    data_url = f"https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/{platform}_data.json"

    try:
        response = requests.get(data_url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        return

    company = next((i for i in data if company_name.lower() in i.get("handle", "").lower()), None)
    if not company:
        company = next((i for i in data if company_name.lower() in i.get("name", "").lower()), None)
    if not company:
        print("Company not found.")
        return
    output_dir = company.get("handle", company_name).lower().replace(' ', '_')
    os.makedirs(output_dir, exist_ok=True)

    # Save company details
    company_details = os.path.join(output_dir, f"{output_dir}.json")
    with open(company_details, "w") as f:
        json.dump(company, f, indent=2)
    print(f"Saved company data to {company_details}")

    wildcards = []
    domains = []

    for asset in company.get("targets", {}).get("in_scope", []):
        atype = asset.get("asset_type")
        aid = asset.get("asset_identifier", "")
        cleaned = clean_domain(aid)
        if atype == "WILDCARD" and cleaned:
            wildcards.append(cleaned)
        elif atype == "URL" and cleaned:
            domains.append(cleaned)
    if wildcards:
        wildcards_path = os.path.join(output_dir, "Wildcards.txt")
        with open(wildcards_path, "w") as f:
            for w in set(wildcards):
                f.write(w + "\n")
        print(f"Saved {len(set(wildcards))} wildcards to {wildcards_path}")

    if domains:
        domains_path = os.path.join(output_dir, "Domains.txt")
        with open(domains_path, "w") as f:
            for d in set(domains):
                f.write(d + "\n")
        print(f"Saved {len(set(domains))} domains to {domains_path}")

    if not wildcards and not domains:
        print("No wildcard or URL assets found for this company.")
        
    # Copy local files
    destination_path = os.path.join(output_dir, "combine_subs.py")
    try:
        shutil.copy("subdomain_enum.py", destination_path)
        print(f"Copied 'subdomain_enum.py' to {destination_path}")
    except IOError as e:
        print(f"Error copying '{filename}' to '{destination_path}': {e}")

if __name__ == "__main__":
    main()
