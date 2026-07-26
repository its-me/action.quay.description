# Markdown transformations for the description content, invoked via
# `jq -f markdown.jq` with a `--arg mode` selecting which one to run.
# Kept separate from action.yaml so the regex-heavy logic can be read,
# tested, and diffed on its own.

def escape_regex:
  gsub("(?<c>[\\^$.|?*+(){}\\[\\]\\\\])"; "\\\(.c)");

# Rewrites relative markdown links/images to absolute GitHub URLs:
# images (matching $exts_raw, a comma-separated extension list) go to
# "raw" links, everything else (including badge-wrapped-in-link and
# reference-style link definitions) goes to "blob" links. Absolute
# links, in-page anchors, and titled links/images are preserved as-is
# or handled explicitly; see action.quay.description's README for the
# exact coverage.
def url_completion($exts_raw; $raw; $blob):
  ($exts_raw | split(",") | map(escape_regex) | join("|")) as $exts
  | gsub("(?<left>!\\[[^\\]]*\\])\\((?<url>[^:)#\\s\"][^:)\\s\"]*\\.(" + $exts + "))(?<title>(?:\\s+\"[^\"]*\")?)\\)"; "\(.left)(" + $raw + "\(.url)\(.title))")
  | gsub("(?<left>\\[!\\[[^\\]]*\\]\\([^)]*\\)\\])\\((?<url>[^:)#\\s\"][^:)\\s\"]*)(?<title>(?:\\s+\"[^\"]*\")?)\\)"; "\(.left)(" + $blob + "\(.url)\(.title))")
  | gsub("(?<left>(?<!!)\\[[^\\]]+\\])\\((?<url>[^:)#\\s\"][^:)\\s\"]*)(?<title>(?:\\s+\"[^\"]*\")?)\\)"; "\(.left)(" + $blob + "\(.url)\(.title))")
  | split("\n")
  | map(gsub("(?<left>^\\[[^\\]]+\\]:[ \\t]+)(?<url>[^:)#\\s\"][^:)\\s\"]*)(?=\\s|$)"; "\(.left)" + $blob + "\(.url)"))
  | join("\n");

def utf8len:
  explode | map(if . < 128 then 1 elif . < 2048 then 2 elif . < 65536 then 3 else 4 end) | add // 0;

# If truncation left an odd number of ``` fence markers, close the
# dangling fence so the rest of the rendered page doesn't turn into code.
def close_unclosed_fence:
  . as $s
  | ($s | split("\n")) as $lines
  | (reduce $lines[] as $line (false; if ($line | test("^```")) then (. | not) else . end)) as $in_fence
  | if $in_fence then $s + "\n```" else $s end;

# Unicode-safe truncation to at most `n` bytes: cuts on a whole
# codepoint, backs off to the last complete line, then closes any
# fence left open by that cut.
def truncate_bytes(n):
  if (. | utf8len) <= n then .
  else
    . as $s
    | (first(range(n; -1; -1) as $k | $s[0:$k] | select((. | utf8len) <= n))) as $cut
    | ($cut | rindex("\n")) as $nl
    | (if $nl then $cut[0:$nl] else $cut end)
    | close_unclosed_fence
  end;

if $mode == "url-completion" then
  $content | url_completion($exts_raw; $raw; $blob)
elif $mode == "truncate" then
  $content | truncate_bytes($max)
else
  error("markdown.jq: unknown mode \($mode)")
end
