from pathlib import Path
import hashlib,re
ROOT=Path(__file__).resolve().parent
ui=(ROOT/'ui.py').read_text(encoding='utf-8')
# Protected modules must remain on the verified playback baseline.
EXPECTED={
 'sorter_seek.py':'c67f95eda3714fba923d96afa4e436a63d85d850930563e6eea16bf1f31e36c8',
 'sorter_native_player.py':'1778fc9045394cc2ba35aadea07f72b3c89bce437a5b0bdbb2e387969629c546',
 'spider_state.py':'598bfecd3353ef634dc34fbe425b8a95f528341fa9c06cf4615931ba0aa48e0c',
}
for name,expected in EXPECTED.items():
    got=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    assert got==expected,(name,got,expected)
# Mute is stateful and must affect both Qt and native backend paths.
assert "self._muted=bool(prefs.get('sorter_muted',False))" in ui
assert "shortcut('M',self.toggle_mute)" in ui
assert "self.mute_btn=QPushButton('🔇' if self._muted else '🔊')" in ui
assert "def _output_volume(self)->float:" in ui
assert "'sorter_muted':bool(self._muted)" in ui
assert "'volume':self._output_volume()" in ui
# Scrub drag may update UI state only; the real backend gets one seek on release.
start=ui.index('    def _seek_live(self,value:int):',ui.index('class SorterProPage'))
end=ui.index('    def _seek_finished(self,value:int):',start)
block=ui[start:end]
assert 'setPosition' not in block
assert "_native_send({'cmd':'seek'" not in block
finish=ui[end:ui.index('    def seek_relative',end)]
assert '_request_video_seek(int(value),allow_repair=True)' in finish
assert 'drag_ms=' in finish
print('REGRESSION_TEST_3_27_0_CHECKPOINT1: PASS')
