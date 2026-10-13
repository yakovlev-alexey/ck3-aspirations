"""python -m tools.game_runner --config PATH run automation-smoke --repeat 3"""
import argparse
import json
import sys
from .runner import Config, GameRunner
from .registry import SCENARIOS


def main():
    parser = argparse.ArgumentParser(description="Bounded disposable CK3 scenario runner")
    parser.add_argument("--config", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    scenario = commands.add_parser("run")
    scenario.add_argument("scenario", choices=SCENARIOS)
    scenario.add_argument("--repeat", type=int, default=1, choices=range(1, 11))
    managed = commands.add_parser("session", help="Prepare, run, collect evidence and restore a disposable session")
    managed.add_argument("scenario", choices=SCENARIOS)
    managed.add_argument("--repeat", type=int, default=1, choices=range(1, 11))
    managed.add_argument("--deadline", type=int, default=240, choices=range(1, 901), metavar="SECONDS")
    commands.add_parser("observe")
    commands.add_parser("mcp", help="Serve MCP 2025-11-25 over local stdio")
    advance = commands.add_parser("advance-days")
    advance.add_argument("days", type=int, choices=range(1, 31))
    args = parser.parse_args()
    if args.command == "mcp":
        from contextlib import redirect_stdout
        from .mcp_server import serve
        try:
            with redirect_stdout(sys.stderr):
                runner = GameRunner(Config.load(args.config))
        except (RuntimeError, ValueError, OSError) as error:
            print("MCP configuration failed: " + str(error), file=sys.stderr)
            return 1
        return serve(runner)
    if args.command == "session":
        from .session import run_managed_session
        try:
            result = run_managed_session(args.config, args.scenario, args.repeat, args.deadline)
        except (RuntimeError, ValueError, OSError) as error:
            result = {"status": "transport_error", "error": str(error)}
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "passed" else 1
    runner = None
    try:
        runner = GameRunner(Config.load(args.config))
        if args.command == "run":
            result = runner.run_scenario(args.scenario, args.repeat)
        elif args.command == "observe":
            result = runner.observe()
        else:
            result = runner.advance_days(args.days)
    except (RuntimeError, ValueError, OSError) as error:
        result = {"status": "transport_error", "error": str(error)}
    finally:
        if runner is not None:
            try:
                runner.close()
            except (RuntimeError, ValueError, OSError) as error:
                result = {"status": "transport_error", "error": "Cleanup failed: " + str(error), "result": locals().get("result")}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
