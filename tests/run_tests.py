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

# the default config's spacers and bars, for the assertions
NBSP = "|TInterface\\Store\\ServicesAtlas:0:0.175:0:0:1024:1024:1023:1024:1023:1024|t"


def bar(rgb):
    """The bar that starts each line of a quote (or an alert, in its kind's color)."""
    return ("|TInterface\\Buttons\\WHITE8X8:0:0.15:0:0:8:8:0:8:0:8:%s|t"
            "|TInterface\\Store\\ServicesAtlas:0:0.5:0:0:1024:1024:1023:1024:1023:1024|t" % rgb)


QBAR = bar("110:110:110")
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
    # a render error raises, instead of becoming the plain text fallback players would see
    lua.execute('LibStub("LibSimpleHTMLMarkdown-1.0").raise_errors = true')
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
    # the text assigned to "local text"; a comment above it shows the [====[ ]====] syntax
    demo = re.search(r"local text = \[(=+)\[\n?(.*?)\]\1\]", read(ROOT, "Demo.lua"), re.S).group(2)
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
    # footnotes: numbered in order of first reference, listed at the end; unknown ones stay as typed
    ("b[^two] a[^one] b[^two] [^none]\n\n[^one]: First.\n[^two]: Second,\n  continued.",
     ["b|cff00dddd[1]|r a|cff00dddd[2]|r b|cff00dddd[1]|r [^none]", "<hr />",
      "[1]|r|TInterface\\Store\\ServicesAtlas:0:0.25:0:0:1024:1024:1023:1024:1023:1024|t Second,\ncontinued."],
     ["[^one]:", "First.</p>\n<p>|cff00dddd[1]"]),
    ("```\n[^1]\n```\n\n[^1]: note", ["[^1]"], ["<hr />"]),
    # link urls keep balanced parentheses; shortcut and collapsed references resolve
    ("[w](https://x.example/A_(b))", ['href="https://x.example/A_(b)"'], []),
    ("[w](<https://x.example/a b> \"title\")", ['href="https://x.example/a b"'], ["title"]),
    ("[id] and [id][] and [x][id]\n\n[id]: https://id.example",
     ['<a href="https://id.example">id</a> and <a href="https://id.example">id</a> and <a href="https://id.example">x</a>'], []),
    ("[not a link]", ["[not a link]"], ["<a"]),
    ("![i][] ![i]\n\n[i]: Interface\\\\ICONS\\\\X", ['<img src="Interface\\ICONS\\X" />'], ["!<a", "\\\\"]),
    # ~~~ and longer fences; a fence closes only with the same character, at least as long
    ("~~~\n<b>x</b>\n~~~", ["&lt;b&gt;x&lt;/b&gt;"], ["~~~"]),
    ("````\n```\ninner\n```\n````", ["```\n<br />inner\n<br />```"], []),
    ("~~~\n```\nstill code\n~~~\nafter", ["```", "<p>after</p>"], []),
    # a backslash at the end of a line breaks it
    ("one\\\ntwo", ["one<br/>\ntwo"], ["\\"]),
    # a bullet list, or one starting at 1, can start right after a paragraph line
    ("Text\n- a\n- b", ["<p>Text</p>", "|t *|T"], ["- a"]),
    ("The answer is\n42. Not a list.", ["42. Not a list."], [" 42."]),
    # a rule indented under a list item stays in the list; an unindented one ends it
    ("- a\n\n  ***\n\n- b", ["<hr />"], []),
    ("- a\n- b\n---\n\nafter", ["<hr />", "<p>after</p>"], ["<h2>"]),
    # a setext heading takes every line of its paragraph
    ("one\ntwo\n===", ["<h1>one\ntwo</h1>"], ["<p>one"]),
    # blockquotes: one left-aligned block with a bar starting each line, without quote marks or rules
    ("> one\n> two", ["<p>|cffc0c0c0" + QBAR + "one\ntwo|r</p>"], ['align="center"', '"', "<hr"]),
    # code, a heading, and a nested quote stay inside the one quote block; a nested quote's lines
    # get the outer bar and their own
    (">     code", [QBAR + "|cff66bbbbcode"], []),
    ("> # Head\n> text", [QBAR + "|cff00ddddHead|r<br />" + QBAR], ["<h1>"]),
    ("> outer\n>> inner", ["<br />" + QBAR + "|cffa8a8a8" + QBAR + "inner|r"], []),
    # a list in a quote leaves no line with only a bar on it
    ("> - a\n> - b\n>\n> after", [QBAR + "\n\n\nafter"], [QBAR + "<br />", QBAR + "\n\n<br />"]),
    # letter and Roman numeral lists need two or more items in sequence
    ("A. Lincoln was president.", ["<p>A. Lincoln was president.</p>"], []),
    ("I. M. Pei was an architect.", ["<p>I. M. Pei was an architect.</p>"], []),
    ("a) one\nb) two", [" a)", " b)"], []),
    ("h. eight\ni. nine", [" h.", " i."], []),
    ("iv. four\nv. five", [" iv.", " v."], []),
    # ordered items keep the delimiter typed
    ("1) one\n2) two", [" 1)", " 2)"], [" 1."]),
    # heading anchors: {#id} isn't shown; #id links pass through
    ("## Setup {#setup}\n\n[jump](#setup)", ["<h2>Setup</h2>", '<a href="#setup">jump</a>'], ["{#"]),
    ("Text {#not-a-heading}", ["{#not-a-heading}"], []),
    # GitHub alerts; an unknown kind stays a blockquote
    ("> [!WARNING]\n> Careful.",
     ["<p>" + bar("210:153:34") + "|TInterface\\DialogFrame\\UI-Dialog-Icon-AlertNew:0|t |cffd29922Warning|r<br />" +
      bar("210:153:34") + "Careful.</p>"], ["[!WARNING]", QBAR]),
    ("> [!bogus]\n> x", [QBAR + "[!bogus]"], []),
    # a blank line ends a quote, so each alert is its own block; a > line alone continues one
    ("> [!NOTE]\n> a\n\n> [!TIP]\n> b",
     ["|cff4493f8Note|r<br />" + bar("68:147:248") + "a</p>", "|cff3fb950Tip|r<br />" + bar("63:185:80") + "b</p>"],
     ["[!TIP]"]),
    ("> one\n\n> two", [QBAR + "one|r</p>", QBAR + "two|r</p>"], []),
    ("> one\n>\n> two", ["one<br />" + QBAR + NBSP + "<br />" + QBAR + "two|r</p>"], []),
    # definition lists; a ": " line without a term is text
    ("Term\n: One\n: Two", ["|cff00ddddTerm|r<br />", "|tOne<br />", "|tTwo<br />"], ["<p>: "]),
    (": alone", ["<p>: alone</p>"], []),
    # highlight, superscript and subscript
    ("==hi==", ["|cffffff66hi|r"], ["=="]),
    ("a == b == c", ["a == b == c"], []),
    ("x^2^ H~2~O x^(n+1)^", ["x²", "H₂O", "x⁽ⁿ⁺¹⁾"], ["^", "~"]),
    ("4^th^", ["4|cffb0b0b0th|r"], []),
    ("\\^x\\^ \\==y\\==", ["^x^", "==y=="], ["|cff"]),
    ("~~strike~~ and ~sub~", ["|cff808080strike|r", "|cffb0b0b0sub|r"], []),
    # atlases are inline |A escapes, not <img> blocks
    ("a ![](atlas:groupfinder-icon-role-large-tank) b ![](atlas:x 16x20)",
     ["a |A:groupfinder-icon-role-large-tank:0:0|a b |A:x:20:16|a"], ["<img"]),
    ("![t][a]\n\n[a]: atlas:x", ["|A:x:0:0|a"], ["<img"]),
    # shortcodes; unknown ones, times, and escaped ones stay as typed
    (":check: :gold: :nope: 10:30:45 \\:check:",
     ["ReadyCheck-Ready:0|t", "UI-GoldIcon:0|t", ":nope:", "10:30:45", " :check:"], []),
    ("`:check:`", [":check:"], ["ReadyCheck"]),
    # game links are ordinary links
    ("[Fireball](spell:133)", ['<a href="spell:133">Fireball</a>'], []),
    # a game icon is shown in the line (outside the game, the question mark icon)
    ("a ![](spell:133) b ![](item:6948 20x20)",
     ["a |TInterface\\ICONS\\INV_Misc_QuestionMark:0:0|t b |TInterface\\ICONS\\INV_Misc_QuestionMark:20:20|t"], ["<img"]),
    ("![](quest:5)", ['<img src="quest:5" />'], []),
    # a texture marked inline is shown in the line; one that isn't is a block
    ("a ![](Interface\\\\ICONS\\\\X 16x16 inline) b", ["a |TInterface\\ICONS\\X:16:16|t b"], ["<img"]),
    ("a ![](Interface\\\\ICONS\\\\X inline) b", ["a |TInterface\\ICONS\\X:0:0|t b"], []),
    ("![](Interface\\\\ICONS\\\\X 16x16)", ['<img src="Interface\\ICONS\\X" width="16" height="16" />'], ["|T"]),
    ("![i][r]\n\n[r]: item:6948", ["|TInterface\\ICONS\\INV_Misc_QuestionMark:0:0|t"], ["<img"]),
    # a loose item's later paragraphs start one list_indent in per level; nested lists keep their own
    ("- a\n\n  more", ["<br />\n\n|TInterface\\Store\\ServicesAtlas:0:1.5:0:0:1024:1024:1023:1024:1023:1024|tmore"], []),
    ("- a\n\n  - b\n\n    more b",
     ["|TInterface\\Store\\ServicesAtlas:0:1.5:0:0:1024:1024:1023:1024:1023:1024|t" * 2 + "more b"],
     ["|TInterface\\Store\\ServicesAtlas:0:1.5:0:0:1024:1024:1023:1024:1023:1024|t" * 3]),
    # h4-h6 are body-sized lines: h4 in the strong color, h5 in strong_em's, h6 muted
    ("#### Four {#four}\n##### Five\n###### Six",
     ["<p>|cff00ddddFour|r</p>", "<p>|cff80ffd0Five|r</p>", "<p>|cff9d9d9dSix|r</p>"], ["<h3>", "{#"]),
    ("### Three", ["<h3>Three</h3>"], []),
    # ***both*** has a color of its own
    ("***both*** ___too___", ["|cff80ffd0both|r |cff80ffd0too|r"], ["|cff00dddd"]),
    ("**strong *em* inside**", ["|cff00ddddstrong |cff00dd00em|r inside|r"], []),
]


