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
            ]
          );

      venv = pythonSet.mkVirtualEnv "najs-venv" {
        najs = [ "dev" ];
      };
    in
    {
      checks.najs-pytest =
        pkgs.runCommand "najs-pytest"
          {
            nativeBuildInputs = [
              venv
              pkgs.nats-server
            ];
          }
          ''
            export HOME=$TMPDIR
            cp -r ${inputs.self + "/tests"} tests
            chmod -R +w tests
            pytest tests
            touch $out
          '';
    };
}
