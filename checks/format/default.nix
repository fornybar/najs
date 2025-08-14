{ inputs, pkgs, ... }:
let
  treefmt = inputs.treefmt-nix.lib.evalModule pkgs (inputs.self + "/treefmt.nix");
in
treefmt.config.build.check inputs.self