def check_cache(lua, failures):
    """Repeat renders come from the cache, and any change to the settings renders again."""
    lua.execute("""
        local l = LibStub("LibSimpleHTMLMarkdown-1.0")
        CACHE_RESULTS = {}
        local function note(name, ok) CACHE_RESULTS[#CACHE_RESULTS + 1] = ok and "" or name end
        local doc = "*em* and :check:"
        l.render_cache, l.render_cache_count = {}, 0
        local markdown, calls = l.markdown, 0
        l.markdown = function(...) calls = calls + 1 return markdown(...) end

        local first = l:ToHTML(doc)
        note("a repeat render wasn't served from the cache", l:ToHTML(doc) == first and calls == 1)

        l.config.em = "|cff123456"
        note("a change to the shared config served a stale render", l:ToHTML(doc):find("|cff123456em", 1, true))
        l.config.em = "|cff00dd00"
        note("the original config didn't come back from the cache", l:ToHTML(doc) == first)

        note("per-call options served a stale render", l:ToHTML(doc, { em = "|cffabcdef" }):find("|cffabcdefem", 1, true))
        local md = l:New({ [":check:"] = "CHECK" })
        note("a :New() renderer served the library's render", md:ToHTML(doc):find("CHECK", 1, true))
        md.config[":check:"] = "CHANGED"
        note("a change to a :New() renderer's settings served a stale render", md:ToHTML(doc):find("CHANGED", 1, true))

        local before = calls
        for i = 1, l.render_cache_limit + 5 do l:ToHTML("doc " .. i) end
        note("the cache grew past its limit", l.render_cache_count <= l.render_cache_limit)
        note("rendering stopped calling markdown", calls > before)
        l.markdown = markdown
    """)
    for problem in lua_list(lua.globals().CACHE_RESULTS):
        if problem:
            failures.append("cache: " + problem)


