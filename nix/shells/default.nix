{ project, ... }:
{
  perSystem =
    { pkgs, ... }:
    let
      scope = project.forPython {
        inherit pkgs;
        editable = {
          root = "$REPO_ROOT";
          members = [ "najs" ];
        };
      };

      venv = scope.mkEditableVenv {
        name = "najs-dev";
        dependencies = {
          najs = [ "dev" ];
        };
      };
    in
    {
      devShells.default = pkgs.mkShell {
        packages = [
          venv
          pkgs.nats-server
          pkgs.uv
        ];

        env = {
          UV_NO_SYNC = "1";
          UV_PYTHON = scope.pythonSet.python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };

        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
        '';
      };
    };
}
