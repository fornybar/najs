# najs

Simple helper functions for utilizing NATS Jetstream with [nats-py](https://github.com/nats-io/nats.py).

## Packaging model

This repo supports two Nix consumer workflows:

1. **Conventional nixpkgs overlay consumers**
   - Use `overlays.default`.
   - This exports `pythonPackagesExtensions` entries such as `python3Packages.najs` and `python3Packages.nkeys`.
   - `uv.lock` and version specifiers in `pyproject.toml` are ignored, only nixpkgs names are resolved

2. **uv2nix consumers**
   - Use the root uv workspace + `uv.lock` as Python dependency truth.
   - Use uv2nix workspace overlays and environment construction (`mkVirtualEnv`) in downstream flakes.
