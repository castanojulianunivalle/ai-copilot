from __future__ import annotations

import json

from dotenv import load_dotenv

from daily_reporter.clickup import ClickUpClient
from daily_reporter.config import load_settings


def main() -> None:
    load_dotenv(override=False)
    s = load_settings()
    c = ClickUpClient(token=s.clickup_token)

    teams = c.get_teams()
    print("Teams:")
    print(json.dumps(teams, ensure_ascii=False, indent=2)[:8000])

    for t in teams:
        team_id = str(t.get("id") or "")
        if not team_id:
            continue
        try:
            templates = c.get_task_templates(team_id=team_id)
            print(f"\nTask templates for team {team_id}:")
            simplified = [
                {
                    "id": x.get("id"),
                    "name": x.get("name") or x.get("title"),
                    "type": x.get("type"),
                }
                for x in templates
            ]
            print(json.dumps(simplified, ensure_ascii=False, indent=2)[:8000])
        except Exception as exc:  # noqa: BLE001
            print(f"\nFailed to list templates for team {team_id}: {exc}")


if __name__ == "__main__":
    main()


