{
  description = "Eviny EMPS projects";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    snowfall-lib = {
      url = "github:snowfallorg/lib";
      inputs.nixpkgs.follows = "nixpkgs";
    };
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
    {
      snowfall-lib,
      ...
    }@inputs:
    snowfall-lib.mkFlake {
      inherit inputs;
      src = ./.;

      outputs-builder = channels: {
        formatter = inputs.treefmt-nix.lib.mkWrapper channels.nixpkgs ./treefmt.nix;
      };
    };
}
