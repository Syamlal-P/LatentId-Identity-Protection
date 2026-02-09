import torch
import torch.nn.functional as F
from diffusers import AutoencoderKL
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os

class CloakIDEngine:
    """
    Core Adversarial Engine implementing Layer 1: Latent Space Poisoning.
    Uses a targeted gradient attack against the VAE (Variational Autoencoder).
    """
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[*] Initializing CloakID Engine on {self.device}...")
        
        # We use the VAE from Stable Diffusion as the attack target
        # This is the 'Latent Poisoning' mentioned in your synopsis
        try:
            self.vae = AutoencoderKL.from_pretrained(
                "stabilityai/sd-vae-ft-mse", 
                torch_dtype=torch.float32
            ).to(self.device)
            self.vae.eval()
        except Exception as e:
            print(f"[!] Error loading VAE weights: {e}")
            self.vae = None

    def preprocess(self, pil_img):
        # VAE expects 512x512 normalized tensors
        img = pil_img.resize((512, 512))
        img = np.array(img).astype(np.float32) / 255.0
        img = img[None].transpose(0, 3, 1, 2)
        img = torch.from_numpy(img).to(self.device)
        return 2.0 * img - 1.0

    def postprocess(self, tensor):
        img = (tensor / 2 + 0.5).clamp(0, 1)
        img = img.detach().cpu().permute(0, 2, 3, 1).numpy()[0]
        return Image.fromarray((img * 255).astype(np.uint8))

    def apply_defense(self, image_path, eps=8/255, steps=10):
        """
        Implementation of Layer 1: Latent Poisoning via PGD
        Maximizes the distance between original latent and the 'poisoned' version.
        """
        if self.vae is None:
            return None, "VAE weights not loaded."

        original_pil = Image.open(image_path).convert("RGB")
        x = self.preprocess(original_pil)
        x_adv = x.clone().detach().requires_grad_(True)

        # Target: We want the VAE to think this image is a random gray target
        # instead of a face. This 'poisons' the reconstruction.
        target_latent = torch.randn((1, 4, 64, 64)).to(self.device) * 0.1

        print(f"[*] Starting PGD Attack ({steps} steps)...")
        for i in range(steps):
            # Encode the current (perturbed) image
            latents = self.vae.encode(x_adv).latent_dist.sample()
            
            # Loss: We WANT the latents to be far away from the original
            # or close to a 'broken' target latent.
            loss = F.mse_loss(latents, target_latent)
            
            # Gradient Descent
            loss.backward()
            
            with torch.no_grad():
                # Apply perturbations (Projected Gradient Descent)
                grad = x_adv.grad.sign()
                x_adv = x_adv + (eps / steps) * grad
                # Ensure the perturbed image stays within valid pixel range
                x_adv = torch.max(torch.min(x_adv, x + eps), x - eps)
                x_adv = x_adv.clamp(-1, 1)
            
            x_adv.requires_grad_(True)
            print(f"    Step {i+1}/{steps} | Loss: {loss.item():.4f}")

        return self.postprocess(x_adv), "Success"

class CloakIDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CloakID: Adversarial Defense v1.0")
        self.root.geometry("900x600")
        self.root.configure(bg="#0f172a")

        self.engine = CloakIDEngine()
        self.current_file = None
        self.processed_pil = None

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1e293b", height=80)
        header.pack(fill="x", side="top")
        tk.Label(header, text="CloakID Framework", font=("Arial", 18, "bold"), 
                 bg="#1e293b", fg="#3b82f6").pack(pady=10)

        # Main Layout
        main_frame = tk.Frame(self.root, bg="#0f172a")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Control Panel (Left)
        ctrl_panel = tk.Frame(main_frame, bg="#1e293b", width=250, padx=15, pady=15)
        ctrl_panel.pack(side="left", fill="y", padx=(0, 20))
	tk.Button(ctrl_panel, text="Apply Immunization", command=self.process_image, 
          bg="#10b981", fg="white", font=("Arial", 10, "bold"), 
          relief="flat", pady=10).pack(fill="x", pady=20)
	tk.Button(
    ctrl_panel,
    text="Download Protected Image",
    command=self.download_image,
    bg="#6366f1",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    pady=8
).pack(fill="x", pady=5)


        tk.Label(ctrl_panel, text="PROTECTION SETTINGS", font=("Arial", 10, "bold"), 
                 bg="#1e293b", fg="#94a3b8").pack(anchor="w", pady=(0, 15))

        tk.Button(ctrl_panel, text="Upload Image", command=self.load_image, 
                  bg="#3b82f6", fg="white", font=("Arial", 10, "bold"), 
                  relief="flat", pady=8).pack(fill="x", pady=5)

        tk.Label(ctrl_panel, text="Intensity (ε):", bg="#1e293b", fg="white").pack(anchor="w", pady=(10, 0))
        self.eps_slider = ttk.Scale(ctrl_panel, from_=2, to=32, orient="horizontal")
        self.eps_slider.set(8)
        self.eps_slider.pack(fill="x", pady=5)

        tk.Button(ctrl_panel, text="Apply Immunization", command=self.process_image, 
                  bg="#10b981", fg="white", font=("Arial", 10, "bold"), 
                  relief="flat", pady=10).pack(fill="x", pady=20)

        # Preview Area (Right)
        self.preview_label = tk.Label(main_frame, text="Upload an image to begin", 
                                      bg="#020617", fg="#475569", font=("Arial", 12))
        self.preview_label.pack(side="right", expand=True, fill="both")

        # Status Bar
        self.status_var = tk.StringVar(value="System Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", 
                              anchor="w", bg="#0f172a", fg="#64748b", padx=10)
        status_bar.pack(side="bottom", fill="x")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if file_path:
            self.current_file = file_path
            img = Image.open(file_path).resize((400, 400))
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
            self.status_var.set(f"Loaded: {os.path.basename(file_path)}")

    def process_image(self):
        if not self.current_file:
            messagebox.showwarning("Warning", "Please upload an image first!")
            return
    def download_image(self):
        if self.processed_pil is None:
            messagebox.showwarning("Warning", "No protected image to download!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
            ],
            title="Save Protected Image"
        )

        if file_path:
            self.processed_pil.save(file_path, quality=100)
            messagebox.showinfo("Saved", "Protected image saved successfully!")

        def run():
            self.status_var.set("Running PGD Latent Poisoning... (Please wait)")
            eps = self.eps_slider.get() / 255.0
            processed, msg = self.engine.apply_defense(self.current_file, eps=eps)
            
            if processed:
                self.processed_pil = processed
                photo = ImageTk.PhotoImage(processed.resize((400, 400)))
                self.preview_label.config(image=photo)
                self.preview_label.image = photo
                self.status_var.set("Immunization Complete. Image Protected.")
                messagebox.showinfo("Success", "Adversarial noise injected successfully. This image will now cause VAE reconstruction failure in Diffusion Models.")
            else:
                self.status_var.set(f"Error: {msg}")

        threading.Thread(target=run).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = CloakIDApp(root)
    root.mainloop()