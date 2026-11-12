# Changelog

Releases are numbered `<major>.0.<minor>` after the LibStub version they register, so 1.0.1 is
`LibSimpleHTMLMarkdown-1.0` minor 1. Each release's upload changelog is its own section below.

## 1.0.4

Syntax from other Markdown flavors (not in CommonMark or GFM, but what other renderers use):

- GitHub's alerts: a quote starting `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, or `[!CAUTION]` shows
  an icon and a colored title, then its text.
- Definition lists: a term line, then `: definition` lines.
- `==Highlight==`, shown in a color, and `x^2^` / `H~2~O`, shown with Unicode superscript and subscript
  characters (`script_glyphs`).
- Heading ids: `## Setup {#setup}` hides the id, and `:GetHeadings(text)` lists every heading's level, text,
  and id, for a table of contents or for handling `[links](#setup)`.

WoW extensions:

- Atlases: `![](atlas:name)` or `![](atlas:name 32x32)` is shown in the line.
- Shortcodes: `:check:`, `:x:`, `:question:`, `:warning:`, `:gold:`, `:silver:`, `:copper:`, `:tank:`,
  `:healer:`, and `:dps:` become icons. Add your own as config keys, like `[":myicon:"]`.
- `:ShowLinkTooltip(owner, link)` and `:HideLinkTooltip()` show the game's tooltip for links such as
  `[Fireball](spell:133)` from a frame's hyperlink scripts.

`\^`, `\=`, and `\:` are backslash escapes, for text these would otherwise change.

Faster:

- Rendering is several times faster: a 51 KB news page went from about 450 ms to about 60 ms. Showing a
  document again with the same settings takes no time at all, since recent renders are kept (changing any
  setting renders it again).

Blockquotes look like they do in other renderers: left-aligned gray text with a bar at the start of each line
(`blockquote_bar`), instead of centered yellow text in quote marks between two rules. A quote inside a quote
adds its own bar, and alerts have a bar in their kind's color (`admonition_note_bar` and so on). SimpleHTML
can't put a bar on the wrapped part of a long line.

Also:

- A loose list item's later paragraphs and code start indented under the item's text.
- `***both***` has a color of its own (`strong_em`), instead of em's color inside strong's.
- A blank line ends a blockquote, so two quotes (or alerts) with a blank line between them are two blocks. A
  line of just `>` still continues a quote.

## 1.0.3

New Markdown support:

- Nested lists. Each level is indented further, and `list_marker_2`, `list_marker_3`, and so on can give each
  level its own marker.
- Task lists: `- [ ]` and `- [x]` show an empty box or a check mark.
- Tables. SimpleHTML can't lay out columns, so each row is a line of cells between separators, with the header
  row colored.
- `~~Strikethrough~~`, shown dimmed.
- Bare `https://` and `www.` addresses become links.
- Footnotes: `[^id]` shows a number, and the notes (`[^id]: text`) are listed at the end of the document.
- `~~~` code fences, and fences of four or more backticks, which can hold a ``` line.
- Shortcut references (`[id]`) and image references (`![alt][]`, `![alt]`).
- A backslash at the end of a line breaks it, like two trailing spaces.

Settings without changing other AddOns' text:

- `:ToHTML(text, settings)` applies settings to that call only, and `:New(settings)` makes a renderer with its
  own settings. Changing the library's `config` table changes the text of every AddOn that uses it.
- The AceGUI widget's settings now apply only to the widget.
- When a newer copy of the library loads, the config changes AddOns made to the older copy are kept. They
  were dropped.

Bug fixes:

- A closing tag with no opening tag (`</a>`), a tag left open, or `<br>` without a slash no longer makes
  SimpleHTML show the whole document as raw text.
- Blockquote lines are joined with a space instead of run together, and a blank `>` line no longer adds a `"`.
- `snake_case_names` aren't emphasized, `#hashtag` isn't a heading, and `**x**` is strong.
- A `|` in code is shown as itself instead of starting a UI escape sequence.
- The `^` that ends a list is no longer shown.
- Lists are numbered correctly when an item spans several lines, and an item's indented paragraphs, code, and
  rules stay in the item. Ordered items keep the `)` or `.` typed after their number.
- A bullet list, or one starting at 1, can start right after a paragraph line. An unindented rule or heading
  ends a list.
- "A. Lincoln was president." and "I. M. Pei" aren't lists: a letter or Roman numeral list needs at least
  two items in sequence.
- A footnote definition no longer turns into a broken link definition that eats the note's first word.
- Link urls keep balanced parentheses, as in `(https://en.wikipedia.org/wiki/Lua_(programming_language))`, and
  backslash escapes work in link definitions' urls.
- A setext heading (text underlined with `===` or `---`) takes every line of its paragraph.
- Blockquotes keep code indented in them as code, and a heading or quote inside a quote stays in it instead of
  leaving a stray `"` on a line of its own.

Also new: `Showcase.lua`, an in-game tour of everything the library renders (enable it in
`LibSimpleHTMLMarkdown.xml`, then type `/lshm`), and tests that run on every push and before each release.

## 1.0.2

Bug fixes. Each of these could leave a document mangled, or make SimpleHTML show the whole document as raw text.

- An unclosed code fence no longer turns later documents into code blocks, including documents from other AddOns,
  since the library object is shared.
- A `<` that doesn't start a tag (`x<y`, `<3`) is escaped.
- Raw HTML blocks pass through unchanged instead of being wrapped in another `<p>`. HTML inside a code fence stays code.
- Blocks are never nested: loose list items, code in list items, and headings or images inside another block become
  a flat run of blocks.
- Numeric character references and common named entities (Latin-1, dashes, curly quotes, arrows, and so on) are
  decoded to the character. Any other entity is shown literally.

## 1.0.1

First release. LibSimpleHTMLMarkdown is a fork of [LibMarkdown-1.0](https://github.com/endurantgames/WoW-LibMarkdown)
by Oraibi-MoonGuard, which is no longer maintained, starting from its last version, minor 9. It registers under its
own LibStub name, `LibSimpleHTMLMarkdown-1.0`, so it never collides with copies of LibMarkdown that other AddOns
still embed.

- `:ToHTML()` accepts a table of strings, as documented; LibMarkdown always printed an error.
- Reference links and images, `<user@example.org>` autolinks, and a code fence on the last line no longer error.
- Roman numeral lists (`i.`, `ii.`) are recognized as Roman numerals.
- The AceGUI widget is `SimpleHTMLMarkdown_Description`, and it only registers when `AceGUI-3.0` is loaded.

See [Changes from LibMarkdown](https://github.com/Twintop/LibSimpleHTMLMarkdown#changes-from-libmarkdown) for every
rename and fix.
