from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parent

def sha(name): return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

assert sha('sorter_seek.py')=='c67f95eda3714fba923d96afa4e436a63d85d850930563e6eea16bf1f31e36c8'
assert sha('ai_engine.py')=='40a2681c9f8f468dd98fa27159ad1d2fb36867f5e343024e6557eb3f6acb5cca'
assert sha('spider_state.py')=='598bfecd3353ef634dc34fbe425b8a95f528341fa9c06cf4615931ba0aa48e0c'
assert sha('sorter_native_player.py')=='1778fc9045394cc2ba35aadea07f72b3c89bce437a5b0bdbb2e387969629c546'

ui=(ROOT/'ui.py').read_text(encoding='utf-8')
start=ui.index('class ScrubSlider(QSlider):'); end=ui.index('class InstagramManagerPage(QWidget):')
assert hashlib.sha256(ui[start:end].encode('utf-8')).hexdigest()=='40cb8c0b90167341535239aaaac0bd22aa38813c1a149d54bfab17e9cc525e6a'
worker=ui[ui.index('class ThumbnailDecodeWorker(QThread):'):ui.index('class MosaicPageLoadWorker(QThread):')]
assert '_prepare_render_image' in worker
assert 'image.scaled(' in worker and 'SmoothTransformation' in worker
cache=ui[ui.index('    def cache_image(self, path: str, image: QImage'):ui.index('    def _pix(self, path)',ui.index('    def cache_image(self, path: str, image: QImage'))]
assert 'pix.scaled(' not in cache and 'QPixmap.fromImage(image)' in cache
paint_start=ui.index('    def paint(self, painter, option, index):',ui.index('class WebMosaicDelegate'))
paint_end=ui.index('        painter.restore()',paint_start)
paint=ui[paint_start:paint_end]
assert '.scaled(' not in paint
assert 'painter.drawPixmap(target,pix,pix.rect())' in paint
print('REGRESSION_TEST_3_25_0: Spider GUI hot path protected + off-thread scaling OK')
