import glob
import sqlite3
from pathlib import Path

DB_PATH = "data/gm.db"

def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    sql_files = sorted(glob.glob("sql/*.sql"))
    if not sql_files:
        raise SystemExit("No SQL files found in sql/")

    print(f"Found {len(sql_files)} SQL files.")
    ok = 0

    for fp in sql_files:
        name = Path(fp).name
        sql = Path(fp).read_text(encoding="utf-8").strip()
        if not sql:
            print(f"[EMPTY] {name}")
            continue
        try:
            cur.execute(sql)
            rows = cur.fetchmany(3)
            print(f"[OK] {name}  sample_rows={rows}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {name}  error={e}")

    con.close()
    print(f"Done. OK={ok}/{len(sql_files)}")

if __name__ == "__main__":
    main()
