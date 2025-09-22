#!/usr/bin/env python3
"""Run queries in `queries.sql` and export results to CSV in `outputs/`."""

from connection import F1DatabaseConnector
import os
import csv
from typing import List

QUERIES_FILE = os.path.join(os.path.dirname(__file__), "queries.sql")
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def load_queries(path: str) -> List[str]:
    """Return SQL statements split by semicolons, skipping `--` lines."""
    if not os.path.exists(path):
        return []
    stmts: List[str] = []
    buf: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line.strip().startswith("--"):
                continue
            buf.append(line + "\n")
            if ";" in line:
                stmt = "".join(buf).strip()
                if stmt:
                    stmts.append(stmt)
                buf = []
    # leftover without semicolon
    tail = "".join(buf).strip()
    if tail:
        stmts.append(tail)
    return [s.strip().rstrip(";") + ";" for s in stmts if s and s.strip() != ";"]

def run_and_export(connector: F1DatabaseConnector, statements: List[str]):
    if not connector.connection:
        raise RuntimeError("Database connection is not established.")
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    cur = connector.connection.cursor()
    for i, sql in enumerate(statements, start=1):
        try:
            cur.execute(sql)
            if cur.description:
                cols = [d[0] for d in cur.description]
                out = os.path.join(OUTPUTS_DIR, f"q{i}.csv")
                with open(out, "w", newline="", encoding="utf-8") as fh:
                    w = csv.writer(fh)
                    w.writerow(cols)
                    while True:
                        batch = cur.fetchmany(1000)
                        if not batch:
                            break
                        w.writerows(batch)
                print(f"Saved: {out}")
            else:
                print(f"Query {i} affected rows: {cur.rowcount}")
        except Exception as e:
            print(f"Query {i} failed: {e}")
            try:
                connector.connection.rollback()
            except Exception:
                pass
    cur.close()


def main():
    print("Running queries and exporting CSVs...")
    connector = F1DatabaseConnector()
    if not connector.connect():
        print("Failed to connect. Please check your .env settings.")
        return
    try:
        queries = load_queries(QUERIES_FILE)
        if not queries:
            print(f"No queries loaded from {QUERIES_FILE}. Ensure the file exists and contains SQL statements.")
            return
        run_and_export(connector, queries)
    finally:
        connector.disconnect()


if __name__ == "__main__":
    main()
