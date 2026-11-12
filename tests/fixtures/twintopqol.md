
# 1.0.2-release (2026-11-08)

## General

- Now works on Classic Era and The Burning Crusade Classic too, alongside retail and WoW Forever.

## Flight Timer

New: times every flight you take from a flight master, so the next time you fly that route you know how long is left. It's off until you turn on the bar, the tooltips, or both, on the Flight Timer page under General (flights are timed while either is on).

- Hover a flight point on the flight map to see how long the flight there takes.
- The first time you fly a route, a bar counts up while it's timed. After that, the bar counts down the time left.
- A route you haven't flown yet gets an estimate, marked with ~, once you've flown each of its legs on its own.
- Each route keeps its fastest time, shared by all your characters. A route is timed by every stop it makes, so a character that knows fewer flight points, and flies a longer way to the same place, gets times of its own.
- Flights you leave early (by requesting an early landing, taking a summon, or porting into a battleground or dungeon) aren't recorded.
- On WoW Forever, flights with and without the Frequent Flier legacy perk are timed separately, so a respec doesn't throw either off. A route timed only one way is estimated for the other.
- Drag the bar to move it. On the Flight Timer page, you can also put the bar back where it started, or forget every recorded time.
- Make the bar your own on the same page: lock it in place (a locked bar lets clicks through), set its width and height, pick its texture and font from any LibSharedMedia status bar texture and font, set its font size, and choose its color, plus the color it shows while timing a new route. The bar shows a preview while the page is open.

## Jokes

- Name a channel to tell a joke there instead of group chat: `/tqol joke say`, `yell`, `emote`, `party`, `raid`, `rw` (raid warning), `instance`, `guild`, `officer`, or `whisper` and a name. The chat box's short forms work too (`s`, `y`, `p`, `g`, `w`, and so on).
- As in the chat box, party and raid go to instance chat in a group from the Dungeon Finder or Raid Finder.
- When nobody would hear it, like guild chat when you're not in a guild, nothing is sent and you're told why.

## Talents

- On Classic Era and The Burning Crusade Classic, the Talents table lists every talent in your three talent trees: name, spell ID (of the rank you've learned), talent ID, tree, tab and index, icon ID, ranks, and whether it's learned.
- Sorting, tooltips, shift-click links, and export work just as they do on retail, and the table updates when you learn or reset talents.

## News

- This window now pops up after an update as it should. Before, the login sequence closed it as soon as it opened.

---

# 1.0.1-release (2026-11-04)
## Jokes

- Run copyedit over the jokes list to fix typos, grammar, punctuation, and remove duplicates and near-duplicates. The list is now ~450 jokes, down from ~500.
- If you've customized your joke list, you'll keep it as is. To get the updated jokes, reset your list to the defaults in the Joke Editor.

---

# 1.0.0-release (2026-11-03)

The first public release of Twintop QOL: a grab-bag of quality-of-life (and silly) things for World of Warcraft.

## General

- Type `/tqol` to open the Twintop QOL window, which holds every page and setting. It's also listed under Options > AddOns.
- Ready check response: when you answer "ready" to a ready check, sends a message to the channel you pick: say (the default), yell, raid, raid warning, party, or emote. "Yes chef!" by default, or type your own. Turn it on in the General page.
- Works on both retail and WoW Forever.

## Jokes

- Type `/tqol joke` to tell a joke in your group's chat: raid, instance, or party, whichever fits. Nothing is sent when you're not in a group.
- Ships with over 500 jokes, from groan-worthy terrible dad joke puns to a few written just for WoW players.
- Wipe jokes: after a boss wipe, tells your group a joke to lighten the mood. Turn them on in the Jokes Configuration page, and choose which content they play in: open world, each dungeon and raid difficulty, Mythic+, delves, scenarios, battlegrounds, and arenas.
- By default, jokes don't repeat until every joke on your list has been told, even across sessions. Uncheck it in Configuration for pure random picks.

## Joke Editor

- Type `/tqol jokes` to edit your joke list in game: add your own, fix the ones you don't like, and delete the ones that don't land.
- One joke per line, with line numbers and a highlight on the line you're editing.
- Reset to Defaults brings back the original list at any time.
- If you never customize your list, you get new jokes automatically as they're added in updates.

## Talents

- Type `/tqol talents` (or `/tqol df`) for a sortable table of every talent in your active loadout, built for addon and WeakAura authors, theorycrafters, and the curious.
- Shows each talent's name, spell ID, entry ID, node ID, definition ID, icon ID, tree ID, ranks, and whether it's active.
- Click a column header to sort by it. Hover a row for the spell tooltip, or shift-click to link the spell in chat.
- Export the whole table as tab-separated text, ready to paste into a spreadsheet.
- Updates automatically when you change talents, specialization, or dual spec.

## News

- This window: shows what's new whenever a new version is released. You can turn it off, and reopen it any time with `/tqol news`.

