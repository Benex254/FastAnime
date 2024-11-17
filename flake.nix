{
  description = "A command-line interface for browsing anime";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs }: {
    # Generate packages for all supported systems
    packages = nixpkgs.lib.genAttrs nixpkgs.lib.systems.supportedSystems (system: let
      pkgs = import nixpkgs { inherit system; };
    in pkgs.python3Packages.buildPythonApplication {
      pname = "fastanime";
      version = "2.7.5";

      # Path to your project source
      src = ./.;

      # Specify runtime dependencies
      propagatedBuildInputs = with pkgs.python3Packages; [
          click, rich, inquirerpy, requests, thefuzz, plyer, fastapi,yt-dlp, mpv,dbus-python
      ];

      # CLI entry point (matches your pyproject.toml or setup.py configuration)
      # Example: Entry point defined as `console_scripts` in pyproject.toml
      entryPoints = {
        "console_scripts" = {
          fastanime = "fastanime:FastAnime";
        };
      };

      meta = with pkgs.lib; {
        description = "A command-line interface for browsing anime";
        license = licenses.unlicense;
        maintainers = [ maintainers.Benex254 ];
        platforms = platforms.all; # Cross-platform compatibility
      };
    });
  };
}
