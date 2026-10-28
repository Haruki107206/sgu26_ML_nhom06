"""Download the official UCI Online Retail II workbook into data/raw/."""
from pathlib import Path
import zipfile
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
ZIP_PATH = RAW_DIR / "online_retail_ii.zip"


def find_workbook():
    candidates = list(RAW_DIR.rglob("*.xlsx"))
    if not candidates:
        return None
    preferred = [p for p in candidates if "online" in p.name.lower() and "retail" in p.name.lower()]
    return preferred[0] if preferred else candidates[0]


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    existing = find_workbook()
    if existing:
        print(f"Dataset da co san: {existing}")
        return

    print("Dang tai Online Retail II tu UCI (tep goc khoang 43.5 MB)...")
    try:
        with requests.get(DATA_URL, stream=True, timeout=(20, 180)) as response:
            response.raise_for_status()
            with ZIP_PATH.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output.write(chunk)
    except requests.RequestException as exc:
        ZIP_PATH.unlink(missing_ok=True)
        raise SystemExit(
            "Khong tai duoc dataset. Hay kiem tra ket noi mang hoac tai thu cong tu "
            "https://archive.ics.uci.edu/dataset/502/online+retail+ii, sau do dat file .xlsx vao data/raw/.\n"
            f"Chi tiet: {exc}"
        ) from exc

    try:
        with zipfile.ZipFile(ZIP_PATH) as archive:
            # Extract only Excel workbook(s), avoiding unrelated archive paths.
            workbook_members = [name for name in archive.namelist() if name.lower().endswith(".xlsx")]
            if not workbook_members:
                raise RuntimeError("Khong tim thay file .xlsx trong goi tai ve tu UCI.")
            for member in workbook_members:
                destination = RAW_DIR / Path(member).name
                with archive.open(member) as src, destination.open("wb") as dst:
                    while True:
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        dst.write(chunk)
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        raise SystemExit(f"Khong the giai nen dataset: {exc}") from exc
    finally:
        ZIP_PATH.unlink(missing_ok=True)

    workbook = find_workbook()
    if not workbook:
        raise SystemExit("Tai ve xong nhung khong tim thay file Excel. Vui long kiem tra data/raw/.")
    print(f"Hoan tat. Dataset nam tai: {workbook}")


if __name__ == "__main__":
    main()
