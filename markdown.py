#!/usr/bin/env python3
# Markdown transformations for the description content, invoked as
# `python3 markdown.py MODE [options]` with content piped on stdin.
# Kept separate from action.yaml so the regex-heavy logic can be read,
# tested, and diffed on its own.

import argparse
import re
import sys


def url_completion(content: str, exts_raw: str, raw: str, blob: str) -> str:
    # Rewrites relative markdown links/images to absolute GitHub URLs:
    # images (matching exts_raw, a comma-separated extension list) go to
    # "raw" links, everything else (including badge-wrapped-in-link and
    # reference-style link definitions) goes to "blob" links. Absolute
    # links, in-page anchors, and titled links/images are preserved as-is
    # or handled explicitly; see the action's README for the exact coverage.
    exts = "|".join(re.escape(ext) for ext in exts_raw.split(","))

    content = re.sub(
        r'(?P<left>!\[[^\]]*\])\((?P<url>[^:)#\s"][^:)\s"]*\.(?:' + exts + r'))(?P<title>(?:\s+"[^"]*")?)\)',
        lambda m: f'{m["left"]}({raw}{m["url"]}{m["title"]})',
        content,
    )
    content = re.sub(
        r'(?P<left>\[!\[[^\]]*\]\([^)]*\)\])\((?P<url>[^:)#\s"][^:)\s"]*)(?P<title>(?:\s+"[^"]*")?)\)',
        lambda m: f'{m["left"]}({blob}{m["url"]}{m["title"]})',
        content,
    )
    content = re.sub(
        r'(?P<left>(?<!!)\[[^\]]+\])\((?P<url>[^:)#\s"][^:)\s"]*)(?P<title>(?:\s+"[^"]*")?)\)',
        lambda m: f'{m["left"]}({blob}{m["url"]}{m["title"]})',
        content,
    )

    ref_re = re.compile(r'^(?P<left>\[[^\]]+\]:[ \t]+)(?P<url>[^:)#\s"][^:)\s"]*)(?=\s|$)')
    lines = [ref_re.sub(lambda m: f'{m["left"]}{blob}{m["url"]}', line) for line in content.split("\n")]
    return "\n".join(lines)


def close_unclosed_fence(s: str) -> str:
    # If truncation left an odd number of ``` fence markers, close the
    # dangling fence so the rest of the rendered page doesn't turn into code.
    in_fence = False
    for line in s.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
    return s + "\n```" if in_fence else s


def truncate_bytes(s: str, n: int) -> str:
    # Unicode-safe truncation to at most `n` bytes: cuts on a whole
    # codepoint, backs off to the last complete line, then closes any
    # fence left open by that cut.
    encoded = s.encode("utf-8")
    if len(encoded) <= n:
        return s
    cut_bytes = encoded[:n]
    while True:
        try:
            cut = cut_bytes.decode("utf-8")
            break
        except UnicodeDecodeError:
            cut_bytes = cut_bytes[:-1]
    newline = cut.rfind("\n")
    if newline != -1:
        cut = cut[:newline]
    return close_unclosed_fence(cut)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["url-completion", "truncate"])
    parser.add_argument("--exts", default="")
    parser.add_argument("--raw", default="")
    parser.add_argument("--blob", default="")
    parser.add_argument("--max", type=int, default=0)
    args = parser.parse_args()

    content = sys.stdin.read()
    if args.mode == "url-completion":
        sys.stdout.write(url_completion(content, args.exts, args.raw, args.blob))
    else:
        sys.stdout.write(truncate_bytes(content, args.max))


if __name__ == "__main__":
    main()
