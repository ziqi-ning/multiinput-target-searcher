from machine import I2C,Pin,PWM,Timer,UART
from math import ceil
import time, utime, sys
import random



# 音符频率表：从C0到B9，覆盖10个八度
TONES = {
    'C0':16, 'C#0':17, 'D0':18, 'D#0':19, 'E0':21, 'F0':22,
    'F#0':23, 'G0':24, 'G#0':26, 'A0':28, 'A#0':29, 'B0':31,
    'C1':33, 'C#1':35, 'D1':37, 'D#1':39, 'E1':41, 'F1':44,
    'F#1':46, 'G1':49, 'G#1':52, 'A1':55, 'A#1':58, 'B1':62,
    'C2':65, 'C#2':69, 'D2':73, 'D#2':78, 'E2':82, 'F2':87,
    'F#2':92, 'G2':98, 'G#2':104, 'A2':110, 'A#2':117, 'B2':123,
    'C3':131, 'C#3':139, 'D3':147, 'D#3':156, 'E3':165, 'F3':175,
    'F#3':185, 'G3':196, 'G#3':208, 'A3':220, 'A#3':233, 'B3':247,
    'C4':262, 'C#4':277, 'D4':294, 'D#4':311, 'E4':330, 'F4':349,
    'F#4':370, 'G4':392, 'G#4':415, 'A4':440, 'A#4':466, 'B4':494,
    'C5':523, 'C#5':554, 'D5':587, 'D#5':622, 'E5':659, 'F5':698,
    'F#5':740, 'G5':784, 'G#5':831, 'A5':880, 'A#5':932, 'B5':988,
    'C6':1047, 'C#6':1109, 'D6':1175, 'D#6':1245, 'E6':1319, 'F6':1397,
    'F#6':1480, 'G6':1568, 'G#6':1661, 'A6':1760, 'A#6':1865, 'B6':1976,
    'C7':2093, 'C#7':2217, 'D7':2349, 'D#7':2489, 'E7':2637, 'F7':2794,
    'F#7':2960, 'G7':3136, 'G#7':3322, 'A7':3520, 'A#7':3729, 'B7':3951,
    'C8':4186, 'C#8':4435, 'D8':4699, 'D#8':4978, 'E8':5274, 'F8':5588,
    'F#8':5920, 'G8':6272, 'G#8':6645, 'A8':7040, 'A#8':7459, 'B8':7902,
    'C9':8372, 'C#9':8870, 'D9':9397, 'D#9':9956, 'E9':10548, 'F9':11175,
    'F#9':11840, 'G9':12544, 'G#9':13290, 'A9':14080, 'A#9':14917, 'B9':15804
}
# 乐谱
happy_birthday = (  # 生日歌
    "0 G4 2 0; 0 G4 2 0; "
    "2 A4 4 0; 6 G4 4 0; "
    "10 C5 4 0; 14 B4 8 0; "
    "22 G4 8 0; 30 A4 4 0; "
    "34 G4 4 0; 38 D5 4 0; "
    "42 C5 8 0; 50 G4 8 0; "
    "58 G4 4 0; 62 E5 4 0; "
    "66 C5 4 0; 70 C5 4 0; "
    "74 B4 8 0; 82 A4 8 0; "
    "90 F5 4 0; 94 E5 4 0; "
    "98 C5 4 0; 102 D5 4 0; "
    "106 C5 12 0"
)
little_star = (  # 小星星
    "0 C4 2 0; 0 C4 2 0; "
    "2 G4 2 0; 2 G4 2 0; "
    "4 A4 2 0; 4 A4 2 0; "
    "6 G4 4 0; "
    "10 F4 2 0; 10 F4 2 0; "
    "12 E4 2 0; 12 E4 2 0; "
    "14 D4 2 0; 14 D4 2 0; "
    "16 C4 4 0; "
    "20 G4 2 0; 20 G4 2 0; "
    "22 F4 2 0; 22 F4 2 0; "
    "24 E4 2 0; 24 E4 2 0; "
    "26 D4 4 0; "
    "30 G4 2 0; 30 G4 2 0; "
    "32 F4 2 0; 32 F4 2 0; "
    "34 E4 2 0; 34 E4 2 0; "
    "36 D4 4 0; "
    "40 C4 2 0; 40 C4 2 0; "
    "42 G4 2 0; 42 G4 2 0; "
    "44 A4 2 0; 44 A4 2 0; "
    "46 G4 4 0; "
    "50 F4 2 0; 50 F4 2 0; "
    "52 E4 2 0; 52 E4 2 0; "
    "54 D4 2 0; 54 D4 2 0; "
    "56 C4 8 0"
)
ode_to_joy = (  # 欢乐颂
    "0 E4 2 0; 0 E4 2 0; "
    "2 F4 2 0; 2 G4 2 0; "
    "4 G4 2 0; 4 F4 2 0; "
    "6 E4 2 0; 6 D4 2 0; "
    "8 C4 2 0; 8 C4 2 0; "
    "10 D4 2 0; 10 E4 2 0; "
    "12 E4 3 0; 14 D4 1 0; "
    "16 D4 4 0; "
    "20 E4 2 0; 20 E4 2 0; "
    "22 F4 2 0; 22 G4 2 0; "
    "24 G4 2 0; 24 F4 2 0; "
    "26 E4 2 0; 26 D4 2 0; "
    "28 C4 2 0; 28 C4 2 0; "
    "30 D4 2 0; 30 E4 2 0; "
    "32 D4 3 0; 34 C4 1 0; "
    "36 C4 8 0"
)
jingle_bells = (  # 铃儿响叮当
    "0 E4 2 0; 0 E4 2 0; "
    "2 E4 4 0; "
    "6 E4 2 0; 6 E4 2 0; "
    "8 E4 4 0; "
    "12 E4 2 0; 12 G4 2 0; "
    "14 C4 2 0; 14 D4 2 0; "
    "16 E4 8 0; "
    "24 F4 2 0; 24 F4 2 0; "
    "26 F4 3 0; 28 F4 1 0; "
    "30 F4 2 0; 30 E4 2 0; "
    "32 E4 2 0; 32 E4 2 0; "
    "34 E4 2 0; 34 D4 2 0; "
    "36 D4 2 0; 36 E4 2 0; "
    "38 D4 4 0; 42 G4 4 0; "
    "46 E4 2 0; 46 E4 2 0; "
    "48 E4 4 0; "
    "52 E4 2 0; 52 E4 2 0; "
    "54 E4 4 0; "
    "58 E4 2 0; 58 G4 2 0; "
    "60 C4 2 0; 60 D4 2 0; "
    "62 E4 8 0; "
    "70 F4 2 0; 70 F4 2 0; "
    "72 F4 3 0; 74 F4 1 0; "
    "76 F4 2 0; 76 E4 2 0; "
    "78 E4 2 0; 78 E4 2 0; "
    "80 G4 2 0; 80 G4 2 0; "
    "82 F4 2 0; 82 D4 2 0; "
    "84 C4 12 0"
)
mary_lamb = (  # 玛丽有只小羊羔
    "0 E4 2 0; 0 D4 2 0; "
    "2 C4 2 0; 2 D4 2 0; "
    "4 E4 2 0; 4 E4 2 0; "
    "6 E4 4 0; "
    "10 D4 2 0; 10 D4 2 0; "
    "12 D4 4 0; "
    "16 E4 2 0; 16 G4 2 0; "
    "18 G4 4 0; "
    "22 E4 2 0; 22 D4 2 0; "
    "24 C4 2 0; 24 D4 2 0; "
    "26 E4 2 0; 26 E4 2 0; "
    "28 E4 2 0; 28 E4 2 0; "
    "30 D4 2 0; 30 D4 2 0; "
    "32 E4 2 0; 32 D4 2 0; "
    "34 C4 8 0"
)
super_mario = (  # 超级玛丽主题曲
    "0 E5 1 0; 1 E5 1 0; "
    "2 0 1 0; "  # 休止符
    "3 E5 1 0; 4 0 1 0; "
    "5 C5 1 0; 6 E5 1 0; "
    "7 G5 2 0; "
    "9 0 2 0; "
    "11 G4 2 0; "
    "13 0 2 0; "
    "15 C5 2 0; "
    "17 0 1 0; "
    "18 G4 1 0; 19 0 1 0; "
    "20 E4 2 0; "
    "22 0 1 0; "
    "23 A4 1 0; 24 B4 1 0; "
    "25 A#4 1 0; 26 A4 1 0; "
    "27 G4 1 0; 28 E5 1 0; "
    "29 G5 1 0; 30 A5 1 0; "
    "31 F5 1 0; 32 G5 1 0; "
    "33 0 1 0; "
    "34 E5 1 0; 35 C5 1 0; "
    "36 D5 1 0; 37 B4 1 0; "
    "38 0 2 0"
)
chord_progression = (  # 和弦
    "0 C4 4 0; 0 E4 4 0; 0 G4 4 0; "  # C
    "4 F4 4 0; 4 A4 4 0; 4 C5 4 0; "  # F
    "8 G4 4 0; 8 B4 4 0; 8 D5 4 0; "  # G
    "12 C4 4 0; 12 E4 4 0; 12 G4 4 0; "  # C
    "16 A3 4 0; 16 C4 4 0; 16 E4 4 0; "  # Am
    "20 D3 4 0; 20 F3 4 0; 20 A3 4 0; "  # Dm
    "24 E3 4 0; 24 G3 4 0; 24 B3 4 0; "  # Em
    "28 C4 4 0; 28 E4 4 0; 28 G4 8 0"  # C
)
# 用于查询是否存在歌曲
class StringMatcher:
    def __init__(self, string_list):
        self._candidate_list = string_list
        self._query = None
        self.match_result = False

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value
        self.match_result = value in self._candidate_list
        
