{
  inputs,
  system,
  pkgs,
  ...
}:
let
  inherit (inputs.self.packages.${system}) natsy;
in
pkgs.mkShell {
  inputsFrom = [ natsy ];

  packages =
    with pkgs;
    [
      nats-server
    ]
    ++ natsy.dependency-groups.dev;

  shellHook = ''
    root=$(git rev-parse --show-toplevel)
    export PYTHONPATH=$(printf '%s:' $root/packages/*/src)$PYTHONPATH
  '';
}
