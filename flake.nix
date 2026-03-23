{
  description = "Eviny EMPS projects";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    systems.url = "github:nix-systems/default";
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
    inputs@{ self, nixpkgs, ... }:
    let
      systems = import inputs.systems;

      mkPkgs =
        system:
        import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [ self.overlays.default ];
        };

      forAllSystems = function: nixpkgs.lib.genAttrs systems (system: function (mkPkgs system));

      mkTreefmt = pkgs: inputs.treefmt-nix.lib.evalModule pkgs ./treefmt.nix;
    in
    {
      overlays.default = import ./overlays/default { inherit inputs; };

      packages = forAllSystems (pkgs: {
        najs = pkgs.callPackage ./packages/najs { inherit inputs; };
        nkeys-py = pkgs.callPackage ./packages/nkeys-py { };
        default = self.packages.${pkgs.system}.najs;
      });

      checks = forAllSystems (pkgs: {
        format = (mkTreefmt pkgs).config.build.check self;
        najs-build = self.packages.${pkgs.system}.najs;
      });

      formatter = forAllSystems (pkgs: (mkTreefmt pkgs).config.build.wrapper);

      devShells = forAllSystems (pkgs: {
        default = import ./shells/default/default.nix {
          inherit inputs pkgs;
          system = pkgs.system;
        };
      });
    };
}
