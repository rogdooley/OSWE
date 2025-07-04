from pathlib import Path
import tempfile
import shutil

def file_exists(path: str | Path) -> bool:
    return Path(path).is_file()

def dir_exists(path: str | Path) -> bool:
    return Path(path).is_dir()

def ensure_dir(path: str | Path):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)

def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding='utf-8')

def write_text(path: str | Path, content: str):
    Path(path).write_text(content, encoding='utf-8')

def read_lines(path: str | Path) -> list[str]:
    return Path(path).read_text(encoding='utf-8').splitlines()

def write_lines(path: str | Path, lines: list[str]):
    Path(path).write_text('\n'.join(lines), encoding='utf-8')

def get_files_by_ext(path: str | Path, ext: str) -> list[Path]:
    """Recursively find files by extension"""
    return list(Path(path).rglob(f'*.{ext.lstrip(".")}'))

def is_safe_path(base: Path, target: Path) -> bool:
    """Prevent directory traversal — checks if target is under base"""
    try:
        base = base.resolve()
        target = target.resolve()
        return target.is_relative_to(base)
    except Exception:
        return False

def create_temp_file(suffix: str = '', prefix: str = 'tmp') -> Path:
    """Returns a path to a new temp file"""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    return Path(path)

def copy_file(src: str | Path, dst: str | Path, overwrite: bool = True):
    src = Path(src)
    dst = Path(dst)
    if dst.exists() and not overwrite:
        raise FileExistsError(f"{dst} already exists")
    shutil.copy2(src, dst)