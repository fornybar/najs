{ project, ... }:
{
  perSystem =
    { pkgs, ... }:
    let
      scope = project.forPython {
        inherit pkgs;
      };
    in
    {
      checks.najs-pytest = scope.mkPytestCheck {
        package = "najs";
        groups = [ "dev" ];
        paths = [ "tests" ];
        nativeBuildInputs = [
          pkgs.nats-server
        ];
        env = {
          HOME = "/tmp";
        };
      };
    };
}
