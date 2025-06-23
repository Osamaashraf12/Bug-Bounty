# Bug-Bounty
## Introduction
Every bug bounty hunter starts with the repetitive task of scope collection. This tool automates that process by fetching target data and performing subdomain enumeration with live domain filtering.<br/>
Currently, it supports **HackerOne** (via bounty-targets-data) and will be updated to support more platforms in the future.

## Installation
```
git clone https://github.com/Osamaashraf12/bug-bounty.git
cd bug-bounty
```
> Please do not change the directory structure, as the scripts rely on specific paths.

## Usage
```
python fetch_company_data.py <company_name> <platform_code>
# Example: python fetch_company_data.py oppo H

python subdomain_enum.py
```
- Platform code `H` stands for HackerOne. (Only platform in the first commit)
- The first script fetches and extracts the scopes.
- The second script performs subdomain enumeration and DNS filtering.

## Data source
This tool uses the [bounty-targets-data](https://github.com/arkadiyt/bounty-targets-data/tree/main) repository to fetch scope data from HackerOne.
