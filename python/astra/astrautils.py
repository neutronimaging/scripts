import numpy as np

def create_cone_vec_geometry(
    angles, SOD, SDD,
    px_size, det_px,
    piercing_px,
    cor=(0, 0, 0) ):
    """
    piercing_px: (py, px) in pixels (row, col) = (height, width) direction
    """
    H, W = det_px
    dy, dx = px_size
    py, px = piercing_px  # detector pixel (row, col) where beam hits

    vectors = []

    for theta in angles:
        R = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta),  np.cos(theta), 0],
            [0,              0,             1]
        ])

        obj = np.array(cor)
        src = obj + R @ np.array([-SOD, 0, 0])
        det_center_nominal = obj + R @ np.array([SDD - SOD, 0, 0])

        # Detector axes in world space
        u_vec = R @ np.array([0, dx, 0])  # across columns
        v_vec = R @ np.array([0, 0, dy])  # down rows

        # Offset in pixels from center
        px_offset = (px - W / 2) * u_vec
        py_offset = (py - H / 2) * v_vec

        # Adjusted detector center
        det_c = det_center_nominal + px_offset + py_offset

        vectors.append(np.concatenate([src, det_c, u_vec, v_vec]))

    return vectors