from __future__ import annotations

import json
from pathlib import Path

TAXONOMY_JSON = Path(__file__).resolve().parent / "taxonomy.json"
TTL_OUTPUT = Path(__file__).resolve().parent / "issues.ttl"


def _load_taxonomy() -> list[dict]:
    with open(TAXONOMY_JSON, encoding="utf-8") as f:
        return json.load(f)


def generate_ttl() -> str:
    taxonomy = _load_taxonomy()
    lines = [
        '@prefix pm: <http://polymap.kr/ontology#> .',
        '@prefix skos: <http://www.w3.org/2004/02/skos/core#> .',
        '',
    ]

    for parent in taxonomy:
        slug = parent["slug"]
        name = parent["name"]
        children = parent.get("children", [])

        lines.append(f'pm:{slug} a pm:Issue ;')
        lines.append(f'    skos:prefLabel "{name}"@ko')
        if children:
            child_refs = ", ".join(f"pm:{c['slug']}" for c in children)
            lines[-1] += " ;"
            lines.append(f"    skos:narrower {child_refs} .")
        else:
            lines[-1] += " ."

        for child in children:
            lines.append("")
            lines.append(f"pm:{child['slug']} a pm:Issue ;")
            lines.append(f'    skos:prefLabel "{child["name"]}"@ko ;')
            lines.append(f"    skos:broader pm:{slug} .")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    ttl = generate_ttl()
    TTL_OUTPUT.write_text(ttl, encoding="utf-8")
    print(f"Generated {TTL_OUTPUT}")


if __name__ == "__main__":
    main()
