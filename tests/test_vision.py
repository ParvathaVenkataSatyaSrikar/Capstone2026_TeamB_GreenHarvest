"""Test crop image diagnosis pipeline."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIXTURE = ROOT / "tests" / "fixtures" / "images" / "sample_leaf.jpg"
GEN = ROOT / "tests" / "fixtures" / "generate_sample_image.py"


def main():
    if not FIXTURE.exists():
        import subprocess
        subprocess.run([sys.executable, str(GEN)], check=False)

    if not FIXTURE.exists():
        print("FAIL: no test image — run tests/fixtures/generate_sample_image.py")
        sys.exit(1)

    from src.vision.disease_detector import analyze_crop_image

    data = FIXTURE.read_bytes()
    result = analyze_crop_image(data, mime="image/jpeg", crop="cotton", district="Warangal")
    print(f"Provider: {result.provider}")
    print(f"Offline: {result.offline}")
    print(f"Label: {result.diagnosis.label}")
    print(f"Confidence: {result.diagnosis.confidence}")
    print(f"Type: {result.diagnosis.issue_type}")
    print("\n--- Response preview ---\n")
    print(result.formatted_response[:600])
    print("\nOK")
    sys.exit(0)


if __name__ == "__main__":
    main()
