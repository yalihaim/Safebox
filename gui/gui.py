import customtkinter as ctk
from tkinter import filedialog, simpledialog, messagebox
import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from client import client

# === Global Styling ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class PrettySafeBoxGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SafeBox Secure Client")
        self.geometry("750x550")
        self.resizable(False, False)

        # === Fonts ===
        self.header_font = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        self.normal_font = ctk.CTkFont(size=14)

        # === Main Frame ===
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#222", width=600, height=450)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.client_id = ctk.StringVar(value="client123")
        self.build_gui()

    def build_gui(self):
        # Header
        ctk.CTkLabel(self.main_frame, text="🚀 SafeBox Secure Client", font=self.header_font).pack(pady=(20, 10))

        # Client ID input
        ctk.CTkLabel(self.main_frame, text="Client ID:", font=self.normal_font).pack()
        ctk.CTkEntry(self.main_frame, textvariable=self.client_id, width=240, corner_radius=10).pack(pady=5)

        # Buttons
        button_style = {"width": 200, "height": 40, "corner_radius": 12, "font": self.normal_font}
        ctk.CTkButton(self.main_frame, text="📤 Upload File", command=self.choose_file, **button_style).pack(pady=8)
        ctk.CTkButton(self.main_frame, text="📥 Download File", command=self.prompt_download, **button_style).pack(pady=8)
        ctk.CTkButton(self.main_frame, text="🗂️ List Files", command=self.list_files_gui, **button_style).pack(pady=8)

        # Log box
        self.log_box = ctk.CTkTextbox(self.main_frame, width=520, height=140, font=("Consolas", 12))
        self.log_box.pack(pady=10)
        self.log_box.configure(state="disabled")

    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def choose_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                response = client.upload_file(file_path, self.client_id.get())
                self.log(f"Upload: {os.path.basename(file_path)} -> {response.status_code}")
                if response.status_code == 200:
                    self.log("✅ Upload succeeded and file deleted.")
            except Exception as e:
                self.log(f"❌ Upload error: {e}")

    def prompt_download(self):
        filename = simpledialog.askstring("Download File", "Enter filename to download:")
        if filename:
            try:
                response = client.download_file(filename, self.client_id.get())
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    self.log(f"✅ Downloaded {filename} successfully.")
                else:
                    self.log(f"❌ Download failed: {response.status_code} - {response.text}")
            except Exception as e:
                self.log(f"❌ Download error: {e}")

    def list_files_gui(self):
        try:
            response = client.list_files(self.client_id.get())
            if response.status_code == 200:
                self.log("📁 Files:\n" + "\n".join(response.json()))
            else:
                self.log(f"❌ List error: {response.status_code} - {response.text}")
        except Exception as e:
            self.log(f"❌ List error: {e}")


if __name__ == "__main__":
    app = PrettySafeBoxGUI()
    app.mainloop()