FUZZ_INLINE = [
    "word", "words here", "*em*", "**strong**", "***both***", "_em_", "__strong__", "snake_case", "~~gone~~",
    "==hi==", "x^2^", "H~2~O", "`code`", "``a ` b``", "`|cffff0000x`", "[link](https://a.example/b_(c))",
    "[ref]", "[ref][]", "[text][ref]", "![](Interface\\\\ICONS\\\\X 16x16)", "![](atlas:x 8x8)", "![](spell:133)",
    "![i](Interface\\\\X 12x12 inline)", "<https://q.example>", "https://bare.example/x.", "www.w.example",
    ":check:", ":nope:", "10:30", "{rt1}", "{Skull}", "&amp;", "&copy;", "&#169;", "&#x2014;", "&bogus;", "&",
    "AT&T", "|cff00ff00green|r", "|TInterface\\\\X:0|t", "<b>bold</b>", "</a>", '<a href="x">', "<br>", "x<y",
    "<3", ">", "\\*", "\\_", "\\#", "\\~", "\\^", "[^1]", "[^nope]", "{#id}", "é", "[", "]", "(", ")", "*", "_",
    "**", "~", "^", "=", "|", "||", "\\", "<!-- c -->", "<span>s</span>", "#tag", "a*b*c", "[x](spell:133)",
]


