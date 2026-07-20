# Quay.io repository description

A GitHub Action that updates a Quay.io repository's description from a
markdown file.

## Why this exists

- It's a plain composite action — a handful of `curl`/`jq` calls —
  with no Docker daemon required to start it, so it runs on minimal
  runners, including this account's `ubuntu-slim` runner.
- It parses Quay's `org+robotname` robot-account username format
  automatically, rather than expecting the namespace pre-split.
- It rewrites relative markdown links/images to absolute GitHub URLs
  (`url-completion`), since Quay renders the description outside the
  repository's context.

## Usage

```yaml
name: Quay.io Description Update

on:
  push:
    branches: [main]
    paths:
      - QUAY.md
  workflow_dispatch:

jobs:
  quay:
    runs-on: ubuntu-slim
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v7
      - uses: its-me/action.quay.description@v1
        with:
          namespace: ${{ secrets.QUAY_USERNAME }}
          api-token: ${{ secrets.QUAY_API_TOKEN }}
          repository: workflow
```

## Inputs

| Name               | Description                                                                                                                     | Default   |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `namespace`        | Quay.io namespace to publish under. For a robot account username in the form `org+robotname`, pass it as-is — the `+robotname` suffix is stripped automatically. | _(none)_  |
| `repository`       | Quay.io repository name, without the namespace (e.g. `workflow`).                                                                   | _(none)_  |
| `api-token`        | Quay.io OAuth application token.                                                                                                    | _(none)_  |
| `description-file` | Path to a markdown file whose full content becomes the repository description.                                                     | `QUAY.md` |
| `url-completion`   | Rewrite relative markdown links/images in the description to absolute GitHub URLs, since Quay.io renders the description outside the repository's context. Covers `![alt](path)` and `[label](path)` references (with or without a title), `[![alt](img)](path)` badge-links, and `[ref]: path` link reference definitions. In-page anchors (`#section`) are deliberately left as-is. | `false`   |
| `image-extensions` | Comma-separated file extensions treated as images when `url-completion` is enabled.                                                 | `bmp,gif,jpg,jpeg,png,svg,webp` |

## Description file format

`description-file` (default `QUAY.md`) is a plain markdown file — its
entire content becomes the repository description as-is. Unlike
[its-me/action.hub.description](https://github.com/its-me/action.hub.description),
there's no short/full split, since Quay.io's API only has a single
`description` field.

## Length limit

The description is truncated to 25,000 bytes in a Unicode-safe way —
truncation always lands on a whole character, never mid-codepoint — and
then backs off to the last complete line, so a cut never lands mid-way
through a markdown link or image reference (relevant since
`url-completion` can expand a short relative path into a much longer
absolute URL). If the cut leaves an unclosed ` ``` ` code fence open, a
closing fence is appended so the rest of the page doesn't render as
code. This isn't a confirmed Quay.io limit (its `description` column
is an unbounded `TEXT` field); it's a conservative safety cap matching
Docker Hub's known limit. When truncation happens, a `::warning::`
annotation is emitted in the job log.

## Retries

The description update request retries up to 3 times (5-second delay)
on transient failures — timeouts, connection refused, and HTTP
408/429/5xx — via `curl --retry`. Permanent failures (e.g. a bad
`api-token`) are not retried.

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for the full text.
