{ inputs, ... }:

final: prev: {
  pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
    (python-final: python-prev: {
      najs = python-prev.pkgs.callPackage (inputs.self + "/packages/najs") { };
    })
  ];
}
