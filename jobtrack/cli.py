"""Command-line interface for jobtrack."""

import argparse
import sys
from typing import List, Optional

from . import __version__
from .db import Database
from .models import Application, STATUSES


def _print_table(apps: List[Application]) -> None:
    if not apps:
        print("No applications yet. Add one with:  jobtrack add ...")
        return
    header = f"{'ID':>3}  {'DATE':<10}  {'STATUS':<10}  {'COMPANY':<22}  POSITION"
    print(header)
    print("-" * len(header))
    for a in apps:
        company = (a.company[:21] + "…") if len(a.company) > 22 else a.company
        print(f"{a.id:>3}  {a.applied_on:<10}  {a.status:<10}  {company:<22}  {a.position}")


def cmd_add(args: argparse.Namespace, db: Database) -> int:
    app = Application(
        id=None,
        company=args.company,
        position=args.position,
        status=args.status,
        applied_on=args.date or "",
        location=args.location or "",
        url=args.url or "",
        salary=args.salary or "",
        notes=args.notes or "",
    )
    new_id = db.add(app)
    print(f"Added application #{new_id}: {app.company} — {app.position}")
    return 0


def cmd_list(args: argparse.Namespace, db: Database) -> int:
    _print_table(db.list(status=args.status))
    return 0


def cmd_show(args: argparse.Namespace, db: Database) -> int:
    app = db.get(args.id)
    if not app:
        print(f"No application with id {args.id}", file=sys.stderr)
        return 1
    for field in ("id", "company", "position", "status", "applied_on",
                  "location", "url", "salary", "notes"):
        print(f"{field:>11}: {getattr(app, field)}")
    return 0


def cmd_status(args: argparse.Namespace, db: Database) -> int:
    if db.set_status(args.id, args.new_status):
        print(f"Application #{args.id} -> {args.new_status}")
        return 0
    print(f"No application with id {args.id}", file=sys.stderr)
    return 1


def cmd_delete(args: argparse.Namespace, db: Database) -> int:
    if db.delete(args.id):
        print(f"Deleted application #{args.id}")
        return 0
    print(f"No application with id {args.id}", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jobtrack", description="Track your job applications from the terminal."
    )
    parser.add_argument("--version", action="version", version=f"jobtrack {__version__}")
    parser.add_argument("--db", default=None, help="path to the SQLite database file")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a new application")
    p_add.add_argument("company")
    p_add.add_argument("position")
    p_add.add_argument("--status", choices=STATUSES, default="applied")
    p_add.add_argument("--date", help="application date (YYYY-MM-DD); defaults to today")
    p_add.add_argument("--location")
    p_add.add_argument("--url")
    p_add.add_argument("--salary")
    p_add.add_argument("--notes")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="list applications")
    p_list.add_argument("--status", choices=STATUSES, help="filter by status")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="show one application in detail")
    p_show.add_argument("id", type=int)
    p_show.set_defaults(func=cmd_show)

    p_status = sub.add_parser("status", help="change the status of an application")
    p_status.add_argument("id", type=int)
    p_status.add_argument("new_status", choices=STATUSES)
    p_status.set_defaults(func=cmd_status)

    p_del = sub.add_parser("delete", help="delete an application")
    p_del.add_argument("id", type=int)
    p_del.set_defaults(func=cmd_delete)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    db = Database(args.db)
    try:
        return args.func(args, db)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
