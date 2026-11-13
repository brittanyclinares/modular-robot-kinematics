import argparse
import math


def rotate_frame(yaw, pitch):
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    return ((cy * cp, -sy, cy * sp), (sy * cp, cy, sy * sp), (-sp, 0, cp))


def multiply(left, right):
    return tuple(tuple(sum(a * b for a, b in zip(row, col)) for col in zip(*right)) for row in left)


def advance(point, frame, distance):
    return tuple(coordinate - distance * row[0] for coordinate, row in zip(point, frame))


def forward_kinematics(angles, spacing=1.0):
    """Return module centers and connectors for yaw/pitch pairs in radians."""
    if not math.isfinite(spacing) or spacing <= 0:
        raise ValueError("spacing must be finite and positive")
    frame = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    centers = [(0, 0, 0)]
    joints = []
    for yaw, pitch in angles:
        if not all(math.isfinite(angle) for angle in (yaw, pitch)):
            raise ValueError("joint angles must be finite")
        joint = advance(centers[-1], frame, spacing / 2)
        joints.append(joint)
        frame = multiply(frame, rotate_frame(yaw, pitch))
        centers.append(advance(joint, frame, spacing / 2))
    return centers, joints


def check():
    straight, _ = forward_kinematics([(0, 0)] * 3, spacing=2)
    assert straight == [(0, 0, 0), (-2, 0, 0), (-4, 0, 0), (-6, 0, 0)]
    centers, joints = forward_kinematics([(math.pi / 2, math.pi / 4), (-0.2, 0.4)])
    expected = (-0.5, -math.sqrt(0.125), math.sqrt(0.125))
    assert math.dist(centers[1], expected) < 1e-12
    for front, joint, rear in zip(centers, joints, centers[1:]):
        assert math.isclose(math.dist(front, joint), 0.5)
        assert math.isclose(math.dist(rear, joint), 0.5)
    print("Kinematics checks passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    if parser.parse_args().check:
        check()
    else:
        centers, _ = forward_kinematics([(0.45, 0.2), (-0.3, 0.1), (0.25, -0.3)])
        for index, center in enumerate(centers):
            print(f"Module {index}: " + ", ".join(f"{value:.3f}" for value in center))
