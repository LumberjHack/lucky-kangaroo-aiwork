from PIL import Image as PILImage
try:
    from rembg import remove as rembg_remove
except Exception:
    rembg_remove = None


def generate_image_variants(src_path, remove_bg=False):
    """Generate large and thumbnail variants; optionally remove background (placeholder)."""
    return {}


def simulate_ai_analysis(filename):
    """Simulate AI analysis of uploaded image (placeholder)."""
    return {
        'category': 'Divers',
        'estimated_value': 100,
        'confidence': 75,
        'tags': ['objet']
    }
