# Development Setup

## Commit FLOW

Commit to develop branch:

```bash
flake8 . --exclude=web --count --exit-zero --max-complexity=20 --max-line-length=256 --statistics

git checkout v1.0.8-rc
git add .
git commit -m "fix: jwt  Subject must be a string"
git push
```

## Generate release for production

Create MR to main

Merge MR

Update local main branch

```bash
git pull
```


Create new branch from main v1.0.9-rc

```bash
git fetch --prune
git checkout -b v1.0.9-rc
```
Change web/package.json for next release

```bash
git add .
git commit -m "docs: bump version to 1.0.9-rc"
git push -u origin v1.0.9-rc
```