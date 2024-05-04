from pathlib import Path
import argparse
import subprocess
import typing as tp
import os


def run_solution(input_file: Path, params: str, output_file: tp.Optional[str],
                 env_list: tp.Optional[tp.List[str]]) -> bytes:
    env = ' '.join(env_list) if env_list else ''
    with open(input_file) as fin:
        p = subprocess.Popen(f'{env} ./solution {params}'.strip(), stdin=fin, stdout=subprocess.PIPE, shell=True)
        res, _ = p.communicate()
        if p.returncode != 0:
            raise RuntimeError(f'Solution failed with code {p.returncode} on test {input_file}')
    if output_file:
        if res:
            raise RuntimeError(f'Unexpected output on test {input_file}')
        with open(output_file, 'rb') as f:
            res = f.read()
        os.remove(output_file)
    return res


def parse_inf_file(f):
    res = {}

    def parse_param(key, val):
        if key == 'params':
            if key in res:
                raise RuntimeError("Duplicated params")
            res[key] = val
        elif key == 'environ':
            res[key] = res.get(key, []).append(val)
        else:
            raise RuntimeError(f"Unknown inf param {key} = {val}")

    for line in f.readlines():
        if not line.strip():
            continue
        key, val = line.split(' = ')
        val = val.strip()
        parse_param(key, val)
    return res


parser = argparse.ArgumentParser()
parser.add_argument('--fill', action='store_true')
parser.add_argument('--output-file', required=False)
args = parser.parse_args()

for test in sorted(Path('tests').glob('*.dat')):
    inf = Path(str(test.absolute()).removesuffix('.dat') + '.inf')
    ans = Path(str(test.absolute()).removesuffix('.dat') + '.ans')
    meta = {}
    if inf.is_file():
        with open(inf) as f:
            meta = parse_inf_file(f)
    if not ans.is_file() and not args.fill:
        raise RuntimeError("No answer for test " + test.name)
    res = run_solution(test, meta.get('params', ''), args.output_file, meta.get('environ'))
    if not args.fill:
        with open(ans, 'rb') as expected:
            if expected.read() != res:
                with open('output', 'wb') as f:
                    f.write(res)
                raise RuntimeError(f"Output missmatched on test {test}. Check \"output\" file")
    else:
        with open(ans, 'wb') as fout:
            fout.write(res)
