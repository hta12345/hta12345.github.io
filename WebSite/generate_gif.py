import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as R
import sys
import os

# Parametreler
L_base = 1.0
L_arm1 = 2.0
L_arm2 = 2.0
L_tip = 1.0

def sph_to_cart(az_deg, el_deg):
    az = np.radians(az_deg)
    el = np.radians(el_deg)
    x = np.cos(el) * np.cos(az)
    y = np.cos(el) * np.sin(az)
    z = np.sin(el)
    return np.array([x, y, z])

def solve_motor_angles_v7_5(target_az, target_el, plat_roll, plat_pitch, tip_az, tip_el):
    target_vec = sph_to_cart(target_az, target_el)
    r_plat_x = R.from_euler('x', plat_roll, degrees=True)
    r_plat_y = R.from_euler('y', plat_pitch, degrees=True)
    r_plat = r_plat_x * r_plat_y
    tip_vec_local = sph_to_cart(tip_az, tip_el)

    def objective(x):
        q1_deg, q2_deg = x
        r_q1 = R.from_euler('x', q1_deg, degrees=True)
        r_q2 = R.from_euler('y', q2_deg, degrees=True)
        r_total = r_plat * r_q1 * r_q2
        current_pointer = r_total.apply(tip_vec_local)
        diff = current_pointer - target_vec
        return np.sum(diff**2)

    bounds = [(-90, 90), (-90, 90)]
    res = minimize(objective, [0, 0], bounds=bounds, method='L-BFGS-B')
    return res.x[0], res.x[1], res.fun

# GIF Ayarları
frames = 60
fig = plt.figure(figsize=(7, 6), dpi=100)
# Saydam arkaplan GIF'te sorun yaratabilir, koyu gri yapalım
fig.patch.set_facecolor('#0d1117') 
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0d1117')

def update(frame):
    ax.clear()
    
    # Animasyon senaryosu:
    # Azimut 0'dan 360'a döner, Elevasyon +/- 10 derece salınır
    az = (frame / frames) * 360.0
    el = 45.0 + 10.0 * np.sin(2 * np.pi * frame / frames)
    plat_roll = 10.0 * np.sin(2 * np.pi * frame / frames)
    plat_pitch = 10.0 * np.cos(2 * np.pi * frame / frames)
    tip_az = 0.0
    tip_el = 90.0
    
    q1, q2, error = solve_motor_angles_v7_5(az, el, plat_roll, plat_pitch, tip_az, tip_el)
    
    # Çizim mantığı
    r_plat = R.from_euler('x', plat_roll, degrees=True) * R.from_euler('y', plat_pitch, degrees=True)
    r_q1 = R.from_euler('x', q1, degrees=True)
    r_q2 = R.from_euler('y', q2, degrees=True)
    
    tip_az_r = np.radians(tip_az)
    tip_el_r = np.radians(tip_el)
    tip_vec_local_unit = np.array([
        np.cos(tip_el_r) * np.cos(tip_az_r),
        np.cos(tip_el_r) * np.sin(tip_az_r),
        np.sin(tip_el_r)
    ])
    
    p0 = np.array([0., 0., 0.])
    p1 = p0 + r_plat.apply(np.array([0., 0., L_base]))
    p2 = p1 + (r_plat * r_q1).apply(np.array([0., 0., L_arm1]))
    p_elbow = p2 + (r_plat * r_q1 * r_q2).apply(np.array([0., 0., L_arm2]))
    
    r_global_arm2 = r_plat * r_q1 * r_q2
    v_tip_global = r_global_arm2.apply(tip_vec_local_unit)
    p_tip = p_elbow + v_tip_global * L_tip

    arm_color = '#4da8da'
    tip_color = '#ff6b6b'

    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], color='#8892b0', lw=4)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color=arm_color, lw=4)
    ax.plot([p2[0], p_elbow[0]], [p2[1], p_elbow[1]], [p2[2], p_elbow[2]], color=arm_color, lw=4)
    ax.plot([p_elbow[0], p_tip[0]], [p_elbow[1], p_tip[1]], [p_elbow[2], p_tip[2]], color=tip_color, lw=4)
    
    ax.scatter(p0[0], p0[1], p0[2], s=50, c='#8892b0')
    ax.scatter(p1[0], p1[1], p1[2], s=40, c='#64ffda')
    ax.scatter(p2[0], p2[1], p2[2], s=40, c='#64ffda')
    ax.scatter(p_elbow[0], p_elbow[1], p_elbow[2], s=30, c='#ff6b6b')

    vec_len = 2.0
    ax.quiver(p_tip[0], p_tip[1], p_tip[2], 
                   v_tip_global[0]*vec_len, v_tip_global[1]*vec_len, v_tip_global[2]*vec_len, 
                   color='lime', linewidth=2, length=1.0, normalize=False)

    scale = 5.0
    t_vec = sph_to_cart(az, el) * scale
    ax.quiver(0, 0, 0, t_vec[0], t_vec[1], t_vec[2], 
                   color='orange', linewidth=1.5, linestyle='--', length=1.0, normalize=False)

    lim = 5
    ax.set_xlim([-lim, lim])
    ax.set_ylim([-lim, lim])
    ax.set_zlim([0, 7])
    
    # Görsel ayarlar
    ax.grid(True, color='#ffffff', alpha=0.1)
    ax.tick_params(colors='#8892b0')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    for spine in ax.spines.values():
        spine.set_edgecolor('#ffffff')
        spine.set_alpha(0.1)
        
    ax.set_title(f"Target Az: {az:.1f}° | Q1: {q1:.1f}° | Q2: {q2:.1f}°", color='#ccd6f6', pad=10, fontsize=12)
    ax.view_init(elev=20, azim=135)
    
    # Print progress
    print(f"Generating frame {frame+1}/{frames}...", end='\r')

print("Starting GIF generation...")
ani = FuncAnimation(fig, update, frames=frames, interval=100)
output_path = r"d:\WebSite\xymount.gif"
ani.save(output_path, writer=PillowWriter(fps=15))
print("\nGIF saved to:", output_path)
