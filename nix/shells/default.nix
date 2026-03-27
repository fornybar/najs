{ workspace, inputs, ... }:
{
  perSystem =
    { pkgs, ... }:
    let
      python = pkgs.lib.head (
        inputs.pyproject-nix.lib.util.filterPythonInterpreters {
          inherit (workspace) requires-python;
          inherit (pkgs) pythonInterpreters;
        }
      );

      pythonSet =
        (pkgs.callPackage inputs.pyproject-nix.build.packages {
          inherit python;
        }).overrideScope
          (
            pkgs.lib.composeManyExtensions [
              inputs.pyproject-build-systems.overlays.wheel
              (workspace.mkPyprojectOverlay { sourcePreference = "wheel"; })
              (workspace.mkEditablePyprojectOverlay { root = "$REPO_ROOT"; })
            ]
          );

      venv = pythonSet.mkVirtualEnv "najs-dev" {
        najs = [ "dev" ];
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
          UV_PYTHON = python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };

        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
        '';
      };
    };
}
