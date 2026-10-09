"""An oblique 3D camera: points in a box-shaped world to frame pixels, with zoom and focus.

World axes: x to the right, y away from the viewer (drawn obliquely up and to the side), z up.
`scale` is pixels per world unit; `focus` the world point drawn at `centre`; `direction` 1 or -1
flips which way y leans; `kx`, `ky` the oblique shear. Two helpers for fabric and paper edges,
`ripple` and `clip`, sit beside it. Standard library only.
"""

import math


class Camera:
    def __init__(self, scale, focus, centre, direction=1, kx=0.40, ky=0.34):
        self.scale, self.focus, self.centre = scale, tuple(focus), tuple(centre)
        self.direction, self.kx, self.ky = direction, kx, ky

    def point(self, x, y, z):
        fx, fy, fz = self.focus
        return (self.centre[0] + self.scale * ((x - fx) + self.direction * self.kx * (y - fy)),
                self.centre[1] - self.scale * ((z - fz) + self.ky * (y - fy)))


def between(a, b, p):
    """The camera p of the way from a to b (scale, focus and centre; a's direction and shear)."""
    def lerp(u, v):
        return u + (v - u) * p
    return Camera(lerp(a.scale, b.scale), tuple(lerp(u, v) for u, v in zip(a.focus, b.focus)),
                  tuple(lerp(u, v) for u, v in zip(a.centre, b.centre)), a.direction, a.kx, a.ky)


def front(cam, pts, y=0.0):
    """(x, z) points on the plane at depth y."""
    return [cam.point(x, y, z) for (x, z) in pts]


def top(cam, pts, z=0.0):
    """(x, y) points on the plane at height z."""
    return [cam.point(x, y, z) for (x, y) in pts]


def end(cam, pts, x=0.0):
    """(y, z) points on the plane at x."""
    return [cam.point(x, y, z) for (y, z) in pts]


def ripple(x0, x1, z, amp, n=16, phase=0.0):
    """A wavy edge: n + 1 (x, z) points from x0 to x1 about z, never further than amp from it;
    `phase` shifts the waves. For cloth and paper edges (the prototype's `ripple`)."""
    return [(x0 + (x1 - x0) * i / n,
             z + amp * math.sin(i * 1.9 + phase) * (0.55 + 0.45 * math.sin(i * 0.83 + 1.0)))
            for i in range(n + 1)]


def clip(pts, f):
    """The polygon `pts` cut to the side where f(point) >= 0: vertices on that side are kept and
    each edge that crosses is cut at the crossing (the prototype's `clip_half`)."""
    out = []
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        fa, fb = f(a), f(b)
        if fa >= 0:
            out.append(a)
        if (fa >= 0) != (fb >= 0):
            t = fa / (fa - fb)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out
