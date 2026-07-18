# Publishing cooling-tower-chem to PyPI

The package is release-ready: it builds a clean `sdist` + `wheel`, passes
`twine check`, and has a `.github/workflows/publish.yml` that publishes on a
GitHub Release via **PyPI Trusted Publishing** (OIDC — no stored token).

Two ways to publish. Trusted Publishing (A) is recommended.

## A. Trusted Publishing (recommended, no secrets)

One-time setup on PyPI (needs your PyPI login — a maintainer action, so it's
yours to do):

1. Sign in at https://pypi.org and go to
   **Your projects → Publishing** (or, before the first release,
   https://pypi.org/manage/account/publishing/).
2. Add a **pending publisher** with:
   - **PyPI Project Name:** `cooling-tower-chem`
   - **Owner:** `Madhvansh`
   - **Repository name:** `cooling-tower-chem`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi`
3. In the GitHub repo, create an **Environment** named `pypi`
   (Settings → Environments → New environment). No secrets needed.
4. Cut a release:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   gh release create v0.1.0 --title "v0.1.0" --notes-file CHANGELOG.md
   ```
   The `Publish to PyPI` workflow builds and uploads automatically.

## B. Manual upload with a token (fallback)

```bash
python -m pip install build twine
python -m build
python -m twine upload dist/*        # username: __token__ , password: your PyPI API token
```

Create the token at https://pypi.org/manage/account/token/ (scope it to this
project after the first upload).

## After publishing

- Verify: `pip install cooling-tower-chem && ctchem --version`
- The PyPI page and download stats become the *real, independently verifiable*
  evidence of ecosystem use — exactly the signal the open-source program looks
  for. Downloads show up at https://pypistats.org/packages/cooling-tower-chem
  within a day or two.
