# toolz.nix
{
  lib,
  buildPythonPackage,
  fetchFromGitHub,
}:

buildPythonPackage rec {
  pname = "pypinyin-dict";
  version = "0.9.0";
  format = "setuptools";

  src = fetchFromGitHub {
    owner = "mozillazg";
    repo = "pypinyin-dict";
    tag = "v${version}";
    hash = "sha256-87JADcWEDI54EIu69qwJO2p5IKiqEXz8g+I40OG2AQs=";
  };
}
