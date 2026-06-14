{
  pkgs,
  config,
  ...
}: let
  apiPort = 8000;
in {
  name = "Siege Scoreboard";

  packages = with pkgs; [
    git
  ];

  cachix.pull = ["rbabaev"];

  languages = {
    python = {
      enable = true;
      uv = {
        enable = true;
      };
    };

    javascript = {
      enable = true;
      pnpm = {
        enable = true;
        install.enable = true;
      };
    };
  };

  env = {
    APP_PORT = toString config.processes.api.ports.http.value;
    DATABASE_URL = "sqlite:///./data/scoreboard.db";
  };

  tasks."css:build" = {
    exec = "pnpm run build:css";
    before = [
      "devenv:processes:api"
      "devenv:processes:tailwind"
    ];
  };

  processes = {
    api = {
      ports.http = {
        allocate = apiPort;
      };
      exec = ''
        uv run uvicorn app.main:app --reload --host 0.0.0.0 --port ''${APP_PORT}
      '';
      cwd = config.devenv.root;
      ready.http.get = {
        port = apiPort;
        path = "/health";
      };
    };

    tailwind = {
      exec = "pnpm run watch:css";
      cwd = config.devenv.root;
    };
  };

  scripts = {
    lint.exec = "uv run ruff check .";
    format.exec = "uv run ruff format .";
    build-css.exec = "pnpm run build:css";
  };
}
