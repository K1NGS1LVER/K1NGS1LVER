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

FONT = "system-ui,-apple-system,Segoe UI,Roboto,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,monospace"

PALETTE = {
    "python": "#3572A5", "javascript": "#f1e05a", "typescript": "#3178c6",
    "jupyter notebook": "#DA5B0B", "c": "#555555", "css": "#563d7c",
    "html": "#e34c26", "kotlin": "#A97BFF", "c++": "#f34b7d",
    "dart": "#00B4AB", "go": "#00ADD8", "java": "#b07219",
    "rust": "#dea584", "shell": "#89e051", "ruby": "#701516",
}


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
            contributionsCollection {
              totalCommitContributions
              contributionCalendar {
                weeks { contributionDays { date contributionCount } }
              }
            }
          }
        }
        """,
        {"login": LOGIN},
    )["user"]["contributionsCollection"]

    return {
        "followers": user["followers"],
        "repos": len(repos),
        "stars": sum(r["stargazers_count"] for r in repos),
        "commits": gql["totalCommitContributions"],
        "weeks": [
            [d["contributionCount"] for d in w["contributionDays"]]
            for w in gql["contributionCalendar"]["weeks"]
        ],
        "languages": Counter(r["language"] for r in repos if r["language"]),
    }


def stat_card(x, label, value):
    return (
        f'<g transform="translate({x},0)">'
        f'<rect width="140" height="60" rx="10" fill="#0b1020" stroke="#1e2a4a" stroke-width="1"/>'
        f'<text x="14" y="24" font-family="{MONO}" font-size="10" fill="#64748b">{label}</text>'
        f'<text x="14" y="46" font-family="{MONO}" font-size="22" font-weight="700" fill="url(#bar)">{value}</text>'
        f"</g>"
    )


def stats_svg(data):
    cards = [
        ("COMMITS 12MO", fmt(data["commits"])),
        ("STARS EARNED", fmt(data["stars"])),
        ("FOLLOWERS", fmt(data["followers"])),
        ("PUBLIC REPOS", fmt(data["repos"])),
    ]
    cards = "".join(stat_card(i * 156, label, value) for i, (label, value) in enumerate(cards))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 180" width="100%" height="auto">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0b1020"/><stop offset="100%" stop-color="#0f1a33"/>
    </linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#38bdf8"/><stop offset="50%" stop-color="#818cf8"/><stop offset="100%" stop-color="#c084fc"/>
    </linearGradient>
    <linearGradient id="glow" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.3"/><stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="680" height="180" rx="20" fill="url(#bg)"/>
  <rect x="24" y="24" width="632" height="132" rx="14" fill="none" stroke="#1e2a4a" stroke-width="1.5"/>
  <rect x="24" y="24" width="632" height="132" rx="14" fill="url(#glow)"/>
  <text x="44" y="56" font-family="{FONT}" font-size="18" font-weight="700" fill="#f1f5f9">GitHub Stats</text>
  <text x="44" y="74" font-family="{FONT}" font-size="11.5" fill="#64748b">live from the GitHub API</text>
  <g transform="translate(44,92)">{cards}</g>
  <text x="44" y="168" font-family="{MONO}" font-size="10" fill="#334155">github.com/{LOGIN}</text>
</svg>
"""


def heatmap_svg(data):
    levels = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

    def color(n):
        if n == 0:
            return levels[0]
        if n <= 2:
            return levels[1]
        if n <= 5:
            return levels[2]
        if n <= 9:
            return levels[3]
        return levels[4]

    cells = []
    for w, week in enumerate(data["weeks"]):
        for d, count in enumerate(week):
            cells.append(
                f'<rect x="{w * 11}" y="{d * 11}" width="9" height="9" rx="2" fill="{color(count)}">'
                f"<title>{count} contributions</title></rect>"
            )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 200" width="100%" height="auto">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0b1020"/><stop offset="100%" stop-color="#0f1a33"/>
    </linearGradient>
    <linearGradient id="glow" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.3"/><stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="680" height="200" rx="20" fill="url(#bg)"/>
  <rect x="24" y="24" width="632" height="152" rx="14" fill="none" stroke="#1e2a4a" stroke-width="1.5"/>
  <rect x="24" y="24" width="632" height="152" rx="14" fill="url(#glow)"/>
  <text x="44" y="56" font-family="{FONT}" font-size="18" font-weight="700" fill="#f1f5f9">Contribution Activity</text>
  <text x="44" y="74" font-family="{FONT}" font-size="11.5" fill="#64748b">commits per day over the last 12 months</text>
  <g transform="translate(44,92)">
    <rect width="600" height="84" rx="8" fill="#0b1020" stroke="#1e2a4a" stroke-width="1"/>
    <g transform="translate(8,8)">{"".join(cells)}</g>
  </g>
  <g transform="translate(44,182)" font-family="{MONO}" font-size="9" fill="#64748b">
    <text x="0" y="9">Less</text>
    <rect x="32" y="0" width="10" height="10" rx="2" fill="#161b22"/>
    <rect x="46" y="0" width="10" height="10" rx="2" fill="#0e4429"/>
    <rect x="60" y="0" width="10" height="10" rx="2" fill="#006d32"/>
    <rect x="74" y="0" width="10" height="10" rx="2" fill="#26a641"/>
    <rect x="88" y="0" width="10" height="10" rx="2" fill="#39d353"/>
    <text x="104" y="9">More</text>
  </g>
</svg>
"""


def languages_svg(data):
    top = data["languages"].most_common(6)
    peak = max((count for _, count in top), default=1)
    rows = []
    for i, (lang, count) in enumerate(top):
        y = 64 + i * 22
        width = round(300 * count / peak)
        color = PALETTE.get(lang.lower(), "#818cf8")
        rows.append(
            f'<text x="44" y="{y + 10}" font-family="{FONT}" font-size="12" fill="#cbd5e1">{esc(lang)}</text>'
            f'<rect x="180" y="{y}" width="300" height="11" rx="5.5" fill="#0b1020" stroke="#1e2a4a" stroke-width="1"/>'
            f'<rect x="180" y="{y}" width="{width}" height="11" rx="5.5" fill="{color}"/>'
            f'<text x="490" y="{y + 10}" font-family="{MONO}" font-size="10" fill="#64748b">{count} repos</text>'
        )
    height = 88 + len(top) * 22
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 {height}" width="100%" height="auto">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0b1020"/><stop offset="100%" stop-color="#0f1a33"/>
    </linearGradient>
    <linearGradient id="glow" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.3"/><stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="680" height="{height}" rx="20" fill="url(#bg)"/>
  <rect x="24" y="24" width="632" height="{height - 48}" rx="14" fill="none" stroke="#1e2a4a" stroke-width="1.5"/>
  <rect x="24" y="24" width="632" height="{height - 48}" rx="14" fill="url(#glow)"/>
  <text x="44" y="56" font-family="{FONT}" font-size="18" font-weight="700" fill="#f1f5f9">Languages</text>
  <text x="44" y="76" font-family="{FONT}" font-size="11.5" fill="#64748b">by how many of my repositories use each</text>
  {"".join(rows)}
</svg>
"""


def main():
    data = collect()
    out = os.path.join(ROOT, "assets")
    os.makedirs(out, exist_ok=True)
    for name, svg in (
        ("stats.svg", stats_svg(data)),
        ("heatmap.svg", heatmap_svg(data)),
        ("languages.svg", languages_svg(data)),
    ):
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote assets/{name}")


if __name__ == "__main__":
    main()
