from pathlib import Path
p=Path('ui.py')
s=p.read_text(encoding='utf-8')
def once(old,new):
    global s
    if s.count(old)!=1: raise RuntimeError('anchor mismatch: '+old[:80])
    s=s.replace(old,new,1)
once("prefs=load_settings();self._saved_volume=max(0,min(100,int(prefs.get('sorter_volume',65) or 65)));self._saved_speed=float(prefs.get('sorter_speed',1.0) or 1.0)","prefs=load_settings();self._saved_volume=max(0,min(100,int(prefs.get('sorter_volume',65) or 65)));self._saved_speed=float(prefs.get('sorter_speed',1.0) or 1.0);self._muted=bool(prefs.get('sorter_muted',False));self._scrub_started_at=0.0")
once("self.player=self._players[0];self.audio=self._audios[0];self.player.setVideoOutput(self.video);self.audio.setVolume(0.65)","self.player=self._players[0];self.audio=self._audios[0];self.player.setVideoOutput(self.video);self.audio.setVolume(0.0 if self._muted else self._saved_volume/100.0)")
once("self.volume=QSlider(Qt.Orientation.Horizontal);self.volume.setRange(0,100);self.volume.setValue(self._saved_volume);self.volume.setFixedWidth(115);self.volume.setToolTip('Громкость');self.volume.valueChanged.connect(self._apply_volume);transport.addWidget(self.volume)\n        self.autoplay=QCheckBox('Автозапуск')","self.volume=QSlider(Qt.Orientation.Horizontal);self.volume.setRange(0,100);self.volume.setValue(self._saved_volume);self.volume.setFixedWidth(115);self.volume.setToolTip('Громкость');self.volume.valueChanged.connect(self._apply_volume);transport.addWidget(self.volume)\n        self.mute_btn=QPushButton('🔇' if self._muted else '🔊');self.mute_btn.setFixedWidth(42);self.mute_btn.setToolTip('M — выключить/включить звук');self.mute_btn.clicked.connect(self.toggle_mute);transport.addWidget(self.mute_btn)\n        self.autoplay=QCheckBox('Автозапуск')")
once("self.video_controls=[self.back5,self.play,self.fwd5,self.seek,self.time_label,self.seek_status,self.speed,self.volume_label,self.volume,self.autoplay]","self.video_controls=[self.back5,self.play,self.fwd5,self.seek,self.time_label,self.seek_status,self.speed,self.volume_label,self.volume,self.mute_btn,self.autoplay]")
once("shortcut('Shift+J',lambda:self.seek_relative(-60000)),shortcut('Shift+L',lambda:self.seek_relative(60000)),\n            shortcut('F',self._toggle_current_favorite)","shortcut('Shift+J',lambda:self.seek_relative(-60000)),shortcut('Shift+L',lambda:self.seek_relative(60000)),shortcut('M',self.toggle_mute),\n            shortcut('F',self._toggle_current_favorite)")
once("    def _apply_volume(self,value):\n        vol=max(0,min(100,int(value)))/100.0\n        if self.audio:\n            try:self.audio.setVolume(vol)\n            except Exception:pass\n        if self._native_active:self._native_send({'cmd':'volume','value':vol})\n        self._prefs_timer.start()\n\n    def _save_player_prefs(self):\n        try:save_settings({'sorter_volume':int(self.volume.value()),'sorter_speed':float(self.speed.currentData() or 1.0)})\n        except Exception:pass\n","    def _output_volume(self)->float:\n        return 0.0 if self._muted else max(0,min(100,int(self.volume.value())))/100.0\n\n    def _apply_volume(self,value):\n        vol=self._output_volume()\n        if self.audio:\n            try:self.audio.setVolume(vol)\n            except Exception:pass\n        if self._native_active:self._native_send({'cmd':'volume','value':vol})\n        self._prefs_timer.start()\n\n    def toggle_mute(self):\n        self._muted=not bool(self._muted);vol=self._output_volume()\n        if self.audio:\n            try:self.audio.setVolume(vol)\n            except Exception:pass\n        if self._native_active:self._native_send({'cmd':'volume','value':vol})\n        if hasattr(self,'mute_btn'):\n            self.mute_btn.setText('🔇' if self._muted else '🔊')\n            self.mute_btn.setToolTip(('Звук выключен' if self._muted else 'Звук включён')+' · M — переключить')\n        self._prefs_timer.start()\n\n    def _save_player_prefs(self):\n        try:save_settings({'sorter_volume':int(self.volume.value()),'sorter_speed':float(self.speed.currentData() or 1.0),'sorter_muted':bool(self._muted)})\n        except Exception:pass\n")
once("    def _seek_started(self):\n        self._seek_dragging=True;self._capture_current_frame_signature()","    def _seek_started(self):\n        self._seek_dragging=True;self._scrub_started_at=time.monotonic();self._capture_current_frame_signature()")
start=s.index('    def _seek_live(self,value:int):',s.index('class SorterProPage'))
end=s.index('    def seek_relative',start)
s=s[:start]+"""    def _seek_live(self,value:int):
        self._seek_dragging=True
        if not self.player or not self._video_is_visible():return
        dur=self._current_duration_ms();target=max(0,min(dur,int(value))) if dur>0 else max(0,int(value));self._pending_seek_target=target
        # v3.27: dragging is UI-only; one deterministic backend seek happens on release.
        self.time_label.setText(f'{self._fmt_ms(target)} / {self._fmt_ms(dur)}')

    def _seek_finished(self,value:int):
        self._seek_dragging=False;drag_ms=max(0,int((time.monotonic()-float(self._scrub_started_at or time.monotonic()))*1000));self._seek_trace('scrub_finished',target=int(value),logical=self._current_position_ms(),frame=int(getattr(self,'_video_frame_timeline_ms',-1)),drag_ms=drag_ms);self._request_video_seek(int(value),allow_repair=True)

"""+s[end:]
s=s.replace("try:self.audio.setVolume(self.volume.value()/100.0)","try:self.audio.setVolume(self._output_volume())")
s=s.replace("try:audio.setVolume(self.volume.value()/100.0)","try:audio.setVolume(self._output_volume())")
s=s.replace("'volume':self.volume.value()/100.0","'volume':self._output_volume()")
p.write_text(s,encoding='utf-8')
