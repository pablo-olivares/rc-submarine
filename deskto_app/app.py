import threading
import time
import customtkinter as ctk
import serial

# --- CONFIGURATION ---
SERIAL_PORT = "COM3"  # <-- Double-check your COM port number!
BAUD_RATE = 115200

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FullTelemetryApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("RC Submarine Master Telemetry Center")
        self.geometry("600x550")

        # --- UI LAYOUT DESIGN ---
        self.header_label = ctk.CTkLabel(
            self, text="RC SUBMARINE SYSTEM DATA", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.pack(pady=15)

        # Main Grid Container to split data side-by-side
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=20, pady=5)

        # === LEFT PANEL: Motor & Power Metrics ===
        self.left_panel = ctk.CTkFrame(self.grid_container, width=270)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.motor_lbl = ctk.CTkLabel(self.left_panel, text="PROMOTION & POWER", font=ctk.CTkFont(size=14, weight="bold"))
        self.motor_lbl.pack(pady=10)

        # RPM Card
        self.rpm_val = self.create_data_row(self.left_panel, "Shaft Velocity:", "0 RPM", text_color="#1f538d", size=20)
        # Pot Card
        self.pot_val = self.create_data_row(self.left_panel, "Potentiometer Input:", "0 / 4095")
        # PWM Duty Card
        self.pwm_val = self.create_data_row(self.left_panel, "PWM Duty Cycle:", "0%")
        # CPU Load Benchmark Card
        self.cpu_val = self.create_data_row(self.left_panel, "CPU Load Benchmark:", "0%", text_color="#d32f2f")

        # === RIGHT PANEL: Hardware Pins & Status ===
        self.right_panel = ctk.CTkFrame(self.grid_container, width=270)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.status_lbl = ctk.CTkLabel(self.right_panel, text="HARDWARE STATE PINS", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_lbl.pack(pady=10)

        # LED Status Rows
        self.led1_val = self.create_data_row(self.right_panel, "Status LED 1:", "OFF")
        self.led2_val = self.create_data_row(self.right_panel, "Status LED 2:", "OFF")
        self.led3_val = self.create_data_row(self.right_panel, "Status LED 3:", "OFF")

        # === BOTTOM PANEL: IMU Navigation Data ===
        self.imu_panel = ctk.CTkFrame(self)
        self.imu_panel.pack(fill="x", padx=30, pady=15)

        self.imu_lbl = ctk.CTkLabel(self.imu_panel, text="GY-521 IMU NAVIGATION VECTOR", font=ctk.CTkFont(size=14, weight="bold"))
        self.imu_lbl.pack(pady=5)

        self.accel_val = ctk.CTkLabel(self.imu_panel, text="Accel ──> X: 0 | Y: 0 | Z: 0", font=ctk.CTkFont(size=14, family="Courier"))
        self.accel_val.pack(pady=2)

        self.gyro_val = ctk.CTkLabel(self.imu_panel, text="Gyro  ──> X: 0 | Y: 0 | Z: 0", font=ctk.CTkFont(size=14, family="Courier"))
        self.gyro_val.pack(pady=8)

        # Status Footer Bar
        self.status_label = ctk.CTkLabel(self, text="Awaiting handshake with STM32...", text_color="yellow")
        self.status_label.pack(side="bottom", pady=5)

        # --- DATA PIPELINE THREADING ---
        self.running = True
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()

    def create_data_row(self, parent, label_text, default_val, text_color=None, size=14):
        """Helper function to cleanly pack structured visual data frames."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=6)
        lbl = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=12))
        lbl.pack(side="left", padx=5)
        val = ctk.CTkLabel(frame, text=default_val, font=ctk.CTkFont(size=size, weight="bold"), text_color=text_color)
        val.pack(side="right", padx=5)
        return val

    def read_serial_data(self):
        while self.running:
            try:
                with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1.5) as ser:
                    self.status_label.configure(text=f"CONNECTED TO {SERIAL_PORT} (STREAM LIVE)", text_color="green")

                    while self.running:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line:
                            data_fields = line.split(",")

                            # Match your exact 12-variable packet configuration
                            if len(data_fields) == 13:
                                rpm, pot, duty, led1, led2, led3, ax, ay, az, gx, gy, gz, cpu_load = data_fields

                                # Update Left Panel
                                self.rpm_val.configure(text=f"{rpm} RPM")
                                self.pot_val.configure(text=f"{pot} / 4095")
                                self.pwm_val.configure(text=f"{duty}%")
                                self.cpu_val.configure(text=f"{cpu_load} %")

                                # Update Right Panel (Color code matching states)
                                self.led1_val.configure(text=led1, text_color="green" if "ON" in led1 else "gray")
                                self.led2_val.configure(text=led2, text_color="green" if "ON" in led2 else "gray")
                                self.led3_val.configure(text=led3, text_color="green" if "ON" in led3 else "gray")

                                # Update Bottom IMU Vectors
                                self.accel_val.configure(text=f"Accel ──> X: {ax.strip()} | Y: {ay.strip()} | Z: {az.strip()}")
                                self.gyro_val.configure(text=f"Gyro  ──> X: {gx.strip()} | Y: {gy.strip()} | Z: {gz.strip()}")

            except (serial.SerialException, IndexError):
                self.status_label.configure(text="CONNECTION BREAKDOWN. Retrying link pipeline...", text_color="red")
                time.sleep(1.5)

    def destroy(self):
        self.running = False
        super().destroy()


if __name__ == "__main__":
    app = FullTelemetryApp()
    app.mainloop()
