"""Fail if the TOC or an XML file it loads would load a demo or test script.

    python tests/check_release_files.py

Demo.lua and Showcase.lua are for development: enable them locally in LibSimpleHTMLMarkdown.xml, but
commit them commented out. If one shipped enabled, every player would load it, and it creates frames,
a slash command, and a chat message on login. The Tests workflow runs this on every push, and the
Release workflow before packaging a tag, so a commit that loads one can't be released.

Lines inside <!-- --> comments don't count. Run_tests.py doesn't run this check, so tests pass
locally while the showcase is enabled.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_SCRIPTS = {"demo.lua", "showcase.lua"}


def loaded_files(path):
    """Files the TOC or a UI XML file loads, from the folder it's in, with comments removed."""
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    folder = os.path.dirname(path)
    if path.lower().endswith(".toc"):
        names = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
    else:
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        names = re.findall(r"<(?:Script|Include)\b[^>]*\bfile\s*=\s*[\"']([^\"']+)[\"']", text, re.I)
    return [os.path.normpath(os.path.join(folder, n.replace("\\", os.sep))) for n in names]


def main():
    problems, seen = [], set()
    pending = [os.path.join(ROOT, "LibSimpleHTMLMarkdown.toc")]
    while pending:
        path = pending.pop()
        if path in seen or not os.path.exists(path):
            continue
        seen.add(path)
        for file in loaded_files(path):
            name = os.path.basename(file).lower()
            if name in DEV_SCRIPTS:
                problems.append("%s loads %s" % (os.path.relpath(path, ROOT), os.path.relpath(file, ROOT)))
            if file.lower().endswith((".xml", ".toc")):
                pending.append(file)
    for p in problems:
        print("FAIL " + p + ": comment it out before committing a release")
    if not problems:
        print("no demo or test scripts are loaded")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
