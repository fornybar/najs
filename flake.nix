{
  description = "Eviny EMPS projects";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    systems.url = "github:nix-systems/default";
    flake-parts.url = "github:hercules-ci/flake-parts";

    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs@{
      flake-parts,
      nixpkgs,
      self,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import inputs.systems;
      imports = [ inputs.treefmt-nix.flakeModule ];

      flake.overlays.default = import ./overlays/default { inherit inputs; };

      perSystem =
        { system, config, ... }:
        let
          pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
            overlays = [ self.overlays.default ];
          };
        in
        {
          treefmt = import ./treefmt.nix;

          packages = {
            najs = pkgs.callPackage ./packages/najs { inherit inputs; };
            nkeys-py = pkgs.callPackage ./packages/nkeys-py { };
            default = config.packages.najs;
          };

          checks.najs-build = config.packages.najs;

          devShells.default = import ./shells/default/default.nix {
            inherit inputs pkgs system;
          };
        };
    };
}
