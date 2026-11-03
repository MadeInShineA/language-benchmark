{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
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
        pkgs = nixpkgs.legacyPackages.${system};

      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # Python dependencies
            python3
            uv

            # JS dependencies
            bun
            nodejs

            # Go dependencies
            go
            gopls

            # Rust dependencies
            rustc
            cargo
            clippy
            rust-analyzer
            rustfmt

            # C dependencies
            gcc
            clang
          ];

          env.LD_LIBRARY_PATH =
            with pkgs;
            lib.makeLibraryPath [
              stdenv.cc.cc.lib
              zlib
              libxcb
              libGL
              glib
            ];

        };
      }
    );
}
