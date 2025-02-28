{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };

  outputs = {nixpkgs, ...}: let
    pkgs = nixpkgs.legacyPackages."x86_64-linux";
  in {
    devShells.x86_64-linux.default = pkgs.mkShell {
      packages = [
        (pkgs.python311.withPackages (p:
          with p; [
            pydantic
            fastapi
            pandas
            numpy
            pyarrow
            ipykernel
            pip
            jupyterlab
            pytest
          ]))
      ];
    };
  };
}
