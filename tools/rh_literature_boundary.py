"""Compare the import reach of the literature table and four archive entry points."""

import argparse
from functools import cache
import json
from pathlib import Path

from count_rh_source_imports import header_imports


ROUTES = {
    "conditional": (
        "Formalism.GammaFactorNonvanishing.CritLine",
        "Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.TopPlug",
        "Development.WeilBound.CoreStatements.StandardPublishedResults.StandardTheoremStatements.GreenRegularCharacters",
        "Development.AbelianVarietyTheory.Proofs.InertiaEigenvalues.SumRangeEqRoots",
    ),
    "budget": (
        "Development.AutomorphicArithmetic.AutomorphicVarieties.ModularityArgument.ThresholdArguments.DenseThresholdCases.VwinOfRow",
    ),
    "family": (
        "Development.AutomorphicArithmetic.ThetaCorrespondence.ThetaPairLifts.ThirdPlaceSeries.SiegelEisensteinSecondTermHypotheses",
    ),
    "main": ("Main",),
}


def compare(source, scan):
    table = json.loads(scan.read_text(encoding="utf-8"))
    if table["revision"] != "6193bb5":
        raise ValueError("Expected the literature scan for archive 6193bb5.")
    rows = [row for row in table["statements"]
            if not row["package"] and not row["unfollowed"] and row["proof_modules"]]

    @cache
    def path_for(module):
        return source.joinpath(*module.split(".")).with_suffix(".lean")

    @cache
    def imports(module):
        return tuple(header_imports(path_for(module)))

    def close(starts):
        pending = list(starts)
        reached = set()
        while pending:
            module = pending.pop()
            if module not in reached:
                reached.add(module)
                pending.extend(imports(module))
        return reached

    table_roots = {mod for row in rows for mod in row["table_modules"]}
    proof_roots = {mod for row in rows for mod in row["proof_modules"]}
    before, followed = close(table_roots), close(proof_roots)
    @cache
    def lines(module):
        raw = path_for(module).read_bytes()
        return raw.count(b"\n") + int(bool(raw) and not raw.endswith(b"\n"))

    def size(modules):
        return {"files": len(modules), "lines": sum(map(lines, modules))}

    result = {
        "rows": len(rows),
        "table_roots": len(table_roots),
        "proof_roots": len(proof_roots),
        "table": size(before),
        "followed": size(followed),
        "removed": size(before - followed),
        "added": size(followed - before),
        "routes": {},
    }
    for key, roots in ROUTES.items():
        route = close(roots)
        result["routes"][key] = {
            "within": size(route & followed),
            "outside": size(route - followed),
            "literature_only": size(followed - route),
        }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="pinned archive's extracted/lean/src")
    parser.add_argument("scan", type=Path, help="crew_visuals/rh_published_scan2.json")
    args = parser.parse_args()
    print(json.dumps(compare(args.source.resolve(), args.scan.resolve()), indent=2))
