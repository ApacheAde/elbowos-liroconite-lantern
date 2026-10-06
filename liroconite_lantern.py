#!/usr/bin/env python3
"""Liroconite Lantern — neon flare-catch arcade for ElbowOS.

Steer a copper lantern up a teal mine shaft.
Flare the wick to snare sea-green moths.
Smoke wisps snuff the combo.
Left / Right (or A / D) steer. Space flares.
"""
import math
import os
import shutil
import subprocess
import sys
import pygame

W, H = 1080, 1920
FPS = 30
OUT_NAME = "LiroconiteLantern_ElbowOS.mp4"
PAL = {
    "bg0": (4, 22, 28),
    "bg1": (10, 58, 62),
    "wall": (18, 72, 68),
    "ore": (72, 210, 168),
    "flame": (255, 186, 72),
    "copper": (214, 132, 64),
    "moth": (120, 255, 214),
    "wisp": (186, 92, 210),
    "ink": (3, 12, 16),
    "cream": (255, 236, 210),
}


def clamp(v, a, b):
    return a if v < a else b if v > b else v


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 540.0
        self.y = 1280.0
        self.scroll = 0.0
        self.score = 0
        self.combo = 1
        self.t = 0
        self.flare = 0
        self.flash = 0
        self.moths = []
        self.wisps = []
        self.parts = []
        self.ores = [
            {"x": 120 + (i % 2) * 840, "y": 180 + i * 220, "r": 28 + (i % 3) * 8}
            for i in range(10)
        ]
        self._spawn(8, moth=True)
        self._spawn(3, moth=False)

    def _spawn(self, n, moth):
        bag = self.moths if moth else self.wisps
        for i in range(n):
            bag.append({
                "x": 180 + ((self.t * 17 + i * 137) % 720),
                "y": 360 + ((self.t * 29 + i * 211) % 1100),
                "ph": i * 0.7,
                "alive": True,
            })

    def step(self, steer, flare_on=False):
        self.t += 1
        self.x = clamp(self.x + steer, 160, 920)
        self.y = 1180 + math.sin(self.t / 28.0) * 70
        self.scroll += 1.6
        if flare_on:
            self.flare = 16
        if self.flare:
            self.flare -= 1
        if self.flash:
            self.flash -= 1
        radius = 150 + (90 if self.flare else 0)
        for m in self.moths:
            if not m["alive"]:
                continue
            m["ph"] += 0.05
            m["x"] += math.sin(m["ph"]) * 2.4
            m["y"] += 1.5
            if (m["x"] - self.x) ** 2 + (m["y"] - self.y) ** 2 < radius ** 2 and self.flare:
                m["alive"] = False
                self.score += 100 * self.combo
                self.combo = min(9, self.combo + 1)
                self.flash = 5
                self._burst(m["x"], m["y"], PAL["moth"])
            elif m["y"] > H + 40:
                m["alive"] = False
        for w in self.wisps:
            if not w["alive"]:
                continue
            w["ph"] += 0.04
            w["x"] += math.cos(w["ph"]) * 2.1
            w["y"] += 2.2
            if (w["x"] - self.x) ** 2 + (w["y"] - self.y) ** 2 < 70 ** 2:
                w["alive"] = False
                self.score = max(0, self.score - 60)
                self.combo = 1
                self.flare = 0
                self._burst(w["x"], w["y"], PAL["wisp"])
            elif w["y"] > H + 40:
                w["alive"] = False
        if self.t % 28 == 0:
            self._spawn(1, moth=True)
        if self.t % 70 == 0:
            self._spawn(1, moth=False)
        self.moths = [m for m in self.moths if m["alive"]][-18:]
        self.wisps = [w for w in self.wisps if w["alive"]][-8:]
        self.parts = [p for p in self.parts if p["life"] > 0]
        for p in self.parts:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
        for o in self.ores:
            o["y"] += 1.6
            if o["y"] > H + 40:
                o["y"] = -30

    def _burst(self, x, y, col):
        for i in range(12):
            a = i / 12 * math.tau
            self.parts.append({
                "x": x, "y": y, "vx": math.cos(a) * 4, "vy": math.sin(a) * 4,
                "life": 18, "col": col,
            })

    def draw(self, surf, font, font_sm):
        surf.fill(PAL["bg0"])
        for y in range(0, H, 10):
            k = y / H
            pygame.draw.rect(surf, (
                int(PAL["bg0"][0] * (1 - k) + PAL["bg1"][0] * k),
                int(PAL["bg0"][1] * (1 - k) + PAL["bg1"][1] * k),
                int(PAL["bg0"][2] * (1 - k) + PAL["bg1"][2] * k),
            ), (0, y, W, 10))
        pygame.draw.rect(surf, PAL["wall"], (0, 0, 110, H))
        pygame.draw.rect(surf, PAL["wall"], (W - 110, 0, 110, H))
        for i in range(16):
            y = int((i * 140 - self.scroll) % H)
            pygame.draw.rect(surf, (28, 96, 88), (0, y, 110, 18))
            pygame.draw.rect(surf, (28, 96, 88), (W - 110, y, 110, 18))
        for o in self.ores:
            glow = 80 if abs(o["x"] - self.x) < 260 and abs(o["y"] - self.y) < 260 else 0
            col = (min(255, PAL["ore"][0] + glow), min(255, PAL["ore"][1]), PAL["ore"][2])
            pygame.draw.circle(surf, col, (int(o["x"]), int(o["y"])), o["r"])
            pygame.draw.circle(surf, PAL["cream"], (int(o["x"]), int(o["y"])), o["r"], 3)
        rad = 150 + (90 if self.flare else 0)
        glow = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 190, 80, 70 if self.flare else 36), (rad, rad), rad)
        surf.blit(glow, (self.x - rad, self.y - rad))
        for m in self.moths:
            self._moth(surf, m["x"], m["y"], PAL["moth"])
        for w in self.wisps:
            self._moth(surf, w["x"], w["y"], PAL["wisp"])
        for p in self.parts:
            pygame.draw.circle(surf, p["col"], (int(p["x"]), int(p["y"])), 5)
        pygame.draw.line(surf, PAL["copper"], (int(self.x), 0), (int(self.x), int(self.y) - 50), 4)
        pygame.draw.circle(surf, PAL["copper"], (int(self.x), int(self.y)), 42)
        pygame.draw.circle(surf, PAL["flame"], (int(self.x), int(self.y) - 8), 18 + (8 if self.flare else 0))
        pygame.draw.circle(surf, PAL["cream"], (int(self.x), int(self.y) - 12), 7)
        banner = pygame.Surface((W, 200), pygame.SRCALPHA)
        banner.fill((3, 12, 16, 175))
        surf.blit(banner, (0, 0))
        title = font.render("LIROCONITE LANTERN", True, PAL["flame"])
        surf.blit(title, (W // 2 - title.get_width() // 2, 34))
        sub = font_sm.render("flare the wick  \u00b7  snare the moths", True, PAL["ore"])
        surf.blit(sub, (W // 2 - sub.get_width() // 2, 108))
        sc = font.render(f"SCORE  {self.score}", True, PAL["cream"])
        surf.blit(sc, (W // 2 - sc.get_width() // 2, 148))
        foot = pygame.Surface((W, 90), pygame.SRCALPHA)
        foot.fill((3, 12, 16, 185))
        surf.blit(foot, (0, H - 90))
        tag = font_sm.render("x.com/ElbowOS", True, PAL["copper"])
        surf.blit(tag, (W // 2 - tag.get_width() // 2, H - 62))
        if self.flash:
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash.fill((120, 255, 214, 36))
            surf.blit(flash, (0, 0))

    def _moth(self, surf, x, y, col):
        pygame.draw.circle(surf, col, (int(x), int(y)), 10)
        pygame.draw.ellipse(surf, col, (int(x) - 28, int(y) - 8, 22, 14))
        pygame.draw.ellipse(surf, col, (int(x) + 6, int(y) - 8, 22, 14))


def _fonts():
    return pygame.font.Font(None, 72), pygame.font.Font(None, 42)


def play():
    pygame.init()
    screen = pygame.display.set_mode((W // 2, H // 2))
    pygame.display.set_caption("Liroconite Lantern \u2014 ElbowOS")
    clock = pygame.time.Clock()
    font, font_sm = _fonts()
    canvas = pygame.Surface((W, H))
    g = Game()
    while True:
        steer, flare = 0.0, False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                flare = True
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                g.reset()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            steer -= 7
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            steer += 7
        g.step(steer, flare)
        g.draw(canvas, font, font_sm)
        screen.blit(pygame.transform.smoothscale(canvas, screen.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def record():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    surf = pygame.Surface((W, H))
    font, font_sm = _fonts()
    out_dir = "/home/workdir/artifacts"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, OUT_NAME)
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        "-movflags", "+faststart", out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    g = Game()
    try:
        for i in range(FPS * 15):
            target = 320 + (i % 180) / 180 * 440
            steer = clamp(target - g.x, -9, 9)
            g.step(steer, i % 22 == 0)
            g.draw(surf, font, font_sm)
            proc.stdin.write(pygame.image.tostring(surf, "RGB"))
    finally:
        proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", "replace")
    rc = proc.wait()
    if rc != 0:
        sys.stderr.write(err)
        raise SystemExit(f"ffmpeg failed: {rc}")
    alt = "/workspace/artifacts/" + OUT_NAME
    if os.path.abspath(out) != os.path.abspath(alt):
        shutil.copy2(out, alt)
    print(out)


if __name__ == "__main__":
    play() if "--play" in sys.argv else record()
