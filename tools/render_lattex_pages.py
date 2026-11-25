"""Refresh the inline LatteX formulas in local HTML pages.

Run with Java 25 and LATTEX_JAR set to a LatteX jar. The data-tex attribute
is the source of truth. Use --check to compare against the committed rendering.
"""

import argparse
import base64
from html import unescape
import os
from pathlib import Path
import re
import subprocess
import tempfile
from xml.etree import ElementTree


FORMULA = re.compile(
    r'(<span class="lattex" data-tex="([^"]*)")(?: style="[^"]*")?>.*?</span>',
    re.DOTALL,
)

JAVA = """
import com.lattex.api.Color;
import com.lattex.api.LatteX;
import com.lattex.api.RenderOptions;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

class RenderPageMath {
    public static void main(String[] args) throws Exception {
        var options = RenderOptions.defaults().inline().withColor(Color.CURRENT);
        var reader = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
        var encoder = Base64.getEncoder();
        for (String source; (source = reader.readLine()) != null;) {
            var result = LatteX.renderWithDiagnostics(source, options);
            var diagnostic = result.diagnostics();
            boolean clean = diagnostic.outcome().name().equals("OK")
                && diagnostic.detail().isEmpty() && diagnostic.caveats().isEmpty();
            String value = clean ? result.svg() : diagnostic.toString();
            System.out.println((clean ? "ok" : "error") + "\\t"
                + encoder.encodeToString(value.getBytes(StandardCharsets.UTF_8)));
        }
    }
}
"""


def render(sources, jar):
    with tempfile.TemporaryDirectory() as scratch:
        java = Path(scratch) / "RenderPageMath.java"
        java.write_text(JAVA, encoding="utf-8")
        result = subprocess.run(["java", "-cp", str(jar), str(java)],
                                input="\n".join(sources) + "\n", encoding="utf-8",
                                capture_output=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or f"Java exited with code {result.returncode}.")
    records = result.stdout.splitlines()
    if len(records) != len(sources):
        raise SystemExit(f"LatteX returned {len(records)} records for {len(sources)} formulas.")
    rendered = {}
    failures = []
    for source, record in zip(sources, records):
        state, payload = record.split("\t", 1)
        value = base64.b64decode(payload).decode()
        if state == "ok":
            rendered[source] = value.strip()
        else:
            failures.append(f"{source}\n  {value}")
    if failures:
        raise SystemExit("\n".join(failures))
    return rendered


def embed(svg):
    root = ElementTree.fromstring(svg)
    _, top, width, height = map(float, root.attrib["viewBox"].split())
    # LatteX renders the reference font at 40 user units. Scale the ink box and
    # its baseline together. The wrapper may shrink when a formula is wider
    # than the column. No SVG path or label is changed.
    depth = max(0, top + height) / 40
    style = (f"display:inline-block;width:{width/40:.5g}em;max-width:100%;"
             f"vertical-align:-{depth:.5g}em;line-height:0")
    return style, svg.replace("<svg ", '<svg style="display:block;width:100%;height:auto" ', 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare without rewriting")
    parser.add_argument("pages", nargs="+", type=Path)
    args = parser.parse_args()
    jar = Path(os.environ.get("LATTEX_JAR", ""))
    if not jar.is_file():
        parser.error("set LATTEX_JAR to a LatteX jar")
    pages = {path: path.read_text(encoding="utf-8") for path in args.pages}
    sources = dict.fromkeys(unescape(m[2]) for page in pages.values() for m in FORMULA.finditer(page))
    if not sources:
        parser.error("no data-tex formulas found")
    if any("\n" in source or "\r" in source for source in sources):
        parser.error("keep each data-tex formula on one line")
    rendered = render(sources, jar.resolve())

    def replace(match):
        style, svg = embed(rendered[unescape(match[2])])
        return f'{match[1]} style="{style}">{svg}</span>'

    stale = []
    for path, page in pages.items():
        generated = FORMULA.sub(replace, page)
        if generated != page:
            if args.check:
                stale.append(path)
            else:
                path.write_text(generated, encoding="utf-8")
    if stale:
        raise SystemExit("Stale LatteX output in " + ", ".join(map(str, stale)))
    count = sum(len(FORMULA.findall(page)) for page in pages.values())
    print(f"{count} LatteX formulas ({len(sources)} distinct) across {len(pages)} pages.")


if __name__ == "__main__":
    main()
