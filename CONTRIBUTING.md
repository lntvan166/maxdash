# Contributing

maxdash gets better every time someone tries it on a bike. **Protocol findings are the most wanted
contribution**: the more bikes tested, the clearer the protocol becomes for everyone.

## Ways to help

| You have | Do this |
|---|---|
| Tried an app on your bike (any result, even "nothing happened") | [Open a bike report](https://github.com/lntvan166/maxdash/issues/new?template=bike-report.yml) |
| Found a command or value the docs get wrong or miss | [Open a protocol finding](https://github.com/lntvan166/maxdash/issues/new?template=protocol-finding.yml), or a pull request |
| Designed your own dash or phone screens | [Share your design](https://github.com/lntvan166/maxdash/issues/new?template=template-share.yml) |
| Fixed a doc, a typo, an install step | A pull request |
| A question or an idea | [Open an issue](https://github.com/lntvan166/maxdash/issues/new/choose): the answer then helps everyone |
| No GitHub account | Message the author on Telegram (see Contact in the [README](README.md)) |

Every issue and pull request is read; the author decides case by case what goes in.

## Rules for protocol facts

Every fact in `docs/protocol/` and every vector in `vectors/` carries one source label
([what they mean](docs/protocol/README.md#source-labels)):

- **observed**: you saw it on a real bike. Add your test to [observations.md](docs/protocol/observations.md)
  as `## <date> — <bike>, dash <part>, <you>` and point the label at it.
- **documented — not yet observed**: from public information, not yet seen on a bike.
- **assumed**: a guess or a design choice.

When your bike disagrees with a documented fact, the bike wins: change the doc, keep the old claim in your
observation entry.

**Never** paste code, text or binaries from vendor apps or firmware, and never use vendor logos.
Describe behaviour in your own words. Leave out serials, VINs, plates, home addresses, passkeys and CCU codes.

## Checks

```sh
python3 tools/lint.py            # leaks, source labels, links, skill paths
python3 tools/check_vectors.py   # every vector recomputed
python3 -m unittest tools/test_lint.py tools/test_check_vectors.py
npm install && node tools/check_templates.mjs   # templates: safe area, screenshots
```

CI runs the Python checks and a secret scan on every pull request.

## Licence

By contributing you agree that docs and vectors are released under CC BY 4.0, and templates, tools and the
skill under MIT.
