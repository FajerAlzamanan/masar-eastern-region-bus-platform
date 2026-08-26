import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.pipeline import run_full_pipeline


if __name__ == "__main__":
    result = run_full_pipeline(write_outputs=True)
    print("Generated tables:")
    for name, frame in result["dataset"].items():
        print(f"- {name}: {len(frame)} rows")
    print(f"Quality score: {result['validation']['quality_score']}")
    print(f"Recommendation status: {result['recommendation']['status']}")
