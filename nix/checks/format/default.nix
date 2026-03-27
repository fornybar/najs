{ ... }:
{
  perSystem =
    { ... }:
    {
      treefmt =
        { config, ... }:
        {
          projectRootFile = "flake.nix";
          programs = {
            nixfmt.enable = true;
            toml-sort.enable = true;
          };
          settings = {
            formatter = {
              ruff-check = {
                command = config.programs.ruff-check.package;
                options = [
                  "check"
                  "--fix-only"
                  "--force-exclude"
                ];
                includes = [
                  "*.py"
                  "*.pyi"
                ];
              };
              ruff-format = {
                command = config.programs.ruff-format.package;
                options = [
                  "format"
                  "--force-exclude"
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
        };
    };
}