def fuzz_document(rng):
    """A random document built from every block and inline syntax, valid and malformed."""
    def inline():
        return " ".join(rng.choice(FUZZ_INLINE) for _ in range(rng.randint(1, 6)))

    def block(depth=0):
        kind = rng.randint(0, 17)
        if kind == 0:
            return "#" * rng.randint(1, 7) + rng.choice([" ", ""]) + inline() + rng.choice(["", " {#h}", " ##"])
        if kind == 1:
            return "\n".join(inline() + rng.choice(["", "  ", "\\"]) for _ in range(rng.randint(1, 3)))
        if kind in (2, 3):
            lines = []
            for _ in range(rng.randint(1, 5)):
                marker = rng.choice(["-", "*", "+", "1.", "2)", "a)", "b.", "i.", "ii]", "- [ ]", "- [x]"])
                lines.append(" " * rng.choice([0, 0, 2, 4, 1]) + marker + " " + inline())
                if rng.random() < 0.3:
                    lines.append(rng.choice(["", "  " + inline(), "      code", "  ***", "  > q"]))
            return "\n".join(lines) + rng.choice(["", "\n^"])
        if kind == 4:
            inner = block(depth + 1) if depth < 2 and rng.random() < 0.5 else inline()
            prefix = rng.choice(["> ", ">", "> > ", ">> "])
            head = rng.choice(["", "> [!NOTE]\n", "> [!WARNING]\n", "> [!bogus]\n"])
            return head + "\n".join(prefix + line for line in inner.split("\n")) + rng.choice(["", "\nlazy", "\n>"])
        if kind == 5:
            fence = rng.choice(["```", "~~~", "````", "```lua"])
            body = "\n".join(rng.choice(FUZZ_INLINE + ["```", "~~~", "<p>x</p>", "  x"]) for _ in range(rng.randint(0, 4)))
            return fence + "\n" + body + rng.choice(["\n" + fence.rstrip("lua"), "\n```", ""])
        if kind == 6:
            return "\n".join("    " + rng.choice(FUZZ_INLINE) for _ in range(rng.randint(1, 3)))
        if kind == 7:
            cols = rng.randint(1, 4)
            row = lambda: "| " + " | ".join(rng.choice(FUZZ_INLINE + ["", "a \\| b"]) for _ in range(rng.randint(1, cols + 1))) + " |"
            delim = "|" + "|".join(rng.choice(["---", ":-:", "--:", ":--", "x"]) for _ in range(cols)) + "|"
            return "\n".join([row(), delim] + [row() for _ in range(rng.randint(0, 3))])
        if kind == 8:
            return rng.choice(["<p>raw</p>", '<p align="center">c</p>', "<div>\n*d*\n</div>", "<hr/>", "<p>open",
                               "</p>", "<p><p>n</p></p>", "<h1>h</h1>", "<img src='x'/>", "<!-- c -->"])
        if kind == 9:
            return inline() + "\n: " + inline() + rng.choice(["", "\n: " + inline()])
        if kind == 10:
            return "[^1]: " + inline() + rng.choice(["", "\n  more"])
        if kind == 11:
            return "[ref]: " + rng.choice(["https://r.example", "atlas:x", "Interface\\\\X", "<https://r.example>"])
        if kind == 12:
            return rng.choice(["---", "***", "___", "* * *", "===", "^"])
        if kind == 13:
            return inline() + "\n" + rng.choice(["===", "---"])
        if kind == 14:
            return ": " + inline()
        if kind == 15:
            return "\t" + inline() + "\n \t" + inline()
        if kind == 16:
            return "\n".join(block(depth + 1) for _ in range(2)) if depth < 2 else inline()
        return inline()

    return rng.choice(["\n", "\n\n", "\r\n"]).join(block() for _ in range(rng.randint(1, 8)))


