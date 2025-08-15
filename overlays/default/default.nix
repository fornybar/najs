{ inputs, ... }:

final: prev: {
  pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
    (python-final: python-prev: {
      nkeys = python-prev.pkgs.callPackage (inputs.self + "/packages/nkeys-py") { };
      najs = python-prev.pkgs.callPackage (inputs.self + "/packages/najs") {
        inherit inputs;
      };
    })
  ];
}
