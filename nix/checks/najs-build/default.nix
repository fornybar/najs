{ self, ... }:
{
  perSystem =
    { pkgs, ... }:
    let
      pkgs' = pkgs.extend self.overlays.default;
    in
    {
      checks.najs-build = pkgs'.python3Packages.najs;
    };
}
