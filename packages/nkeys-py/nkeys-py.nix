{
  fetchFromGitHub,
  buildPythonPackage,
  setuptools,
  pynacl,
  ...
}:
buildPythonPackage rec {
  pname = "nkeys";
  version = "0.2.1";
  pyproject = true;
  src = fetchFromGitHub {
    inherit pname version;
    owner = "nats-io";
    repo = "nkeys.py";
    rev = "v0.2.1";
    sha256 = "sha256-DBAjNZFZVlwL5mQCudy4BbOLrhq1QliUSG1RdiLjKj0=";
  };
  nativeBuildInputs = [ setuptools ];
  propagatedBuildInputs = [ pynacl ];
}
