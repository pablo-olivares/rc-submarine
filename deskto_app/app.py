import threading
import time
import customtkinter as ctk
import serial

# --- CONFIGURATION ---
# Change 'COM3' to match your actual STM32 virtual COM port (e.g., '/dev/ttyACM0' on Linux/Mac)
SERIAL_PORT = "COM3"
BAUD_RATE = 115200

# Initialize CustomTkinter Window Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TelemetryApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("STM32 Motor & IMU Telemetry Panel")
        self.geometry("500x400")

        # --- UI LAYOUT DESIGN ---
        self.header_label = ctk.CTkLabel(
            self, text="SYSTEM TELEMETRY", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.header_label.pack(pady=20)

        # Motor RPM Display Box
        self.rpm_frame = ctk.CTkFrame(self)
        self.rpm_frame.pack(fill="x", padx=40, pady=10)
        self.rpm_title = ctk.CTkLabel(
            self.rpm_frame, text="Motor Output Speed:", font=ctk.CTkFont(size=14)
        )
        self.rpm_title.pack(side="left", padx=20, pady=10)
        self.rpm_val = ctk.CTkLabel(
            self.rpm_frame,
            text="0 RPM",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1f538d",
        )
        self.rpm_val.pack(side="right", padx=20, pady=10)

        # Potentiometer / PWM Display Box
        self.pot_frame = ctk.CTkFrame(self)
        self.pot_frame.pack(fill="x", padx=40, pady=10)
        self.pot_title = ctk.CTkLabel(
            self.pot_frame, text="Potentiometer (ADC):", font=ctk.CTkFont(size=14)
        )
        self.pot_title.pack(side="left", padx=20, pady=10)
        self.pot_val = ctk.CTkLabel(
            self.pot_frame,
            text="0",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.pot_val.pack(side="right", padx=20, pady=10)

        # MPU6050 Accelerometer Display Box
        self.imu_frame = ctk.CTkFrame(self)
        self.imu_frame.pack(fill="x", padx=40, pady=10)
        self.imu_title = ctk.CTkLabel(
            self.imu_frame, text="IMU Accelerometer:", font=ctk.CTkFont(size=14)
        )
        self.imu_title.pack(anchor="w", padx=20, pady=5)

        self.imu_val = ctk.CTkLabel(
            self.imu_frame,
            text="X: 0  |  Y: 0  |  Z: 0",
            font=ctk.CTkFont(size=16, family="Courier"),
        )
        self.imu_val.pack(pady=10)

        # Status Footer Bar
        self.status_label = ctk.CTkLabel(
            self, text="Connecting to STM32...", text_color="yellow"
        )
        self.status_label.pack(side="bottom", pady=10)

        # --- DATA PIPELINE THREADING ---
        self.running = True
        self.serial_thread = threading.Thread(
            target=self.read_serial_data, daemon=True
        )
        self.serial_thread.start()

    def read_serial_data(self):
        """Background thread worker to poll raw data packets from the serial cable channel."""
        while self.running:
            try:
                with serial.Serial(
                    SERIAL_PORT, BAUD_RATE, timeout=1.5
                ) as ser:
                    self.status_label.configure(
                        text=f"Connected to {SERIAL_PORT}", text_color="green"
                    )

                    while self.running:
                        line = (
                            ser.readline().decode("utf-8", errors="ignore").strip()
                        )
                        if line:
                            # Split comma separated elements back into array variables
                            data_fields = line.split(",")

                            if len(data_fields) == 5:
                                rpm, pot, acc_x, acc_y, acc_z = data_fields

                                # Safely push UI graphical changes back onto main loop tree
                                self.rpm_val.configure(text=f"{rpm} RPM")
                                self.pot_val.configure(text=f"{pot} / 4095")
                                self.imu_val.configure(
                                    text=f"X: {acc_x} | Y: {acc_y} | Z: {acc_z}"
                                )

            except (serial.SerialException, IndexError):
                # Gracefully handle disconnects/reboots of the development board
                self.status_label.configure(
                    text="Connection Lost. Retrying...", text_color="red"
                )
                time.sleep(2.0)

    def destroy(self):
        self.running = False
        super().destroy()


if __name__ == "__main__":
    app = TelemetryApp()
    app.mainloop()
