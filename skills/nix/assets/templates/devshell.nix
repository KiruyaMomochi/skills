{
  description = "A powerful devshell environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    devshell.url = "github:numtide/devshell";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, devshell, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ devshell.overlays.default ];
        };
      in
      {
        devShells.default = pkgs.devshell.mkShell {
          name = "my-project";
          
          # Add packages here
          packages = with pkgs; [
            git
            # python3
            # rustc
          ];

          # Environment variables
          env = [
            # {
            #   name = "HTTP_PORT";
            #   value = "8080";
            # }
          ];

          # Custom commands provided by devshell
          commands = [
            {
              help = "print hello";
              name = "hello";
              command = "echo 'Hello World!'";
            }
          ];
        };
      }
    );
}
