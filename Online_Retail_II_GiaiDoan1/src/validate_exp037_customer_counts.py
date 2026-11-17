"""Reconcile full RFM CustomerIDs with the labels produced by EXP-037."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Đối chiếu số khách trước/sau phân cụm EXP-037 theo CustomerID."
    )
    parser.add_argument(
        "--rfm", type=Path, default=ROOT / "outputs/tables/rfm_table.csv"
    )
    parser.add_argument(
        "--labels",
        type=Path,
        default=ROOT / "outputs/tables/customer_clusters_full.csv",
    )
    parser.add_argument("--id-column", default="CustomerID")
    parser.add_argument("--cluster-column", default="cluster")
    args = parser.parse_args()

    for path in (args.rfm, args.labels):
        if not path.is_file():
            print(f"CHƯA THỂ KIỂM TRA: không tìm thấy {path}", file=sys.stderr)
            return 2

    try:
        rfm_rows = read_rows(args.rfm)
        label_rows = read_rows(args.labels)
        for rows, column, path in (
            (rfm_rows, args.id_column, args.rfm),
            (label_rows, args.id_column, args.labels),
            (label_rows, args.cluster_column, args.labels),
        ):
            if not rows or column not in rows[0]:
                raise ValueError(f"Thiếu cột {column!r} trong {path}.")
    except (OSError, ValueError, csv.Error) as exc:
        print(f"KHÔNG HỢP LỆ: {exc}", file=sys.stderr)
        return 2

    rfm_ids = [row[args.id_column].strip() for row in rfm_rows]
    label_ids = [row[args.id_column].strip() for row in label_rows]
    blank_ids = sum(not customer_id for customer_id in rfm_ids + label_ids)
    rfm_counts = Counter(customer_id for customer_id in rfm_ids if customer_id)
    label_counts = Counter(customer_id for customer_id in label_ids if customer_id)
    missing_ids = set(rfm_counts) - set(label_counts)
    extra_ids = set(label_counts) - set(rfm_counts)
    duplicate_rfm_ids = sum(count - 1 for count in rfm_counts.values() if count > 1)
    duplicate_label_ids = sum(count - 1 for count in label_counts.values() if count > 1)
    blank_labels = sum(not row[args.cluster_column].strip() for row in label_rows)
    cluster_sizes = Counter(
        row[args.cluster_column].strip()
        for row in label_rows
        if row[args.cluster_column].strip()
    )

    print(f"RFM: {len(rfm_rows)} dòng; ID không trống: {len(rfm_counts)}")
    print(f"Bảng nhãn: {len(label_rows)} dòng; ID không trống: {len(label_counts)}")
    print(
        f"ID thiếu nhãn: {len(missing_ids)}; ID ngoài RFM: {len(extra_ids)}; "
        f"ID trống: {blank_ids}"
    )
    print(
        f"ID trùng RFM: {duplicate_rfm_ids}; ID trùng nhãn: {duplicate_label_ids}; "
        f"nhãn cụm trống: {blank_labels}"
    )
    print(
        "Kích thước cụm: "
        + ", ".join(f"{label}={count}" for label, count in sorted(cluster_sizes.items()))
    )

    passed = not any(
        (
            blank_ids,
            duplicate_rfm_ids,
            duplicate_label_ids,
            blank_labels,
            missing_ids,
            extra_ids,
        )
    ) and len(rfm_rows) == len(label_rows)
    print(
        "KẾT QUẢ: "
        + ("PASS — số khách và CustomerID khớp." if passed else "FAIL — cần rà soát chênh lệch.")
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
