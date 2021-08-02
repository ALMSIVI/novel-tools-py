import csv, os

def read(dir: str):
    volumes = []
    with open(os.path.join(dir, 'list.csv'), 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['type'] == 'volume':
                volumes.append({'name': row['text'], 'volume': row.get('c_formatted', row['formatted'])})

    return volumes