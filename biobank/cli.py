"""Interfaccia a riga di comando (REQ-10)."""
import argparse
import sys

from biobank.db import connect
from biobank.service import BiobankError, SampleService


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="biobank", description="Biobank Tracker")
    p.add_argument("--db", default="biobank.db", help="percorso del database")
    sub = p.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="registra un campione")
    add.add_argument("sample_id")
    add.add_argument("sample_type")
    add.add_argument("collection_date", help="AAAA-MM-GG")
    add.add_argument("location")

    show = sub.add_parser("show", help="mostra un campione")
    show.add_argument("sample_id")

    lst = sub.add_parser("list", help="elenca i campioni")
    lst.add_argument("--type", dest="sample_type")
    lst.add_argument("--status")

    mv = sub.add_parser("move", help="sposta un campione")
    mv.add_argument("sample_id")
    mv.add_argument("new_location")

    st = sub.add_parser("status", help="cambia lo stato di un campione")
    st.add_argument("sample_id")
    st.add_argument("new_status")

    hist = sub.add_parser("history", help="storico di un campione")
    hist.add_argument("sample_id")
    return p


def _print_sample(s: dict) -> None:
    print(f"{s['sample_id']}\t{s['sample_type']}\t{s['collection_date']}"
          f"\t{s['location']}\t{s['status']}")


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    conn = connect(args.db)
    service = SampleService(conn)
    try:
        if args.command == "add":
            _print_sample(service.register(
                args.sample_id, args.sample_type, args.collection_date, args.location))
        elif args.command == "show":
            _print_sample(service.get(args.sample_id))
        elif args.command == "list":
            for s in service.search(args.sample_type, args.status):
                _print_sample(s)
        elif args.command == "move":
            _print_sample(service.move(args.sample_id, args.new_location))
        elif args.command == "status":
            _print_sample(service.set_status(args.sample_id, args.new_status))
        elif args.command == "history":
            for e in service.history(args.sample_id):
                print(f"{e['timestamp']}\t{e['action']}\t{e['details']}")
        return 0
    except BiobankError as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()
