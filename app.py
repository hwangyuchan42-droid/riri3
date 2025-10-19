import os, sys, re, math, random, pygame, time
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
SONG_DIR = os.path.join(BASE, 'songs')
SFX_DIR = os.path.join(BASE, 'sfx')
for d in (SONG_DIR, SFX_DIR):
    if not os.path.exists(d):
        os.makedirs(d)
def resource_path(relative_path):
    # exe로 빌드된 경우(sys._MEIPASS 존재), 아니면 현재 폴더 기준
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

MUSIC_FILENAME = "밤을 달리다.ogg"
MUSIC_PATH = resource_path(MUSIC_FILENAME)


pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("Audio init failed:", e)

WIDTH, HEIGHT = 720, 1280
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyRhythm - 밤을 달리다 ✨")
clock = pygame.time.Clock()

font_paths = [
    "C:/Windows/Fonts/malgun.ttf",
    "C:/Windows/Fonts/gulim.ttf",
    "/Library/Fonts/AppleGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
]
FONT_PATH = None
for p in font_paths:
    if os.path.exists(p):
        FONT_PATH = p
        break
if FONT_PATH:
    def make_font(sz): return pygame.font.Font(FONT_PATH, sz)
else:
    def make_font(sz): return pygame.font.SysFont("Arial", sz)

WHITE = (255,255,255)
LIGHT = (230,230,230)
GRAY = (28,28,28)
ACCENT = (70,160,240)
GREEN = (80,200,120)
RED = (220,80,80)
YELLOW = (240,220,70)
BLACK = (0,0,0)
PURPLE = (180,100,255)
CYAN = (100,220,255)
PINK = (255,100,180)

DIFFICULTIES = {
    '1': {'name':'쉬움','lanes':3,'hit_window':0.20,'speed':800},
    '2': {'name':'보통','lanes':4,'hit_window':0.12,'speed':1000},
    '3': {'name':'어려움','lanes':6,'hit_window':0.07,'speed':1200}
}

