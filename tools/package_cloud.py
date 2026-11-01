"""Build a private execution bundle from explicit project assets; never include keys."""
import argparse
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.protocol import sha256


def package(output):
    files = [p for folder in ['src', 'benchmarks'] for p in (ROOT / folder).glob('*.py')]
    files += [ROOT / 'finalSok3_pytorch.pt', *(ROOT / 'checkpoints/ensemble').glob('ensemble_model_*.pt')]
    files += [ROOT / 'data' / name for name in (
        'sokoban_3box_test.txt', 'sokoban_5box_test.txt', 'sokoban_7box_original_test.txt',
        'sokoban_7box_original_test.provenance.json')]
    files += [ROOT / 'README.md', ROOT / 'requirements.txt', ROOT / 'licenses/UPSTREAM_CC0.txt']
    hashes = {str(p.relative_to(ROOT)).replace('\\', '/'): sha256(p) for p in files}
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, str(p.relative_to(ROOT)).replace('\\', '/'))
        z.writestr('BUNDLE_SHA256.json', json.dumps(hashes, indent=2))
    print('Saved:', output, 'SHA256:', sha256(output))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'output/risk_averse_sokoban.zip')
    package(parser.parse_args().output)
