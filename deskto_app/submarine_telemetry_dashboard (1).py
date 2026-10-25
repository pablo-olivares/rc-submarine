import os
import sys
import math
import time
import threading
from PIL import Image
import customtkinter as ctk

# Ensure Pygame runs headlessly behind the scenes
os.environ['SDL_VIDEODRIVER'] = 'dummy'
try:
    import pygame
except ImportError:
    print("Pygame missing! Install it via: pip install pygame-ce pillow pyserial")
    sys.exit(1)

try:
    import serial
except ImportError:
    print("PySerial missing! Install it via: pip install pyserial")
    sys.exit(1)

class Headless3DEngine:
    """Calculates 3D math projections and draws an orientation block to an image buffer."""
    def __init__(self, width=460, height=380, obj_filepath="submarine_hull.obj"):
        pygame.init()
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))

        # Automatically load the custom submarine structural CAD design
        self.load_obj_mesh(obj_filepath)

    def load_obj_mesh(self, filepath):
        """Parses a universal OBJ file to extract physical 3D mesh vectors."""
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    if line.startswith('v'):
                        # Extract raw vertex elements: v x y z
                        parts = line.split()
                        # Apply a scale factor to size the CAD model nicely on screen
                        x = float(parts[1]) * 1.5
                        y = float(parts[2]) * 1.5
                        z = float(parts[3]) * 1.5
                        self.vertices.append([x,y,z])

                    elif line.startswith('f'):
                        # Extract face connectivity mapping index keys: f v1/vt1/vn1 v2/vt2/vn2 ...
                        parts = line.split()[1:]
                        face_indices = []
                        for part in parts:
                            # OBJ file indexing is 1-based; convert to Python 0-based indexing
                            idx = int(part.split('/')[0]) - 1
                            face_indices.append(idx)

                        # Apply a shaded color theme across the imported panels
                        # You can also randomize these colors slightly to create visible surface shading
                        color = (0, 150, 160)
                        self.faces.append((tuple(face_indices), color))

                print(f"CAD Mesh Loaded Successfully: {len(self.vertices)} vertices, {len(self.faces)} faces.")

        except Exception as e:
            print(f"Mesh loading defaulted to safety block profile: {e}")
            # Fallback safe bounding box configuration if the file is missing or corrupted
            # 3D rectangular box vertices (Submarine Sled profile representation)
            self.vertices = [
                [-45, -110, -25], [45, -110, -25], [45, 110, -25], [-45, 110, -25],
                [-45, -110, 45],  [45, -110, 45], [45, 110, 45],  [-45, 110, 45]
            ]
            # Faces mapped to coordinate indexes with custom coloring
            self.faces = [
                ((0, 1, 2, 3), (30, 160, 70)),    # Top Deck (Green)
                ((4, 5, 6, 7), (40, 40, 40)),      # Bottom Hull (Dark Gray)
                ((0, 1, 5, 4), (0, 180, 180)),    # Front Nose (Cyan)
                ((2, 3, 7, 6), (180, 50, 50)),    # Rear Tail (Red)
                ((0, 3, 7, 4), (50, 100, 180)),   # Left Port Side (Blue)
                ((1, 2, 6, 5), (180, 180, 40))    # Right Starboard Side (Yellow)
            ]

    def render(self, pitch, roll, yaw):
        """Applies Euler angles transformations using a solid depth-sorted projection."""
        self.surface.fill((24, 24, 24)) # Matches background gray
        
        # Convert incoming telemetry floats to radians
        rad_p = math.radians(pitch)
        rad_r = math.radians(roll)
        rad_y = math.radians(yaw)

        rotated_vertices = []
        for x, y, z in self.vertices:
            # 1. Roll transformation (Z-Axis)
            x1 = x * math.cos(rad_r) - y * math.sin(rad_r)
            y1 = x * math.sin(rad_r) + y * math.cos(rad_r)
            z1 = z

            # 2. Pitch transformation (X-Axis)
            x2 = x1
            y2 = y1 * math.cos(rad_p) - z1 * math.sin(rad_p)
            z2 = y1 * math.sin(rad_p) + z1 * math.cos(rad_p)

            # 3. Yaw transformation (Y-Axis)
            x3 = x2 * math.cos(rad_y) + z2 * math.sin(rad_y)
            y3 = y2
            z3 = -x2 * math.sin(rad_y) + z2 * math.cos(rad_y)

            # Perspective matrix distance calculation
            view_dist = 450
            scale = view_dist / (view_dist + z3)
            proj_x = int(self.width / 2 + x3 * scale)
            proj_y = int(self.height / 2 + y3 * scale)
            rotated_vertices.append((proj_x, proj_y, z3))

        # Depth-sorting (Z-Buffering emulation)
        face_depths = []
        for face, color in self.faces:
            # FIXED: Targets index 2 of each vertex tuple to sum only Z-axis depth values
            avg_z = sum(rotated_vertices[v][2] for v in face) / 4.0
            face_depths.append((avg_z, face, color))
        face_depths.sort(key=lambda item: item[0], reverse=True)

        # Draw projected geometry polygons
        for _, face, color in face_depths:
            points = [(rotated_vertices[v][0], rotated_vertices[v][1]) for v in face]
            pygame.draw.polygon(self.surface, color, points)
            pygame.draw.polygon(self.surface, (200, 200, 200), points, 1) # Wireframe edges

        raw_str = pygame.image.tobytes(self.surface, 'RGB')
        return Image.frombytes('RGB', (self.width, self.height), raw_str)


