{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    nixpkgs,
    pyproject-nix,
    ...
  }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};

    project = pyproject-nix.lib.project.loadPyproject {
      projectRoot = ./.;
    };

    python = pkgs.python313;

    # Returns a function that can be passed to `python.withPackages`
    arg = project.renderers.withPackages {inherit python;};

    # Returns a wrapped environment (virtualenv like) with all our packages
    projectEnv = python.withPackages arg;

     runScript = pkgs.writeShellScript "bita-run" ''
      exec ${projectEnv}/bin/fastapi run bita
    '';

    devScript = pkgs.writeShellScript "bita-dev" ''
      exec ${projectEnv}/bin/fastapi dev bita
    '';

  in {
    # Development shell
    devShells.${system}.default = pkgs.mkShell {
      packages = [
        projectEnv
        pkgs.git
      ];

      shellHook = ''
        echo "🚀 Bita development environment"
        echo "Available commands:"
        echo "  fastapi dev bita          - Start development server"
        echo "  pytest                    - Run tests"
        echo "  ruff check .              - Lint code"
        echo "  ruff format .             - Format code"
        echo "  mypy bita                 - Type check"
        echo "  python generate-data.py   - Generate test data"
        echo "  nix build                 - Build the package"
        echo "  nix run                   - Run the application"
      '';
    };

    # Build the package
    packages.${system} = {
      default = python.pkgs.buildPythonPackage (
        project.renderers.buildPythonPackage {inherit python;}
      );
    };

    # Application for running
    apps.${system} = {
      default = {
        type = "app";
        program = "${runScript}";
      };

      dev = {
        type = "app";
        program = "${devScript}";
      };

    };
  };
}
