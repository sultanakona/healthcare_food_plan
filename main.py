"""
Main entry point for AI Nutrition Recommendation System
"""
import argparse
import sys
import uvicorn
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def run_api(host="0.0.0.0", port=8000, reload=True):
    """Run the FastAPI application"""
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


def run_data_pipeline(steps=None):
    """Run data processing pipelines"""
    print("🔄 Running data processing pipelines...")
    
    if steps is None or "all" in steps:
        steps = ["step1", "step2", "step3", "step4"]
    
    for step in steps:
        print(f"  ▶️ Executing {step}...")
        # Import and run pipeline steps
        # This would call your actual pipeline functions
        
    print("✅ Pipeline completed!")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Nutrition Recommendation System"
    )
    
    parser.add_argument(
        "command",
        choices=["api", "pipeline", "test"],
        help="Command to run"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API host (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API port (default: 8000)"
    )
    
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload"
    )
    
    parser.add_argument(
        "--steps",
        nargs="+",
        help="Pipeline steps to run (e.g., step1 step2)"
    )
    
    args = parser.parse_args()
    
    if args.command == "api":
        print(f"🚀 Starting API server on {args.host}:{args.port}")
        run_api(
            host=args.host,
            port=args.port,
            reload=not args.no_reload
        )
    
    elif args.command == "pipeline":
        run_data_pipeline(args.steps)
    
    elif args.command == "test":
        print("🧪 Running tests...")
        # Run your tests here
        print("✅ Tests completed!")


if __name__ == "__main__":
    main()
