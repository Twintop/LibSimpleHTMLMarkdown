-- A page-by-page tour of everything LibSimpleHTMLMarkdown renders, for checking by eye in game.
-- Enable it in LibSimpleHTMLMarkdown.xml, then type /lshm (or /script LSHMShowcaseFrame:Show()).
--
-- Each case shows its markdown source, what you should see, and then the rendered result.
-- Every case is rendered on its own, so one that breaks can't hide the others on its page; if
-- a whole page shows as raw HTML, one of its cases produced markup SimpleHTML can't parse.
--
-- The cases are also the library's test fixtures: tests/run_tests.py renders every one of them
-- and checks the output, so add a case here when you add a feature.

local LSHM = LibStub("LibSimpleHTMLMarkdown-1.0")

LibSimpleHTMLMarkdownShowcase = {
  { title = "Headings",
    cases = {
      { name = "ATX headings",
        md = "# Heading 1\n## Heading 2\n### Heading 3\n#### Heading 4\n##### Heading 5\n###### Heading 6",
        expect = "Three heading styles, then Heading 4 to 6 at text size: 4 in the strong color, " ..
                 "5 in the ***both*** color, 6 in gray." },
      { name = "Setext headings",
        md = "Heading 1\n=========\n\nHeading 2\n---------",
        expect = "A Heading 1 and a Heading 2, no rules." },
      { name = "Closing hashes",
        md = "## Closed heading ##\n\n## C#",
        expect = "\"Closed heading\" without #s, then \"C#\" keeping its #." },
      { name = "Not headings",
        md = "#hashtag is text\n\n#5 is text too",
        expect = "Two plain paragraphs that start with #." },
      { name = "Setext heading over two lines",
        md = "A heading that\nwraps in the source\n-------------------",
        expect = "One Heading 2 holding both lines." },
    } },

  { title = "Paragraphs and emphasis",
    cases = {
      { name = "Paragraphs and line breaks",
        md = "These two lines\njoin into one paragraph.\n\nThis line ends with two spaces  \nso this is on a new line.\n\n" ..
             "This line ends with a backslash\\\nso this is on a new line too.",
        expect = "One joined paragraph, then two paragraphs with a line break in each." },
      { name = "Footnotes",
        md = "Arcane Blast stacks four times.[^stacks] Its cost grows with each stack.[^cost]\n\n" ..
             "[^cost]: Each stack adds 100% to the base mana cost.\n" ..
             "[^stacks]: The stacks end 18 seconds after the first cast,\n  or when you cast Arcane Barrage.",
        expect = "[1] and [2] in the text, numbered in reading order, then a rule and the two notes " ..
                 "(the end of the document; each case here is its own document)." },
      { name = "Emphasis",
        md = "*em* and _em_, **strong** and __strong__, **3** and *x*, ***both*** and ___both___.",
        expect = "em in the em color, strong in the strong color, including the one-character ones, " ..
                 "and both in a color of its own (mint)." },
      { name = "Strikethrough",
        md = "~~struck through~~ and ~~ not this ~~",
        expect = "\"struck through\" dimmed gray; SimpleHTML can't draw a line through text. " ..
                 "The second stays as typed, since it has spaces inside the ~~." },
      { name = "Underscores inside words",
        md = "snake_case_name and __init__ and a*b*c",
        expect = "snake_case_name as typed, init in strong, and b in em." },
      { name = "Backslash escapes",
        md = "\\*not em\\* \\_not em\\_ \\# \\~\\~not struck\\~\\~ \\[not a link\\](x)",
        expect = "Every character shown as typed, without the backslashes." },
    } },

  { title = "Code",
    cases = {
      { name = "Code spans",
        md = "Use `LibStub(\"x\")` here. ``a ` inside`` works. `|cffff0000not red|r` stays literal.",
        expect = "Three spans in the code color. The last shows its | characters instead of turning red." },
      { name = "Fenced code block",
        md = "```\nlocal x = 1\n  indented line\n<p>html in code</p>\n```",
        expect = "Three lines of code; the second indented, the third shows its <p> tags." },
      { name = "Indented code block",
        md = "Text first.\n\n    print(\"four spaces\")\n    print(\"make code\")",
        expect = "A paragraph, then two lines of code." },
      { name = "Other fences",
        md = "~~~\ntilde fence\n~~~\n\n````\n```\na fence inside a fence\n```\n````",
        expect = "Two code blocks: \"tilde fence\", then three lines with the ``` lines shown." },
      { name = "Unclosed fence",
        md = "```\nthis fence is never closed",
        expect = "The line in the code color. The next case still renders normally." },
      { name = "After the unclosed fence",
        md = "This is a **normal** paragraph.",
        expect = "A normal paragraph, not code." },
    } },

  { title = "Lists",
    cases = {
      { name = "Bullets",
        md = "* star\n+ plus\n- dash",
        expect = "One list of three items, all with the same marker." },
      { name = "Ordered lists",
        md = " 1. one\n 2. two\n^\n\n a) alpha\n B) Bravo\n^\n\n i] roman one\n II. roman two",
        expect = "Three separate lists: numbers, letters, and Roman numerals, numbered as typed, " ..
                 "with the ) or . typed (i] shows as i.)." },
      { name = "Not lists",
        md = "A. Lincoln was president.\n\nI. M. Pei was an architect.\n\nThe answer is\n42. Not a list.",
        expect = "Three plain paragraphs: a letter or numeral list needs two items in sequence, " ..
                 "and only a list starting at 1 can follow a paragraph line." },
      { name = "List after a paragraph",
        md = "Shopping:\n- bread\n- milk",
        expect = "\"Shopping:\", then a two-item list." },
      { name = "Continuation lines",
        md = "1. first item\n   continues here\n2. second item",
        expect = "\"first item continues here\" as item 1, then item 2." },
      { name = "Nested lists",
        md = "- fruit\n  - apple\n  - pear\n    - conference\n- vegetables\n  1. carrot\n  2. leek",
        expect = "Each level indented further than its parent, each item on its own line." },
      { name = "Loose list",
        md = "- first\n\n- second, with a paragraph:\n\n  more about the second item\n\n      /reload\n\n" ..
             "  - nested\n\n    more about the nested item",
        expect = "Two items. The second item's paragraph and its /reload code start indented under its text, " ..
                 "and the nested item's paragraph is indented one step further." },
      { name = "Rule in a list",
        md = "- above the rule\n\n  ***\n\n- below the rule\n---\n\nafter the list",
        expect = "An item, a rule, the next item (no empty line before it), a second rule ending the list, then a paragraph." },
      { name = "Task lists",
        md = "- [ ] not done\n- [x] done\n1. [X] numbered and done",
        expect = "An empty box, then a green check in place of the markers. The numbered one keeps its number." },
      { name = "List terminator",
        md = "- list one\n^\n- list two",
        expect = "Two lists, with no ^ visible." },
    } },

  { title = "Links and images",
    cases = {
      { name = "Links",
        md = "[inline](https://commonmark.org/help/), [reference][cm], [cm][], <https://example.org>, " ..
             "<user@example.org>\n\n[cm]: https://commonmark.org",
        expect = "Five links. Clicking an http link opens a box with its address." },
      { name = "More link forms",
        md = "[Lua](https://en.wikipedia.org/wiki/Lua_(programming_language)), [wow], and an image by reference: ![sap]\n\n" ..
             "[wow]: https://worldofwarcraft.blizzard.com\n[sap]: Interface\\\\ICONS\\\\ABILITY_SAP.PNG",
        expect = "Two links (the first opens the full address, ending in \"language)\"), then a Sap icon." },
      { name = "Bare urls",
        md = "Visit https://example.org/path_(info). Or www.example.org, or [https://x.example](https://x.example).",
        expect = "Three links. The period and comma after the first two aren't part of them." },
      { name = "Custom link",
        md = "[Next page](showcase:next)",
        expect = "A link that turns to the next page." },
      { name = "Images",
        md = "![Sap](Interface\\\\ICONS\\\\ABILITY_SAP.PNG 32x32)\n\n" ..
             "![Sap](Interface\\\\ICONS\\\\ABILITY_SAP.PNG \"Sap, centered\" 48x48 center)",
        expect = "A 32x32 Sap icon, then a centered 48x48 one with a caption." },
    } },

  { title = "Blockquotes, rules, and tables",
    cases = {
      { name = "Blockquote",
        md = "> These lines\n> join together.\n>\n> A second paragraph.",
        expect = "Left-aligned gray text with a thin gray bar at the start of each line, empty line included, " ..
                 "so the bar runs down the quote: one line, an empty line, then the second paragraph." },
      { name = "Long quote line",
        md = "> This quote line is long enough to wrap in the frame, to show what happens to the bar " ..
             "when SimpleHTML wraps a line: it can only start the line, not each wrapped part of it.",
        expect = "The bar starts the line; the wrapped part starts at the left edge." },
      { name = "Blockquote with a list",
        md = "> - quoted item\n> - another\n>\n> After the list.",
        expect = "A quote holding a two-item list then a line, each line starting with the bar, " ..
                 "and no line with only a bar on it." },
      { name = "Blockquote with a heading, code, and a quote",
        md = "> ## Patch notes\n> Fixed a bug.\n>\n>     /reload\n>\n> > Quoted in the quote.\n>\n> Back in the outer quote.",
        expect = "One quote: the heading as a line in the strong color, the text, /reload in the code color, " ..
                 "then the inner quote with two bars in a paler color, then a line with one bar again." },
      { name = "Horizontal rules",
        md = "above\n\n---\n\n***\n\n___\n\nbelow",
        expect = "Three rules between \"above\" and \"below\"." },
      { name = "Table",
        md = "| Spell | Cost | Notes |\n|-------|-----:|-------|\n| Fireball | 2% | **hot** |\n" ..
             "| Frostbolt | 1% | `a|b` |\n| Escaped \\| pipe | | |",
        expect = "A header row in the header color, then three rows with cells between dim | separators. " ..
                 "The code shows a|b, and \"Escaped | pipe\" keeps its pipe." },
      { name = "Centered table",
        md = "| Left | Right |\n|:----:|:-----:|\n| a | b |",
        expect = "Both rows centered, since every column is." },
    } },

  { title = "HTML, entities, and icons",
    cases = {
      { name = "HTML blocks",
        md = "<p align=\"center\">A centered paragraph in raw HTML.</p>\n\n<hr/>\n\n" ..
             "<p>Unknown tags are hidden: [<strong>you can't see this</strong>]</p>",
        expect = "A centered paragraph, a rule, then empty [ ] brackets." },
      { name = "Broken HTML",
        md = "A stray </a> close, an <a href=\"x\">unclosed link, a <br> break, and x<y <3",
        expect = "One paragraph that renders (not raw HTML). The link runs to the end; x<y <3 shows as typed." },
      { name = "Character references",
        md = "&amp; &lt; &gt; &quot; &copy; &eacute; &mdash; &hellip; &rarr; &spades; &#169; &#x2014; &bogus;",
        expect = "& < > \" © é — … → ♠ © — then &bogus; as typed. A missing glyph shows as a box." },
      { name = "Spacing entities",
        md = "a&nbsp;b a&emsp;b a&ensp;b a&em13;b a&thinsp;b",
        expect = "Five pairs, with gaps from widest (emsp) down." },
      { name = "Raid target icons",
        md = "{rt1} {rt2} {rt3} {rt4} {rt5} {rt6} {rt7} {rt8} {star} {Skull} {X}",
        expect = "The eight raid target icons, then star, skull, and cross again." },
      { name = "WoW escape sequences",
        md = "|cffff8000Orange text|r, an icon |TInterface\\ICONS\\INV_Misc_QuestionMark:0|t, " ..
             "and an atlas |A:groupfinder-icon-role-large-tank:16:16|a.",
        expect = "Orange text, a question mark icon, and a tank role icon." },
    } },

  { title = "Extensions from other Markdown flavors",
    cases = {
      { name = "Alerts",
        md = "> [!NOTE]\n> Useful to know.\n\n> [!TIP]\n> Helpful advice.\n\n> [!IMPORTANT]\n> Key information.\n\n" ..
             "> [!WARNING]\n> Needs **attention** now.\n\n> [!CAUTION]\n> Could go wrong.",
        expect = "Five blocks, each with an icon and a colored title (Note, Tip, Important, Warning, Caution), " ..
                 "then its text, with a bar in that kind's color (blue, green, purple, yellow, red) down its lines." },
      { name = "Definition lists",
        md = "Insanity\n: The resource Shadow Priests build.\n: Spent by Devouring Plague.\nVoidform\n: An older mechanic.",
        expect = "\"Insanity\" in the strong color with two indented definitions under it, then \"Voidform\" with one." },
      { name = "Highlight",
        md = "Remember to ==renew your buffs== before the pull.",
        expect = "\"renew your buffs\" in yellow; SimpleHTML can't color a background." },
      { name = "Superscript and subscript",
        md = "x^2^, x^(n+1)^, H~2~O, and the 4^th^ boss.",
        expect = "x², x⁽ⁿ⁺¹⁾, H₂O as Unicode characters, then \"th\" dimmed (there's no superscript t or h). " ..
                 "A box means the font has no glyph for that character." },
      { name = "Heading anchors",
        md = "### Rotation {#rotation}\n\n[Back to the rotation](#rotation)",
        expect = "A \"Rotation\" heading, without its {#rotation}. Clicking the link prints the heading it points to, " ..
                 "found with :GetHeadings()." },
    } },

  { title = "WoW extensions",
    cases = {
      { name = "Atlas images",
        md = "Roles: ![](atlas:groupfinder-icon-role-large-tank) ![](atlas:groupfinder-icon-role-large-heal) " ..
             "![](atlas:groupfinder-icon-role-large-dps), and a bigger one: ![](atlas:groupfinder-icon-role-large-tank 32x32)",
        expect = "Tank, healer, and damage role icons in the line, then a larger tank icon. They don't break the line." },
      { name = "Game icons and inline textures",
        md = "Cast ![](spell:133) [Fireball](spell:133), use ![](item:6948) [Hearthstone](item:6948), " ..
             "earn ![](achievement:6 20x20) [Level 10](achievement:6). An unknown spell: ![](spell:999999999). " ..
             "A texture in the line: ![](Interface\\\\ICONS\\\\ABILITY_SAP.PNG inline), and a block one:\n\n" ..
             "![](Interface\\\\ICONS\\\\ABILITY_SAP.PNG 32x32)",
        expect = "The Fireball, Hearthstone, and Level 10 icons before their links (the achievement icon bigger), " ..
                 "a question mark for the unknown spell, a Sap icon inside the line, then a 32x32 Sap icon as a block." },
      { name = "Shortcodes",
        md = ":check: done, :x: not done, :question: unknown, :warning: careful. " ..
             "Costs 1:gold: 50:silver: 25:copper:. :tank: :healer: :dps: :unknown: stays as typed, as does 10:30:45.",
        expect = "Check, cross, question mark, and alert icons; gold, silver, and copper coins; the three role icons. " ..
                 ":unknown: and 10:30:45 as typed." },
      { name = "Game links",
        md = "[Fireball](spell:133), [Hearthstone](item:6948), and [Level 10](achievement:6).",
        expect = "Three links. Hovering one shows the game's tooltip for it (ShowLinkTooltip)." },
    } },

  { title = "Options",
    cases = {
      { name = "Per-call options",
        md = "*em* and **strong**\n\n- a list item",
        options = { em = "|cffff4040", ["/em"] = "|r", list_marker = "|TInterface\\COMMON\\Indicator-Yellow.PNG:0|t" },
        expect = "em in red and a yellow dot marker, from options passed to ToHTML. The next case is back to the defaults." },
      { name = "Defaults again",
        md = "*em* and **strong**\n\n- a list item",
        expect = "The default em color and * marker: the previous case's options didn't stick." },
    } },
}

