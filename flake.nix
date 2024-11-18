{
  description = "FastAnime Project Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs { inherit system; };

      python = pkgs.python310;
      pythonPackages = python.pkgs;
      fastanimeEnv = pythonPackages.buildPythonApplication {
        pname = "fastanime";
        version = "2.7.5";

        src = ./.;

        preBuild = ''
          sed -i 's/rich>=13.9.2/rich>=13.8.1/' pyproject.toml
        '';

        # Add runtime dependencies
        propagatedBuildInputs = with pythonPackages; [
          click
          inquirerpy
          requests
          rich
          thefuzz
          yt-dlp
          dbus-python
          hatchling
        ];

        # Ensure compatibility with the pyproject.toml
        format = "pyproject";
      };

    in
    {
      packages.default = fastanimeEnv;

      # DevShell for development
      devShells.default = pkgs.mkShell {
        buildInputs = [
          fastanimeEnv
          pythonPackages.hatchling
        ];
      };
    });
}
