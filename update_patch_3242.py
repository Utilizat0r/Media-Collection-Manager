from pathlib import Path

root = Path(__file__).resolve().parent

NEW_DOWNLOAD = r'''def download_package(manifest: dict, dest_dir: str | Path, progress=None, status=None) -> Path:
    url = str(manifest.get('url') or '').strip()
    expected = str(manifest.get('sha256') or '').lower().strip()
    if not url or len(expected) != 64:
        raise RuntimeError('Некорректный manifest обновления')

    root = Path(dest_dir)
    root.mkdir(parents=True, exist_ok=True)
    final = root / f"mcm_update_{manifest.get('version', 'new')}.zip"
    part = final.with_suffix('.part')
    status_path = root / f"update_progress_{uuid.uuid4().hex}.json"
    try:
        part.unlink(missing_ok=True)
    except Exception:
        pass

    _atomic_json(status_path, {'state': 'running', 'phase': 'connect', 'detail': 'Подключение к GitHub…', 'done': 0, 'total': 0})
    _start_download_progress_window(status_path, str(manifest.get('version') or ''), root)

    def emit_phase(phase: str, detail: str = '', done: int = 0, total: int = 0):
        _atomic_json(status_path, {'state': 'running', 'phase': phase, 'detail': detail, 'done': int(done or 0), 'total': int(total or 0)})
        if status:
            try:
                status(str(phase), str(detail))
            except Exception:
                pass

    def emit_progress(done: int, total: int, detail: str = ''):
        _atomic_json(status_path, {'state': 'running', 'phase': 'download', 'detail': detail, 'done': int(done or 0), 'total': int(total or 0)})
        if progress:
            try:
                progress(int(done or 0), int(total or 0))
            except Exception:
                pass

    try:
        h = hashlib.sha256()
        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
            'Cache-Control': 'no-cache',
            'Accept': 'application/octet-stream',
        })
        with urllib.request.urlopen(req, timeout=60) as response, part.open('wb') as f:
            total = int(response.headers.get('Content-Length') or 0)
            done = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                h.update(chunk)
                done += len(chunk)
                emit_progress(done, total, '')

        emit_phase('verify', 'Проверка SHA-256…')
        if h.hexdigest().lower() != expected:
            try:
                part.unlink()
            except Exception:
                pass
            raise RuntimeError('SHA-256 обновления не совпадает')

        emit_phase('archive', 'Проверка целостности ZIP…')
        os.replace(part, final)
        with zipfile.ZipFile(final, 'r') as archive:
            bad = archive.testzip()
            if bad:
                raise RuntimeError('Повреждён файл внутри обновления: ' + str(bad))

        _atomic_json(status_path, {'state': 'done', 'phase': 'ready', 'detail': 'Пакет проверен. Начинаю установку…', 'done': 100, 'total': 100})
        return final
    except Exception as exc:
        _atomic_json(status_path, {'state': 'error', 'phase': 'error', 'detail': str(exc), 'done': 0, 'total': 1})
        raise
'''

try:
    p = root / 'app_core.py'
    s = p.read_text(encoding='utf-8')
    for old in (
        'APP_VERSION = "3.24.2 Update Progress UX"',
        'APP_VERSION = "3.24.1 Playback Recovery Hotfix"',
    ):
        if old in s:
            s = s.replace(old, 'APP_VERSION = "3.24.3 Direct ZIP OTA"', 1)
            p.write_text(s, encoding='utf-8')
            break
except Exception:
    pass

try:
    p = root / 'updater.py'
    s = p.read_text(encoding='utf-8')
    s = s.replace('import base64\n', '', 1)
    s = s.replace("USER_AGENT = 'MediaCollectionManager-Updater/1.1'", "USER_AGENT = 'MediaCollectionManager-Updater/1.2'", 1)
    start = s.index('def download_package(')
    end = s.index('\ndef launch_installer(', start)
    s = s[:start] + NEW_DOWNLOAD + '\n' + s[end + 1:]
    s = s.replace("'decode':'Подготовка пакета…',", '', 1)
    p.write_text(s, encoding='utf-8')
except Exception:
    pass

try:
    Path(__file__).unlink(missing_ok=True)
except Exception:
    pass
