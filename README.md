# The World in One Page — Dense Grid, 24 November 2026

[![news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Tenguu0/news-image-20261124-v3-dense-grid/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Tenguu0/news-image-20261124-v3-dense-grid/reward.svg)](https://make.fun/bounty/news-image-20261124)

A make.fun entry for
[news-image-20261124](https://make.fun/bounty/news-image-20261124):
the world news of Tuesday 24 November 2026 as one broadsheet front
page — built dense on purpose. A red-kicker lead on the IRGC's
claimed Patriot radar strikes in Bahrain, then a uniform 3×4 grid of
twelve more stories (Kyiv, COP31, the ICJ Myanmar verdict, the
Shenzhen trilateral, Alcaraz, the Libya warship strike, Seoul's jet
scramble, the Megaspeed blacklist, China's death sentence for
spying, the Pentagon's Canada rebuke, Zelensky's four-way talks
call, the Mecca missile interception), plus a MEANWHILE strip with
four more items. Thirteen stories, eighteen news items, no wasted
whitespace.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `out/entry.png` (1024×1024 PNG). Python 3.12+, standard
library only — no network, no randomness, no clock, so every run
writes the same bytes.

## How it works

`entry.png` was composed by `build_page.py` (PIL + DejaVu fonts):
a newsprint masthead with the date in full, the lead story, the
twelve-cell grid, and the MEANWHILE footer. Every word on the page
is typeset by PIL. `main.py` is the entry program: it copies the
composed image to the output directory. The stories and their
sources are listed in `NEWS.md`.