def check_fuzz(lua, failures):
    """Random documents must render, and render to markup SimpleHTML can parse."""
    import random
    seed = int(os.environ.get("FUZZ_SEED", "1"))
    count = int(os.environ.get("FUZZ_COUNT", "400"))
    lib = lua.eval('(LibStub("LibSimpleHTMLMarkdown-1.0"))')
    render = lua.eval(
        "function(lib, s) local ok, r = pcall(lib.ToHTML, lib, s) if ok then return r end return 'ERROR: ' .. tostring(r) end")
    rng, reported = random.Random(seed), 0
    for i in range(count):
        md = fuzz_document(rng)
        bad = problems(render(lib, md), md)
        if bad and reported < 5:
            reported += 1
            failures.append("fuzz (FUZZ_SEED=%d, document %d): %s\n    markdown: %r" % (seed, i, "; ".join(bad), md))
        elif bad:
            reported += 1
    if reported > 5:
        failures.append("fuzz: %d more documents failed" % (reported - 5))


def check_fallback(lua, failures):
    """A render error is reported to the error handler, and the text is shown as plain paragraphs."""
    lua.execute("""
        local l = LibStub("LibSimpleHTMLMarkdown-1.0")
        local markdown = l.markdown
        REPORTED = nil
        geterrorhandler = function() return function(message) REPORTED = message end end
        l.raise_errors, l.render_cache, l.render_cache_count = false, {}, 0
        l.markdown = function() error("boom") end
        FALLBACK = l:ToHTML("A <b>bold</b> & |cffff0000red|r line\\nnext line\\n\\nsecond paragraph")
        l.markdown, l.raise_errors, geterrorhandler = markdown, true, nil
    """)
    html, reported = lua.globals().FALLBACK, lua.globals().REPORTED
    want = ("<html><body><p>A &lt;b&gt;bold&lt;/b&gt; &amp; ||cffff0000red||r line<br />next line</p>\n"
            "<p>second paragraph</p></body></html>")
    if html != want:
        failures.append("fallback: got %r, want %r" % (html, want))
    if not reported or "boom" not in reported:
        failures.append("fallback: the error wasn't reported to the error handler: %r" % reported)
    for p in problems(html, ""):
        failures.append("fallback: " + p)


def check_game_icons(lua, failures):
    """game_icon uses the client's API: C_Spell and C_Item on Retail, the older globals on Classic."""
    lua.execute("""
        local l = LibStub("LibSimpleHTMLMarkdown-1.0")
        ICONS = {}
        C_Spell = { GetSpellTexture = function(id) return id == 133 and 135812 or nil end }
        C_Item = { GetItemIconByID = function(id) return 134414 end }
        C_CurrencyInfo = { GetCurrencyInfo = function(id) return { iconFileID = 1455894 } end }
        GetAchievementInfo = function(id) return id, "n", 10, true, 1, 1, 1, "d", 0, 236496 end
        ICONS[1] = l.game_icon("spell", "133")
        ICONS[2] = l.game_icon("spell", "999")
        ICONS[3] = l.game_icon("item", "6948")
        ICONS[4] = l.game_icon("currency", "1792")
        ICONS[5] = l.game_icon("achievement", "6")
        C_Spell, C_Item = nil, nil
        GetSpellTexture = function(id) return "Interface\\\\ICONS\\\\Spell_Fire_FlameBolt" end
        GetItemIcon = function(id) error("no such item") end
        ICONS[6] = l.game_icon("spell", "133")
        ICONS[7] = l.game_icon("item", "1")
        C_CurrencyInfo, GetAchievementInfo, GetSpellTexture, GetItemIcon = nil, nil, nil, nil
    """)
    got = [str(x) for x in lua_list(lua.globals().ICONS)]
    q = "Interface\\ICONS\\INV_Misc_QuestionMark"
    want = ["135812", q, "134414", "1455894", "236496", "Interface\\ICONS\\Spell_Fire_FlameBolt", q]
    if got != want:
        failures.append("game_icon: got %r, want %r" % (got, want))


