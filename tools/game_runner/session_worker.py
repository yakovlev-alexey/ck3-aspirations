"""Private worker launched only by the managed supervisor after Job assignment."""
import json
import sys
from pathlib import Path
from .runner import Config, GameRunner


class BorrowedGuard:
    def __init__(self, root):
        self.path = root / '.asp-automation.lock'
    def acquire(self):
        if not (self.path / 'owner.json').exists():
            raise RuntimeError('Managed parent lock is absent')
    def close(self):
        pass


def main():
    if sys.stdin.readline().strip() != 'go':
        raise RuntimeError('Managed worker was not released by its supervisor')
    payload = json.loads(Path(sys.argv[1]).read_text())
    config_path = Path(sys.argv[1]).with_name('config.json')
    config_path.write_text(json.dumps(payload['config']), encoding='utf-8')
    runner = GameRunner(Config.load(config_path))
    runner.guard = BorrowedGuard(runner.config.user_data)
    runner.launch_save = Path(payload['save'])
    runner.request_journal = Path(payload['journal'])
    runner.backend.process_journal = Path(sys.argv[1]).with_name('game-processes.json')
    try:
        result = runner.run_scenario(payload['scenario'], payload['repeat'])
    finally:
        # Parent owns files and profile, including cleanup after worker termination.
        runner.backend.stop()
    print(json.dumps(result))


if __name__ == '__main__':
    main()
