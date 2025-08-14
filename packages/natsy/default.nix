{
  inputs,
  python3,
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
    nativeCheckInputs = [ python3.pkgs.pytestCheckHook ];
  };
in
python3.pkgs.buildPythonPackage (buildAttrs // extraAttrs)
