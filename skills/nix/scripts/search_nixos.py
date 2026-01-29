#!/usr/bin/env python3
import sys
import json
import argparse
import urllib.request
import urllib.error
import re
import textwrap

# Configuration derived from reverse engineering search.nixos.org
# These might change, so we keep them constants
API_ENDPOINT = "https://search.nixos.org/backend"
# Default to unstable, but allow override
DEFAULT_CHANNEL = "unstable"

# Mapping channels to indices (Based on latest-44 series)
# We can try to make this dynamic or just hardcode the most common ones
INDICES = {
    "unstable": "latest-44-nixos-unstable",
    "24.11": "latest-44-nixos-24.11",
    "24.05": "latest-44-nixos-24.05",
}

# Credentials (publicly exposed in their JS bundle)
# User: aWVSALXpZv
# Pass: X8gPHnzL52wFEekuxsfQ9cSh
AUTH_HEADER = "Basic YVdWU0FMWHBadjpYOGdQSG56TDUyd0ZFZWt1eHNmUTljU2g="

def search(query, type="packages", channel="unstable", from_item=0, size=20):
    index = INDICES.get(channel, INDICES["unstable"])
    url = f"{API_ENDPOINT}/{index}/_search"
    
    # Construct ES Query
    # Based on simple multi_match. We can enhance this to match their actual logic
    # which uses function_score and fuzzy matching.
    
    es_query = {}
    
    if type == "packages":
        es_query = {
            "from": from_item,
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "type": "cross_fields",
                                "query": query,
                                "analyzer": "whitespace",
                                "auto_generate_synonyms_phrase_query": False,
                                "operator": "and",
                                "fields": [
                                    "package_attr_name^9",
                                    "package_attr_name.*^5.3999999999999995",
                                    "package_programs^9",
                                    "package_programs.*^5.3999999999999995",
                                    "package_pname^6",
                                    "package_pname.*^3.5999999999999996",
                                    "package_description^1.3",
                                    "package_description.*^0.78",
                                    "package_longDescription^1",
                                    "package_longDescription.*^0.6",
                                    "flake_name^0.5",
                                    "flake_name.*^0.3",
                                    "flake_description^0.5",
                                    "flake_description.*^0.3"
                                ],
                                "tie_breaker": 0.3
                            }
                        }
                    ],
                    "filter": [
                        {"term": {"type": "package"}}
                    ]
                }
            },
            "sort": ["_score"] 
        }
    elif type == "options":
        es_query = {
            "from": from_item,
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "option_name^4",
                                    "option_description^2",
                                    "option_default"
                                ]
                            }
                        }
                    ],
                    "filter": [
                        {"term": {"type": "option"}}
                    ]
                }
            }
        }
    elif type == "options-prefix":
        # Search for options that start with a specific prefix
        es_query = {
            "from": from_item,
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "prefix": {
                                "option_name": query
                            }
                        }
                    ],
                    "filter": [
                        {"term": {"type": "option"}}
                    ]
                }
            },
            "sort": [{"option_name": "asc"}]
        }

    req = urllib.request.Request(
        url,
        data=json.dumps(es_query).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Authorization": AUTH_HEADER
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.URLError as e:
        print(f"Error querying NixOS Search: {e}", file=sys.stderr)
        return None

def strip_html(text):
    """Remove HTML tags and clean up the text."""
    if not text:
        return ""
    # Remove <rendered-html> wrapper
    text = re.sub(r'</?rendered-html>', '', text)
    # Convert <code> to backticks
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text)
    # Convert <pre><code> blocks to indented text
    text = re.sub(r'<pre><code>(.*?)</code></pre>', lambda m: '\n' + textwrap.indent(m.group(1), '    '), text, flags=re.DOTALL)
    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"')
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def format_package(hit):
    source = hit["_source"]
    name = source.get("package_attr_name", source.get("package_pname", "Unknown"))
    version = source.get("package_pversion", "")
    desc = source.get("package_description", "")
    programs = source.get("package_programs", [])
    homepage = source.get("package_homepage", [])
    license_info = source.get("package_license", [])
    position = source.get("package_position", "")  # e.g. "pkgs/applications/.../default.nix:42"
    
    lines = [f"## {name} ({version})"]
    if desc:
        lines.append(f"  {desc}")
    if position:
        lines.append(f"  Source: {position}")
    if programs:
        lines.append(f"  Programs: {', '.join(programs)}")
    if homepage:
        hp = homepage[0] if isinstance(homepage, list) else homepage
        lines.append(f"  Homepage: {hp}")
    if license_info:
        lic = license_info[0].get("fullName", license_info[0]) if isinstance(license_info, list) and license_info else license_info
        if isinstance(lic, dict):
            lic = lic.get("fullName", str(lic))
        lines.append(f"  License: {lic}")
    lines.append("")
    return "\n".join(lines)

def format_option(hit):
    source = hit["_source"]
    name = source.get("option_name", "Unknown")
    opt_type = source.get("option_type", "unknown")
    default = source.get("option_default", None)
    example = source.get("option_example", None)
    desc = strip_html(source.get("option_description", ""))
    src = source.get("option_source", "")
    
    lines = [f"## {name}"]
    lines.append(f"  Type: {opt_type}")
    if default is not None:
        # Format multiline defaults nicely
        default_str = str(default)
        if '\n' in default_str:
            lines.append(f"  Default:")
            for line in default_str.split('\n'):
                lines.append(f"    {line}")
        else:
            lines.append(f"  Default: {default_str}")
    if src:
        lines.append(f"  Declared in: {src}")
    if desc:
        lines.append(f"  Description: {desc}")
    if example is not None:
        example_str = str(example)
        if '\n' in example_str:
            lines.append(f"  Example:")
            for line in example_str.split('\n'):
                lines.append(f"    {line}")
        else:
            lines.append(f"  Example: {example_str}")
    lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Search NixOS packages and options",
        epilog="""Examples:
  %(prog)s firefox                      # Search for packages matching 'firefox'
  %(prog)s --type options services.ssh  # Search for options matching 'services.ssh'
  %(prog)s --prefix services.postgresql # List all options under services.postgresql.*
  %(prog)s --size 50 nginx              # Get up to 50 results
"""
    )
    parser.add_argument("query", help="Search term or prefix")
    parser.add_argument("--type", "-t", choices=["packages", "options"], default="packages", 
                        help="Type of search (default: packages)")
    parser.add_argument("--prefix", "-p", action="store_true",
                        help="Search options by prefix (lists all options starting with query)")
    parser.add_argument("--channel", "-c", default="unstable", 
                        help="NixOS channel (unstable, 24.11, 24.05)")
    parser.add_argument("--size", "-n", type=int, default=20,
                        help="Number of results to return (default: 20)")
    parser.add_argument("--json", "-j", action="store_true", 
                        help="Output raw JSON from the API")
    
    args = parser.parse_args()
    
    # Determine search type
    search_type = args.type
    if args.prefix:
        search_type = "options-prefix"

    results = search(args.query, search_type, args.channel, size=args.size)
    
    if not results:
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        hits = results.get("hits", {}).get("hits", [])
        total = results.get("hits", {}).get("total", {}).get("value", 0)
        
        print(f"Found {total} results for '{args.query}' (showing {len(hits)}):\n")
        
        for hit in hits:
            if search_type == "packages":
                print(format_package(hit))
            else:
                print(format_option(hit))

if __name__ == "__main__":
    main()
