{
  description = "Implementation of the word2vec algorithm";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
        };
      in {
        devShells.default = pkgs.mkShell {
          venvDir = ".venv";

          packages = with pkgs; [
            (with python3Packages; [
              venvShellHook
              #locust
              gevent
              numpy
              pydantic
              pandas
              pyarrow
              docker
              pyyaml
            ])
          ];
        };
      }
    );
}