class SubmarineTelemetryDashboard(ctk.CTk):
    def __init__(self, serial_port="COM3", baud_rate=115200):
        super().__init__()
        self.title("RC Submarine Integrated Control Center")
        self.geometry("1100x620")
        ctk.set_appearance_mode("dark")
        
        self.serial_port = serial_port
        self.baud_rate = baud_rate

        # Grid Layout Definition
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        self.render_engine = Headless3DEngine(460, 380)

        # ==========================================
        # LEFT REGION: TELEMETRY DISPLAY FRAME
        # ==========================================
        self.left_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        self.main_title = ctk.CTkLabel(self.left_frame, text="SYSTEM LIVE TELEMETRY", font=("Arial", 18, "bold"), text_color="#00cccc")
        self.main_title.pack(pady=12)

        # Group Frame 1: Power & Propulsion
        self.power_group = ctk.CTkFrame(self.left_frame, fg_color="#262626")
        self.power_group.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(self.power_group, text="POWER & PROPULSION SYSTEM", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=2)
        self.lbl_rpm = ctk.CTkLabel(self.power_group, text="Motor Speed: 0 RPM", font=("Arial", 13))
        self.lbl_rpm.pack(anchor="w", padx=15)
        self.lbl_pot = ctk.CTkLabel(self.power_group, text="Potentiometer ADC: 0 / 4095", font=("Arial", 13))
        self.lbl_pot.pack(anchor="w", padx=15)
        self.lbl_pwm = ctk.CTkLabel(self.power_group, text="Duty Cycle: 0.0%", font=("Arial", 13))
        self.lbl_pwm.pack(anchor="w", padx=15, pady=(0, 5))

        # Group Frame 2: Motor Control States
        self.state_group = ctk.CTkFrame(self.left_frame, fg_color="#262626")
        self.state_group.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(self.state_group, text="MOTOR CONTROL MACHINE STATE", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=2)
        self.lbl_state = ctk.CTkLabel(self.state_group, text="OFFLINE", font=("Arial", 14, "bold"), text_color="#ffb300")
        self.lbl_state.pack(anchor="w", padx=15, pady=(0, 5))

        # Group Frame 3: Logic Hardware Pins
        self.pins_group = ctk.CTkFrame(self.left_frame, fg_color="#262626")
        self.pins_group.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(self.pins_group, text="HARDWARE INTERFACE LOGIC PINS", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=2)
        self.lbl_led1 = ctk.CTkLabel(self.pins_group, text="LED Pin 1: OFF", font=("Arial", 13), text_color="#888888")
        self.lbl_led1.pack(anchor="w", padx=15)
        self.lbl_led2 = ctk.CTkLabel(self.pins_group, text="LED Pin 2: OFF", font=("Arial", 13), text_color="#888888")
        self.lbl_led2.pack(anchor="w", padx=15)
        self.lbl_led3 = ctk.CTkLabel(self.pins_group, text="LED Pin 3: OFF", font=("Arial", 13), text_color="#888888")
        self.lbl_led3.pack(anchor="w", padx=15, pady=(0, 5))

        # Group Frame 4: GY-521 Data Array
        self.imu_group = ctk.CTkFrame(self.left_frame, fg_color="#262626")
        self.imu_group.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(self.imu_group, text="GY-521 NAVIGATION MATRIX VECTORS", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=2)
        self.lbl_accel = ctk.CTkLabel(self.imu_group, text="Accel -> AX: 0 | AY: 0 | AZ: 0", font=("Arial", 13))
        self.lbl_accel.pack(anchor="w", padx=15)
        self.lbl_gyro = ctk.CTkLabel(self.imu_group, text="Gyro  -> GX: 0 | GY: 0 | GZ: 0", font=("Arial", 13))
        self.lbl_gyro.pack(anchor="w", padx=15)
        self.lbl_angles = ctk.CTkLabel(self.imu_group, text="Calculated -> Pitch: 0.00° | Roll: 0.00°", font=("Arial", 13), text_color="#00cccc")
        self.lbl_angles.pack(anchor="w", padx=15, pady=(0, 5))

        # Group Frame 5: CPU Benchmarking Tracker
        self.cpu_group = ctk.CTkFrame(self.left_frame, fg_color="#262626")
        self.cpu_group.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(self.cpu_group, text="MICROCONTROLLER PROFILING RUNTIME", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=2)
        self.lbl_cpu = ctk.CTkLabel(self.cpu_group, text="Core CPU Load: 0.00%", font=("Arial", 13))
        self.lbl_cpu.pack(anchor="w", padx=15, pady=(0, 5))

        # Connection Status Bar
        self.lbl_conn_status = ctk.CTkLabel(self.left_frame, text="Status: Disconnected", font=("Arial", 12, "italic"), text_color="#e94560")
        self.lbl_conn_status.pack(pady=5)

        # ==========================================
        # RIGHT REGION: VISUAL ATTITUDE RENDERING FRAME
        # ==========================================
        self.right_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.right_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        self.render_title = ctk.CTkLabel(self.right_frame, text="REAL-TIME ORIENTATION MONITOR", font=("Arial", 18, "bold"), text_color="#00cccc")
        self.render_title.pack(pady=12)

        self.screen_3d = ctk.CTkLabel(self.right_frame, text="")
        self.screen_3d.pack(padx=15, pady=10, fill="both", expand=True)

        self.thread_running = True
        self.serial_worker = threading.Thread(target=self.serial_hardware_ingestion_engine, daemon=True)
        self.serial_worker.start()

    def serial_hardware_ingestion_engine(self):
        while self.thread_running:
            try:
                self.lbl_conn_status.configure(text=f"Status: Searching on {self.serial_port}...", text_color="#ffb300")
                with serial.Serial(self.serial_port, self.baud_rate, timeout=0.5) as ser:
                    ser.reset_input_buffer()
                    self.lbl_conn_status.configure(text=f"Status: Connected to {self.serial_port}", text_color="#1db954")
                    
                    while self.thread_running:
                        # This guarantees you are reading the latest real-time physical packet
                        if ser.in_waiting > 200:
                            ser.reset_input_buffer()

                        if ser.in_waiting:
                            try:
                                # Read raw line directly from the peripheral
                                raw_bytes = ser.readline()
                                if not raw_bytes:
                                    continue

                                raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
                                if not raw_line:
                                    continue
                                    
                                raw_tokens = raw_line.split(',')
                                
                                # Enforce index safety boundaries to guarantee full aligned dataset extraction
                                if len(raw_tokens) >= 14:
                                    self.after(0, self.update_dashboard_ui, raw_tokens[:14])
                            except Exception as parse_err:
                                print(f"Parser processing glitch: {parse_err}")
                        
                        time.sleep(0.005)
                        
            except serial.SerialException:
                self.lbl_conn_status.configure(text=f"Status: Device disconnected. Retrying link...", text_color="#e94560")
                time.sleep(2.0)

    def update_dashboard_ui(self, dataset):
        """Unpacks fields and runs scale conversions according to aligned telemetry contract."""
        rpm, pot, pwm, p1, p2, p3, ax, ay, az, gx, gy, gz, cpu, state = dataset

        # Update Propulsion Section
        self.lbl_rpm.configure(text=f"Motor Speed: {rpm} RPM")
        self.lbl_pot.configure(text=f"Potentiometer ADC: {pot} / 4095")
        self.lbl_pwm.configure(text=f"Duty Cycle: {pwm}%")

        # Update Control Machine State String text configurations Safely
        self.lbl_state.configure(text=state)
        if "FORWARD" in state or "ON" in state:
            self.lbl_state.configure(text_color="#1db954")
        elif "REVERSE" in state:
            self.lbl_state.configure(text_color="#e94560")
        else:
            self.lbl_state.configure(text_color="#ffb300")

        # Update Hardware Interface Pins
        self.lbl_led1.configure(text=f"LED Pin 1: {'ON' if p1=='1' or p1=='ON' else 'OFF'}", text_color="#1db954" if (p1=='1' or p1=='ON') else "#888888")
        self.lbl_led2.configure(text=f"LED Pin 2: {'ON' if p2=='1' or p2=='ON' else 'OFF'}", text_color="#1db954" if (p2=='1' or p2=='ON') else "#888888")
        self.lbl_led3.configure(text=f"LED Pin 3: {'ON' if p3=='1' or p3=='ON' else 'OFF'}", text_color="#1db954" if (p3=='1' or p3=='ON') else "#888888")

        # Update Vectors Array Coordinate Text Fields
        self.lbl_accel.configure(text=f"Accel -> AX: {ax} | AY: {ay} | AZ: {az}")
        self.lbl_gyro.configure(text=f"Gyro  -> GX: {gx} | GY: {gy} | GZ: {gz}")
        self.lbl_cpu.configure(text=f"Core CPU Load: {cpu}%")

        # ==========================================
        # 📐 SCALED IMU CONVERSION (RAW REGISTER TO G-FORCE)
        # ==========================================
        try:
            # Values are already processed into true physical g-units by the STM32!
            raw_ax = float(ax) / 16384.0
            raw_ay = float(ay) / 16384.0
            raw_az = float(az) / 16384.0
            
            # Run trigonometry on the normalized acceleration coordinates
            calculated_pitch = math.atan2(raw_ax, math.sqrt(raw_ay**2 + raw_az**2)) * (180.0 / math.pi)
            calculated_roll = math.atan2(raw_ay, raw_az) * (180.0 / math.pi)
            calculated_yaw = 0.0 
            
            self.lbl_angles.configure(text=f"Calculated -> Pitch: {calculated_pitch:.2f}° | Roll: {calculated_roll:.2f}°")
        except (ValueError, ZeroDivisionError):
            calculated_pitch, calculated_roll, calculated_yaw = 0.0, 0.0, 0.0

        # Pass live variables to rendering engine
        pil_frame = self.render_engine.render(calculated_pitch, calculated_roll, calculated_yaw)
        ctk_image_obj = ctk.CTkImage(light_image=pil_frame, dark_image=pil_frame, size=(460, 380))
        
        self.screen_3d.configure(image=ctk_image_obj)
        self.screen_3d.image = ctk_image_obj

    def destroy(self):
        self.thread_running = False
        pygame.quit()
        super().destroy()

if __name__ == "__main__":
    # Adjust "COM3" to match your active Windows Device Manager assignment
    app = SubmarineTelemetryDashboard(serial_port="COM3", baud_rate=115200)
    app.mainloop()