def check_headings(lua, failures):
    lib = lua.eval('(LibStub("LibSimpleHTMLMarkdown-1.0"))')
    headings = lua.eval('function(l, s) local o = {} for _, h in ipairs(l:GetHeadings(s)) do '
                        'o[#o + 1] = h.level .. ":" .. h.id .. "=" .. h.text end return table.concat(o, " | ") end')
    got = headings(lib, "# Intro\n## Setup {#custom}\n## Intro\n#### Deep **one**\nSetext\n---\n"
                        "```\n# not a heading\n```\n- # in a list")
    want = "1:intro=Intro | 2:custom=Setup | 2:intro-1=Intro | 4:deep-one=Deep **one** | 2:setext=Setext"
    if got != want:
        failures.append("GetHeadings: got %r, want %r" % (got, want))


def check_upgrade(failures):
    """A newer copy of the library keeps the config changes AddOns made to the older one."""
    source = read(ROOT, "LibSimpleHTMLMarkdown.lua")

    def load(lua, minor):
        lua.execute(re.sub(r"local\s+MARKDOWN10_MINOR = \d+", "local MARKDOWN10_MINOR = %d" % minor, source, count=1))
        return lua.eval('(LibStub("LibSimpleHTMLMarkdown-1.0"))')

    lua = lua51.LuaRuntime(unpack_returned_tuples=True)
    lua.execute("strmatch = string.match; strfind = string.find")
    lua.execute(read(ROOT, "LibStub", "LibStub.lua"))

    # from minor 2 and earlier, which kept no copy of their defaults
    lib = load(lua, 1000)
    lib.config_defaults = None
    lib.config.strong = "|cffffcc00"
    lib.config.custom = "kept"
    lib = load(lua, 1001)
    if lib.config.strong != "|cffffcc00" or lib.config.custom != "kept" or lib.config.em != "|cff00dd00":
        failures.append("upgrade: changes made under a copy without config_defaults weren't kept")

    # from a copy with defaults: changed keys are kept, the rest take the new copy's defaults
    lib.config.em = "|cffff9966"
    # code left at an older default that the new copy changed
    lua.execute('local l = LibStub("LibSimpleHTMLMarkdown-1.0") l.config_defaults.code = "|cff000000" l.config.code = "|cff000000"')
    lib = load(lua, 1002)
    if lib.config.em != "|cffff9966" or lib.config.strong != "|cffffcc00":
        failures.append("upgrade: changes made under a copy with config_defaults weren't kept")
    if lib.config.code != "|cff66bbbb":
        failures.append("upgrade: a key left at its old default didn't take the new default")


def check_state(lua, failures):
    lib = lua.eval('(LibStub("LibSimpleHTMLMarkdown-1.0"))')
    render = lua.eval("function(r, s, o) return r:ToHTML(s, o) end")

    # an unclosed fence in one document doesn't turn the next into code
    render(lib, "```\nnever closed")
    if "|cff66bbbb" in render(lib, "plain"):
        failures.append("state: an unclosed fence leaked into the next document")

    # h4 follows the renderer's strong color, and can be shown as h3 as before
    if "<p>|cffffcc00Four|r</p>" not in render(lib, "#### Four", lua.eval('{ strong = "|cffffcc00" }')):
        failures.append("state: h4 didn't take the strong color from the settings")
    as_h3 = lua.eval('{ h4 = "<h3>", ["/h4"] = "</h3><br />", h4_style = false }')
    if "<h3>Four</h3>" not in render(lib, "#### Four", as_h3):
        failures.append("state: h4 couldn't be set back to <h3>")

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
    check_upgrade(failures)
    check_headings(lua, failures)
    check_cache(lua, failures)
    check_fallback(lua, failures)
    check_game_icons(lua, failures)
    check_fuzz(lua, failures)

    if update:
        print("updated %d golden files" % written)
    for f in failures:
        print("FAIL " + f)
    print("%d documents, %d assertions: %s" % (len(docs), len(ASSERTIONS), "%d failures" % len(failures) if failures else "all passed"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
