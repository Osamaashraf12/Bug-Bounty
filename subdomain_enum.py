import os
import subprocess


def run_dnsx(input_file, output_file):
    try:
        print("Running dnsx for live domains")
        process = subprocess.run(
            ["dnsx", "-silent", "-cname", "-resp", "-l", input_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        domains = set()
        for line in process.stdout.splitlines():
            if line.strip():
                domain = line.split()[0]
                domains.add(domain)

        with open(output_file, "w") as f:
            for domain in sorted(domains):
                f.write(domain + "\n")

        print(f"Live subdomains saved to {output_file} ({len(domains)} entries).")
    except Exception as e:
        print(f"Error running dnsx: {e}")


def run_enum_pipeline(wildcard_file="Wildcards.txt", live_subdomains="live_subdomains.txt"):
    if not os.path.exists(wildcard_file):
        print(f"{wildcard_file} not found.")
        return

    all_subdomains = set()

    print(f"Running Sublist3r on domains in {wildcard_file}.")
    with open(wildcard_file, 'r') as f:
        for domain in f:
            domain = domain.strip()
            if not domain:
                continue

            print(f"Enumerating {domain}.")
            output_file = f"{domain}_subs.txt"
            subprocess.run([
                "python", "../Sublist3r/sublist3r.py",
                "-d", domain,
                "-v",
                "-o", output_file
            ])

            if os.path.exists(output_file):
                with open(output_file, 'r') as subdomain_file:
                    for line in subdomain_file:
                        subdomain = line.strip().lower()
                        if subdomain:
                            all_subdomains.add(subdomain)

    # Save raw subdomains (Sublist3r output)
    with open("raw_subdomains.txt", "w") as f:
        for sub in sorted(all_subdomains):
            f.write(sub + "\n")
    print(f"Saved raw subdomains to raw_subs.txt ({len(all_subdomains)} entries).")

    # Deduplicate and clean
    print("Cleaning duplicate subdomains.")
    base_domains = set(sub[4:] if sub.startswith("www.") else sub for sub in all_subdomains)

    final_subdomains = set()
    for sub in all_subdomains:
        base = sub[4:] if sub.startswith("www.") else sub
        if sub.startswith("www.") and base in base_domains:
            continue
        final_subdomains.add(sub)

    # Save unique subdomains
    with open("unique_subdomains.txt", "w") as f:
        for sub in sorted(final_subdomains):
            f.write(sub + "\n")
    print(f"Saved cleaned subdomains to unique_subs.txt ({len(final_subdomains)} entries).")

    # DNS filtering
    run_dnsx("unique_subdomains.txt", live_subdomains)

    # Optional cleanup
    for file in os.listdir():
        if file.endswith("_subs.txt"):
            try:
                os.remove(file)
                print(f"Deleted {file}.")
            except OSError as e:
                print(f"Could not delete {file}: {e}")


if __name__ == "__main__":
    run_enum_pipeline()
