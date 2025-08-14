{ inputs, ... }:

final: prev: {
  pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
    (python-final: python-prev: {
      natsy = python-prev.pkgs.callPackage (inputs.self + "/packages/natsy") { };
    })
  ];
}
