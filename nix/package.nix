{
  inputs,
  python,
  pkgs,
  ...
}:
let
  project = inputs.pyproject-nix.lib.project.loadPyproject {
    projectRoot = ./..;
  };
  buildAttrs = project.renderers.buildPythonPackage {
    inherit python;
  };
  extraAttrs = {
    nativeCheckInputs = [
      python.pkgs.pytestCheckHook
      python.pkgs."pytest-asyncio"
      pkgs.nats-server
    ];
  };
in
python.pkgs.buildPythonPackage (buildAttrs // extraAttrs)
