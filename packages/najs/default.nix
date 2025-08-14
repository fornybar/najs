{
  inputs,
  python3,
  pkgs,
  ...
}:
let
  project = inputs.pyproject-nix.lib.project.loadPyproject {
    projectRoot = ./.;
  };
  buildAttrs = project.renderers.buildPythonPackage {
    python = python3;
    groups = [
      "dev"
    ];
  };
  extraAttrs = {
    nativeCheckInputs = [
      python3.pkgs.pytestCheckHook
      pkgs.nats-server
    ];
  };
in
python3.pkgs.buildPythonPackage (buildAttrs // extraAttrs)
