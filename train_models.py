import sys
sys.path.append('modules')

from modules.ml_models import train_models_from_dataset

if __name__ == "__main__":
    print("Starting ML Model Training...\n")
    
    # Train all models
    manager, results = train_models_from_dataset()
    
    print("\n Training complete! Models saved to 'models/' directory")
    print("\nYou can now use these models for predictions.")
