{
  description = "Shell for TA work in Python";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-25.11";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    name = "PyTA";
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = with pkgs;
        builtins.concatLists [
          [
            graphviz
            python313
          ]
          (with python313Packages; [
            django
            graphviz
            haversine
            networkx
          ])
        ];

      shellHook = ''
        export NIXSHELL="$NIXSHELL+${name}"
      '';
    };
  };
}
