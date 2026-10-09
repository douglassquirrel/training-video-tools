"""videotools.camera: the oblique projection the bed video used, as numbers."""

import pytest

from videotools.camera import Camera, between, clip, end, front, ripple, top


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


def test_ripple_runs_from_x0_to_x1_in_n_steps_about_z_within_the_amplitude():
    pts = ripple(10.0, 20.0, 5.0, 0.5, n=4)
    assert len(pts) == 5
    assert [x for x, _ in pts] == [10.0, 12.5, 15.0, 17.5, 20.0]
    assert all(abs(z - 5.0) <= 0.5 for _, z in pts)
    assert pts != ripple(10.0, 20.0, 5.0, 0.5, n=4, phase=1.0)       # the phase moves the waves
    assert ripple(10.0, 20.0, 5.0, 0.0, n=4) == [(x, 5.0) for x in (10.0, 12.5, 15.0, 17.5, 20.0)]


def test_clip_keeps_the_side_of_a_polygon_where_f_is_not_negative_cutting_edges_where_it_crosses():
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    assert clip(square, lambda p: p[0] - 1) == [(1.0, 0.0), (4, 0), (4, 4), (1.0, 4.0)]   # x >= 1
    assert clip(square, lambda p: 1) == square                                            # all kept
    assert clip(square, lambda p: -1) == []                                               # all cut
