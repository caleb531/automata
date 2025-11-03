# Automata Release Checklist

If you are an Automata collaborator, this is a checklist you can follow to
properly publish a release to GitHub and PyPI.

- [ ] Before Release
  - [ ] Checkout `develop` branch and pull
  - [ ] Run tests and coverage report (`pytest --cov`)
    - [ ] All tests pass
    - [ ] Code coverage is over 90% for all files
  - [ ] Update Migration Guide with details of any breaking API changes and
    upgrade path, if applicable
  - [ ] Update README and Migration Guide with latest major release (e.g. v8),
    if applicable
  - [ ] Write release notes for new release
  - [ ] Check copyright line break in README (there should be two spaces after
    the *Copyright \<year\> Caleb Evans* line; sometimes these can get removed
    while editing the README, depending on your editor's settings
  - [ ] Check copyright year (the end year in the range should always be the
    current year)
- [ ] Release
  - [ ] Merge `develop` into `main`
    - [ ] `git checkout main`
    - [ ] `git pull`
    - [ ] `git merge develop`
  - [ ] Commit version bump in `pyproject.toml`
    - [ ] Commit message must be `Prepare v<new_version> release` (e.g. `Prepare v8.0.0 release`)
  - [ ] Tag commit with new release number
    - [ ] Tag name must be v-prefixed, followed by the semantic version (e.g.
      `v8.0.0`)
  - [ ] Push new commit and tag with `git push && git push --tags`
- [ ] Post-Release
  - [ ] Check [package page on PyPI](https://pypi.org/project/automata-lib/) to
    ensure that new release is public
  - [ ] Post new GitHub Release with release notes
  - [ ] Rebase `develop` on top of latest `main`
    - `git checkout develop`
    - `git pull`
    - `git rebase main`
    - `git push`
