# Dev notes — how I work on Trinetra

Quick reference so I don't have to re-remember the workflow.

## The one-folder rule
My repo lives in **exactly one folder** on my Mac. A new zip from Claude is NOT
a new project — it's just newer files for this same folder. Never make a second
`trinetra` folder.

## Updating from a new zip (in place — keeps git history)
```bash
# run from INSIDE my repo folder
unzip -o ~/Downloads/trinetra.zip -d /tmp/tri_latest   # unzip to a throwaway spot
cp -R /tmp/tri_latest/trinetra/. .                      # copy new files over old; .git untouched
git add -A
git commit -m "describe what changed"
git push
```

## Updating from just a few changed files (the usual case)
Claude hands me one or two files → I save them in the right place → then:
```bash
git add -A
git commit -m "describe what changed"
git push
```
No unzip needed.

## First-time GitHub auth (only once)
GitHub killed password auth. Use the CLI:
```bash
brew install gh
gh auth login      # GitHub.com → HTTPS → Yes → login with browser
```
After this, `git push` just works.

## Running Trinetra
```bash
export PYTHONPATH=.
python -m trinetra.cli scan --launch chaicart --html report.html   # scan + report
python -m trinetra.cli dashboard --launch chaicart --serve          # live UI at :7000
python -m trinetra.cli arm --repo /path/to/a/repo                   # install the commit wall
python -m trinetra.cli feed --brain ollama                          # third eye (needs Ollama)
python -m trinetra.cli validate --astra <id> --launch chaicart      # sandbox-test a drafted astra
python -m trinetra.cli review --approve <id>                        # approve it
```

## Local brain (Ollama) — one time
```bash
brew install ollama
ollama pull qwen2.5-coder:7b     # best fit for a 16GB MacBook Air M4
ollama serve                     # usually already running
```

## Responsible use
Only run Trinetra against targets I own or have permission to test. ChaiCart is
a deliberately vulnerable demo; its "secrets" are fake.
