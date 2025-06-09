{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils = {
      url = "github:numtide/flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        myPython = pkgs.python3.override {
          self = myPython;
          packageOverrides = pyfinal: pypref: {
            pypinyin-dict = pyfinal.callPackage ./nix/pypinyin-dict.nix { };
          };
        };
      in
      {
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = with pkgs; [
            (myPython.withPackages (
              ps: with ps; [
                genanki
                pypinyin
                gtts
                openai
                mypy
                zhon
                pypinyin-dict
                zstandard
              ]
            ))

            opencc
          ];
        };
      }
    );
}
