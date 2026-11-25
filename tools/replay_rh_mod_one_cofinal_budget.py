"""Replay the cofinal modulus-one budget cut against the pinned Lean archive."""

import argparse
from hashlib import sha256
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


FIELD_PATH = Path("Development/AutomorphicArithmetic/CharacterBoxes/FieldChi.lean")
SUPPLY_PATH = Path("Development/AutomorphicArithmetic/ShortNorms/supplyOfAdmOf.lean")
FIELD_HASH = "784b9d6aed0292547065a98f2577d41f82269332559815f38fc85da4f69369b3"
SUPPLY_HASH = "b70c2177d57dfcd03f82784741813b7c6e6b525c69ffec5cae5527f03013a364"
HERE = Path(__file__).resolve().parent


def pinned_text(source, path, digest):
    data = (source / path).read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"{path} differs from archive revision 6193bb5.")
    return data.decode("utf-8")


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected exactly one archive occurrence of {old!r}")
    return text.replace(old, new, 1)


def modify_field(text):
    # ordAny already proves the upper bound on the order multiplier.
    # Retain it in the conclusion of the field construction.
    text = replace_once(text, "UpperTheory.Top.fieldChi :", "ZetaWindowSupply.fieldChiBound :")
    text = replace_once(text, "1 ≤ c ∧ ∀ e ≥ e0,",
                        "1 ≤ c ∧ c ≤ Nat.card (Subgroup.zpowers ψ.χ) ∧ ∀ e ≥ e0,")
    text = replace_once(text, "⟨c, e1, hc1, -, hord⟩", "⟨c, e1, hc1, hcmax, hord⟩")
    return replace_once(text, ", hc1,\n    fun e", ", hc1, hcmax,\n    fun e")


def modify_supply(text):
    # Keep the host proof and replace the budget lookup with its exact result.
    text = replace_once(text, "import Development.AutomorphicArithmetic.CharacterBoxes.WinPairs",
                        "import Development.AutomorphicArithmetic.CharacterBoxes.TwistForm")
    text = replace_once(text, "import Development.AutomorphicArithmetic.CharacterBoxes.FieldChi\n", "")
    text = replace_once(text, "import Development.AutomorphicArithmetic.MeanSquareBounds.pairEx\n", "")
    old = "theorem UpperTheory.T3.supplyOfAdmOf :"
    definition = """
namespace ZetaWindowSupply

/-- The arithmetic data consumed by the archived host construction. -/
def WindowData (ψ : PChar) : Prop :=
  ∀ (eps c : ℝ), 0 < eps → eps < 1 / 52 → 1 ≤ c → c ≤ Nat.card (Subgroup.zpowers ψ.χ) →
    ∃ J : ℝ, 1 ≤ J ∧ ∀ y : ℝ, ∃ Z : ℝ, y ≤ Z ∧
      ∀ x : ℝ, Z ≤ x → x ≤ Z ^ ((3 : ℝ) / 2) →
        ∃ (Y : ℝ) (q d e : ℕ), WinDatum ψ eps J c x Y q d e

end ZetaWindowSupply

theorem ZetaWindowSupply.supplyOfAdmOfWindows :
"""
    text = replace_once(text, old, definition.rstrip())
    text = replace_once(text, "∀ ψ : PChar, VWinAt ψ 401 →",
                        "∀ ψ : PChar, ZetaWindowSupply.WindowData ψ →")
    text = replace_once(text, "intro hSup ψ hV hAdm", "intro hSup ψ hWindows hAdm")
    text = replace_once(text, "⟨c, e0, hc, hF⟩ := UpperTheory.Top.fieldChi ψ",
                        "⟨c, e0, hc, hcmax, hF⟩ := ZetaWindowSupply.fieldChiBound ψ")
    return replace_once(
        text,
        "UpperTheory.Top.winPairs ψ eps (c : ℝ) heps heps' (by exact_mod_cast hc) hV QH.pairEx",
        "hWindows eps (c : ℝ) heps heps' (by exact_mod_cast hc) (by exact_mod_cast hcmax)",
    )


def compose(*parts):
    imports, bodies = [], []
    for part in parts:
        body = []
        for line in part.splitlines():
            if line.startswith("import "):
                if line not in imports:
                    imports.append(line)
            else:
                body.append(line)
        bodies.append("\n".join(body))
    return "\n".join(imports + [""] + bodies) + "\n"


def generate(source):
    field = modify_field(pinned_text(source, FIELD_PATH, FIELD_HASH))
    supply = modify_supply(pinned_text(source, SUPPLY_PATH, SUPPLY_HASH))
    cuts = (HERE / "rh_mod_one_input_cuts.lean").read_text(encoding="utf-8")
    budget = (HERE / "rh_mod_one_cofinal_budget.lean.in").read_text(encoding="utf-8")
    return compose(field, supply, cuts, budget)


def replay(source, project):
    with TemporaryDirectory(prefix="cofinal-budget-replay-") as directory:
        endpoint = Path(directory) / "ModOneCofinalBudget.lean"
        endpoint.write_text(generate(source), encoding="utf-8")
        subprocess.run(["lake", "env", "lean", "--tstack=400000", str(endpoint)],
                       cwd=project, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive_source", type=Path, help="archive src directory at 6193bb5")
    parser.add_argument("compiled_project", type=Path, help="Lean 4.33.1 archive project with the imports built")
    args = parser.parse_args()
    replay(args.archive_source.resolve(), args.compiled_project.resolve())
