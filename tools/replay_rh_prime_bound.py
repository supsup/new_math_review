"""Rebuild the 31-file analytic route using an existing compiled Mathlib project."""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory
from time import monotonic


IMPORT = re.compile(r'^\s*(?:(?:public|private|meta|all)\s+)*import\s+([\w.]+)\s*(?:--.*)?$')
LEAN_ARGS = ['--tstack=400000', '-DautoImplicit=false', '-DrelaxedAutoImplicit=false',
             '-DmaxSynthPendingDepth=3', '-Dpp.unicode.fun=true', '-DmaxHeartbeats=4000000']


def archive_imports(source, entry):
    ordered = []
    seen = set()

    def visit(file):
        for line in file.read_text(encoding='utf-8').splitlines():
            match = IMPORT.fullmatch(line)
            if not match:
                continue
            module = Path(*match[1].split('.')).with_suffix('.lean')
            path = source / module
            if module not in seen and path.is_file():
                seen.add(module)
                visit(path)
                ordered.append(module)

    visit(entry)
    if len(ordered) != 31:
        raise SystemExit(f'Expected 31 archive imports at revision 6193bb5, found {len(ordered)}.')
    return ordered


def mathlib_environment(project, source):
    def lake_var(name):
        return subprocess.check_output(['lake', 'env', 'printenv', name], cwd=project,
                                       text=True).strip()

    # Reject any precompiled checkout of the archive. Every archive module
    # used in this replay must come from the new temporary build.
    archive_roots = {path.name if path.is_dir() else path.with_suffix('.olean').name
                     for path in source.iterdir() if path.is_dir() or path.suffix == '.lean'}
    libraries = []
    for entry in lake_var('LEAN_PATH').split(os.pathsep):
        path = (project / entry).resolve()
        if path.is_dir() and not any((path / root).exists() for root in archive_roots):
            libraries.append(str(path))
    if not any((Path(path) / 'Mathlib.olean').is_file() for path in libraries):
        raise SystemExit('No eligible compiled Mathlib found in the project’s Lean path.')
    environment = dict(os.environ)
    environment['PATH'] = lake_var('PATH')
    environment.pop('LEAN_SRC_PATH', None)
    return environment, libraries


def replay(source, project):
    entry = Path(__file__).with_name('rh_zeta_prime_bound.lean')
    modules = archive_imports(source, entry)
    environment, libraries = mathlib_environment(project, source)
    before = monotonic()
    with TemporaryDirectory(prefix='prime-bound-replay-') as directory:
        sources, outputs = Path(directory) / 'src', Path(directory) / 'olean'
        outputs.mkdir()
        environment['LEAN_PATH'] = os.pathsep.join([str(outputs), *libraries])
        lean = ['lean', *LEAN_ARGS, f'--root={sources}']
        for module in modules:
            target, olean = sources / module, outputs / module.with_suffix('.olean')
            target.parent.mkdir(parents=True, exist_ok=True)
            olean.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / module, target)
            subprocess.run([*lean, '-o', str(olean), str(target)],
                           cwd=sources, env=environment, check=True)
        endpoint = sources / 'PrimeBound.lean'
        shutil.copyfile(entry, endpoint)
        subprocess.run([*lean, str(endpoint)], cwd=sources, env=environment, check=True)
        size = sum(path.stat().st_size for path in outputs.rglob('*') if path.is_file())
        elapsed = monotonic() - before
        print(f'Compiled {len(modules)} archive modules from source in {elapsed:.1f} s. '
              f'Temporary compiled output: {size:,} bytes.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive_source', type=Path, help='archive src directory at 6193bb5')
    parser.add_argument('mathlib_project', type=Path, help='Lean 4.33.1 project with Mathlib built')
    args = parser.parse_args()
    replay(args.archive_source.resolve(), args.mathlib_project.resolve())
