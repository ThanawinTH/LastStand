import sys
from pathlib import Path

# Ensure the project root is always on sys.path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ui.stats_dashboard import StatsDashboardApp


def main() -> None:
    app = StatsDashboardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
