# Quay.io repository description

A GitHub Action that updates a Quay.io repository's description from a
markdown file.

## Usage

```yaml
name: Update descriptions

on:
  push:
    branches: [main]
    paths:
      - QUAY.md
  workflow_dispatch:

jobs:
  update-quay:
    runs-on: ubuntu-slim
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v7
      - uses: its-me/action.quay.description@v0
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
| `url-completion`   | Rewrite relative markdown links/images in the description to absolute GitHub URLs, since Quay.io renders the description outside the repository's context. Covers plain `![alt](path)` and `[label](path)` references; titled links/images, in-page anchors, and image-wrapped-in-link badges are left as-is. | `false`   |
| `image-extensions` | Comma-separated file extensions treated as images when `url-completion` is enabled.                                                 | `bmp,gif,jpg,jpeg,png,svg,webp` |

## Description file format

`description-file` (default `QUAY.md`) is a plain markdown file — its
entire content becomes the repository description as-is. Unlike
[its-me/action.hub.description](https://github.com/its-me/action.hub.description),
there's no short/full split, since Quay.io's API only has a single
`description` field.

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for the full text.
