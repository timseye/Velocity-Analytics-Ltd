import open3d as o3d
import shutil
import os

print("Downloading fresh bunny model...")

# Download from Open3D's dataset
bunny_mesh = o3d.data.BunnyMesh()
print(f"Downloaded to: {bunny_mesh.path}")

# Copy to current directory
destination = os.path.join(os.path.dirname(__file__), "bunny_model.ply")
shutil.copy(bunny_mesh.path, destination)
print(f"Fresh model saved to: {destination}")
print("Model ready!")