if not CreateFrame then return end -- the tests load this file outside the game

local SOURCE_SPACE = "|TInterface\\Store\\ServicesAtlas:0:0.3:0:0:1024:1024:1023:1024:1023:1024|t"

-- shows text exactly as typed, independent of the library, so a rendering bug can't hide it
local function literal(text, color)
  local lines = {}
  for line in (text .. "\n"):gmatch("(.-)\n") do
    local spaces, rest = line:match("^( *)(.*)$")
    rest = rest:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub("|", "||")
    table.insert(lines, SOURCE_SPACE:rep(#spaces) .. rest)
  end
  return "<p>" .. color .. table.concat(lines, "<br/>") .. "|r</p>"
end

local function body(html)
  return (html:gsub("^%s*<html>%s*<body>", ""):gsub("</body>%s*</html>%s*$", ""))
end

local function render_page(index)
  local section = LibSimpleHTMLMarkdownShowcase[index]
  local parts = { "<html><body>" }
  for _, case in ipairs(section.cases) do
    table.insert(parts, "<h3>" .. case.name .. "</h3>")
    table.insert(parts, literal(case.md, "|cff9d9d9d"))
    table.insert(parts, literal("Expect: " .. case.expect, "|cffffd100"))
    table.insert(parts, "<br/>")
    table.insert(parts, body(LSHM:ToHTML(case.md, case.options)))
    table.insert(parts, "<br/><hr/><br/>")
  end
  table.insert(parts, "</body></html>")
  return table.concat(parts, "\n")
end

local frame = _G["LSHMShowcaseFrame"] or CreateFrame("Frame", "LSHMShowcaseFrame", UIParent, "SimplePanelTemplate")
frame:SetSize(720, 640)
frame:SetPoint("CENTER")
frame:SetMovable(true)
frame:EnableMouse(true)
frame:RegisterForDrag("LeftButton")
frame:SetScript("OnDragStart", frame.StartMoving)
frame:SetScript("OnDragStop", frame.StopMovingOrSizing)
frame:Hide()
tinsert(UISpecialFrames, "LSHMShowcaseFrame")

frame.title = frame.title or frame:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
frame.title:SetPoint("TOP", 0, -14)

frame.scroll = frame.scroll or CreateFrame("ScrollFrame", "LSHMShowcaseScroll", frame, "UIPanelScrollFrameTemplate")
frame.scroll:SetPoint("TOPLEFT", 16, -40)
frame.scroll:SetPoint("BOTTOMRIGHT", -36, 44)

frame.html = frame.html or CreateFrame("SimpleHTML", "LSHMShowcaseHTML", frame.scroll)
frame.html:SetWidth(660)
frame.scroll:SetScrollChild(frame.html)

frame.html:SetFontObject("h1", "GameFontNormalHuge")
frame.html:SetTextColor("h1", 0, 0.6, 1, 1)
frame.html:SetFontObject("h2", "GameFontNormalLarge")
frame.html:SetTextColor("h2", 0, 1, 0, 1)
frame.html:SetFontObject("h3", "GameFontNormal")
frame.html:SetTextColor("h3", 0.4, 0.8, 1, 1)
frame.html:SetFontObject("p", "GameFontHighlight")
frame.html:SetHyperlinkFormat("[|cff3399ff|H%s|h%s|h|r]")

local function make_button(name, label, point, x)
  local button = _G[name] or CreateFrame("Button", name, frame, "UIPanelButtonTemplate")
  button:SetSize(100, 24)
  button:SetPoint(point, x, 14)
  button:SetText(label)
  return button
end

local prevButton = make_button("LSHMShowcasePrev", "< Previous", "BOTTOMLEFT", 16)
local nextButton = make_button("LSHMShowcaseNext", "Next >", "BOTTOMRIGHT", -16)
frame.page = frame.page or 1

function frame:ShowPage(index)
  local count = #LibSimpleHTMLMarkdownShowcase
  self.page = (index - 1) % count + 1
  self.title:SetFormattedText("LibSimpleHTMLMarkdown minor %d, page %d of %d: %s", LSHM.minor or 0,
                              self.page, count, LibSimpleHTMLMarkdownShowcase[self.page].title)
  self.html:SetText(render_page(self.page))
  self.html:SetHeight(math.max(self.html:GetContentHeight() or 0, 1))
  self.scroll:SetVerticalScroll(0)
end

prevButton:SetScript("OnClick", function() frame:ShowPage(frame.page - 1) end)
nextButton:SetScript("OnClick", function() frame:ShowPage(frame.page + 1) end)
frame:SetScript("OnShow", function(self) self:ShowPage(self.page) end)

frame.html:SetScript("OnHyperlinkClick", function(_, link, text)
  if link == "showcase:next" then
    frame:ShowPage(frame.page + 1)
  elseif link:match("^#") then
    -- SimpleHTML can't scroll to a heading; a real handler could switch tabs or pages here
    for _, section in ipairs(LibSimpleHTMLMarkdownShowcase) do
      for _, case in ipairs(section.cases) do
        for _, heading in ipairs(LSHM:GetHeadings(case.md)) do
          if "#" .. heading.id == link then
            print(("[LibSimpleHTMLMarkdown showcase] %s points to the level %d heading \"%s\" in \"%s\"")
                  :format(link, heading.level, heading.text, case.name))
          end
        end
      end
    end
  elseif link:match("^https?://") or link:match("^mailto:") then
    StaticPopup_Show("LIBSIMPLEHTMLMARKDOWN_SHOWCASE_URL", text, nil, { url = link })
  else
    print("[LibSimpleHTMLMarkdown showcase] clicked link:", link)
  end
end)

-- game links ([Fireball](spell:133)) show the game's tooltip
frame.html:SetScript("OnHyperlinkEnter", function(self, link) LSHM:ShowLinkTooltip(self, link) end)
frame.html:SetScript("OnHyperlinkLeave", function() LSHM:HideLinkTooltip() end)

StaticPopupDialogs["LIBSIMPLEHTMLMARKDOWN_SHOWCASE_URL"] = {
  text = "Link: %s", wide = true, closeButton = true, hasEditBox = true, hideOnEscape = true, timeout = 60,
  button1 = OKAY,
  OnShow = function(self, data)
    local editBox = (self.GetEditBox and self:GetEditBox()) or self.editBox or self.EditBox
    editBox:SetText(data.url)
    editBox:HighlightText()
  end,
  OnAccept = function(self) self:Hide() end,
  EditBoxOnEnterPressed = function(self) self:GetParent():Hide() end,
  EditBoxOnEscapePressed = function(self) self:GetParent():Hide() end,
}

SLASH_LIBSIMPLEHTMLMARKDOWNSHOWCASE1 = "/lshm"
SlashCmdList["LIBSIMPLEHTMLMARKDOWNSHOWCASE"] = function() frame:Show() end

print("[|cff00ddddLibSimpleHTMLMarkdown|r] showcase loaded. Type |cff00dddd/lshm|r to see it.")