class MusicPlayer:
    def __init__(self, song_string=happy_birthday, looping=True, tempo=3, 
                 volume=0.5, pins=None, auto_play=False, tick_ms=10):
        """
        song_string: 乐谱字符串，格式：'时间 音符 时长 乐器;...'
        looping: 是否循环播放
        tempo: 节拍速度，值越大越慢
        volume: 音量大小百分比(0~1)，volume=duty/65535，其中duty为PWM占空比(0~65535)
        pins: 输出引脚列表
        auto_play: 是否自动开始播放
        tick_ms: 自动播放时的时间间隔(ms)
        """
        self.tempo = max(1, tempo)
        self.song_string = song_string
        self.looping = looping
        volume = max(0, min(1, volume))
        duty = int(65535 * volume)
        self.duty = min(65535, max(0, duty))
        self.tick_ms = tick_ms
        self.is_playing = False
        self.is_stopped = False
        self.timer = -1
        self.beat = -1
        self.arp_index = 0
        if pins is None:
            pins = [Pin(0)]
        self.pwms = []
        for pin in pins:
            pwm = PWM(pin)
            pwm.duty_u16(0)
            self.pwms.append(pwm)
        self.notes_by_beat = []
        self.active_notes = []
        self.note_durations = []
        self._parse_song()
        self.play_timer = None
        if auto_play:
            self.play()
    def _parse_song(self):
