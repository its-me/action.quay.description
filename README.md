# Quay.io description

A GitHub Action that updates a Quay.io repository's description from a
markdown file.

It replaces the `update-quay` job pattern duplicated across this account's
image repositories (e.g.
[its-me/image-workflow](https://github.com/its-me/image-workflow)'s
`update-descriptions.yaml`) with a single reusable step.

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
      - uses: its-me/action.quay.description@v1
        with:
          namespace: ${{ secrets.QUAY_USERNAME }}
          api-token: ${{ secrets.QUAY_API_TOKEN }}
          repository: workflow
```

## Inputs

| Name         | Description                                                                                                                     | Default   |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `namespace`  | Quay.io namespace to publish under. For a robot account username in the form `org+robotname`, pass it as-is — the `+robotname` suffix is stripped automatically. | _(none)_  |
| `repository` | Quay.io repository name, without the namespace (e.g. `workflow`).                                                                   | _(none)_  |
| `api-token`  | Quay.io OAuth application token.                                                                                                    | _(none)_  |
| `file`       | Path to a markdown file whose full content becomes the repository description.                                                     | `QUAY.md` |

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for the full text.
