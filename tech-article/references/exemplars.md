# Exemplars: technical articles from before 2023

Calibration material for [tech-article](../SKILL.md) and [tech-docs](../../tech-docs/SKILL.md). Read two pieces of the same kind as your draft before writing, for how they open, pace an explanation and name things. Borrow the approach, never the wording. Pieces the user or the project supplies come first; this list comes after them and after the project's own published articles.

The list holds human-written articles that reached at least 150 points on Hacker News before 1 January 2023, found with the 62 searches listed at the end, deduplicated by URL and filtered by hand to practitioner articles and essays (no launches, news, repositories, PDFs or videos). The 2023 cut-off keeps the list ahead of the spread of generated text.

- **Year** is the year in the Hacker News title when given, otherwise the earliest submission year; it can be later than first publication.
- **Points** and **HN** refer to the highest-scoring submission of that URL.
- **Read it for** is what the piece does well; "—" means the page was not read. Author names were not all checked against the pages.
- **Corpus** ✓ marks the 29 texts (about 120,000 words of prose) behind the [wording checker](../scripts/check_tells.py)'s baseline rates. The texts themselves are not stored in this repository.

## (a) Visual or interactive explainers (15)

| Title | Author / site | Year | Points | Article | HN | Read it for | Corpus |
|---|---|---|---|---|---|---|---|
| Gently Down the Stream: an illustrated guide to Apache Kafka | Mitch Seymour | 2021 | 1797 | [link](https://gentlydownthe.stream/) | [hn](https://news.ycombinator.com/item?id=27541339) | Illustrated story format explaining Kafka without jargon |  |
| Every Byte of a TLS Connection Explained and Reproduced | Michael Driscoll (ulfheim.net) | 2018 | 1185 | [link](https://tls.ulfheim.net/) | [hn](https://news.ycombinator.com/item?id=18200749) | Annotates every byte of a real handshake; the reader can check each claim against the hex |  |
| A visual guide to SSH tunnels | robotmoon.com | 2021 | 963 | [link](https://robotmoon.com/ssh-tunnels/) | [hn](https://news.ycombinator.com/item?id=26053323) | — | ✓ |
| An interactive guide to Flexbox | Josh W. Comeau | 2022 | 813 | [link](https://www.joshwcomeau.com/css/interactive-guide-to-flexbox/) | [hn](https://news.ycombinator.com/item?id=33718508) | Interactive demos placed right after each concept, in a conversational voice | ✓ |
| Markov Chains Explained Visually | Victor Powell & Lewis Lehe (Explained Visually) | 2014 | 779 | [link](http://setosa.io/ev/markov-chains/) | [hn](https://news.ycombinator.com/item?id=17766358) | Short prose paired with live diagrams the reader can tweak |  |
| Inside a fast CSS engine | Lin Clark (Mozilla Hacks) | 2017 | 660 | [link](https://hacks.mozilla.org/2017/08/inside-a-super-fast-css-engine-quantum-css-aka-stylo/) | [hn](https://news.ycombinator.com/item?id=15073414) | Code-cartoon walkthrough of a browser engine pipeline | ✓ |
| The Illustrated Stable Diffusion | Jay Alammar | 2022 | 629 | [link](https://jalammar.github.io/illustrated-stable-diffusion/) | [hn](https://news.ycombinator.com/item?id=33084205) | Figure-driven explanation that layers detail gradually | ✓ |
| Introduction to A* | Amit Patel (Red Blob Games) | 2014 | 509 | [link](http://www.redblobgames.com/pathfinding/a-star/introduction.html) | [hn](https://news.ycombinator.com/item?id=8059237) | Builds A* up from breadth-first search, one interactive step at a time |  |
| Feature Visualization: How neural nets build up their understanding of images | Olah, Mordvintsev & Schubert (Distill) | 2017 | 461 | [link](https://distill.pub/2017/feature-visualization/) | [hn](https://news.ycombinator.com/item?id=15646037) | Distill's standard for figures integrated with the argument | ✓ |
| Xplain: Explaining X11 for the rest of us | Jasper St. Pierre (Xplain) | 2014 | 456 | [link](https://magcius.github.io/xplain/article/) | [hn](https://news.ycombinator.com/item?id=12042548) | — |  |
| Floating Point Visually Explained | Fabien Sanglard | 2017 | 451 | [link](http://fabiensanglard.net/floating_point_visually_explained/) | [hn](https://news.ycombinator.com/item?id=15359574) | Replaces the textbook formula with a 'window and offset' mental model |  |
| Raft Consensus Animated | Ben Johnson (The Secret Lives of Data) | 2014 | 411 | [link](https://thesecretlivesofdata.com/raft/) | [hn](https://news.ycombinator.com/item?id=32484584) | Animation only; no extractable prose |  |
| A cartoon intro to DNS over HTTPS | Lin Clark (Mozilla Hacks) | 2018 | 400 | [link](https://hacks.mozilla.org/2018/05/a-cartoon-intro-to-dns-over-https/) | [hn](https://news.ycombinator.com/item?id=17196415) | Code-cartoon style: each panel carries one idea |  |
| The Illustrated Word2vec | Jay Alammar | 2019 | 348 | [link](https://jalammar.github.io/illustrated-word2vec/) | [hn](https://news.ycombinator.com/item?id=19498356) | Starts from an everyday analogy (personality vectors) before the model |  |
| Tasks, microtasks, queues and schedules | Jake Archibald | 2015 | 152 | [link](https://jakearchibald.com/2015/tasks-microtasks-queues-and-schedules/) | [hn](https://news.ycombinator.com/item?id=10072656) | Animated step-through of the event loop with a quiz-style opening | ✓ |

## (b) Deep-dive explainers of a mechanism (17)

| Title | Author / site | Year | Points | Article | HN | Read it for | Corpus |
|---|---|---|---|---|---|---|---|
| Reading privileged memory with a side-channel | Jann Horn (Google Project Zero) | 2018 | 2334 | [link](https://googleprojectzero.blogspot.com/2018/01/reading-privileged-memory-with-side.html) | [hn](https://news.ycombinator.com/item?id=16065845) | — | ✓ |
| Extreme HTTP Performance Tuning | Marc Richards (talawah.io) | 2021 | 976 | [link](https://talawah.io/blog/extreme-http-performance-tuning-one-point-two-million/) | [hn](https://news.ycombinator.com/item?id=27226382) | — | ✓ |
| The HTTP crash course nobody asked for | Amos Wenger (fasterthanli.me) | 2022 | 902 | [link](https://fasterthanli.me/articles/the-http-crash-course-nobody-asked-for) | [hn](https://news.ycombinator.com/item?id=33280605) | Long-form, hands-on exploration that shows real tool output at each step | ✓ |
| Htop Explained | Pēteris Ņikiforovs | 2016 | 818 | [link](https://peteris.rocks/blog/htop/) | [hn](https://news.ycombinator.com/item?id=21414882) | Explains every field of a familiar screen by tracing it to its source | ✓ |
| Git from the inside out | Mary Rose Cook (Code Words) | 2016 | 722 | [link](https://codewords.recurse.com/issues/two/git-from-the-inside-out) | [hn](https://news.ycombinator.com/item?id=12802949) | Builds a model of Git by watching the .git directory change command by command | ✓ |
| SQLite Internals: Pages and B-trees | Ben Johnson (Fly.io) | 2022 | 667 | [link](https://fly.io/blog/sqlite-internals-btree/) | [hn](https://news.ycombinator.com/item?id=32250426) | — | ✓ |
| Why is Rosetta 2 fast? | Dougall Johnson | 2022 | 650 | [link](https://dougallj.wordpress.com/2022/11/09/why-is-rosetta-2-fast/) | [hn](https://news.ycombinator.com/item?id=33533132) | — | ✓ |
| Every 7.8μs your computer’s memory has a hiccup | Marek Majkowski (Cloudflare) | 2018 | 570 | [link](https://blog.cloudflare.com/every-7-8us-your-computers-memory-has-a-hiccup/) | [hn](https://news.ycombinator.com/item?id=18517081) | Starts from a measurable anomaly and explains it down to DRAM refresh |  |
| Macbook charger teardown: surprising complexity inside Apple's power adapter | Ken Shirriff (righto.com) | 2015 | 556 | [link](http://www.righto.com/2015/11/macbook-charger-teardown-surprising.html) | [hn](https://news.ycombinator.com/item?id=10628212) | Hardware teardown explained component by component with photos | ✓ |
| Text Rendering Hates You | Aria Beingessner (Gankra) | 2019 | 542 | [link](https://gankra.github.io/blah/text-hates-you/) | [hn](https://news.ycombinator.com/item?id=21105625) | — | ✓ |
| How Does Sqlite Work? | Julia Evans | 2014 | 480 | [link](https://jvns.ca/blog/2014/09/27/how-does-sqlite-work-part-1-pages/) | [hn](https://news.ycombinator.com/item?id=23663071) | Learning-out-loud voice; shows the questions as well as the answers |  |
| Emoji Under the Hood | Nikita Prokopov (tonsky) | 2021 | 430 | [link](https://tonsky.me/blog/emoji/) | [hn](https://news.ycombinator.com/item?id=26574008) | — |  |
| How Does React Tell a Class from a Function? | Dan Abramov (overreacted) | 2018 | 348 | [link](https://overreacted.io/how-does-react-tell-a-class-from-a-function/) | [hn](https://news.ycombinator.com/item?id=18586004) | Turns a small question into a tour of the language, with the dead ends kept in | ✓ |
| How does Apple privately find offline devices? | Matthew Green | 2019 | 347 | [link](https://blog.cryptographyengineering.com/2019/06/05/how-does-apple-privately-find-your-offline-devices/) | [hn](https://news.ycombinator.com/item?id=20109218) | — |  |
| How does rsync work? | Michael Stapelberg | 2022 | 319 | [link](https://michael.stapelberg.ch/posts/2022-07-02-rsync-how-does-it-work/) | [hn](https://news.ycombinator.com/item?id=31958536) | — |  |
| Why do CPUs have multiple cache levels? | Fabian Giesen (The ryg blog) | 2016 | 309 | [link](https://fgiesen.wordpress.com/2016/08/07/why-do-cpus-have-multiple-cache-levels/) | [hn](https://news.ycombinator.com/item?id=12245458) | — |  |
| Following a Select Statement Through Postgres Internals | Pat Shaughnessy | 2014 | 302 | [link](http://patshaughnessy.net/2014/10/13/following-a-select-statement-through-postgres-internals) | [hn](https://news.ycombinator.com/item?id=11467309) | Follows one query through the source code, function by function |  |

## (c) Build-your-own / from-scratch tutorials (13)

| Title | Author / site | Year | Points | Article | HN | Read it for | Corpus |
|---|---|---|---|---|---|---|---|
| Build Your Own React | Rodrigo Pombo | 2019 | 1478 | [link](https://pomb.us/build-your-own-react/) | [hn](https://news.ycombinator.com/item?id=21536789) | Rebuilds React step by step, each step a small runnable increment | ✓ |
| Build Your Own Text Editor (multi-chapter; index page) | Paige Ruten (snaptoken) | 2017 | 1275 | [link](http://viewsourcecode.org/snaptoken/kilo/) | [hn](https://news.ycombinator.com/item?id=14046446) | — |  |
| A from-scratch tour of Bitcoin in Python | Andrej Karpathy | 2021 | 1208 | [link](https://karpathy.github.io/2021/06/21/blockchain/) | [hn](https://news.ycombinator.com/item?id=27593772) | — | ✓ |
| Implementing a Neural Network from Scratch in Python | Victor Zhou | 2019 | 616 | [link](https://victorzhou.com/blog/intro-to-neural-networks/) | [hn](https://news.ycombinator.com/item?id=19320217) | — |  |
| Writing an OS in Rust: Introduction to Paging | Philipp Oppermann | 2019 | 597 | [link](https://os.phil-opp.com/paging-introduction/) | [hn](https://news.ycombinator.com/item?id=18903235) | — | ✓ |
| Writing a SQLite clone from scratch in C (multi-part; index page) | cstack | 2017 | 574 | [link](https://cstack.github.io/db_tutorial/) | [hn](https://news.ycombinator.com/item?id=15168467) | — |  |
| Write Your Own Virtual Machine | Justin Meiners & Ryan Pendleton | 2018 | 546 | [link](https://justinmeiners.github.io/lc3-vm/) | [hn](https://news.ycombinator.com/item?id=18678699) | — | ✓ |
| Let's code a TCP/IP stack | Sami Niiranen | 2016 | 440 | [link](https://www.saminiir.com/lets-code-tcp-ip-stack-1-ethernet-arp/) | [hn](https://news.ycombinator.com/item?id=27654182) | — |  |
| Writing a SQL database from scratch in Go | Phil Eaton | 2020 | 430 | [link](https://notes.eatonphil.com/database-basics.html) | [hn](https://news.ycombinator.com/item?id=22850817) | — |  |
| How I wrote a self-hosting C compiler in 40 days | Rui Ueyama | 2015 | 429 | [link](http://www.sigbus.info/how-i-wrote-a-self-hosting-c-compiler-in-40-days.html) | [hn](https://news.ycombinator.com/item?id=10731002) | Dated build diary: progress and mistakes recorded day by day | ✓ |
| How to Write a Spelling Corrector | Peter Norvig | 2016 | 401 | [link](http://norvig.com/spell-correct.html) | [hn](https://news.ycombinator.com/item?id=12453535) | Short essay where every paragraph earns its code | ✓ |
| Writing a C Compiler, Part 1 | Nora Sandler | 2017 | 369 | [link](https://norasandler.com/2017/11/29/Write-a-Compiler.html) | [hn](https://news.ycombinator.com/item?id=15821899) | — |  |
| Parsing Expressions (Crafting Interpreters, ch. 6) | Robert Nystrom (Crafting Interpreters) | 2017 | 347 | [link](http://www.craftinginterpreters.com/parsing-expressions.html) | [hn](https://news.ycombinator.com/item?id=13914218) | Precise, warm book-chapter prose with code introduced in small pieces |  |

## (d) Postmortems and debugging stories (12)

| Title | Author / site | Year | Points | Article | HN | Read it for | Corpus |
|---|---|---|---|---|---|---|---|
| Why Is This Website Port Scanning Me? | Charlie Belmer (Nullsweep) | 2020 | 1294 | [link](https://nullsweep.com/why-is-this-website-port-scanning-me/) | [hn](https://news.ycombinator.com/item?id=23246170) | — |  |
| Understanding how Facebook disappeared from the internet | Cloudflare blog | 2021 | 1226 | [link](https://blog.cloudflare.com/october-2021-facebook-outage/) | [hn](https://news.ycombinator.com/item?id=28752131) | — | ✓ |
| The Apple GPU and the impossible bug | Alyssa Rosenzweig | 2022 | 965 | [link](https://rosenzweig.io/blog/asahi-gpu-part-5.html) | [hn](https://news.ycombinator.com/item?id=31367365) | — | ✓ |
| This shouldn't have happened: A vulnerability postmortem | Tavis Ormandy (Google Project Zero) | 2021 | 938 | [link](https://googleprojectzero.blogspot.com/2021/12/this-shouldnt-have-happened.html) | [hn](https://news.ycombinator.com/item?id=29407636) | — |  |
| Stack Overflow Outage Postmortem | Stack Exchange | 2016 | 862 | [link](http://stackstatus.net/post/147710624694/outage-postmortem-july-20-2016) | [hn](https://news.ycombinator.com/item?id=12131909) | — |  |
| A Google Cloud support engineer solves a tough DNS case | Google Cloud blog | 2020 | 771 | [link](https://cloud.google.com/blog/topics/inside-google-cloud/google-cloud-support-engineer-solves-a-tough-dns-case) | [hn](https://news.ycombinator.com/item?id=23235995) | — | ✓ |
| Roblox October Outage Postmortem | Roblox Engineering | 2022 | 687 | [link](https://blog.roblox.com/2022/01/roblox-return-to-service-10-28-10-31-2021/) | [hn](https://news.ycombinator.com/item?id=30013919) | — | ✓ |
| Debugging an evil Go runtime bug | Hector Martin (marcan) | 2017 | 498 | [link](https://marcan.st/2017/12/debugging-an-evil-go-runtime-bug/) | [hn](https://news.ycombinator.com/item?id=15845118) | — | ✓ |
| Uncovering a 24-year-old bug in the Linux Kernel | Skroutz Engineering | 2021 | 497 | [link](https://engineering.skroutz.gr/blog/uncovering-a-24-year-old-bug-in-the-linux-kernel/) | [hn](https://news.ycombinator.com/item?id=33214439) | — | ✓ |
| Debugging memory corruption: who the hell writes “2” into my stack? | Unity Technologies blog | 2016 | 409 | [link](https://blog.unity.com/technology/debugging-memory-corruption-who-the-hell-writes-2-into-my-stack-2) | [hn](https://news.ycombinator.com/item?id=29215725) | — |  |
| Postmortem of database outage of January 31 | GitLab | 2017 | 377 | [link](https://about.gitlab.com/2017/02/10/postmortem-of-database-outage-of-january-31/) | [hn](https://news.ycombinator.com/item?id=13619714) | Candid timeline of an operator error with a full list of what went wrong | ✓ |
| Debugging PostgreSQL performance the hard way | JustWatch Engineering | 2016 | 359 | [link](https://www.justwatch.com/blog/post/debugging-postgresql-performance-the-hard-way/) | [hn](https://news.ycombinator.com/item?id=12606480) | — |  |

## (e) Reference-style "what every programmer should know" pieces (12)

| Title | Author / site | Year | Points | Article | HN | Read it for | Corpus |
|---|---|---|---|---|---|---|---|
| What every programmer should know about SSDs | Database Architects blog | 2021 | 452 | [link](https://databasearchitects.blogspot.com/2021/06/what-every-programmer-should-know-about.html) | [hn](https://news.ycombinator.com/item?id=27572218) | — |  |
| What every programmer should know about time | unix4lyfe.org | 2011 | 444 | [link](http://unix4lyfe.org/time/) | [hn](https://news.ycombinator.com/item?id=2725015) | — |  |
| Notes on Distributed Systems for Young Bloods | Jeff Hodges | 2013 | 386 | [link](https://www.somethingsimilar.com/2013/01/14/notes-on-distributed-systems-for-young-bloods/) | [hn](https://news.ycombinator.com/item?id=12245909) | — |  |
| Myths Programmers Believe about CPU Caches | Rajiv Prabhakar | 2018 | 366 | [link](https://software.rajivprab.com/2018/04/29/myths-programmers-believe-about-cpu-caches/) | [hn](https://news.ycombinator.com/item?id=21588893) | — |  |
| Falsehoods Programmers believe about Time | Noah Sussman (Infinite Undo) | 2012 | 364 | [link](http://infiniteundo.com/post/25326999628/falsehoods-programmers-believe-about-time) | [hn](https://news.ycombinator.com/item?id=4128208) | — |  |
| What every computer programmer should know about floating point, part 1 | Josh Haberman | 2014 | 323 | [link](http://blog.reverberate.org/2014/09/what-every-computer-programmer-should.html) | [hn](https://news.ycombinator.com/item?id=8321940) | — |  |
| What's New in CPUs Since the 80s and How Does It Affect Programmers? | Dan Luu | 2015 | 305 | [link](http://danluu.com/new-cpu-features/) | [hn](https://news.ycombinator.com/item?id=8873250) | — |  |
| A Programmer’s Introduction to Unicode | Nathan Reed | 2017 | 299 | [link](http://reedbeta.com/blog/programmers-intro-to-unicode/) | [hn](https://news.ycombinator.com/item?id=13790575) | — |  |
| What every programmer should know about memory, Part 1 | Ulrich Drepper (LWN) | 2012 | 236 | [link](http://lwn.net/Articles/250967/?rss=1) | [hn](https://news.ycombinator.com/item?id=3919429) | Exhaustive reference on caches and memory with measurements |  |
| The Absolute Minimum Every Software Developer Must Know About Unicode | Joel Spolsky | 2012 | 214 | [link](http://www.joelonsoftware.com/articles/Unicode.html) | [hn](https://news.ycombinator.com/item?id=3448507) | Opinionated, conversational reference that names the reader's misconception up front |  |
| Falsehoods Programmers Believe About Names | Patrick McKenzie (Kalzumeus) | 2010 | 176 | [link](http://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/) | [hn](https://news.ycombinator.com/item?id=1438472) | The original 'falsehoods' list format |  |
| What Every C Programmer Should Know About Undefined Behavior #1/3 | Chris Lattner (LLVM blog) | 2011 | 155 | [link](http://blog.llvm.org/2011/05/what-every-c-programmer-should-know.html) | [hn](https://news.ycombinator.com/item?id=2540017) | — |  |

## (f) Essays on the craft of writing or explaining (10)

| Title | Author / site | Year | Points | Article | HN | Read it for | Corpus |
|---|---|---|---|---|---|---|---|
| Undervalued Engineering Skills: Writing Well | Gergely Orosz (The Pragmatic Engineer) | 2019 | 1109 | [link](https://blog.pragmaticengineer.com/on-writing-well/) | [hn](https://news.ycombinator.com/item?id=20061078) | — |  |
| How to Write Usefully | Paul Graham | 2020 | 821 | [link](http://paulgraham.com/useful.html) | [hn](https://news.ycombinator.com/item?id=22381861) | — |  |
| How to Write in Plain English | Plain English Campaign | 2020 | 724 | [link](http://www.plainenglish.co.uk/how-to-write-in-plain-english.html) | [hn](https://news.ycombinator.com/item?id=24268382) | — |  |
| Four kinds of documentation | Daniele Procida (Divio) | 2019 | 717 | [link](https://www.divio.com/blog/documentation/) | [hn](https://news.ycombinator.com/item?id=21289832) | The tutorials / how-to / reference / explanation split |  |
| Notes on Technical Writing | Marcus Kazmierczak | 2020 | 414 | [link](https://mkaz.blog/misc/notes-on-technical-writing/) | [hn](https://news.ycombinator.com/item?id=21955306) | — |  |
| How to Write a Git Commit Message | Chris Beams | 2014 | 341 | [link](https://chris.beams.io/posts/git-commit/) | [hn](https://news.ycombinator.com/item?id=13889155) | — |  |
| How to write technical posts so people will read them | Sandy Maguire | 2019 | 257 | [link](https://reasonablypolymorphic.com/blog/writing-technical-posts/) | [hn](https://news.ycombinator.com/item?id=23840787) | — |  |
| Writing great documentation | Jacob Kaplan-Moss | 2010 | 243 | [link](http://jacobian.org/writing/great-documentation/) | [hn](https://news.ycombinator.com/item?id=1431048) | — |  |
| Explaining Code Using ASCII Art | John Regehr | 2019 | 232 | [link](https://blog.regehr.org/archives/1653) | [hn](https://news.ycombinator.com/item?id=31891226) | — |  |
| Technical Writing: Learning from Kernighan | Christoffer Stjernlöf (two-wrongs) | 2018 | 180 | [link](https://two-wrongs.com/technical-writing-learning-from-kernighan.html) | [hn](https://news.ycombinator.com/item?id=17151560) | — |  |

## Search terms used (62)

Hacker News Algolia `search`, `tags=story`, `created_at_i<1672531200`, `points>150`, 30 hits each:

`how does`, `how it works`, `explained`, `visual explanation`, `interactive`, `deep dive`, `internals`, `under the hood`, `from scratch`, `write your own`, `build your own`, `illustrated`, `a visual guide`, `what every programmer should know`, `introduction to`, `primer`, `anatomy of`, `inside`, `the story of`, `postmortem`, `debugging`, `war story`, `lessons learned`, `why is`, `the case for`, `myths`, `falsehoods programmers believe`, `understanding`, `a gentle introduction`, `demystified`, `crash course`, `a tour of`, `how we built`, `scaling`, `performance`, `latency numbers`, `memory`, `garbage collection`, `database internals`, `B-tree`, `TCP`, `DNS`, `TLS`, `git internals`, `compiler`, `CPU cache`, `floating point`, `unicode`, `regex engine`, `OAuth`, `distributed systems`, `raft consensus`, `cryptography explained`, `GPU`, `linux kernel`, `rendering`, `technical writing`, `writing well`, `documentation`, `explaining`, `how to write`, `blog post writing`
