import os
import sys
import math
import time
import threading
from PIL import Image
import customtkinter as ctk

# Force Pygame to run headlessly behind the scenes
os.environ['SDL_VIDEODRIVER'] = 'dummy'
try:
    import pygame
except ImportError:
    print("Pygame missing! Install it via: pip install pygame pillow")
    sys.exit(1)

class Headless3DEngine:
    """Calculates 3D math projections and draws an orientation block to an image buffer."""
    def __init__(self, width=440, height=360):
        pygame.init()
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        
        # 3D rectangular box vertices (Submarine Sled profile representation)
        self.vertices = [
            [-110, -25, -45], [110, -25, -45], [110, 25, -45], [-110, 25, -45],
            [-110, -25, 45],  [110, -25, 45],  [110, 25, 45],  [-110, 25, 45]
        ]
        # Faces mapped to coordinate indexes with custom coloring
        self.faces = [
            ([0, 1, 2, 3], (0, 180, 180)),    # Front Nose (Cyan)
            ([4, 5, 6, 7], (180, 50, 50)),    # Rear Tail (Red)
            ([0, 1, 5, 4], (30, 160, 70)),    # Top Deck (Green)
            ([2, 3, 7, 6], (40, 40, 40)),      # Bottom Hull (Dark Gray)
            ([0, 3, 7, 4], (50, 100, 180)),   # Left Port Side (Blue)
            ([1, 2, 6, 5], (180, 180, 40))    # Right Starboard Side (Yellow)
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
            avg_z = sum(rotated_vertices[v][2] for v in face) / 4.0
            face_depths.append((avg_z, face, color))
        face_depths.sort(key=lambda item: item[0], reverse=True)

        # Draw projected geometry polygons
        for _, face, color in face_depths:
            points = [(rotated_vertices[v][0], rotated_vertices[v][1]) for v in face]
            pygame.draw.polygon(self.surface, color, points)
            pygame.draw.polygon(self.surface, (200, 200, 200), points, 1) # Wireframe edges

        raw_str = pygame.image.tostring(self.surface, 'RGB')
        return Image.frombytes('RGB', (self.width, self.height), raw_str)


class SubmarineTelemetryDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RC Submarine Integrated Control Center")
        self.geometry("1100x620")
        ctk.set_appearance_mode("dark")
        
        # Grid Architecture definition
        self.grid_columnconfigure(0, weight=4) # Left: Raw data display fields
        self.grid_columnconfigure(1, weight=5) # Right: Visual rendering environment
        self.grid_rowconfigure(0, weight=1)

        # Initialize internal 3D Engine Frame
        self.render_engine = Headless3DEngine(460, 380)

        # ==========================================
        # LEFT REGION: TELEMETRY DISPLAY FRAME
        # ==========================================
        self.left_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Panel Section Header
        self.main_title = ctk.CTkLabel(self.left_frame, text="SYSTEM CRADLE TELEMETRY", font=("Arial", 18, "bold"), text_color="#00cccc")
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

        # Group Frame 2: Hardware Control States
        self.state_group = ctk.CTkFrame(self.left_frame, fg_color="#262626")
        self.state_group.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(self.state_group, text="MOTOR CONTROL MACHINE STATE", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=2)
        self.lbl_state = ctk.CTkLabel(self.state_group, text="STOPPED", font=("Arial", 14, "bold"), text_color="#ffb300")
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

        # Group Frame 4: Raw GY-521 Array Coordinates
        self.imu_group = ctk.CTkFrame(self.left_frame, fg_color="#262626")
        self.imu_group.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(self.imu_group, text="GY-521 NAVIGATION MATRIX VECTORS", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=2)
        self.lbl_accel = ctk.CTkLabel(self.imu_group, text="Accel -> AX: 0.00 | AY: 0.00 | AZ: 0.00", font=("Arial", 13))
        self.lbl_accel.pack(anchor="w", padx=15)
        self.lbl_gyro = ctk.CTkLabel(self.imu_group, text="Gyro  -> GX: 0.00 | GY: 0.00 | GZ: 0.00", font=("Arial", 13))
        self.lbl_gyro.pack(anchor="w", padx=15, pady=(0, 5))

        # Group Frame 5: CPU Benchmarking Tracker
        self.cpu_group = ctk.CTkFrame(self.left_frame, fg_color="#262626")
        self.cpu_group.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(self.cpu_group, text="MICROCONTROLLER PROFILING RUNTIME", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=2)
        self.lbl_cpu = ctk.CTkLabel(self.cpu_group, text="Core CPU Load: 0.00%", font=("Arial", 13))
        self.lbl_cpu.pack(anchor="w", padx=15, pady=(0, 5))


        # ==========================================
        # RIGHT REGION: VISUAL ATTITUDE RENDERING FRAME
        # ==========================================
        self.right_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.right_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        self.render_title = ctk.CTkLabel(self.right_frame, text="REAL-TIME ORIENTATION MONITOR", font=("Arial", 18, "bold"), text_color="#00cccc")
        self.render_title.pack(pady=12)

        # Native label wrapper used as an image pipeline interface display screen
        self.screen_3d = ctk.CTkLabel(self.right_frame, text="")
        self.screen_3d.pack(padx=15, pady=10, fill="both", expand=True)

        # Thread Control Flag
        self.thread_running = True
        
        # Kick off background pipeline loop thread to mimic your hardware serial stream handler
        self.serial_consumer_worker = threading.Thread(target=self.serial_ingestion_engine, daemon=True)
        self.serial_consumer_worker.start()

    def serial_ingestion_engine(self):
        """
        Simulates your non-blocking while loop data ingestion background engine.
        Parses incoming hardware serial line telemetry frames using your 14-variable contract.
        """
        step = 0.0
        while self.thread_running:
            # 1. Generate mocking variables to simulate data output
            mock_rpm = int(1200 + math.sin(step * 0.5) * 400)
            mock_pot = int(2048 + math.sin(step) * 1500)
            mock_pwm = (mock_pot / 4095.0) * 100.0
            
            # Oscillating state loops to generate dynamic enum strings
            state_val = int(step) % 3
            mock_state = "STOPPED" if state_val == 0 else "FORWARD" if state_val == 1 else "REVERSE"
            
            # Logic high switches
            mock_pin1 = 1 if math.sin(step * 2) > 0 else 0
            mock_pin2 = 1 if math.cos(step * 1.5) > 0 else 0
            mock_pin3 = 0 if mock_rpm < 1100 else 1
            
            # Matrix axis coordinates matching your sensor vectors
            mock_ax = math.sin(step * 0.8) * 1.1
            mock_ay = math.cos(step * 1.1) * 0.9
            mock_az = math.sin(step * 0.5) * 9.8
            
            mock_gx = math.cos(step * 1.4) * 50.0
            mock_gy = math.sin(step * 0.9) * 35.0
            mock_gz = math.cos(step * 0.6) * 12.0
            
            mock_cpu = 42.5 + math.sin(step * 3) * 5.0

            # 2. Emulate Euler integration conversions (Pitch/Roll/Yaw metrics matching the IMU matrix output)
            sim_pitch = math.sin(step * 0.6) * 30.0
            sim_roll = math.cos(step * 1.1) * 45.0
            sim_yaw = (step * 8.0) % 360.0

            # 3. Create simulated comma-separated packet string contract (14 variables total)
            # Contract Schema: RPM,POT,PWM,STATE,PIN1,PIN2,PIN3,AX,AY,AZ,GX,GY,GZ,CPU
            packet_payload = f"{mock_rpm},{mock_pot},{mock_pwm:.2f},{mock_state},{mock_pin1},{mock_pin2},{mock_pin3},{mock_ax:.2f},{mock_ay:.2f},{mock_az:.2f},{mock_gx:.2f},{mock_gy:.2f},{mock_gz:.2f},{mock_cpu:.2f}"
            
            # 4. Ingest and parse data string stream
            raw_tokens = packet_payload.strip().split(',')
            if len(raw_tokens) == 14:
                # Dispatched cross-thread call via Tkinter scheduler loops to prevent graphics lockup
                self.after(0, self.update_dashboard_ui, raw_tokens, sim_pitch, sim_roll, sim_yaw)

            time.sleep(0.02) # ~50Hz execution loops matching raw Serial polling speeds
            step += 0.03

    def update_dashboard_ui(self, dataset, pitch, roll, yaw):
        """Processes text transformations and triggers the headless pixel matrix buffer updates."""
        # Unpack indices mapped straight to the layout labels
        rpm, pot, pwm, state, p1, p2, p3, ax, ay, az, gx, gy, gz, cpu = dataset

        # Update Propulsion Section
        self.lbl_rpm.configure(text=f"Motor Speed: {rpm} RPM")
        self.lbl_pot.configure(text=f"Potentiometer ADC: {pot} / 4095")
        self.lbl_pwm.configure(text=f"Duty Cycle: {pwm}%")

        # Update Control Machine State String text configurations
        self.lbl_state.configure(text=state)
        if state == "FORWARD":
            self.lbl_state.configure(text_color="#1db954") # Green
        elif state == "REVERSE":
            self.lbl_state.configure(text_color="#e94560") # Red
        else:
            self.lbl_state.configure(text_color="#ffb300") # Amber

        # Update Hardware Interface Pins
        self.lbl_led1.configure(text=f"LED Pin 1: {'ON' if p1=='1' else 'OFF'}", text_color="#1db954" if p1=='1' else "#888888")
        self.lbl_led2.configure(text=f"LED Pin 2: {'ON' if p2=='1' else 'OFF'}", text_color="#1db954" if p2=='1' else "#888888")
        self.lbl_led3.configure(text=f"LED Pin 3: {'ON' if p3=='1' else 'OFF'}", text_color="#1db954" if p3=='1' else "#888888")

        # Update Vectors Array Coordinate Text Fields
        self.lbl_accel.configure(text=f"Accel -> AX: {ax} | AY: {ay} | AZ: {az}")
        self.lbl_gyro.configure(text=f"Gyro  -> GX: {gx} | GY: {gy} | GZ: {gz}")

        # Update Benchmark
        self.lbl_cpu.configure(text=f"Core CPU Load: {cpu}%")

        #Convert raw IMU strings to 3D degrees
        try:
            # Cast raw string tokens into floats safely
            raw_ax = float(ax)
            raw_ay = float(ay)
            raw_az = float(az)

            # Calculate Pitch and Roll from Accelerometer Gravity Vectors
            calculated_pitch = math.atan2(raw_ax, math.sqrt(raw_ay**2 + raw_az**2)) * (180.0 / math.pi)
            calculated_roll = math.atan2(raw_ay, raw_az) * (180.0 / math.pi)

            # For Yaw, fallback to the background integration loop variable
            # until a Magnetometer / Kalman integration step is added.
            calculated_yaw = yaw

        except ValueError:
            # Handle corrupted serial string tokens gracefully without breaking layout loops
            calculated_pitch, calculated_roll, calculated_yaw = 0.0, 0.0, 0.0


        # Run 3D calculations on headless pipeline and load image frame matrix
        pil_frame = self.render_engine.render(calculated_pitch, calculated_roll, calculated_yaw)
        ctk_image_obj = ctk.CTkImage(light_image=pil_frame, dark_image=pil_frame, size=(460, 380))
        
        # Refresh drawing surface layout image
        self.screen_3d.configure(image=ctk_image_obj)
        self.screen_3d.image = ctk_image_obj

    def destroy(self):
        """Graceful thread termination breakdown sequence."""
        self.thread_running = False
        pygame.quit()
        super().destroy()

if __name__ == "__main__":
    app = SubmarineTelemetryDashboard()
    app.mainloop()
