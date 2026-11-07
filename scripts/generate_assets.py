#!/usr/bin/env python3
"""Regenerate the dynamic profile SVGs from real GitHub data.

Runs with the standard library only. Needs GITHUB_TOKEN for GraphQL.
"""
import json
import os
import urllib.error
import urllib.request
from collections import Counter

LOGIN = os.environ.get("GH_LOGIN", "K1NGS1LVER")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT = "ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

BG = "#0b0b0c"
TEXT = "#ecebe7"
MUTED = "#8a8a91"
LINE = "#232327"
TRACK = "#1d1d21"
SKIP_LANGS = {"HTML", "CSS", "SCSS"}
RAMP = ["#d3c4ff", "#b9a1ff", "#9d7bff", "#7d58e8", "#5f3bbb", "#42288a"]
ACCENT = "#9d7bff"


def request(url, data=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-assets"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def graphql(query, variables):
    payload = json.dumps({"query": query, "variables": variables}).encode()
    return request("https://api.github.com/graphql", payload)["data"]


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(n):
    return f"{n:,}"


def collect():
    user = request(f"https://api.github.com/users/{LOGIN}")
    repos = request(f"https://api.github.com/users/{LOGIN}/repos?per_page=100&type=owner")
    repos = [r for r in repos if not r["fork"]]

    gql = graphql(
        """
        query($login: String!) {
          user(login: $login) {
            repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
              totalCount
              nodes { languages(first: 20) { edges { node { name color } } } }
            }
            contributionsCollection {
              totalCommitContributions
            }
          }
        }
        """,
        {"login": LOGIN},
    )["user"]
    contrib = gql["contributionsCollection"]

    languages = Counter()
    for repo in gql["repositories"]["nodes"]:
        names = {edge["node"]["name"] for edge in repo["languages"]["edges"]}
        for name in names - SKIP_LANGS:
            languages[name] += 1

    return {
        "repos": len(repos),
        "repo_total": gql["repositories"]["totalCount"],
        "stars": sum(r["stargazers_count"] for r in repos),
        "commits": contrib["totalCommitContributions"],
        "languages": languages,
    }

def rule(y, x1=44, x2=636):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{LINE}" stroke-width="1"/>'


def stats_svg(data):
    cols = [
        ("contributions, 12 mo", fmt(data["commits"]), True),
        ("stars earned", fmt(data["stars"]), False),
        ("public repos", fmt(data["repos"]), False),
    ]
    parts = [rule(32)]
    col = 592 / 3
    for i, (label, value, primary) in enumerate(cols):
        cx = 44 + col * (i + 0.5)
        if i:
            parts.append(
                f'<line x1="{44 + col * i:.1f}" y1="52" x2="{44 + col * i:.1f}" y2="118" stroke="{LINE}" stroke-width="1"/>'
            )
        parts.append(
            f'<text x="{cx:.1f}" y="92" text-anchor="middle" font-family="{MONO}" font-size="32" font-weight="600" '
            f'fill="{ACCENT if primary else TEXT}">{value}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="114" text-anchor="middle" font-family="{FONT}" font-size="11.5" fill="{MUTED}">{label}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 134" width="100%" height="auto">'
        f'<rect width="680" height="134" fill="{BG}"/>'
        f'{"".join(parts)}'
        f"</svg>\n"
    )


def languages_svg(data):
    rows = data["languages"].most_common(6)
    total = sum(count for _, count in rows) or 1
    bar_w, x = 592, 44
    segments = []
    for i, (name, count) in enumerate(rows):
        width = count / total * bar_w
        segments.append(
            f'<rect x="{x:.1f}" y="70" width="{max(width - 3, 1):.1f}" height="10" fill="{RAMP[i]}"/>'
        )
        x += width

    col = bar_w / 3
    legend = []
    for i, (name, count) in enumerate(rows):
        lx, ly = 44 + (i % 3) * col, 112 + (i // 3) * 30
        legend.append(
            f'<circle cx="{lx + 4}" cy="{ly - 4.5}" r="4" fill="{RAMP[i]}"/>'
            f'<text x="{lx + 16}" y="{ly}" font-family="{FONT}" font-size="13" fill="{TEXT}">{esc(name)}</text>'
            f'<text x="{lx + col - 24:.1f}" y="{ly}" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="{MUTED}">{count} repos</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 166" width="100%" height="auto">
  <rect width="680" height="166" fill="{BG}"/>
  {rule(28)}
  <text x="44" y="54" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT}">Languages</text>
  <text x="636" y="54" text-anchor="end" font-family="{FONT}" font-size="11" fill="{MUTED}">by repositories using each, out of {data["repo_total"]}</text>
  {"".join(segments)}
  {"".join(legend)}
</svg>
"""


def main():
    data = collect()
    out = os.path.join(ROOT, "assets")
    os.makedirs(out, exist_ok=True)
    for name, svg in (
        ("stats.svg", stats_svg(data)),
        ("languages.svg", languages_svg(data)),
    ):
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote assets/{name}")


if __name__ == "__main__":
    main()
