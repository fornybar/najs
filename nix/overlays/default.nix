{ project, ... }:
{
  flake.overlays.default = project.nixpkgs.overlay {
    packages = [
      "najs"
      "nkeys"
      "async-lru"
    ];
  };
}
