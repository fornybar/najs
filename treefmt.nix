{ config, ... }:
let
  inherit (builtins) fromTOML readFile;

  ruff = fromTOML (readFile ./ruff.toml);

in
{
  projectRootFile = "flake.nix";
  programs = {
    nixfmt.enable = true;
    toml-sort.enable = true;
  };
  settings = {
    formatter = {
      ruff-check = {
        excludes = ruff.exclude;
        command = config.programs.ruff-check.package;
        options = [
          "check"
          "--fix-only"
        ];
        includes = [
          "*.py"
          "*.pyi"
        ];
      };
      ruff-format = {
        excludes = ruff.exclude;
        command = config.programs.ruff-format.package;
        options = [
          "format"
        ];
        includes = [
          "*.py"
          "*.pyi"
        ];
      };
      toml-sort.options = [
        "--trailing-comma-inline-array"
      ];
    };
  };
}
