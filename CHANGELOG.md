# Changelog

Releases are numbered `<major>.0.<minor>` after the LibStub version they register, so 1.0.1 is
`LibSimpleHTMLMarkdown-1.0` minor 1. Each release's upload changelog is its own section below.

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
