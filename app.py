import os
import sys
# 1. Environment Compatibility Fixes
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import google.protobuf
if not hasattr(google.protobuf, 'runtime_version'):
    class MockRuntimeVersion:
        class Domain:
            PUBLIC = 1
        def ValidateProtobufRuntimeVersion(self, *args, **kwargs): 
            return None
    google.protobuf.runtime_version = MockRuntimeVersion()

# --- Standard Imports ---
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import numpy as np
from deepface import DeepFace
import tensorflow as tf

class KinderJoyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kinder Joy - Face Identity Protection")
        self.root.geometry("1100x950")
        self.root.configure(bg="#f4f4f9")

        # --- Initialize AI Models ---
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1, refine_landmarks=True
        )

        # --- UI Elements ---
        tk.Label(root, text="🛡️ PROJECT: KINDER JOY", font=("Helvetica", 22, "bold"), bg="#f4f4f9").pack(pady=15)
        
        btn_frame = tk.Frame(root, bg="#f4f4f9")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="1. Upload Image", command=self.upload_image, width=15, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5)
        self.process_btn = tk.Button(btn_frame, text="2. Extract Features", command=self.process_latent_id, state="disabled", width=20, bg="#2196F3", fg="white")
        self.process_btn.grid(row=0, column=1, padx=5)
        
        self.adv_btn = tk.Button(btn_frame, text="3. Apply Adversarial Clock", command=self.generate_adversarial_clock, state="disabled", width=25, bg="#f44336", fg="white")
        self.adv_btn.grid(row=0, column=2, padx=5)

        # Protection Slider (Epsilon)
        tk.Label(root, text="Protection Strength (Epsilon):", bg="#f4f4f9", font=("Arial", 10, "bold")).pack(pady=5)
        self.eps_slider = tk.Scale(root, from_=0.01, to=0.15, resolution=0.01, orient=tk.HORIZONTAL, length=400, bg="#f4f4f9")
        self.eps_slider.set(0.10)
        self.eps_slider.pack(pady=5)

        # Result Display
        display_frame = tk.Frame(root, bg="#f4f4f9")
        display_frame.pack(pady=10)

        self.lbl_orig = tk.Label(display_frame, text="Original Image", bg="#e0e0e0", width=50, height=25)
        self.lbl_orig.grid(row=0, column=0, padx=10)

        self.lbl_proc = tk.Label(display_frame, text="Protected Output", bg="#e0e0e0", width=50, height=25)
        self.lbl_proc.grid(row=0, column=1, padx=10)

        self.txt_output = tk.Text(root, height=10, width=120, font=("Consolas", 9), bg="#ffffff")
        self.txt_output.pack(pady=10)

    def upload_image(self):
        fpath = filedialog.askopenfilename()
        if fpath:
            self.file_path = fpath
            img = Image.open(fpath)
            img.thumbnail((400, 400))
            self.tk_orig = ImageTk.PhotoImage(img)
            self.lbl_orig.config(image=self.tk_orig, text="")
            self.process_btn.config(state="normal")

    def process_latent_id(self):
        if not hasattr(self, 'file_path'): return
        image = cv2.imread(self.file_path)
        self.image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        try:
            # Identity Embedding
            obj = DeepFace.represent(img_path=self.image_rgb, model_name="ArcFace", enforce_detection=False)
            self.original_vector = np.array(obj[0]["embedding"])

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, f"SUCCESS: Features Extracted.\n")
            self.txt_output.insert(tk.END, f"Biometric Embedding Stored. Ready for Perturbation.\n")
            self.adv_btn.config(state="normal")
            messagebox.showinfo("Success", "Ready for Adversarial Perturbation.")
        except Exception as e:
            messagebox.showerror("Error", f"Extraction Failed: {str(e)}")

    def generate_adversarial_clock(self):
        try:
            epsilon = self.eps_slider.get()
            
            # 1. Prepare Image Tensor
            img_tensor = tf.convert_to_tensor(self.image_rgb, dtype=tf.float32)
            img_tensor = tf.expand_dims(img_tensor, 0) / 255.0
            
            # 2. Targeted Feature Perturbation
            # We use a Laplacian Filter to find the 'Identity Edges' 
            kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
            kernel = kernel.reshape((3, 3, 1, 1))
            kernel = np.repeat(kernel, 3, axis=2) 
            
            feature_map = tf.nn.conv2d(img_tensor, kernel, strides=[1, 1, 1, 1], padding='SAME')
            signed_grad = tf.sign(feature_map)
            
            # Apply the optimized noise
            adv_tensor = img_tensor + (epsilon * signed_grad)
            adv_tensor = tf.clip_by_value(adv_tensor, 0, 1)

            # 3. Finalize and Display
            adv_img = (adv_tensor[0].numpy() * 255).astype(np.uint8)
            
            # 4. Extract NEW identity to verify the shift
            obj_new = DeepFace.represent(img_path=adv_img, model_name="ArcFace", enforce_detection=False)
            new_vector = np.array(obj_new[0]["embedding"])

            # Calculate Cosine Similarity
            cos_sim = np.dot(self.original_vector, new_vector) / (np.linalg.norm(self.original_vector) * np.linalg.norm(new_vector))

            # Update UI
            res_pil = Image.fromarray(adv_img)
            res_pil.thumbnail((400, 400))
            self.tk_adv = ImageTk.PhotoImage(res_pil)
            self.lbl_proc.config(image=self.tk_adv, text="")

            self.txt_output.insert(tk.END, f"\n--- TARGETED ADVERSARIAL CLOCK --- \n")
            self.txt_output.insert(tk.END, f"Strength (Epsilon): {epsilon}\n")
            self.txt_output.insert(tk.END, f"Identity Similarity Score: {cos_sim:.4f}\n")
            
            if cos_sim < 0.85:
                self.txt_output.insert(tk.END, "✅ SUCCESS: Identity successfully shifted. Image is protected.\n")
            else:
                self.txt_output.insert(tk.END, "⚠️ WARNING: Similarity still high. Move slider to 0.12+.\n")

        except Exception as e:
            messagebox.showerror("Error", f"Perturbation Failed: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KinderJoyApp(root)

    root.mainloop()


