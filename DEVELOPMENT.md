
# Development Guide – LOFAR RFI Detection

This document describes two modes for running the Flask-based LOFAR RFI detection interface using Docker Compose:

- **Remote/Production mode**: pulls the prebuilt image from GitHub Container Registry (or Docker Hub).
- **Local development mode**: builds the image locally from the source code.

---

## 🧭 Prerequisites

Make sure you have:

- Docker installed and running
- Docker Compose installed (v2 required)
- Internet access (for pulling images in remote mode)

---

## 🔧 1. Running the application – Remote/Production Mode

This mode uses a prebuilt image from your GitHub repository or Docker Hub. It's the default setup for production-like environments.

### **File used**
- `docker-compose.yml`

### **Command**
```bash
docker compose up
```

### **Expected behavior**
- Pulls the image from `ghcr.io/<your-username>/lofar-rfi-detection:latest`
- Maps port 5000 to localhost
- Mounts the `static/images/` directory for access to generated images
- Optionally mounts the data directory if configured

---

## 🛠️ 2. Running the application – Local Development Mode

This mode is used for active development and debugging. It builds the image from your local source code.

### **File used**
- `docker-compose.local.yml`

### **Command**
```bash
docker compose -f docker-compose.local.yml up --build
```

### **Expected behavior**
- Builds the image using your local Dockerfile
- Uses live source code and local `webapp` structure
- Mounts `webapp/static/images/` for real-time access
- Mounts `/mnt/LOFAR0/wait` from host into container at `/data`
- Ideal for testing Flask changes, debugging, or adding features

---

## 📂 Project structure (relevant parts)
```
lofar-RFI-detection/
├── Dockerfile
├── docker-compose.yml              ← Remote image
├── docker-compose.local.yml        ← Local build
├── requirements.txt
├── webapp/
│   ├── app.py
│   ├── config.py
│   ├── state.py
│   ├── templates/
│   ├── static/
│   │   └── images/
```

---

## 🧼 Stopping and cleaning up

To stop the server:

```bash
docker compose down
```

To remove old or dangling images (optional):

```bash
docker image prune
```
