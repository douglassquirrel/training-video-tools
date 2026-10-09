"""An oblique 3D camera: points in a box-shaped world to frame pixels, with zoom and focus.

World axes: x to the right, y away from the viewer (drawn obliquely up and to the side), z up.
`scale` is pixels per world unit; `focus` the world point drawn at `centre`; `direction` 1 or -1
flips which way y leans; `kx`, `ky` the oblique shear. Standard library only.
"""


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
