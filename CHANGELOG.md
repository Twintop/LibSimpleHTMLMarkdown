# Changelog

Releases are numbered `<major>.0.<minor>` after the LibStub version they register, so 1.0.1 is
`LibSimpleHTMLMarkdown-1.0` minor 1. Each release's upload changelog is its own section below.

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
