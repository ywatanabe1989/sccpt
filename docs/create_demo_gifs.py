#!/usr/bin/env python3
"""
Create demonstration GIFs for the CAM documentation.
"""

import os
import sys
from pathlib import Path
import time

# Add the cam package to the path
sys.path.insert(0, str(Path(__file__).parent))

import cam
from PIL import Image, ImageDraw, ImageFont

def create_workflow_demo_gif():
    """Create a GIF demonstrating a typical workflow."""
    print("Creating workflow demonstration GIF...")
    
    temp_dir = Path("/tmp/cam_demo_workflow")
    temp_dir.mkdir(exist_ok=True)
    
    # Create workflow steps
    steps = [
        ("Step 1: Opening Application", (100, 150, 255)),
        ("Step 2: Login Screen", (150, 200, 255)),
        ("Step 3: Dashboard Loading", (200, 220, 255)),
        ("Step 4: Navigating to Settings", (220, 240, 255)),
        ("Step 5: Configuring Options", (240, 255, 220)),
        ("Step 6: Saving Changes", (255, 240, 220)),
        ("Step 7: Success Confirmation", (220, 255, 220))
    ]
    
    image_paths = []
    
    for i, (step_text, bg_color) in enumerate(steps):
        img = Image.new('RGB', (800, 600), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a nicer font, fallback to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # Draw step number and title
        draw.text((50, 50), f"CAM Demo", fill=(50, 50, 50), font=font)
        draw.text((50, 100), step_text, fill=(20, 20, 20), font=font)
        
        # Draw some mock UI elements
        if "Login" in step_text:
            # Login form
            draw.rectangle([200, 200, 600, 250], outline=(100, 100, 100), width=2)
            draw.text((210, 215), "Username: demo@example.com", fill=(60, 60, 60), font=small_font)
            draw.rectangle([200, 270, 600, 320], outline=(100, 100, 100), width=2)
            draw.text((210, 285), "Password: ••••••••", fill=(60, 60, 60), font=small_font)
            draw.rectangle([350, 340, 450, 370], fill=(70, 130, 180), outline=(50, 100, 150))
            draw.text((385, 350), "Login", fill=(255, 255, 255), font=small_font)
        
        elif "Dashboard" in step_text:
            # Dashboard elements
            for j, (x, y) in enumerate([(100, 200), (300, 200), (500, 200), (100, 350), (300, 350), (500, 350)]):
                color = (200 + j*10, 220 + j*5, 240)
                draw.rectangle([x, y, x+150, y+100], fill=color, outline=(150, 150, 150))
                draw.text((x+20, y+40), f"Widget {j+1}", fill=(50, 50, 50), font=small_font)
        
        elif "Settings" in step_text:
            # Settings panel
            settings = ["General", "Security", "Notifications", "Privacy", "Advanced"]
            for j, setting in enumerate(settings):
                y = 180 + j * 60
                draw.rectangle([100, y, 700, y+40], outline=(150, 150, 150), width=1)
                draw.text((120, y+12), setting, fill=(50, 50, 50), font=small_font)
                # Toggle switches
                draw.rectangle([620, y+10, 680, y+30], fill=(100, 200, 100) if j % 2 else (200, 100, 100))
        
        # Add timestamp
        draw.text((650, 550), f"Frame {i+1}/{len(steps)}", fill=(100, 100, 100), font=small_font)
        
        img_path = temp_dir / f"workflow_{i:02d}.jpg"
        img.save(str(img_path), 'JPEG', quality=90)
        image_paths.append(str(img_path))
    
    # Create GIF
    output_path = temp_dir / "workflow_demo.gif"
    result = cam.create_gif_from_files(
        image_paths=image_paths,
        output_path=str(output_path),
        duration=1.2,  # Slower for readability
        optimize=True
    )
    
    return result

def create_monitoring_demo_gif():
    """Create a GIF demonstrating continuous monitoring."""
    print("Creating monitoring demonstration GIF...")
    
    temp_dir = Path("/tmp/cam_demo_monitoring")
    temp_dir.mkdir(exist_ok=True)
    
    # Simulate a monitoring session showing system activity
    frames = []
    
    for i in range(12):  # 12 frames for a nice loop
        img = Image.new('RGB', (800, 600), (240, 248, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # Title
        draw.text((50, 30), "CAM Continuous Monitoring Demo", fill=(50, 50, 150), font=font)
        
        # Fake terminal/console output
        console_lines = [
            "📸 Started monitoring: ~/.cache/cam/20250823_215059_NNNN_*.jpg",
            f"📸 Capture #{i+1:03d}: ~/.cache/cam/20250823_215059_{i:04d}_screenshot.jpg",
            f"📊 Memory usage: {60 + i*2}%",
            f"🔄 CPU activity: {30 + (i*5) % 40}%",
            f"⏱️  Runtime: {i*2} seconds",
            "🔍 Monitoring active processes...",
            "✅ Screenshot saved successfully"
        ]
        
        for j, line in enumerate(console_lines[:6+min(i//2, 1)]):
            y = 100 + j * 25
            draw.text((70, y), line, fill=(50, 50, 50), font=small_font)
        
        # Progress bar
        progress = (i + 1) / 12
        bar_width = 400
        bar_height = 20
        bar_x, bar_y = 200, 350
        
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                      outline=(100, 100, 100), width=2)
        draw.rectangle([bar_x + 2, bar_y + 2, bar_x + int(bar_width * progress) - 2, bar_y + bar_height - 2], 
                      fill=(100, 200, 100))
        
        draw.text((bar_x, bar_y + 30), f"Progress: {progress*100:.0f}% ({i+1}/12 captures)", 
                 fill=(80, 80, 80), font=small_font)
        
        # Activity indicator
        activity_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
        activity_color = activity_colors[i % len(activity_colors)]
        draw.ellipse([720, 80, 750, 110], fill=activity_color)
        draw.text((680, 120), "ACTIVE", fill=activity_color, font=small_font)
        
        # Timestamp
        draw.text((600, 550), f"21:50:{30 + i:02d}", fill=(120, 120, 120), font=small_font)
        
        img_path = temp_dir / f"monitoring_{i:02d}.jpg"
        img.save(str(img_path), 'JPEG', quality=85)
        frames.append(str(img_path))
    
    # Create GIF
    output_path = temp_dir / "monitoring_demo.gif"
    result = cam.create_gif_from_files(
        image_paths=frames,
        output_path=str(output_path),
        duration=0.8,
        optimize=True
    )
    
    return result

def create_error_detection_demo_gif():
    """Create a GIF demonstrating error detection."""
    print("Creating error detection demonstration GIF...")
    
    temp_dir = Path("/tmp/cam_demo_error")
    temp_dir.mkdir(exist_ok=True)
    
    scenarios = [
        ("Normal Operation", (220, 255, 220), "stdout", "✅ All systems operational"),
        ("Warning Detected", (255, 255, 200), "stdout", "⚠️  High memory usage detected"),
        ("Error Condition", (255, 220, 220), "stderr", "❌ Database connection failed"),
        ("Error Recovery", (255, 240, 200), "stdout", "🔄 Attempting reconnection..."),
        ("Back to Normal", (220, 255, 220), "stdout", "✅ Connection restored")
    ]
    
    frames = []
    
    for i, (title, bg_color, category, message) in enumerate(scenarios):
        img = Image.new('RGB', (800, 600), bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # Title
        draw.text((50, 40), "CAM Auto Error Detection", fill=(50, 50, 100), font=font)
        
        # Scenario
        draw.text((50, 100), f"Scenario: {title}", fill=(80, 80, 80), font=font)
        
        # Main message
        msg_color = (200, 50, 50) if category == "stderr" else (50, 150, 50)
        draw.text((50, 160), message, fill=msg_color, font=font)
        
        # Category indicator
        cat_bg = (255, 180, 180) if category == "stderr" else (180, 255, 180)
        cat_text = "STDERR (Error)" if category == "stderr" else "STDOUT (Normal)"
        
        draw.rectangle([50, 220, 300, 260], fill=cat_bg, outline=(100, 100, 100))
        draw.text((60, 232), f"Category: {cat_text}", fill=(50, 50, 50), font=small_font)
        
        # Mock file path
        filename_suffix = "-stderr.jpg" if category == "stderr" else "-stdout.jpg"
        filepath = f"~/.cache/cam/20250823_215{10+i:02d}_001{filename_suffix}"
        draw.text((50, 300), f"📁 Saved as: {filepath}", fill=(100, 100, 100), font=small_font)
        
        # Show automatic categorization process
        draw.text((50, 350), "🤖 CAM automatically detected:", fill=(50, 50, 150), font=small_font)
        detection_text = "Exception context → stderr category" if category == "stderr" else "Normal execution → stdout category"
        draw.text((80, 380), detection_text, fill=(80, 80, 80), font=small_font)
        
        # Time stamp
        draw.text((600, 550), f"21:5{i}:30", fill=(120, 120, 120), font=small_font)
        
        img_path = temp_dir / f"error_detection_{i:02d}.jpg"
        img.save(str(img_path), 'JPEG', quality=85)
        frames.append(str(img_path))
    
    # Create GIF
    output_path = temp_dir / "error_detection_demo.gif"
    result = cam.create_gif_from_files(
        image_paths=frames,
        output_path=str(output_path),
        duration=1.5,  # Slower for readability
        optimize=True
    )
    
    return result

def main():
    """Create all demo GIFs."""
    print("🎬 Creating CAM demonstration GIFs...\n")
    
    gifs_created = []
    
    # Create workflow demo
    workflow_gif = create_workflow_demo_gif()
    if workflow_gif:
        gifs_created.append(("workflow_demo.gif", workflow_gif))
    
    # Create monitoring demo
    monitoring_gif = create_monitoring_demo_gif()
    if monitoring_gif:
        gifs_created.append(("monitoring_demo.gif", monitoring_gif))
    
    # Create error detection demo
    error_gif = create_error_detection_demo_gif()
    if error_gif:
        gifs_created.append(("error_detection_demo.gif", error_gif))
    
    print(f"\n✅ Created {len(gifs_created)} demonstration GIFs:")
    for name, path in gifs_created:
        size_kb = Path(path).stat().st_size / 1024
        print(f"   📹 {name}: {path} ({size_kb:.1f}KB)")
    
    return gifs_created

if __name__ == "__main__":
    main()