#         song_list = StringMatcher(['apple', 'banana', 'cherry'])
#         song_list.query = 'banana'
        note_sequence = self.song_string.split(";")
        max_end = 0
        for note_str in note_sequence:
            if not note_str.strip():
                continue
            parts = note_str.strip().split()
            if len(parts) < 3:
                continue
            start_beat = round(float(parts[0]))
            duration = ceil(float(parts[2]))
            end_beat = start_beat + duration
            if end_beat > max_end:
                max_end = end_beat
        self.song_length = ceil(max_end / 8) * 8
        self.notes_by_beat = [None] * self.song_length
        for note_str in note_sequence:
            if not note_str.strip():
                continue
            parts = note_str.strip().split()
            if len(parts) < 3:
                continue
            beat = round(float(parts[0]))
            note_name = parts[1]
            duration = ceil(float(parts[2]))
            if self.notes_by_beat[beat] is None:
                self.notes_by_beat[beat] = []
            self.notes_by_beat[beat].append({
                'note': note_name,
                'duration': duration,
                'remaining': duration
            })
    def _on_beat(self):
        self.beat += 1
        if self.beat >= self.song_length:
            if self.looping:
                self.beat = 0
                self._clear_active_notes()
            else:
                self.stop()
                return
        self._update_durations()
        self._add_new_notes()
        self._play_current_notes()
    def _update_durations(self):
        i = 0
        while i < len(self.note_durations):
            self.note_durations[i] -= 1
            
            if self.note_durations[i] <= 0:
                self.active_notes.pop(i)
                self.note_durations.pop(i)
            else:
                i += 1
    def _add_new_notes(self):
        if self.beat < len(self.notes_by_beat) and self.notes_by_beat[self.beat] is not None:
            for note_info in self.notes_by_beat[self.beat]:
                self.active_notes.append(note_info['note'])
                self.note_durations.append(note_info['duration'])
    def _play_current_notes(self):
        pwm_count = len(self.pwms)
        note_count = len(self.active_notes)
        for i in range(pwm_count):
            if i < note_count:
                note = self.active_notes[i]
                self.pwms[i].duty_u16(self.duty)
                self.pwms[i].freq(TONES.get(note, 440))
            else:
                self.pwms[i].duty_u16(0)
        if note_count > pwm_count:
            self._play_arpeggio()
    def _play_arpeggio(self):
        last_pwm = self.pwms[-1]
        pwm_count = len(self.pwms)
        note_count = len(self.active_notes)
        if self.arp_index >= note_count - (pwm_count - 1):
            self.arp_index = 0
        note_index = self.arp_index + (pwm_count - 1)
        if note_index < note_count:
            note = self.active_notes[note_index]
            last_pwm.duty_u16(self.duty)
            last_pwm.freq(TONES.get(note, 440))
        self.arp_index += 1
    def _clear_active_notes(self):
        self.active_notes.clear()
        self.note_durations.clear()
        self.arp_index = 0
        for pwm in self.pwms:
            pwm.duty_u16(0)
            
    # Programmable
    def tick(self):  # 手动推进播放一帧 - 返回:(bool)是否还在播放
        if self.is_stopped:
            return False
        self.timer += 1
        if self.timer % self.tempo == 0:
            self._on_beat()
        return True
    def play(self):  # 开始自动播放
        if self.is_playing:
            return
        self.is_playing = True
        self.is_stopped = False
        self.play_timer = Timer(-1)
        self.play_timer.init(
            period=self.tick_ms,
            mode=Timer.PERIODIC,
            callback=lambda t: self.tick()
        )
    def pause(self):  # 暂停播放
        self.is_playing = False
        if self.play_timer:
            self.play_timer.deinit()
            self.play_timer = None
        for pwm in self.pwms:
            pwm.duty_u16(0)
    def resume(self):  # 恢复播放
        if not self.is_playing and not self.is_stopped:
            self.play()
    def stop(self):  # 停止播放并释放资源
        self.is_playing = False
        self.is_stopped = True
        if self.play_timer:
            self.play_timer.deinit()
            self.play_timer = None
        for pwm in self.pwms:
            pwm.duty_u16(0)
            pwm.deinit()
    def set_tempo(self, tempo):  # 设置播放速度
        self.tempo = max(1, tempo)
    def set_volume(self, volume):  # 设置音量 (0-1)
        if 0 <= volume <= 100:
            self.duty = int(volume / 100 * 65535)
    def is_playing(self):  # 是否正在播放
        return self.is_playing and not self.is_stopped
