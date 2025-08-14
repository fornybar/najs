{
  inputs,
  system,
  pkgs,
  ...
}:
let
  inherit (inputs.self.packages.${system}) najs;
in
pkgs.mkShell {
  inputsFrom = [ najs ];

  packages =
    with pkgs;
    [
      nats-server
    ]
    ++ najs.dependency-groups.dev;

  shellHook = ''
    root=$(git rev-parse --show-toplevel)
    export PYTHONPATH=$(printf '%s:' $root/packages/*/src)$PYTHONPATH
  '';
}
