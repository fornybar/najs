{
  description = "najs: NATS JetStream helpers";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    systems.url = "github:nix-systems/default";
    flake-parts.url = "github:hercules-ci/flake-parts";

    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uvloom = {
      url = "github:fornybar/uvloom";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs@{
      flake-parts,
      uvloom,
      ...
    }:
    flake-parts.lib.mkFlake
      {
        inherit inputs;
        specialArgs = {
          project = uvloom.lib.loadProject {
            root = ./.;
          };
        };
      }
      {
        systems = import inputs.systems;

        imports = [
          inputs.treefmt-nix.flakeModule
          ./nix/overlays
          ./nix/checks
          ./nix/shells
        ];
      };
}
