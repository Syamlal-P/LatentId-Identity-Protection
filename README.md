# LatentId  
### Preemptive Digital Identity Protection Against AI-Based Image Regeneration

LatentId is a privacy-preserving image protection system designed to safeguard human identity from misuse by modern AI image generation models. The system allows users to upload personal images and applies subtle, non-destructive transformations that preserve visual quality for humans while reducing the ability of AI systems to reliably reconstruct or regenerate the same individual.

This project focuses on **preemptive identity protection**, shifting the paradigm from reactive deepfake detection to proactive consent-by-design image safety.

---

## 🚀 Key Idea

Modern generative AI models (diffusion-based and multimodal systems) can extract identity-relevant features from publicly available images and regenerate realistic representations of individuals without consent.

**LatentId addresses this problem by:**
- Preserving how images appear to humans
- Altering only AI-interpretable identity features
- Making the image an unreliable biometric source for AI models

The protected image looks unchanged to human viewers but causes **identity drift and inconsistency** when used as input for AI image generation tools.

---

## 🧠 What LatentId Does

- Accepts face, half-body, or full-body images
- Automatically detects and aligns facial regions
- Applies identity-safe image transformations
- Preserves original resolution and visual quality
- Outputs a protected image suitable for real-world use (e.g., social media)

---

## ❌ What LatentId Is NOT

- Not a deepfake detector  
- Not a watermarking system  
- Not a GAN or diffusion model  
- Not a model-specific adversarial attack  
- Not a video or audio protection tool  

LatentId does **not** require access to AI model internals or GPU-based training.

---

## 🏗️ System Workflow

1. **Image Upload**
   - Supports JPEG, PNG, and WebP formats
   - No enforced cropping at upload stage

2. **Face Detection & Alignment**
   - Automatically detects facial region
   - Crops and aligns the face for consistent processing

3. **Identity-Safe Image Processing**
   - Applies imperceptible transformations
   - Preserves visual fidelity (high SSIM)
   - Alters machine-interpretable identity features

4. **Output Generation**
   - Reintegrates processed face into original image
   - Maintains original resolution and aspect ratio
   - Generates an ultra-high-quality protected image

---

## 🔍 Expected Behavior with AI Image Generators

When a LatentId-protected image is uploaded to AI tools such as:
- ChatGPT image models
- Gemini
- Stable Diffusion-based systems
- Multimodal AI generators

The result:
- Does **not reliably preserve the original identity**
- Shows facial structure drift or semantic misinterpretation
- Produces inconsistent identity across generations

⚠️ LatentId does not guarantee total distortion or noise; instead, it ensures **loss of stable identity reconstruction**.

---

## 🧪 Evaluation Criteria

- Human visual similarity
- Structural Similarity Index (SSIM)
- AI identity reconstruction consistency
- Practical usability and image quality

---

## 🛠️ Technologies Used

- Python
- OpenCV
- NumPy
- PIL (Python Imaging Library)

The system is lightweight, reproducible, and suitable for low-resource environments.

---

## 🎓 Academic Relevance

This project is suitable for:
- MSc / MCA / BTech final-year submission
- Privacy-preserving AI research
- Ethical AI and consent-based systems
- Image security and digital identity protection

---

## 📌 Limitations

- Focuses only on static images
- Does not cover real-time video or audio
- Protection effectiveness may vary across AI models

---

## 📄 License & Usage

This project is intended for **academic and research purposes only**.

---

## © Copyright

© 2026 Syamlal  
All rights reserved.
