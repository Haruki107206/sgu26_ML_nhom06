"""Validate the customer-level RFM table and write an auditable CSV report."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "outputs" / "tables" / "rfm_table.csv"
DEFAULT_REPORT = ROOT / "outputs" / "tables" / "rfm_validation_report.csv"
REQUIRED = ("CustomerID", "Recency", "Frequency", "Monetary")


def validate(input_path: Path, report_path: Path) -> bool:
    """Write one row per validation check. Return True only if all checks pass."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []

    def add(check: str, passed: bool, observed: object, expected: str, details: str = "") -> None:
        rows.append({
            "Check": check,
            "Status": "PASS" if passed else "FAIL",
            "Severity": "error",
            "Observed": str(observed),
            "Expected": expected,
            "Details": details,
        })

    exists = input_path.is_file()
    add("rfm_file_exists", exists, input_path if exists else "missing", "file exists")
    if not exists:
        pd.DataFrame(rows).to_csv(report_path, index=False, encoding="utf-8-sig")
        print(f"FAIL: Không tìm thấy bảng RFM: {input_path}")
        print(f"Báo cáo: {report_path}")
        return False

    try:
        rfm = pd.read_csv(input_path, dtype={"CustomerID": "string"})
    except Exception as exc:  # report a readable error instead of a traceback-only failure
        add("rfm_csv_readable", False, type(exc).__name__, "valid CSV", str(exc))
        pd.DataFrame(rows).to_csv(report_path, index=False, encoding="utf-8-sig")
        print(f"FAIL: Không đọc được CSV RFM: {exc}")
        print(f"Báo cáo: {report_path}")
        return False

    missing = sorted(set(REQUIRED) - set(rfm.columns))
    add("required_columns", not missing, ", ".join(rfm.columns), ", ".join(REQUIRED),
        f"Thiếu: {missing}" if missing else "")
    if missing:
        pd.DataFrame(rows).to_csv(report_path, index=False, encoding="utf-8-sig")
        print(f"FAIL: Thiếu cột bắt buộc: {missing}")
        print(f"Báo cáo: {report_path}")
        return False

    customer = rfm["CustomerID"].astype("string").str.strip()
    customer_missing = customer.isna() | customer.eq("")
    duplicate_count = int(customer[~customer_missing].duplicated(keep=False).sum())
    add("customer_id_not_missing", not customer_missing.any(), int(customer_missing.sum()), "0 missing IDs")
    add("customer_id_unique", duplicate_count == 0, duplicate_count, "0 duplicate ID rows")

    numeric = rfm[["Recency", "Frequency", "Monetary"]].apply(pd.to_numeric, errors="coerce")
    finite = np.isfinite(numeric.to_numpy(dtype=float))
    nonfinite_count = int((~finite).sum())
    add("rfm_numeric_finite", nonfinite_count == 0, nonfinite_count, "0 NaN or infinite values")

    negative_count = int((numeric < 0).fillna(False).sum().sum())
    add("rfm_nonnegative", negative_count == 0, negative_count, "0 negative values")
    invalid_frequency = numeric["Frequency"].isna() | numeric["Frequency"].le(0) | (numeric["Frequency"] % 1 != 0)
    add("frequency_positive_integer", not invalid_frequency.any(), int(invalid_frequency.sum()),
        "positive whole-number invoice count")
    invalid_monetary = numeric["Monetary"].isna() | numeric["Monetary"].le(0)
    add("monetary_positive", not invalid_monetary.any(), int(invalid_monetary.sum()),
        "Monetary > 0")
    invalid_recency = numeric["Recency"].isna() | numeric["Recency"].lt(0)
    add("recency_nonnegative", not invalid_recency.any(), int(invalid_recency.sum()),
        "Recency >= 0")
    add("customer_count", len(rfm) > 0, int(len(rfm)), "> 0 rows", 
        f"Unique non-missing IDs: {customer[~customer_missing].nunique()}")

    pd.DataFrame(rows).to_csv(report_path, index=False, encoding="utf-8-sig")
    passed = all(row["Status"] == "PASS" for row in rows)
    failed = [row["Check"] for row in rows if row["Status"] == "FAIL"]
    print(f"{'PASS' if passed else 'FAIL'}: {len(rfm):,} RFM rows; "
          f"{customer[~customer_missing].nunique():,} unique CustomerID")
    if failed:
        print("Checks failed: " + ", ".join(failed))
    print(f"Báo cáo: {report_path}")
    return passed


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="CSV RFM input")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="CSV validation report output")
    args = parser.parse_args()
    return 0 if validate(args.input, args.report) else 1


if __name__ == "__main__":
    sys.exit(main())
