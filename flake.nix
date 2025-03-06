{
  description = "A development environment for working with csharp.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { self, nixpkgs, ... }@inputs:
    inputs.flake-utils.lib.eachDefaultSystem (
      system:
      let
        unstable = import nixpkgs { inherit system; };

         myPython = unstable.python312.withPackages (
          ps: with ps; [
            dash
            plotly
            numpy
          ]
        );
      in
      {
        devShell = unstable.mkShell {
          buildInputs = [
            unstable.nixfmt-rfc-style
            myPython
          ];
        };
      }
    );
}