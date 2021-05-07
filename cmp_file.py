"""Get lines that are the same between files"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file1')
parser.add_argument('file2')

args = parser.parse_args()

def cmpr(element):
    return element[0:element.find('=')].strip()

with open(args.file1, mode='rt') as file1:
    with open(args.file2, mode='rt') as file2:
        lines1 = [l for l in file1.readlines()]
        lines2 = [l for l in file2.readlines()]

line1c = [cmpr(l) for l in lines1]
line2c = [cmpr(l) for l in lines2]

not_in_file2 = [line1e for line1ce, line1e in zip(line1c, lines1) if line1ce not in line2c]

print(("="*10) + ("NEW LINES") +("=" * 10))
print(*not_in_file2)

with open(args.file2, mode='at') as file2:
    file2.writelines(not_in_file2)