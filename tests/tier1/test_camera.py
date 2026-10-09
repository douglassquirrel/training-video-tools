"""videotools.camera: the oblique projection the bed video used, as numbers."""

import pytest

from videotools.camera import Camera, between, end, front, top


def test_the_focus_point_lands_on_the_centre():
    cam = Camera(14.0, (38, 17, -7), (735, 548))
    assert cam.point(38, 17, -7) == (735, 548)


def test_x_goes_right_z_goes_up_and_y_goes_obliquely_by_the_shear():
    cam = Camera(10.0, (0, 0, 0), (100, 100))
    assert cam.point(1, 0, 0) == (110, 100)
    assert cam.point(0, 0, 1) == (100, 90)
    assert cam.point(0, 1, 0) == (pytest.approx(104.0), pytest.approx(96.6))


def test_direction_minus_one_mirrors_the_oblique_shear():
    cam = Camera(10.0, (0, 0, 0), (100, 100), direction=-1)
    assert cam.point(0, 1, 0) == (pytest.approx(96.0), pytest.approx(96.6))


def test_between_interpolates_scale_focus_and_centre():
    a = Camera(10.0, (0, 0, 0), (100, 100))
    b = Camera(20.0, (10, 4, 2), (300, 200))
    c = between(a, b, 0.5)
    assert (c.scale, c.focus, c.centre, c.direction) == (15.0, (5.0, 2.0, 1.0), (200.0, 150.0), 1)


def test_points_on_the_three_planes():
    cam = Camera(10.0, (0, 0, 0), (100, 100))
    assert front(cam, [(1, 2)]) == [cam.point(1, 0, 2)]
    assert front(cam, [(1, 2)], y=3) == [cam.point(1, 3, 2)]
    assert top(cam, [(1, 2)], z=6) == [cam.point(1, 2, 6)]
    assert end(cam, [(2, 3)], x=5) == [cam.point(5, 2, 3)]
