"""Receive the inventoried baseline from TV2's mirror; never accept changed hashes."""
import argparse
import os
import tempfile
import urllib.request
from pathlib import Path

from g2_pipeline import ROOT, rows, selected_sources, verify_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=ROOT/'docs/03_source_inventory.csv')
    parser.add_argument('--raw-dir', type=Path, default=ROOT/'data/raw')
    parser.add_argument('--months', nargs='+', default=['202503','202504','202505','202506'])
    args = parser.parse_args()
    inventory = rows(args.inventory)
    selected = [item for month in sorted(set(args.months)) for item in selected_sources(inventory, month)]
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    for item in selected:
        target = args.raw_dir/item['filename']
        nested = args.raw_dir/item['family']/item['filename']
        existing = target if target.exists() else nested
        if existing.exists():
            verify_file(existing, item)
            print('VERIFIED existing', item['filename'], flush=True)
            continue
        if not item['source_url'].startswith('https://huggingface.co/datasets/impactproject/opm-ehri-data/resolve/'):
            raise ValueError('Only the inventoried TV2 mirror is supported')
        fd, name = tempfile.mkstemp(prefix='.baseline-', dir=args.raw_dir)
        temporary = Path(name)
        try:
            with os.fdopen(fd, 'wb') as output, urllib.request.urlopen(item['source_url'], timeout=120) as response:
                while block := response.read(1024*1024):
                    output.write(block)
            verify_file(temporary, item)
            temporary.replace(target)
            print('VERIFIED received', item['filename'], item['sha256'], flush=True)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
