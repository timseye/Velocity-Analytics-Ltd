#!/usr/bin/env python3
"""
main.py
Runs several SQL analytics from queries.sql against the configured PostgreSQL database
and prints the results to the terminal.
"""

from connection import F1DatabaseConnector
import os
from typing import List

QUERIES_FILE = os.path.join(os.path.dirname(__file__), "queries.sql")


def load_queries(path: str) -> List[str]:
    """Load SQL statements from a .sql file, ignoring comment lines starting with --.
    Splits on semicolons and returns non-empty statements.
    """
    if not os.path.exists(path):
        return []
    stmts: List[str] = []
    buf: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            # skip full-line SQL comments
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
    # cleanup
    return [s.strip().rstrip(";") + ";" for s in stmts if s and s.strip() != ";"]


essential_demo_indices = [0, 1, 2]  # first three queries for demo


def run_queries(connector: F1DatabaseConnector, statements: List[str]):
    if not connector.connection:
        raise RuntimeError("Database connection is not established.")
    cur = connector.connection.cursor()
    for idx in essential_demo_indices:
        if idx >= len(statements):
            break
        sql = statements[idx]
        print("\n=== Executing Query #{} ===".format(idx + 1))
        print(sql)
        cur.execute(sql)
        try:
            columns = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchmany(10)
            if columns:
                print(" | ".join(columns))
            for row in rows:
                print(" | ".join(str(v) for v in row))
        except Exception:
            print(f"Affected rows: {cur.rowcount}")
    cur.close()


def main():
    print("Starting analytics run...")
    connector = F1DatabaseConnector()
    if not connector.connect():
        print("Failed to connect. Please check your .env settings.")
        return
    try:
        queries = load_queries(QUERIES_FILE)
        if not queries:
            print(f"No queries loaded from {QUERIES_FILE}. Ensure the file exists and contains SQL statements.")
            return
        run_queries(connector, queries)
    finally:
        connector.disconnect()


if __name__ == "__main__":
    main()