def try_load(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

perfect_sfx = try_load(os.path.join(SFX_DIR, 'perfect.ogg'))
great_sfx = try_load(os.path.join(SFX_DIR, 'great.ogg'))
miss_sfx = try_load(os.path.join(SFX_DIR, 'miss.ogg'))

def make_tone(freq=440.0, dur=0.12, vol=0.7):
    sr = 44100
    t = np.linspace(0, dur, int(sr*dur), endpoint=False)
    w = (np.sin(2*np.pi*freq*t) * 32767 * vol).astype(np.int16)
    stereo = np.column_stack((w,w)).copy()
    return pygame.sndarray.make_sound(stereo)

if perfect_sfx is None: perfect_sfx = make_tone(1200.0, 0.12, 0.7)
if great_sfx is None:   great_sfx = make_tone(880.0, 0.12, 0.7)
if miss_sfx is None:    miss_sfx = make_tone(300.0, 0.10, 0.8)

NOTE_TIMINGS = [
   1.080,
1.270,
1.481,
1.794,
2.105,
2.297,
2.527,
2.769,
2.995,
3.266,
3.475,
3.655,
3.893,
4.244,
4.735,
4.884,
5.113,
5.477,
5.819,
6.047,
6.237,
6.465,
6.663,
6.931,
7.278,
7.659,
7.890,
8.102,
8.311,
8.567,
8.789,
9.138,
9.475,
9.688,
9.895,
10.097,
10.322,
10.561,
10.773,
11.000,
11.235,
11.723,
11.962,
12.215,
12.724,
12.959,
13.233,
13.841,
14.283,
14.489,
14.677,
14.864,
15.212,
15.538,
15.798,
15.968,
16.093,
16.259,
16.384,
16.590,
16.804,
17.049,
17.275,
17.504,
17.694,
18.020,
18.244,
18.549,
18.836,
19.063,
19.295,
19.546,
19.817,
19.969,
20.194,
20.500,
20.747,
20.983,
21.214,
21.447,
21.656,
21.882,
22.023,
22.329,
22.614,
22.862,
23.088,
23.229,
23.395,
23.522,
23.648,
23.933,
24.200,
24.486,
24.652,
24.878,
25.052,
25.198,
25.344,
25.492,
25.697,
26.001,
26.288,
26.513,
26.772,
27.003,
27.214,
27.320,
27.472,
27.996,
28.204,
28.401,
28.606,
28.884,
29.294,
29.479,
29.607,
29.752,
30.139,
30.345,
30.517,
30.843,
31.096,
31.308,
31.615,
32.041,
32.246,
32.540,
32.966,
33.493,
33.699,
33.917,
34.143,
34.382,
34.588,
34.834,
35.040,
35.263,
35.513,
35.742,
36.207,
36.635,
37.121,
37.341,
37.575,
37.782,
37.988,
38.256,
38.447,
38.754,
38.920,
39.185,
39.552,
39.916,
40.160,
40.312,
40.499,
40.728,
41.034,
41.520,
41.707,
41.953,
42.179,
42.425,
42.657,
43.305,
43.607,
44.033,
44.258,
44.814,
45.100,
45.447,
45.644,
45.910,
46.116,
46.355,
46.765,
47.002,
47.251,
47.698,
48.185,
48.420,
48.651,
48.860,
49.107,
49.341,
49.552,
49.798,
50.004,
50.220,
50.426,
50.639,
50.965,
51.385,
51.858,
52.058,
52.304,
52.519,
52.775,
53.044,
53.236,
53.463,
53.700,
53.947,
54.297,
54.683,
54.849,
55.055,
55.232,
55.377,
55.764,
56.189,
56.435,
56.681,
56.927,
57.172,
57.419,
57.833,
58.039,
58.353,
58.818,
59.005,
59.510,
59.895,
60.084,
60.270,
60.476,
60.653,
60.800,
61.005,
61.183,
61.510,
61.668,
61.813,
61.980,
62.164,
62.390,
62.592,
62.738,
62.924,
63.332,
63.490,
63.616,
63.762,
63.908,
64.073,
64.360,
64.485,
64.651,
64.778,
64.929,
65.275,
65.426,
65.572,
65.738,
65.883,
66.210,
66.676,
66.882,
67.090,
67.315,
67.470,
67.616,
67.885,
68.211,
68.413,
68.660,
69.145,
69.410,
69.637,
69.866,
70.100,
70.346,
70.812,
71.030,
71.258,
71.483,
71.722,
71.955,
72.244,
72.420,
72.706,
72.911,
73.122,
73.368,
74.502,
74.709,
75.159,
75.525,
75.841,
76.168,
76.349,
76.635,
76.781,
77.047,
77.215,
77.342,
77.610,
77.936,
78.352,
78.587,
78.838,
79.050,
79.300,
79.547,
79.753,
79.990,
80.220,
80.486,
80.712,
80.912,
81.338,
81.631,
82.118,
82.282,
82.508,
82.868,
83.242,
83.438,
83.644,
83.903,
84.093,
84.379,
84.565,
84.731,
84.896,
85.262,
85.716,
85.980,
86.228,
86.499,
86.686,
86.932,
87.130,
87.356,
87.814,
88.021,
88.707,
88.993,
89.178,
89.384,
89.632,
89.905,
90.194,
90.581,
90.787,
91.066,
91.237,
91.483,
91.757,
92.003,
92.130,
92.375,
92.642,
93.129,
93.354,
93.814,
94.040,
94.279,
94.492,
94.758,
94.923,
95.208,
95.433,
95.652,
96.041,
96.398,
96.825,
97.032,
97.264,
97.630,
97.955,
98.163,
98.390,
98.614,
98.828,
99.034,
99.250,
99.437,
99.845,
100.271,
100.497,
101.204,
101.411,
101.638,
101.876,
102.067,
102.273,
102.493,
102.699,
103.075,
103.290,
103.537,
103.761,
103.961,
104.188,
104.360,
104.504,
104.672,
104.818,
105.064,
105.349,
105.615,
105.862,
106.088,
106.293,
106.458,
106.764,
106.954,
107.239,
107.485,
107.671,
108.117,
108.344,
108.601,
108.755,
109.019,
109.304,
109.753,
109.901,
110.046,
110.210,
110.336,
110.563,
110.821,
111.110,
111.336,
111.571,
111.780,
111.926,
112.073,
112.240,
112.485,
112.771,
112.999,
113.214,
113.463,
113.669,
113.815,
113.961,
114.245,
114.531,
114.777,
115.045,
115.232,
115.499,
116.008,
116.166,
116.312,
116.476,
116.803,
116.979,
117.102,
117.549,
117.849,
118.055,
118.268,
118.773,
118.979,
119.210,
119.678,
120.103,
120.331,
120.575,
120.785,
121.020,
121.266,
121.491,
121.707,
121.935,
122.203,
122.389,
122.620,
122.885,
123.293,
123.998,
124.238,
124.448,
124.695,
124.951,
125.161,
125.412,
125.645,
125.890,
126.218,
126.793,
126.959,
127.148,
127.293,
127.680,
128.126,
128.321,
128.589,
128.815,
129.054,
129.347,
129.792,
129.973,
130.121,
131.887,
132.093,
132.347,
132.516,
132.682,
132.828,
132.994,
133.180,
133.307,
133.475,
133.643,
133.808,
133.956,
134.140,
134.309,
134.454,
134.620,
134.927,
135.133,
135.550,
135.737,
135.962,
136.124,
136.252,
136.639,
136.804,
137.130,
137.316,
137.462,
137.648,
137.794,
137.961,
138.127,
138.292,
138.460,
138.667,
138.842,
139.249,
139.394,
139.561,
140.025,
140.184,
140.330,
140.477,
140.923,
141.086,
141.231,
141.397,
141.523,
141.869,
142.025,
142.152,
142.339,
142.528,
142.714,
142.920,
143.148,
143.414,
143.880,
144.065,
144.310,
144.537,
144.763,
145.012,
145.325,
145.573,
145.800,
145.968,
146.134,
146.361,
146.610,
146.758,
146.903,
147.091,
147.316,
147.502,
147.767,
147.914,
148.181,
148.329,
148.554,
148.707,
148.872,
149.018,
149.204,
149.474,
149.643,
149.930,
150.116,
150.302,
150.487,
150.634,
150.819,
151.002,
151.289,
151.436,
151.623,
151.850,
152.015,
152.241,
152.408,
152.555,
152.721,
153.026,
153.272,
153.688,
153.834,
154.058,
154.228,
154.394,
154.581,
154.812,
155.138,
155.301,
155.540,
155.711,
155.959,
156.114,
156.301,
156.486,
156.632,
156.979,
157.126,
157.412,
157.579,
157.748,
157.935,
158.060,
158.528,
158.713,
158.959,
159.105,
159.333,
159.533,
160.259,
160.493,
160.703,
160.949,
161.183,
161.394,
161.564,
161.747,
162.033,
162.280,
162.508,
162.982,
163.220,
163.448,
163.635,
163.960,
164.146,
164.333,
164.539,
164.806,
165.011,
165.191,
165.417,
165.648,
165.839,
166.104,
166.431,
166.692,
166.927,
167.112,
167.380,
167.566,
167.751,
168.017,
168.204,
168.415,
168.642,
168.902,
169.174,
169.439,
169.648,
169.877,
170.166,
170.395,
170.626,
170.853,
171.080,
171.454,
171.629,
171.897,
172.144,
172.369,
172.688,
174.215,
174.381,
174.565,
174.813,
174.960,
175.086,
175.312,
175.482,
175.829,
175.992,
176.138,
176.285,
176.410,
176.634,
176.805,
176.931,
177.139,
177.315,
177.661,
177.819,
177.946,
178.071,
178.397,
178.819,
178.966,
179.113,
179.281,
179.608,
179.782,
179.908,
180.054,
180.180,
180.466,
181.012,
181.197,
181.402,
181.621,
181.886,
182.113,
182.371,
182.600,
182.793,
182.938,
183.304,
183.447,
183.811,
183.946,
184.093,
184.277,
184.445,
184.590,
184.775,
185.162,
185.335,
185.541,
186.052,
186.454,
186.639,
186.967,
187.186,
187.392,
187.588,
188.254,
188.938,
190.588,
190.816,
191.024,
191.291,
192.197,
193.143,
194.108,
195.073,
195.603,
195.987,
196.413,
196.858,
197.287,
197.773,
198.259,
198.694,
199.460,
199.705,
200.133,
200.518,
200.926,
201.431,
201.917,
202.365,
202.632,
202.897,
203.084,
203.313,
203.558,
203.794,
204.001,
204.249,
204.435,
204.622,
204.786,
204.953,
205.098,
205.224,
205.369,
205.496,
205.631,
205.757,
205.883,
206.008,
206.116,
206.415,
206.541,
206.647,
206.861,
207.009,
207.114,
207.279,
207.362,
207.508,
207.652,
207.838,
208.044,
208.240,
208.587,
208.855,
209.061,
209.254,
209.501,
209.787,
210.132,
210.314,
210.479,
210.786,
211.192,
211.399,
211.686,
211.871,
212.078,
212.294,
212.520,
212.773,
212.961,
213.186,
213.422,
213.631,
213.795,
213.981,
214.107,
214.433,
214.845,
215.071,
215.318,
215.687,
216.242,
216.449,
216.684,
216.893,
217.159,
217.364,
217.530,
217.736,
218.015,
218.480,
218.727,
218.997,
219.226,
219.459,
219.690,
219.935,
220.152,
220.384,
220.594,
220.838,
221.556,
221.755,
221.982,
222.221,
222.449,
222.654,
222.988,
223.334,
223.625,
223.833,
224.058,
224.308,
224.575,
224.741,
224.926,
225.171,
225.497,
225.952,
226.159,
226.390,
226.620,
226.826,
227.064,
227.295,
227.522,
227.742,
227.969,
228.217,
228.410,
228.557,
228.741,
229.088,
229.550,
229.798,
230.043,
230.393,
230.753,
230.989,
231.199,
231.445,
231.665,
231.895,
232.124,
232.350,
232.549,
232.994,
233.241,
233.468,
233.946,
234.186,
234.401,
234.607,
234.805,
235.052,
235.339,
236.424,
236.613,
236.858,
237.065,
237.257,
237.483,
237.682,
237.889,
238.120,
238.369,
238.614,
238.831,
239.944,
240.133,
240.378,
240.604,
240.838,
241.069,
241.316,
241.542,
241.743,
241.929,
242.270,
242.479,
242.693,
242.999,
243.146,
243.371,
243.633,
243.902,
244.109,
244.344,
244.623,
244.751,
244.894,
245.040,
245.286,
245.531,
245.758,
245.976,
246.245,
246.418,
246.665,
246.850,
247.037,
247.363,
247.605,
247.835,
248.041,
248.257,
248.503,
248.730,
248.887,
249.153,
249.441,
249.666,
249.911,
250.197,
250.342,
250.468,
250.735,
251.001,
251.267,
251.474,
251.910,
252.076,
252.222,
252.411,
252.738,
253.045,
253.291,
253.549,
253.755,
253.952,
254.100,
254.325,
254.639,
254.927,
255.153,
255.386,
255.597,
256.063,
256.234,
256.399,
256.546,
256.731,
256.963,
257.450,
]
random.seed(42)

def generate_pattern_deterministic(timing, num_lanes, difficulty):
    """
    타이밍 값을 기반으로 결정적 패턴 생성
    복잡한 수학 공식을 사용하여 난이도별로 다른 패턴 생성
    """
    # 타이밍을 정수와 소수 부분으로 분리
    int_part = int(timing * 1000)
    frac_part = (timing * 1000) - int_part
    
    if difficulty == 1:  # 쉬움 - 단순 사인파 기반
        # 사인파와 타이밍의 제곱근을 조합
        base = math.sin(timing * 2.71828) * math.sqrt(timing + 1)
        prime_factor = (int_part % 7) * 0.31415
        complex_hash = (base + prime_factor + frac_part * 3.14159) * 100
        
        lane = int(abs(complex_hash)) % num_lanes
        return [lane]
    
    elif difficulty == 2:  # 보통 - 다항식과 삼각함수 조합
        # 복잡한 다항식 해시 함수
        poly = (timing**3 * 0.123 + timing**2 * 4.567 + timing * 8.910)
        trig = math.sin(timing * 1.618) * math.cos(timing * 2.718)
        prime_mix = ((int_part % 13) * 0.769 + (int_part % 17) * 0.541)
        
        hash_val = (poly + trig * 50 + prime_mix + frac_part * 11.11) * 1000
        
        # 노트 개수 결정 (1개 또는 2개)
        note_count = 1 if int(abs(hash_val)) % 3 == 0 else 2
        
        if note_count == 1:
            lane = int(abs(hash_val)) % num_lanes
            return [lane]
        else:
            # 두 개의 독립적인 해시로 레인 선택
            hash1 = int(abs(hash_val)) % num_lanes
            hash2 = int(abs(hash_val * 1.414 + timing * 3.333)) % num_lanes
            
            # 같은 레인이면 인접 레인으로 조정
            if hash1 == hash2:
                hash2 = (hash1 + 1) % num_lanes
            
            return sorted([hash1, hash2])
    
    else:  # 어려움 - 고차 함수와 복잡한 변환
        # 매우 복잡한 해시 함수
        exp_term = math.exp(timing * 0.01) * 0.1
        log_term = math.log(timing + 1) * 2.5
        sin_series = sum(math.sin(timing * (i + 1) * 0.618) for i in range(5))
        cos_series = sum(math.cos(timing * (i + 1) * 1.414) for i in range(3))
        
        # 소수를 이용한 복잡한 해싱
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        prime_hash = sum((int_part % p) * (p / 10.0) for p in primes)
        
        # 최종 해시 값
        mega_hash = (exp_term + log_term + sin_series + cos_series + 
                     prime_hash + frac_part * 31.4159 + timing**2 * 0.0123)
        
        # 노트 개수 결정 (1~4개)
        count_hash = int(abs(mega_hash * 1000))
        weights = [3, 4, 5, 2]  # 1개(3), 2개(4), 3개(5), 4개(2) 가중치
        note_count = 1 + (count_hash % sum(weights))
        
        if note_count <= 3:
            note_count = 1
        elif note_count <= 7:
            note_count = 2
        elif note_count <= 12:
            note_count = 3
        else:
            note_count = 4
        
        # 각 노트의 레인을 독립적인 해시로 결정
        lanes = []
        for i in range(note_count):
            hash_seed = mega_hash + i * 7.777 + timing * (i + 1) * 1.234
            sin_mod = math.sin(hash_seed + i * 2.345) * 100
            cos_mod = math.cos(hash_seed * 1.111 + i * 3.456) * 100
            
            lane_hash = int(abs(hash_seed * 1000 + sin_mod + cos_mod))
            lane = lane_hash % num_lanes
            
            # 중복 체크 및 조정
            attempts = 0
            while lane in lanes and attempts < num_lanes:
                lane = (lane + 1) % num_lanes
                attempts += 1
            
            if lane not in lanes:
                lanes.append(lane)
        
        return sorted(lanes)

def create_chart_from_timings(timings, num_lanes, difficulty):
    """결정적 패턴으로 차트 생성"""
    notes = []
    
    for timing in timings:
        pattern = generate_pattern_deterministic(timing, num_lanes, difficulty)
        for lane in pattern:
            notes.append({'time': timing, 'lane': lane, 'hold': 0.0})
    
    return sorted(notes, key=lambda x: (x['time'], x['lane']))

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.color, self.size = color, size
        self.lifetime, self.age = lifetime, 0.0
    
    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 300 * dt
    
    def draw(self, surf):
        alpha = max(0, int(255 * (1 - self.age / self.lifetime)))
        if alpha <= 0: return
        s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
        pygame.draw.circle(s, self.color + (alpha,), (int(self.size), int(self.size)), int(self.size))
        surf.blit(s, (int(self.x - self.size), int(self.y - self.size)))
    
    def is_dead(self):
        return self.age >= self.lifetime

class Shockwave:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.age = 0.0
        self.lifetime = 0.5
    
    def update(self, dt):
        self.age += dt
    
    def draw(self, surf):
        alpha = int(200 * (1 - self.age / self.lifetime))
        if alpha <= 0: return
        r = int(20 + (self.age / self.lifetime) * 100)
        pygame.draw.circle(surf, self.color + (alpha,), (int(self.x), int(self.y)), r, 3)
    
    def is_dead(self):
        return self.age >= self.lifetime

particles = []
shockwaves = []

def spawn_particles(x, y, count, color, size_range=(3,8)):
    for _ in range(count):
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(100, 300)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 200
        size = random.uniform(*size_range)
        lifetime = random.uniform(0.4, 0.8)
        particles.append(Particle(x, y, vx, vy, color, size, lifetime))

def spawn_shockwave(x, y, color):
    shockwaves.append(Shockwave(x, y, color))

def update_particles(dt):
    for p in particles[:]:
        p.update(dt)
        if p.is_dead():
            particles.remove(p)

def update_shockwaves(dt):
    for s in shockwaves[:]:
        s.update(dt)
        if s.is_dead():
            shockwaves.remove(s)

def draw_particles(surf):
    for p in particles:
        p.draw(surf)

def draw_shockwaves(surf):
    for s in shockwaves:
        s.draw(surf)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(20, 100)
        self.size = random.uniform(1, 3)
        self.brightness = random.randint(100, 255)
    
    def update(self, dt):
        self.y += self.speed * dt
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), int(self.size))

