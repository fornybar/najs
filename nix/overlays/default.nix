{ inputs, ... }:
{
  flake.overlays.default = final: prev: {
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

        najs = python-final.callPackage (inputs.self + "/nix/package.nix") {
          inherit inputs;
          python = python-final.python;
          pkgs = python-prev.pkgs;
        };

        nkeys = python-prev.buildPythonPackage rec {
          pname = "nkeys";
          version = "0.2.1";
          pyproject = true;

          src = python-prev.fetchPypi {
            inherit pname version;
            hash = "sha256-OiAdzSA9i7BboohNRBsskpGLKlN6ENMk5zc4iH3enaM=";
          };

          build-system = [ python-prev.setuptools ];
          dependencies = [ python-prev.pynacl ];
        };

      })
    ];
  };
}
