{ inputs, ... }:

final: prev: {
  pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
    (python-final: python-prev: {
      async-lru =
        if python-prev.async-lru.version == "2.2.0" then
          python-prev.async-lru.overrideAttrs (old: rec {
            version = "2.3.0";
            src = old.src.override {
              tag = "v${version}";
              hash = "sha256-ytmh6tY6AS2VHajCnnRBSi0i57DUu+ikpbil/RwFyYA=";
            };
          })
        else
          python-prev.async-lru;
      nkeys = python-prev.pkgs.callPackage (inputs.self + "/packages/nkeys-py") { };
      najs = python-prev.pkgs.callPackage (inputs.self + "/packages/najs") {
        inherit inputs;
      };
    })
  ];
}
