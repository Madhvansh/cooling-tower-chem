# conda-forge submission

`meta.yaml` here is the recipe for submitting `cooling-tower-chem` to
[conda-forge](https://conda-forge.org/). It is kept in this repository so the
recipe is version-controlled alongside the release it describes.

## Verified against the published artifact

| Field | Value |
|---|---|
| Source | `https://pypi.org/packages/source/c/cooling-tower-chem/cooling_tower_chem-0.1.0.tar.gz` (HTTP 200) |
| `sha256` | `125fcfb84976447098c3194097a8715cf7f2a202b80d683a1651ba7bf16b81b5` — recomputed from the downloaded sdist |
| `LICENSE` | present in the sdist, so `license_file: LICENSE` resolves |
| Runtime deps | none (all `requires_dist` entries are extras-gated) — hence `run: python` only |
| Build backend | `hatchling` |
| Entry point | `ctchem = cooling_tower_chem.cli:main` |

## Submitting

```bash
git clone https://github.com/Madhvansh/staged-recipes.git
cd staged-recipes
git remote add upstream https://github.com/conda-forge/staged-recipes.git
git fetch upstream && git checkout -b cooling-tower-chem upstream/main
mkdir -p recipes/cooling-tower-chem
cp /path/to/cooling-tower-chem/packaging/conda-forge/meta.yaml recipes/cooling-tower-chem/meta.yaml
git add recipes/cooling-tower-chem/meta.yaml
git commit -m "Add cooling-tower-chem"
git push origin cooling-tower-chem
```

Then open a pull request against `conda-forge/staged-recipes`. The PR title
should be `Add cooling-tower-chem`.

## On version bumps

After the recipe is merged, conda-forge creates a feedstock and its bot opens
version-bump PRs automatically. This file then only needs updating if the build
requirements or entry points change — not on every release.