stars = [Star() for _ in range(80)]

class LanePressEffect:
    def __init__(self, lane_idx, x, lane_w):
        self.lane = lane_idx
        self.x = x
        self.lane_w = lane_w
        self.age = 0.0
        self.lifetime = 0.3
    
    def update(self, dt):
        self.age += dt
    
    def draw(self, surf):
        alpha = int(180 * (1 - self.age / self.lifetime))
        if alpha <= 0: return
        s = pygame.Surface((int(self.lane_w), 150), pygame.SRCALPHA)
        color = CYAN + (alpha,)
        pygame.draw.rect(s, color, (0, 0, int(self.lane_w), 150))
        surf.blit(s, (int(self.x - self.lane_w/2), JUDGE_LINE_Y - 75))
    
    def is_dead(self):
        return self.age >= self.lifetime

lane_press_effects = []

def spawn_lane_press(lane_idx, x, lane_w):
    lane_press_effects.append(LanePressEffect(lane_idx, x, lane_w))

def update_lane_press_effects(dt):
    for eff in lane_press_effects[:]:
        eff.update(dt)
        if eff.is_dead():
            lane_press_effects.remove(eff)

def draw_lane_press_effects(surf):
    for eff in lane_press_effects:
        eff.draw(surf)

JUDGE_LINE_Y = int(HEIGHT * 0.78)
NOTE_RADIUS = 32
MUSIC_START_DELAY = 3.0

