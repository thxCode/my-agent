# Resolving a GitHub issue

Shared by every `my-*` skill whose selector is a GitHub issue. Upstream is always **GitHub**. The selector is
the user's current request minus any mode token, and it names exactly one issue in one repo.

## Which repo

`owner/repo` comes from `origin` — `git remote get-url origin`. A selector that carries its own `owner/repo`
**overrides** that.

| Form | Example | Repo |
| --- | --- | --- |
| bare number | `123` | from `origin` |
| hash-prefixed | `#123` | from `origin` |
| full URL | `https://github.com/<owner>/<repo>/issues/123` | from the URL — overrides `origin` |
| qualified | `owner/repo#123` | from the selector — overrides `origin` |

Pass the resolved repo explicitly on every read, so an overriding selector can never be answered from `origin`.

## Read path

Read the issue **and its comments** — title, body, labels, state, discussion:

```sh
gh issue view <n> --repo <owner>/<repo> --comments
```

## Unreadable issue

Not found, no access, or the read fails → **stop and report**. What the issue asks for comes from the thread,
never from the number alone.
