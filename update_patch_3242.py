from __future__ import annotations
import hashlib, os
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FILES={
    'app_core.py':('ee9352acd0ad64720ffa99bf637dbb2b6cf3dd4a57d32fe450d18cda1aa3863b','0d6f090c2d8378e4f9a51b111527152b0172368015cc453a5731a9ff3ef93c48'),
    'sorter_seek.py':('75f2bb1b1039f784cba85cc23224dcd4766dac639b1eb94dfdb3c5527288e139','c67f95eda3714fba923d96afa4e436a63d85d850930563e6eea16bf1f31e36c8'),
    'updater.py':('71c3d85ab5fd05873a4fd01ba46b6df49b25442b501722539f83a0a8e37ee69f','86b4dc09aaf0ea69ea4df6fba4faa70489cd385abdffeb1d578ef617f60ab1f4'),
    'ui.py':('62409be570c7a6f3704ba1b628feea6574fc3dad9a86cf6cbdc1c2f9573d9511','e13e6b85884f80ad5c9e3ab4117aae0547cdef51d9ab4f387d56064d6b288377'),
}

def sha_bytes(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def sha_file(p:Path)->str:return sha_bytes(p.read_bytes())

def write_checked(name:str,text:str):
    p=ROOT/name
    target=FILES[name][1]
    data=text.encode('utf-8')
    if sha_bytes(data)!=target:raise RuntimeError(f'{name}: target hash mismatch')
    tmp=p.with_suffix(p.suffix+'.3245.tmp')
    tmp.write_bytes(data);os.replace(tmp,p)

def patch_core(s:str)->str:
    s=s.replace('APP_VERSION = "3.24.4 No Console Flash"','APP_VERSION = "3.24.5 Sort PRO Recovery"',1)
    s=s.replace('SUBPROCESS_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0\n','',1)
    s=s.replace(', creationflags=SUBPROCESS_NO_WINDOW','').replace(',creationflags=SUBPROCESS_NO_WINDOW','')
    return s

def patch_seek(s:str)->str:
    s=s.replace("SUBPROCESS_NO_WINDOW=getattr(subprocess,'CREATE_NO_WINDOW',0) if os.name=='nt' else 0\n",'',1)
    s=s.replace(',creationflags=SUBPROCESS_NO_WINDOW','')
    return s

def patch_updater(s:str)->str:
    old="""    py=Path(sys.executable)\n    if os.name=='nt':\n        pw=py.with_name('pythonw.exe')\n        if pw.exists():py=pw\n    flags=getattr(subprocess,'CREATE_NO_WINDOW',0) if os.name=='nt' else 0\n"""
    new="""    py=Path(sys.executable)\n    if os.name=='nt':\n        # The installer itself runs under pythonw.exe, but restarting MCM under\n        # pythonw makes console FFmpeg/FFprobe children allocate flashing windows.\n        # Use console-subsystem Python with CREATE_NO_WINDOW instead; children then\n        # inherit the no-console process context without changing Sort PRO commands.\n        console_py=py.with_name('python.exe')\n        if console_py.exists():py=console_py\n    flags=getattr(subprocess,'CREATE_NO_WINDOW',0) if os.name=='nt' else 0\n"""
    if old not in s:raise RuntimeError('updater restart anchor missing')
    return s.replace(old,new,1)

def patch_ui(s:str)->str:
    old="""            launch_installer(path,install,restart,APP_DIR)\n            QMessageBox.information(self,'Обновление','Обновление проверено по SHA-256. MCM сейчас закроется, заменит файлы и запустится снова.')\n            QApplication.quit()\n"""
    new="""            launch_installer(path,install,restart,APP_DIR)\n            # Installer already owns the progress window. Quit immediately so the\n            # user never has to dismiss a second modal OK dialog while it waits.\n            QApplication.quit()\n"""
    if old not in s:raise RuntimeError('update modal anchor missing')
    return s.replace(old,new,1)

PATCHERS={'app_core.py':patch_core,'sorter_seek.py':patch_seek,'updater.py':patch_updater,'ui.py':patch_ui}
ok=True
try:
    for name,patcher in PATCHERS.items():
        p=ROOT/name;got=sha_file(p);base,target=FILES[name]
        if got==target:continue
        if got!=base:raise RuntimeError(f'{name}: unexpected source hash {got}')
        write_checked(name,patcher(p.read_text(encoding='utf-8')))
except Exception as exc:
    ok=False
    try:
        log=Path.home()/'.media_collection_manager'/'logs'/'update_patch_3245_error.txt'
        log.parent.mkdir(parents=True,exist_ok=True);log.write_text(str(exc),encoding='utf-8')
    except Exception:pass
finally:
    if ok:
        try:Path(__file__).unlink(missing_ok=True)
        except Exception:pass