class NoteObj:
    def __init__(self, t, lane, hold=0.0):
        self.time = float(t)
        self.lane = int(lane)
        self.hold = float(hold)
        self.hit = False
        self.missed = False
        self.pulse = 0.0
    
    def y(self, song_time, speed):
        seconds_until = self.time - song_time
        return int(JUDGE_LINE_Y - seconds_until * speed)
    
    def update(self, dt):
        self.pulse += dt * 4

class Chart:
    def __init__(self, notes):
        self.notes = [NoteObj(n['time'], n['lane'], n.get('hold',0.0)) for n in notes]
    
    def upcoming(self, song_time, lookahead=6.0):
        return [n for n in self.notes if (not n.hit and not n.missed and n.time >= song_time - 1.0 and n.time <= song_time + lookahead)]

popups = []

def spawn_popup(text, x, y, color=WHITE, ttl=1.0):
    popups.append({'text':text, 'x':x, 'y':float(y), 'age':0.0, 'ttl':ttl, 'color':color, 'alpha':255, 'scale':0.5})

def update_popups(dt):
    for p in popups[:]:
        p['age'] += dt
        p['y'] -= 80.0 * dt
        p['alpha'] = max(0, int(255*(1 - p['age']/p['ttl'])))
        p['scale'] = min(1.5, 0.5 + (p['age']/p['ttl']) * 2)
        if p['age'] >= p['ttl']:
            popups.remove(p)

def draw_popups(surf):
    for p in popups:
        size = int(48 * p['scale'])
        f = make_font(size)
        s = f.render(p['text'], True, p['color'])
        s.set_alpha(p['alpha'])
        r = s.get_rect(center=(int(p['x']), int(p['y'])))
        surf.blit(s, r)

