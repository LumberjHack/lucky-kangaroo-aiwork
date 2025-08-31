import shutil
from pathlib import Path
from datetime import datetime
from typing import Iterable, Union

PathLike = Union[str, Path]


def snapshot_files(file_paths: Iterable[PathLike], project_root: PathLike = None, backup_root: PathLike = None) -> Path:
    """
    Crée un snapshot daté des fichiers passés en paramètre dans `backend/backup/<YYYYMMDD_HHMMSS>/`.
    - Conserve l'arborescence relative au `project_root` si fourni, sinon au dossier commun des fichiers.
    - Retourne le chemin du dossier de snapshot créé.
    """
    file_paths = [Path(p).resolve() for p in file_paths]
    if not file_paths:
        raise ValueError("Aucun fichier à sauvegarder")

    # Déterminer la racine du projet
    if project_root is None:
        # supposer que ce script est dans backend/utils/backup.py → racine = 2 niveaux au-dessus
        project_root = Path(__file__).resolve().parents[2]
    else:
        project_root = Path(project_root).resolve()

    # Racine des backups
    if backup_root is None:
        backup_root = project_root / 'backend' / 'backup'
    else:
        backup_root = Path(backup_root).resolve()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    snapshot_dir = backup_root / timestamp
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    for src in file_paths:
        try:
            rel = src.relative_to(project_root)
        except ValueError:
            # si le fichier est hors projet, le placer à la racine du snapshot
            rel = Path(src.name)
        dest = snapshot_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return snapshot_dir


def snapshot_globs(globs: Iterable[str], base_dir: PathLike = None, **kwargs) -> Path:
    """
    Snapshot de plusieurs motifs glob sous `base_dir`.
    """
    base = Path(base_dir or Path(__file__).resolve().parents[2]).resolve()
    files = []
    for pattern in globs:
        files.extend(base.glob(pattern))
    return snapshot_files(files, project_root=base, **kwargs)
