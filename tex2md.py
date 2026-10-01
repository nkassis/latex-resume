#!/usr/bin/env python3
"""Convert Resume.tex to Resume.md.

Not a general LaTeX parser — handles only the custom commands and
environments defined in Resume.tex (ressection, ressubsec, reslist,
ressubitem, rescontext, resscope, resitem, bigname, headline) plus the
symbols used there. If new commands are added to Resume.tex, extend the
dispatch tables below.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


# --- brace / arg helpers ---------------------------------------------------

def match_brace(s: str, start: int) -> int:
    """Given s[start] == '{', return the index of the matching '}'."""
    assert s[start] == "{", f"expected {{ at {start}, got {s[start]!r}"
    depth = 0
    i = start
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"unbalanced braces from {start}")


def read_args(s: str, pos: int, n: int) -> tuple[list[str], int]:
    """Consume n brace-delimited args starting at pos."""
    args: list[str] = []
    i = pos
    for _ in range(n):
        while i < len(s) and s[i].isspace():
            i += 1
        end = match_brace(s, i)
        args.append(s[i + 1:end])
        i = end + 1
    return args, i


def find_env(s: str, env: str, start: int) -> int:
    r"""Return index just past the matching \end{env} for the \begin{env}
    located at `start`. Supports same-name nesting."""
    begin_pat = re.compile(r"\\begin\{" + re.escape(env) + r"\}")
    end_pat = re.compile(r"\\end\{" + re.escape(env) + r"\}")
    i = start + len(f"\\begin{{{env}}}")
    depth = 1
    while depth > 0:
        bm = begin_pat.search(s, i)
        em = end_pat.search(s, i)
        if em is None:
            raise ValueError(f"unterminated env {env}")
        if bm and bm.start() < em.start():
            depth += 1
            i = bm.end()
        else:
            depth -= 1
            i = em.end()
    return i


# --- text cleanup ---------------------------------------------------------

SYMBOL_RULES = [
    (re.compile(r"\$\\cdot\$"), "·"),
    (re.compile(r"\$\\to\$"), "→"),
    (re.compile(r"\$\\sim\$"), "~"),
    (re.compile(r"\$\\\{,\\\}\$"), ","),
    (re.compile(r"\{,\}"), ","),
    (re.compile(r"---"), "—"),
    (re.compile(r"--"), "–"),
    (re.compile(r"\\;"), " "),
    (re.compile(r"\\&"), "&"),
    (re.compile(r"\\\$"), "$"),
    (re.compile(r"\\%"), "%"),
    (re.compile(r"\\_"), "_"),
    (re.compile(r"\\#"), "#"),
]

FORMATTING_STRIP = re.compile(
    r"\\(?:Huge|Large|large|small|normalsize|bfseries|itshape|selectfont|flushleft)\b"
)


def strip_formatting(s: str) -> str:
    s = re.sub(r"\\vspace\s*\{[^{}]*\}", "", s)
    s = re.sub(r"\\hspace\s*\{[^{}]*\}", "", s)
    s = re.sub(r"\\rule\s*\{[^{}]*\}\s*\{[^{}]*\}", "", s)
    s = re.sub(r"\\fontfamily\s*\{[^{}]*\}", "", s)
    return FORMATTING_STRIP.sub("", s)


def apply_inline(text: str) -> str:
    r"""Recursively convert \textbf, \textit, \href; apply symbol rules."""
    for pat, repl in SYMBOL_RULES:
        text = pat.sub(repl, text)

    def walk(t: str) -> str:
        out: list[str] = []
        i = 0
        while i < len(t):
            if t.startswith("\\textbf", i):
                j = i + len("\\textbf")
                while j < len(t) and t[j].isspace():
                    j += 1
                if j < len(t) and t[j] == "{":
                    end = match_brace(t, j)
                    out.append("**" + walk(t[j + 1:end]) + "**")
                    i = end + 1
                    continue
            if t.startswith("\\textit", i):
                j = i + len("\\textit")
                while j < len(t) and t[j].isspace():
                    j += 1
                if j < len(t) and t[j] == "{":
                    end = match_brace(t, j)
                    out.append("*" + walk(t[j + 1:end]) + "*")
                    i = end + 1
                    continue
            if t.startswith("\\href", i):
                j = i + len("\\href")
                while j < len(t) and t[j].isspace():
                    j += 1
                if j < len(t) and t[j] == "{":
                    url_end = match_brace(t, j)
                    url = t[j + 1:url_end]
                    k = url_end + 1
                    while k < len(t) and t[k].isspace():
                        k += 1
                    txt_end = match_brace(t, k)
                    label = walk(t[k + 1:txt_end])
                    if url.startswith("mailto:"):
                        out.append(label)
                    else:
                        if not re.match(r"^[a-z]+://", url):
                            url = "https://" + url
                        out.append(f"[{label}]({url})")
                    i = txt_end + 1
                    continue
            out.append(t[i])
            i += 1
        return "".join(out)

    return walk(text)


def collapse_ws(s: str) -> str:
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def clean(s: str) -> str:
    return collapse_ws(apply_inline(strip_formatting(s)))


# --- document walker ------------------------------------------------------

def convert(src: str) -> str:
    macros: dict[str, str] = {}
    for m in re.finditer(r"\\newcommand\{\\(\w+)\}\{([^{}]*)\}", src):
        macros[m.group(1)] = m.group(2)

    db = re.search(r"\\begin\{document\}", src)
    de = re.search(r"\\end\{document\}", src)
    body = src[db.end():de.start()]

    for name, val in macros.items():
        body = re.sub(r"\\" + re.escape(name) + r"(?:\{\})?(?!\w)", val, body)

    out: list[str] = []
    pos = 0
    n = len(body)
    while pos < n:
        while pos < n and body[pos] in " \t\n":
            pos += 1
        if pos >= n:
            break
        if body[pos] == "%":
            nl = body.find("\n", pos)
            pos = n if nl < 0 else nl + 1
            continue
        rest = body[pos:]

        if m := re.match(r"\\bigname\s*\{", rest):
            start = pos + m.end() - 1
            end = match_brace(body, start)
            out.append(f"# {clean(body[start + 1:end])}\n\n")
            pos = end + 1
            continue

        if re.match(r"\\begin\{center\}", rest):
            end_pos = find_env(body, "center", pos)
            inner_start = pos + len("\\begin{center}")
            inner_end = end_pos - len("\\end{center}")
            inner = clean(body[inner_start:inner_end])
            inner = re.sub(r"^\{\s*", "", inner)
            inner = re.sub(r"\s*\}$", "", inner)
            out.append(inner + "\n\n")
            pos = end_pos
            continue

        if m := re.match(r"\\headline\s*\{", rest):
            start = pos + m.end() - 1
            end = match_brace(body, start)
            out.append(f"**{clean(body[start + 1:end])}**\n\n---\n\n")
            pos = end + 1
            continue

        if m := re.match(
            r"\{\s*\\fontfamily\{[^}]*\}\\selectfont\\Large\s+(\w+)\s*\}",
            rest,
        ):
            out.append(f"## {m.group(1)}\n\n")
            pos += m.end()
            continue

        if re.match(r"\\begin\{flushleft\}", rest):
            end_pos = find_env(body, "flushleft", pos)
            inner_start = pos + len("\\begin{flushleft}")
            inner_end = end_pos - len("\\end{flushleft}")
            inner = clean(body[inner_start:inner_end])
            if inner:
                out.append(inner + "\n\n")
            pos = end_pos
            continue

        if m := re.match(r"\\begin\{ressection\}\s*\{", rest):
            title_start = pos + m.end() - 1
            title_end = match_brace(body, title_start)
            title = clean(body[title_start + 1:title_end])
            end_pos = find_env(body, "ressection", pos)
            content_end = end_pos - len("\\end{ressection}")
            content = body[title_end + 1:content_end]
            out.append(f"## {title}\n\n")
            out.append(render_section(content))
            pos = end_pos
            continue

        pos += 1

    text = "".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


def render_section(content: str) -> str:
    out: list[str] = []
    pos = 0
    n = len(content)
    while pos < n:
        while pos < n and content[pos] in " \t\n":
            pos += 1
        if pos >= n:
            break
        if content[pos] == "%":
            nl = content.find("\n", pos)
            pos = n if nl < 0 else nl + 1
            continue
        rest = content[pos:]

        if re.match(r"\\begin\{ressubsec\}\s*\{", rest):
            args, after_args = read_args(
                content, pos + len("\\begin{ressubsec}"), 3
            )
            co, locdates, titlerole = args
            end_pos = find_env(content, "ressubsec", pos)
            inner_end = end_pos - len("\\end{ressubsec}")
            out.append(f"### {clean(co)} — {clean(titlerole)}\n")
            out.append(f"{clean(locdates)}\n\n")
            out.append(render_subsec_body(content[after_args:inner_end]))
            pos = end_pos
            continue

        if re.match(r"\\begin\{reslist\}\s*\{", rest):
            args, after_args = read_args(
                content, pos + len("\\begin{reslist}"), 1
            )
            (cat,) = args
            end_pos = find_env(content, "reslist", pos)
            inner_end = end_pos - len("\\end{reslist}")
            out.append(f"**{clean(cat)}**\n")
            out.append(render_bullets(content[after_args:inner_end]))
            pos = end_pos
            continue

        if m := re.match(r"\\ressubitem\s*\{", rest):
            start = pos + m.end() - 1
            end = match_brace(content, start)
            out.append(f"- {clean(content[start + 1:end])}\n")
            pos = end + 1
            continue

        if m := re.match(r"\\resitem\s*\{", rest):
            start = pos + m.end() - 1
            end = match_brace(content, start)
            out.append(f"{clean(content[start + 1:end])}\n")
            pos = end + 1
            continue

        pos += 1

    s = "".join(out)
    if not s.endswith("\n\n"):
        s = s.rstrip("\n") + "\n\n"
    return s


def render_subsec_body(content: str) -> str:
    out: list[str] = []
    pos = 0
    n = len(content)
    while pos < n:
        while pos < n and content[pos] in " \t\n":
            pos += 1
        if pos >= n:
            break
        if content[pos] == "%":
            nl = content.find("\n", pos)
            pos = n if nl < 0 else nl + 1
            continue
        rest = content[pos:]

        if m := re.match(r"\\rescontext\s*\{", rest):
            start = pos + m.end() - 1
            end = match_brace(content, start)
            out.append(f"*{clean(content[start + 1:end])}*\n\n")
            pos = end + 1
            continue

        if m := re.match(r"\\resscope\s*\{", rest):
            start = pos + m.end() - 1
            end = match_brace(content, start)
            out.append(f"{clean(content[start + 1:end])}\n\n")
            pos = end + 1
            continue

        if m := re.match(r"\\ressubitem\s*\{", rest):
            start = pos + m.end() - 1
            end = match_brace(content, start)
            out.append(f"- {clean(content[start + 1:end])}\n")
            pos = end + 1
            continue

        pos += 1

    s = "".join(out)
    if not s.endswith("\n\n"):
        s = s.rstrip("\n") + "\n\n"
    return s


def render_bullets(content: str) -> str:
    out: list[str] = []
    pos = 0
    n = len(content)
    while pos < n:
        while pos < n and content[pos] in " \t\n":
            pos += 1
        if pos >= n:
            break
        if content[pos] == "%":
            nl = content.find("\n", pos)
            pos = n if nl < 0 else nl + 1
            continue
        rest = content[pos:]
        if m := re.match(r"\\ressubitem\s*\{", rest):
            start = pos + m.end() - 1
            end = match_brace(content, start)
            out.append(f"- {clean(content[start + 1:end])}\n")
            pos = end + 1
            continue
        pos += 1
    s = "".join(out)
    if not s.endswith("\n\n"):
        s = s.rstrip("\n") + "\n\n"
    return s


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: tex2md.py <input.tex> <output.md>", file=sys.stderr)
        sys.exit(2)
    src = Path(sys.argv[1]).read_text()
    Path(sys.argv[2]).write_text(convert(src))


if __name__ == "__main__":
    main()