class SettingsWindow:
    def __init__(self):
        self.active = False
        self.width = 420
        self.height = 380
        self.x = (WIDTH - self.width) // 2
        self.y = (HEIGHT - self.height) // 2
        self.volume_slider_rect = pygame.Rect(self.x + 50, self.y + 100, 320, 30)
        self.sfx_slider_rect = pygame.Rect(self.x + 50, self.y + 160, 320, 30)
        self.hitwindow_slider_rect = pygame.Rect(self.x + 50, self.y + 220, 320, 30)
        self.close_button_rect = pygame.Rect(self.x + 160, self.y + 300, 100, 40)
        self.dragging_volume = False
        self.dragging_sfx = False
        self.dragging_hitwindow = False
    
    def draw(self, surf, volume, sfx_volume, hit_window_factor):
        if not self.active: return
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, WIDTH, HEIGHT))
        surf.blit(overlay, (0, 0))
        
        settings_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(settings_surf, (40, 40, 60, 255), (0, 0, self.width, self.height), border_radius=20)
        pygame.draw.rect(settings_surf, CYAN, (0, 0, self.width, self.height), 3, border_radius=20)
        surf.blit(settings_surf, (self.x, self.y))
        
        draw_text(surf, '⚙ 설정', self.x + self.width//2, self.y + 25, size=32, color=CYAN, center=True)
        
        draw_text(surf, f'음악 볼륨: {int(volume*100)}%', self.x + 50, self.y + 70, size=18, color=WHITE)
        pygame.draw.rect(surf, GRAY, self.volume_slider_rect, border_radius=5)
        fill_width = int(self.volume_slider_rect.width * volume)
        pygame.draw.rect(surf, ACCENT, (self.volume_slider_rect.x, self.volume_slider_rect.y, fill_width, self.volume_slider_rect.height), border_radius=5)
        handle_x = self.volume_slider_rect.x + fill_width
        pygame.draw.circle(surf, WHITE, (handle_x, self.volume_slider_rect.centery), 12)
        
        draw_text(surf, f'효과음 볼륨: {int(sfx_volume*100)}%', self.x + 50, self.y + 130, size=18, color=WHITE)
        pygame.draw.rect(surf, GRAY, self.sfx_slider_rect, border_radius=5)
        sfx_fill_width = int(self.sfx_slider_rect.width * sfx_volume)
        pygame.draw.rect(surf, YELLOW, (self.sfx_slider_rect.x, self.sfx_slider_rect.y, sfx_fill_width, self.sfx_slider_rect.height), border_radius=5)
        sfx_handle_x = self.sfx_slider_rect.x + sfx_fill_width
        pygame.draw.circle(surf, WHITE, (sfx_handle_x, self.sfx_slider_rect.centery), 12)
        
        if hit_window_factor > 0.75:
            difficulty_text = "쉬움"
        elif hit_window_factor > 0.5:
            difficulty_text = "보통"
        elif hit_window_factor > 0.25:
            difficulty_text = "어려움"
        else:
            difficulty_text = "지승민"
        
        draw_text(surf, f'판정 난이도: {difficulty_text}', self.x + 50, self.y + 190, size=18, color=WHITE)
        pygame.draw.rect(surf, GRAY, self.hitwindow_slider_rect, border_radius=5)
        hw_fill_width = int(self.hitwindow_slider_rect.width * hit_window_factor)
        pygame.draw.rect(surf, PINK, (self.hitwindow_slider_rect.x, self.hitwindow_slider_rect.y, hw_fill_width, self.hitwindow_slider_rect.height), border_radius=5)
        hw_handle_x = self.hitwindow_slider_rect.x + hw_fill_width
        pygame.draw.circle(surf, WHITE, (hw_handle_x, self.hitwindow_slider_rect.centery), 12)
        
        pygame.draw.rect(surf, GREEN, self.close_button_rect, border_radius=10)
        draw_text(surf, '닫기', self.close_button_rect.centerx, self.close_button_rect.centery, size=18, color=WHITE, center=True)
    
    def handle_click(self, mx, my):
        if not self.active: return None
        if self.close_button_rect.collidepoint(mx, my):
            return 'close'
        elif self.volume_slider_rect.collidepoint(mx, my):
            self.dragging_volume = True
            return 'volume_drag'
        elif self.sfx_slider_rect.collidepoint(mx, my):
            self.dragging_sfx = True
            return 'sfx_drag'
        elif self.hitwindow_slider_rect.collidepoint(mx, my):
            self.dragging_hitwindow = True
            return 'hitwindow_drag'
        return None
    
    def handle_drag(self, mx):
        if self.dragging_volume:
            t = (mx - self.volume_slider_rect.left) / self.volume_slider_rect.width
            return ('volume', max(0.0, min(1.0, t)))
        elif self.dragging_sfx:
            t = (mx - self.sfx_slider_rect.left) / self.sfx_slider_rect.width
            return ('sfx', max(0.0, min(1.0, t)))
        elif self.dragging_hitwindow:
            t = (mx - self.hitwindow_slider_rect.left) / self.hitwindow_slider_rect.width
            return ('hitwindow', max(0.0, min(1.0, t)))
        return None
    
    def stop_drag(self):
        self.dragging_volume = False
        self.dragging_sfx = False
        self.dragging_hitwindow = False

class RhythmGame:
    def __init__(self):
        self.state = 'menu'
        self.dkey = '2'
        self.d = DIFFICULTIES[self.dkey]
        self.lanes = self.d['lanes']
        self.base_hit_window = self.d['hit_window']
        self.hit_window_factor = 1.0
        self.scroll_speed = self.d['speed']
        self.chart = None
        self.start_time = None
        self.pause_acc = 0.0
        self._pause_start = None
        self.paused = False
        self.volume = 0.85
        self.sfx_volume = 0.9
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.perfects = 0
        self.greats = 0
        self.misses = 0
        self.grade = None
        self.settings = SettingsWindow()
        self.bg_hue = 0.0
        self.music_started = False
        self.input_queue = []
        self.last_input_time = {}
        self.load_chart_for_difficulty()
    
    def load_chart_for_difficulty(self):
        lanes = DIFFICULTIES[self.dkey]['lanes']
        self.scroll_speed = DIFFICULTIES[self.dkey]['speed']
        self.base_hit_window = DIFFICULTIES[self.dkey]['hit_window']
        
        notes = create_chart_from_timings(NOTE_TIMINGS, lanes, int(self.dkey))
        self.chart = Chart(notes)
        self.lanes = lanes
        self.recalc_hit_window()
    
    def recalc_hit_window(self):
        if self.hit_window_factor <= 0.25:
            self.hit_window = self.base_hit_window * 0.5
        else:
            self.hit_window = self.base_hit_window + (1.0 - self.hit_window_factor) * 0.15
    
    def start(self):
        self.state = 'playing'
        self.start_time = pygame.time.get_ticks()/1000.0
        self.pause_acc = 0.0
        self.paused = False
        self.music_started = False
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.perfects = 0
        self.greats = 0
        self.misses = 0
        self.grade = None
        self.input_queue = []
        self.last_input_time = {}
        popups.clear()
        particles.clear()
        shockwaves.clear()
        lane_press_effects.clear()
        pygame.mixer.music.stop()
    
    def song_time(self):
        if self.start_time is None: return 0.0
        elapsed = pygame.time.get_ticks()/1000.0 - self.start_time - self.pause_acc
        return elapsed - MUSIC_START_DELAY
    
    def toggle_pause(self):
        if self.state != 'playing': return
        if self.paused:
            self.paused = False
            if self.music_started:
                pygame.mixer.music.unpause()
            self.pause_acc += pygame.time.get_ticks()/1000.0 - self._pause_start
        else:
            self.paused = True
            if self.music_started:
                pygame.mixer.music.pause()
            self._pause_start = pygame.time.get_ticks()/1000.0
    
    def lane_positions(self):
        lane_w = (WIDTH - 16 * (self.lanes + 1)) / self.lanes
        xs = []
        for i in range(self.lanes):
            x = 16 + i*(lane_w + 16) + lane_w/2
            xs.append(int(x))
        return xs
    
    def update(self, dt):
        self.bg_hue += dt * 10
        if self.bg_hue > 360: self.bg_hue -= 360
        
        if self.state != 'playing' or self.paused: return
        
        while self.input_queue:
            lane, input_time = self.input_queue.pop(0)
            self.process_input(lane, input_time)
        
        elapsed = pygame.time.get_ticks()/1000.0 - self.start_time - self.pause_acc
        if not self.music_started and elapsed >= MUSIC_START_DELAY:
            self.music_started = True
            if os.path.exists(MUSIC_PATH):
                try:
                    pygame.mixer.music.load(MUSIC_PATH)
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play()
                except Exception as e:
                    print("music play error:", e)
        
        st = self.song_time()
        
        for n in self.chart.notes:
            n.update(dt)
        
        for n in self.chart.notes:
            if not n.hit and not n.missed:
                if st - n.time > self.hit_window + 0.08:
                    n.missed = True
                    xs = self.lane_positions()
                    x = xs[n.lane] if n.lane < len(xs) else WIDTH//2
                    spawn_popup("MISS", x, JUDGE_LINE_Y, color=RED, ttl=1.0)
                    miss_sfx.set_volume(self.sfx_volume)
                    miss_sfx.play()
                    self.on_miss(n)
        
        last = max([n.time for n in self.chart.notes]) if self.chart.notes else 0
        if st > last + 2.0:
            self.end()
    
    def handle_input(self, lane):
        if self.state != 'playing' or self.paused: return
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        if lane in self.last_input_time:
            if current_time - self.last_input_time[lane] < 0.03:
                return
        
        self.last_input_time[lane] = current_time
        self.input_queue.append((lane, self.song_time()))
    
    def process_input(self, lane, t):
        xs = self.lane_positions()
        lane_w = (WIDTH - 16 * (self.lanes + 1)) / self.lanes
        x = xs[lane] if lane < len(xs) else WIDTH//2
        spawn_lane_press(lane, x, lane_w)
        spawn_particles(x, JUDGE_LINE_Y, 40, CYAN)
        
        cand = [n for n in self.chart.notes if (not n.hit and not n.missed and n.lane==lane)]
        if not cand:
            spawn_popup("MISS", x, JUDGE_LINE_Y, color=RED, ttl=1.0)
            miss_sfx.set_volume(self.sfx_volume)
            miss_sfx.play()
            spawn_shockwave(x, JUDGE_LINE_Y, RED)
            self.on_miss(None)
            return
        
        cand.sort(key=lambda n: abs(n.time - t))
        best = cand[0]
        delta = abs(best.time - t)
        
        if delta <= self.hit_window:
            if delta <= self.hit_window * 0.35:
                rank = "PERFECT"
                color = GREEN
                perfect_sfx.set_volume(self.sfx_volume)
                perfect_sfx.play()
                spawn_particles(x, JUDGE_LINE_Y, 50, GREEN)
                spawn_shockwave(x, JUDGE_LINE_Y, GREEN)
                self.perfects += 1
            else:
                rank = "GREAT"
                color = YELLOW
                great_sfx.set_volume(self.sfx_volume)
                great_sfx.play()
                spawn_particles(x, JUDGE_LINE_Y, 35, YELLOW)
                spawn_shockwave(x, JUDGE_LINE_Y, YELLOW)
                self.greats += 1
            
            best.hit = True
            spawn_popup(rank, x, JUDGE_LINE_Y, color=color, ttl=1.0)
            self.on_hit(best, delta, rank)
        else:
            best.missed = True
            spawn_popup("MISS", x, JUDGE_LINE_Y, color=RED, ttl=1.0)
            miss_sfx.set_volume(self.sfx_volume)
            miss_sfx.play()
            spawn_shockwave(x, JUDGE_LINE_Y, RED)
            self.on_miss(best)
    
    def on_hit(self, note, delta, rank):
        if rank == 'PERFECT':
            add = 400 + int((1 - (delta/self.hit_window))*200)
        else:
            add = 220 + int((1 - (delta/self.hit_window))*120)
        self.score += add + int(self.combo * 0.1)
        self.combo += 1
        if self.combo > self.max_combo:
            self.max_combo = self.combo
    
    def on_miss(self, note):
        self.combo = 0
        self.misses += 1
    
    def end(self):
        self.state = 'results'
        pygame.mixer.music.stop()
        total = self.perfects + self.greats + self.misses
        acc = ((self.perfects + self.greats)/total) if total>0 else 0.0
        if acc >= 0.98 and self.max_combo > 120:
            self.grade = 'SSS'
        elif acc >= 0.95:
            self.grade = 'SS'
        elif acc >= 0.90:
            self.grade = 'S'
        elif acc >= 0.85:
            self.grade = 'A'
        elif acc >= 0.75:
            self.grade = 'B'
        elif acc >= 0.60:
            self.grade = 'C'
        else:
            self.grade = 'D'

def draw_text(surf, text, x, y, size=24, color=WHITE, center=False):
    f = make_font(size)
    r = f.render(text, True, color)
    if center:
        rect = r.get_rect(center=(x,y))
        surf.blit(r, rect)
    else:
        surf.blit(r, (x,y))

def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

G = RhythmGame()
GEAR_RECT = pygame.Rect(WIDTH-86, 24, 56, 56)

KEY_TO_LANE = {
    pygame.K_a:0, pygame.K_s:1, pygame.K_d:2, pygame.K_f:3, pygame.K_g:4, pygame.K_h:5,
}

running = True

while running:
    dt = clock.tick(FPS)/1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and G.state == 'playing':
                G.toggle_pause()
            elif event.key in KEY_TO_LANE and G.state == 'playing':
                lane = KEY_TO_LANE[event.key]
                if lane is not None and lane < G.lanes:
                    G.handle_input(lane)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            if G.settings.active:
                action = G.settings.handle_click(mx, my)
                if action == 'close':
                    G.settings.active = False
                    if G.paused:
                        G.toggle_pause()
            elif G.state == 'menu':
                if 200 <= my <= 260:
                    if 100 <= mx <= 220:
                        G.dkey='1'
                        G.load_chart_for_difficulty()
                    elif 250 <= mx <= 370:
                        G.dkey='2'
                        G.load_chart_for_difficulty()
                    elif 400 <= mx <= 520:
                        G.dkey='3'
                        G.load_chart_for_difficulty()
                elif 350 <= my <= 430 and WIDTH//2-100 <= mx <= WIDTH//2+100:
                    G.start()
                elif 460 <= my <= 520 and WIDTH//2-80 <= mx <= WIDTH//2+80:
                    G.settings.active = True
            elif G.state == 'playing':
                if GEAR_RECT.collidepoint(mx, my):
                    G.settings.active = True
                    if not G.paused:
                        G.toggle_pause()
                else:
                    lane = None
                    lane_w = (WIDTH - 16 * (G.lanes + 1)) / G.lanes
                    for i in range(G.lanes):
                        left = 16 + i*(lane_w + 16)
                        right = left + lane_w
                        if mx >= left and mx <= right:
                            lane = i
                            break
                    if lane is not None:
                        G.handle_input(lane)
            elif G.state == 'results':
                if 500 <= my <= 560 and WIDTH//2-100 <= mx <= WIDTH//2+100:
                    G.load_chart_for_difficulty()
                    G.start()
                elif 580 <= my <= 640 and WIDTH//2-100 <= mx <= WIDTH//2+100:
                    G.state = 'menu'
        elif event.type == pygame.MOUSEBUTTONUP:
            G.settings.stop_drag()
        elif event.type == pygame.MOUSEMOTION:
            mx = event.pos[0]
            result = G.settings.handle_drag(mx)
            if result:
                if result[0] == 'volume':
                    G.volume = result[1]
                    pygame.mixer.music.set_volume(G.volume)
                elif result[0] == 'sfx':
                    G.sfx_volume = result[1]
                elif result[0] == 'hitwindow':
                    G.hit_window_factor = result[1]
                    G.recalc_hit_window()

    G.update(dt)
    update_popups(dt)
    update_particles(dt)
    update_shockwaves(dt)
    update_lane_press_effects(dt)
    
    for star in stars:
        star.update(dt)

    hue1 = G.bg_hue % 360
    hue2 = (G.bg_hue + 60) % 360
    
    for y in range(0, HEIGHT, 6):
        t = y/HEIGHT
        h = hue1 * (1-t) + hue2 * t
        rgb = hsv_to_rgb(h, 0.6, 0.15)
        pygame.draw.rect(screen, rgb, (0, y, WIDTH, 6))
    
    for star in stars:
        star.draw(screen)

    xs = G.lane_positions()
    lane_w = (WIDTH - 16 * (G.lanes + 1)) / G.lanes
    
    for i,x in enumerate(xs):
        left = x - lane_w/2
        for ly in range(0, HEIGHT, 4):
            alpha = int(30 + 20 * math.sin(ly * 0.02 + G.bg_hue * 0.1))
            s = pygame.Surface((int(lane_w), 4), pygame.SRCALPHA)
            color = (20, 25, 40, alpha)
            pygame.draw.rect(s, color, (0, 0, int(lane_w), 4))
            screen.blit(s, (left, ly))
        
        border_color = hsv_to_rgb((G.bg_hue + i * 40) % 360, 0.8, 0.6)
        pygame.draw.line(screen, border_color, (left, 0), (left, HEIGHT), 2)
        pygame.draw.line(screen, border_color, (left + lane_w, 0), (left + lane_w, HEIGHT), 2)
        
        draw_text(screen, str(i+1), x, JUDGE_LINE_Y+80, size=22, color=LIGHT, center=True)

    draw_lane_press_effects(screen)
    draw_shockwaves(screen)

    glow_surf = pygame.Surface((WIDTH, 20), pygame.SRCALPHA)
    for i in range(10):
        alpha = int(100 * (1 - i/10))
        pygame.draw.line(glow_surf, CYAN + (alpha,), (0, 10), (WIDTH, 10), 2)
    screen.blit(glow_surf, (0, JUDGE_LINE_Y - 10))
    pygame.draw.line(screen, CYAN, (0, JUDGE_LINE_Y), (WIDTH, JUDGE_LINE_Y), 4)

    if G.state == 'playing' and not G.paused:
        st = G.song_time()
        lookahead = 6.0
        
        elapsed = pygame.time.get_ticks()/1000.0 - G.start_time - G.pause_acc
        if elapsed < MUSIC_START_DELAY:
            countdown = int(MUSIC_START_DELAY - elapsed) + 1
            countdown_color = hsv_to_rgb(G.bg_hue, 0.9, 1.0)
            draw_text(screen, str(countdown), WIDTH//2, HEIGHT//2, size=120, color=countdown_color, center=True)
        
        for n in G.chart.upcoming(st, lookahead=lookahead):
            y = n.y(st, G.scroll_speed)
            
            if y < -NOTE_RADIUS or y > HEIGHT + NOTE_RADIUS:
                continue
            
            x = xs[n.lane] if n.lane < len(xs) else WIDTH//2
            
            if n.hit:
                col = GREEN
            elif n.missed:
                col = RED
            else:
                note_hue = (G.bg_hue + y * 0.5) % 360
                col = hsv_to_rgb(note_hue, 0.9, 0.95)
            
            pulse_size = NOTE_RADIUS + int(5 * math.sin(n.pulse))
            
            distance_to_judge = abs(y - JUDGE_LINE_Y)
            max_distance = HEIGHT * 0.5
            opacity_factor = 1.0 - min(1.0, distance_to_judge / max_distance)
            opacity_factor = max(0.3, opacity_factor)
            
            glow_surf = pygame.Surface((pulse_size*3, pulse_size*3), pygame.SRCALPHA)
            for r in range(pulse_size, pulse_size*2, 3):
                alpha = int(80 * (1 - (r-pulse_size)/pulse_size) * opacity_factor)
                pygame.draw.circle(glow_surf, col + (alpha,), (pulse_size*1.5, pulse_size*1.5), r, 3)
            screen.blit(glow_surf, (x - pulse_size*1.5, y - pulse_size*1.5))
            
            note_surf = pygame.Surface((pulse_size*2, pulse_size*2), pygame.SRCALPHA)
            main_alpha = int(255 * opacity_factor)
            pygame.draw.circle(note_surf, col + (main_alpha,), (pulse_size, pulse_size), pulse_size, 4)
            inner_col = tuple(min(255, c + 50) for c in col[:3])
            inner_alpha = int(200 * opacity_factor)
            pygame.draw.circle(note_surf, inner_col + (inner_alpha,), (pulse_size, pulse_size), pulse_size - 6)
            highlight_col = tuple(min(255, c + 100) for c in col[:3])
            highlight_alpha = int(150 * opacity_factor)
            pygame.draw.circle(note_surf, highlight_col + (highlight_alpha,), (pulse_size - 8, pulse_size - 8), pulse_size // 3)
            
            screen.blit(note_surf, (x - pulse_size, y - pulse_size))

    draw_particles(screen)

    if G.state == 'playing':
        hud_surf = pygame.Surface((WIDTH, 140), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (0, 0, 0, 120), (0, 0, WIDTH, 140))
        screen.blit(hud_surf, (0, 0))
        
        draw_text(screen, f'난이도: {DIFFICULTIES[G.dkey]["name"]}  레인:{G.lanes}', WIDTH//2, 20, size=18, color=LIGHT, center=True)
        
        score_color = hsv_to_rgb(G.bg_hue, 0.7, 1.0)
        draw_text(screen, f'점수: {G.score}', 20, 28, size=24, color=score_color)
        
        if G.combo > 50:
            combo_color = PINK
        elif G.combo > 20:
            combo_color = YELLOW
        else:
            combo_color = WHITE
            
        if G.combo > 1:
            draw_text(screen, f'{G.combo-1} COMBO', 250, 200, size=34, color=combo_color)
        
        draw_text(screen, f'Perfect: {G.perfects}  Great: {G.greats}  Miss: {G.misses}', 20, 120, size=18)
        
        pygame.draw.circle(screen, GRAY, GEAR_RECT.center, 28)
        pygame.draw.circle(screen, CYAN, GEAR_RECT.center, 28, 3)
        for i in range(8):
            angle = i * math.pi / 4 + pygame.time.get_ticks() * 0.001
            x1 = GEAR_RECT.centerx + math.cos(angle) * 18
            y1 = GEAR_RECT.centery + math.sin(angle) * 18
            x2 = GEAR_RECT.centerx + math.cos(angle) * 24
            y2 = GEAR_RECT.centery + math.sin(angle) * 24
            pygame.draw.line(screen, CYAN, (x1, y1), (x2, y2), 3)
        pygame.draw.circle(screen, WHITE, GEAR_RECT.center, 10)
        
    else:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
        screen.blit(overlay, (0, 0))
        
        if G.state == 'menu':
            title_color = hsv_to_rgb(G.bg_hue, 0.8, 1.0)
            
            draw_text(screen, '밤을 달리다', WIDTH//2, 140, size=36, color=LIGHT, center=True)
            
            button_y = 220
            button_colors = [GREEN, YELLOW, RED]
            difficulties = ['쉬움', '보통', '어려움']
            button_width = 100
            button_spacing = 140
            start_x = WIDTH//2 - 140
            
            for i, (diff, color) in enumerate(zip(difficulties, button_colors)):
                bx = start_x + i * button_spacing
                btn_rect = pygame.Rect(bx, button_y, button_width, 60)
                
                if str(i+1) == G.dkey:
                    pygame.draw.rect(screen, color, btn_rect, border_radius=10)
                    text_color = BLACK
                else:
                    pygame.draw.rect(screen, GRAY, btn_rect, border_radius=10)
                    pygame.draw.rect(screen, color, btn_rect, 3, border_radius=10)
                    text_color = color
                
                draw_text(screen, diff, btn_rect.centerx, btn_rect.centery - 12, size=18, color=text_color, center=True)
                draw_text(screen, f'{DIFFICULTIES[str(i+1)]["lanes"]}L', btn_rect.centerx, btn_rect.centery + 12, size=14, color=text_color, center=True)
            
            pulse = math.sin(pygame.time.get_ticks() * 0.003) * 0.5 + 0.5
            start_color = tuple(int(c * (0.7 + pulse * 0.3)) for c in CYAN[:3])
            start_btn = pygame.Rect(WIDTH//2 - 110, 340, 220, 80)
            pygame.draw.rect(screen, start_color, start_btn, border_radius=15)
            pygame.draw.rect(screen, CYAN, start_btn, 3, border_radius=15)
            draw_text(screen, 'START', start_btn.centerx, start_btn.centery, size=32, color=WHITE, center=True)
            
            settings_btn = pygame.Rect(WIDTH//2 - 80, 450, 160, 60)
            pygame.draw.rect(screen, PURPLE, settings_btn, border_radius=10)
            pygame.draw.rect(screen, PINK, settings_btn, 2, border_radius=10)
            draw_text(screen, 'Settings', settings_btn.centerx, settings_btn.centery, size=20, color=WHITE, center=True)
            
            draw_text(screen, 'Click lanes or press A/S/D/F/G/H', WIDTH//2, 560, size=14, color=LIGHT, center=True)
            draw_text(screen, 'by.황유찬', WIDTH//2, 590, size=14, color=CYAN, center=True)
            
        elif G.state == 'results':
            draw_text(screen, 'RESULT', WIDTH//2, 100, size=48, color=YELLOW, center=True)
            
            if G.grade in ['SSS', 'SS', 'S']:
                grade_color = PINK
            elif G.grade in ['A', 'B']:
                grade_color = YELLOW
            else:
                grade_color = WHITE
            
            draw_text(screen, f'Grade: {G.grade}', WIDTH//2, 180, size=56, color=grade_color, center=True)
            draw_text(screen, f'Score: {G.score:,}', WIDTH//2, 260, size=28, color=CYAN, center=True)
            
            total = G.perfects + G.greats + G.misses
            acc = ((G.perfects + G.greats)/total*100) if total>0 else 0.0
            draw_text(screen, f'Accuracy: {acc:.1f}%', WIDTH//2, 310, size=24, center=True)
            
            draw_text(screen, f'Perfect: {G.perfects}', WIDTH//2 - 150, 360, size=22, color=GREEN)
            draw_text(screen, f'Great: {G.greats}', WIDTH//2, 360, size=22, color=YELLOW, center=True)
            draw_text(screen, f'Miss: {G.misses}', WIDTH//2 + 150, 360, size=22, color=RED)
            
            draw_text(screen, f'Max Combo: {G.max_combo}', WIDTH//2, 400, size=22, color=PINK, center=True)
            
            restart_btn = pygame.Rect(WIDTH//2 - 110, 480, 220, 60)
            pygame.draw.rect(screen, GREEN, restart_btn, border_radius=10)
            draw_text(screen, 'RETRY', restart_btn.centerx, restart_btn.centery, size=24, color=WHITE, center=True)
            
            menu_btn = pygame.Rect(WIDTH//2 - 110, 560, 220, 60)
            pygame.draw.rect(screen, ACCENT, menu_btn, border_radius=10)
            draw_text(screen, 'MENU', menu_btn.centerx, menu_btn.centery, size=24, color=WHITE, center=True)

    G.settings.draw(screen, G.volume, G.sfx_volume, G.hit_window_factor)
    draw_popups(screen)
    
    if G.paused and not G.settings.active:
        pause_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(pause_surf, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
        screen.blit(pause_surf, (0, 0))
        draw_text(screen, 'PAUSED', WIDTH//2, HEIGHT//2 - 60, size=48, color=CYAN, center=True)
        draw_text(screen, 'Press ESC to resume', WIDTH//2, HEIGHT//2 + 20, size=24, color=WHITE, center=True)

    pygame.display.flip()

pygame.quit()
sys.exit()
z
