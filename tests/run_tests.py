"""Render every test document with LibSimpleHTMLMarkdown and check the output.

    python tests/run_tests.py           run every check
    python tests/run_tests.py --update  rewrite tests/golden/ from the current output, then run the checks

Needs Python 3.8+ and lupa (pip install lupa), which bundles Lua 5.1, the Lua version WoW runs.

The documents are the Showcase.lua cases, the Demo.lua text, tests/probes.py, and tests/fixtures/*.md
(real AddOn news pages). Every one is checked for:
  * markup SimpleHTML can't parse, which makes it show the whole document as raw text
    (not well-formed XML, or an entity other than &amp; &lt; &gt; &quot;);
  * a block (p, h1-h3, img, hr) inside a p or heading, which SimpleHTML can't lay out;
  * a tag SimpleHTML doesn't know that the source didn't contain (SimpleHTML hides those).
Each output is also compared with its golden file in tests/golden/, so any change to the rendering
shows up as a diff to review. ASSERTIONS and the state checks below pin down specific behavior.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

try:
    from lupa import lua51
except ImportError:
    sys.exit("lupa is missing: pip install lupa")

TESTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TESTS)
GOLDEN = os.path.join(TESTS, "golden")
sys.path.insert(0, TESTS)
from probes import PROBES  # noqa: E402

KNOWN_TAGS = {"html", "body", "h1", "h2", "h3", "p", "br", "img", "a", "hr"}
FLOW_BLOCKS = {"p", "h1", "h2", "h3"}
BLOCKS = FLOW_BLOCKS | {"img", "hr"}


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


def load_lua():
    lua = lua51.LuaRuntime(unpack_returned_tuples=True)
    lua.execute("strmatch = string.match; strfind = string.find")  # WoW globals LibStub uses
    lua.execute(read(ROOT, "LibStub", "LibStub.lua"))
    lua.execute(read(ROOT, "LibSimpleHTMLMarkdown.lua"))
    lua.execute(read(ROOT, "Showcase.lua"))  # stops after its cases, since CreateFrame is nil
    return lua


def lua_list(table):
    return [table[i] for i in range(1, len(table) + 1)] if table is not None else []


def documents(lua):
    """(group, name, markdown, options) for every document to render."""
    docs = []
    for s, section in enumerate(lua_list(lua.globals().LibSimpleHTMLMarkdownShowcase), 1):
        for c, case in enumerate(lua_list(section.cases), 1):
            name = "%02d-%02d-%s" % (s, c, re.sub(r"[^a-z0-9]+", "-", case.name.lower()).strip("-"))
            docs.append(("showcase", name, case.md, case.options))
    demo = re.search(r"\[(=+)\[\n?(.*?)\]\1\]", read(ROOT, "Demo.lua"), re.S).group(2)
    docs.append(("demo", "demo", demo, None))
    for name, md in PROBES:
        docs.append(("probes", name, md, None))
    for file in sorted(os.listdir(os.path.join(TESTS, "fixtures"))):
        if file.endswith(".md"):
            docs.append(("fixtures", file[:-3], read(TESTS, "fixtures", file), None))
    return docs


def problems(html, source):
    if html.startswith("ERROR"):
        return [html]
    out = []
    if not (html.startswith("<html><body>") and html.endswith("</body></html>")):
        out.append("not wrapped in <html><body>")
    bad = sorted(set(re.findall(r"&(?!amp;|lt;|gt;|quot;)[#\w]*;?", html)))
    if bad:
        out.append("entities SimpleHTML can't parse: " + " ".join(bad[:8]))
    try:
        root = ET.fromstring(re.sub(r"&(?!amp;|lt;|gt;|quot;)", "&amp;", html))
    except ET.ParseError as e:
        return out + ["not well-formed: %s" % e]
    for el in root.iter():
        tag = el.tag.lower()
        if tag not in KNOWN_TAGS and not re.search(r"<\s*" + re.escape(tag) + r"\b", source, re.I):
            out.append("unknown tag <%s> the source doesn't contain" % el.tag)
        if tag in FLOW_BLOCKS:
            for d in el.iter():
                if d is not el and d.tag.lower() in BLOCKS:
                    out.append("<%s> inside <%s>" % (d.tag, el.tag))
    return sorted(set(out))


# (markdown, strings the output must contain, strings it must not contain)
ASSERTIONS = [
    # a stray inline close is dropped and an unclosed one is closed; void tags are self-closed
    ("a </a> b", [], ["</a>"]),
    ('<a href="x">open', ['<a href="x">open</a></p>'], []),
    ("a<br>b", ["a<br />b"], ["<br>"]),
    ("<p>raw <b>bold</p>", ["<p>raw <b>bold</b></p>"], []),
    # blockquote lines join with whitespace, and blank quote lines don't add quote marks
    ("> one\n> two", ["one\ntwo"], ["onetwo"]),
    ("> one\n>\n> two", [], ['<br />"']),
    # _ inside a word is literal; * still works inside a word
    ("snake_case_name", ["snake_case_name"], ["|cff00dd00"]),
    ("a*b*c", ["a|cff00dd00b|rc"], []),
    # ATX headings need a space after the #s
    ("#hashtag", ["<p>#hashtag</p>"], ["<h1>"]),
    ("# C#", ["<h1>C#</h1>"], []),
    # | in code is doubled so it can't start a WoW escape sequence
    ("`|cffff0000x`", ["||cffff0000x"], []),
    ("```\n|T\n```", ["||T"], []),
    # a one-character strong span
    ("**3**", ["|cff00dddd3|r"], []),
    # strikethrough
    ("~~gone~~", ["|cff808080gone|r"], ["~~"]),
    ("~~ spaced ~~", ["~~ spaced ~~"], []),
    ("\\~\\~kept\\~\\~", ["~~kept~~"], []),
    # task lists
    ("- [ ] open\n- [x] done", ["UI-CheckBox-Up", "ReadyCheck-Ready"], ["[ ]", "[x]"]),
    # nested lists: each level indented one more list_indent, every item on its own line
    ("- a\n  - b\n    - c\n- d", ["0:1.5:0:0"], ["- c", "- b"]),
    ("1. one\n   more\n2. two", [" 1.", " 2."], []),
    # tables
    ("| a | b |\n|---|---|\n| 1 | 2 |", ["|cff00dddda|r", "1  |cff808080|||r  2"], ["|---|"]),
    ("| a |\n|:-:|\n| 1 |", ['<p align="center">'], []),
    ("| `x|y` | z \\| w |\n|---|---|", ["x||y", "z || w"], []),
    # bare urls
    ("see https://example.org/a_(b).", ['<a href="https://example.org/a_(b)">https://example.org/a_(b)</a>.'], []),
    ("www.example.org", ['<a href="http://www.example.org">www.example.org</a>'], []),
    ("[https://x.example](https://y.example)", ['<a href="https://y.example">https://x.example</a>'],
     ['href="https://x.example"']),
    ("<https://q.example>", ['<a href="https://q.example">https://q.example</a>'], ["<a href=\"https://q.example\"><a"]),
    ('<a href="https://r.example">text</a>', ['<a href="https://r.example">text</a>'], []),
    ("`https://code.example`", [], ["<a"]),
]


def check_state(lua, failures):
    lib = lua.eval('(LibStub("LibSimpleHTMLMarkdown-1.0"))')
    render = lua.eval("function(r, s, o) return r:ToHTML(s, o) end")

    # an unclosed fence in one document doesn't turn the next into code
    render(lib, "```\nnever closed")
    if "|cff66bbbb" in render(lib, "plain"):
        failures.append("state: an unclosed fence leaked into the next document")

    # per-call options don't stick, and don't change the shared config
    options = lua.eval('{ em = "|cffff0000" }')
    if "|cffff0000a" not in render(lib, "*a*", options):
        failures.append("state: per-call options weren't applied")
    if "|cffff0000" in render(lib, "*a*") or lib.config.em != "|cff00dd00":
        failures.append("state: per-call options changed the shared config")

    # a :New() renderer has its own settings and falls back to the library's
    md = lua.eval('(LibStub("LibSimpleHTMLMarkdown-1.0"):New({ strong = "|cff0000ff" }))')
    out = render(md, "*a* **b**")
    if "|cff0000ffb" not in out or "|cff00dd00a" not in out:
        failures.append("state: a :New() renderer didn't combine its settings with the defaults: " + out)
    if "|cff0000ff" in render(lib, "**b**"):
        failures.append("state: a :New() renderer changed the shared config")
    lib.config.em = "|cff123456"
    if "|cff123456a" not in render(md, "*a*"):
        failures.append("state: a :New() renderer didn't pick up a change to the library's config")
    lib.config.em = "|cff00dd00"

    # a table that isn't all strings is rejected without erroring
    lua.execute("print = function() end")
    if render(lib, lua.eval("{ 'a', 1 }")) != "":
        failures.append("state: a table with a non-string item wasn't rejected")


def main():
    update = "--update" in sys.argv[1:]
    lua = load_lua()
    lib = lua.eval('(LibStub("LibSimpleHTMLMarkdown-1.0"))')
    render = lua.eval(
        "function(lib, s, o) local ok, r = pcall(lib.ToHTML, lib, s, o) if ok then return r end return 'ERROR: ' .. tostring(r) end")

    failures, written, expected_files = [], 0, set()
    docs = documents(lua)
    for group, name, md, options in docs:
        html = render(lib, md, options)
        for p in problems(html, md):
            failures.append("%s/%s: %s" % (group, name, p))

        path = os.path.join(GOLDEN, group, name + ".html")
        expected_files.add(os.path.normcase(path))
        old = read(path) if os.path.exists(path) else None
        if update and old != html:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(html)
            written += 1
        elif old is None:
            failures.append("%s/%s: no golden file (run with --update to create it)" % (group, name))
        elif old != html:
            failures.append("%s/%s: output differs from tests/golden/%s/%s.html" % (group, name, group, name))

    if os.path.isdir(GOLDEN):
        for dirpath, _, files in os.walk(GOLDEN):
            for file in files:
                path = os.path.join(dirpath, file)
                if os.path.normcase(path) not in expected_files:
                    if update:
                        os.remove(path)
                        written += 1
                    else:
                        failures.append("golden file with no document: " + os.path.relpath(path, TESTS))

    for md, present, absent in ASSERTIONS:
        html = render(lib, md, None)
        for s in present:
            if s not in html:
                failures.append("assertion %r: output lacks %r\n    %s" % (md, s, html))
        for s in absent:
            if s in html:
                failures.append("assertion %r: output contains %r\n    %s" % (md, s, html))

    check_state(lua, failures)

    if update:
        print("updated %d golden files" % written)
    for f in failures:
        print("FAIL " + f)
    print("%d documents, %d assertions: %s" % (len(docs), len(ASSERTIONS), "%d failures" % len(failures) if failures else "all passed"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
