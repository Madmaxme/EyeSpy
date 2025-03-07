#!/usr/bin/env python3
"""
Integration module for adding bio generation to the FaceUpload pipeline
This should be imported in FaceUpload.py
"""

import os
import time
import threading
from BioGenerator import BioGenerator

def add_bio_generator_to_faceupload():
    """
    This function patches the FaceUpload.py module to add bio generation
    It should be called once during system initialization
    """
    try:
        import FaceUpload
        
        # Store the original process_single_face function
        original_process_single_face = FaceUpload.process_single_face
        
        # Create a wrapped version that adds bio generation
        def process_single_face_with_bio(image_file, timeout=300):
            """Wrapper around the original process_single_face that adds bio generation"""
            # Call the original function
            success = original_process_single_face(image_file, timeout)
            
            # If successful, generate bio in a separate thread
            if success:
                try:
                    # Extract the base_image_name from the image_file path
                    base_image_name = os.path.basename(image_file)
                    base_image_name = os.path.splitext(base_image_name)[0]  # Remove extension
                    
                    # Construct the person directory path
                    person_dir = os.path.join(FaceUpload.RESULTS_DIR, base_image_name)
                    
                    if os.path.exists(person_dir):
                        # Run bio generation in a separate thread to not block
                        threading.Thread(
                            target=generate_bio_for_directory,
                            args=(person_dir,),
                            daemon=True
                        ).start()
                except Exception as e:
                    print(f"[BIO_INTEGRATION] Error setting up bio generation: {e}")
            
            return success
        
        # Replace the original function with our wrapped version
        FaceUpload.process_single_face = process_single_face_with_bio
        
        print("[BIO_INTEGRATION] Successfully integrated bio generation into FaceUpload")
        return True
    
    except Exception as e:
        print(f"[BIO_INTEGRATION] Failed to integrate bio generation: {e}")
        return False


def generate_bio_for_directory(person_dir):
    """
    Generate a bio for a person directory
    This function is called in a separate thread after face search completes
    
    Args:
        person_dir: Path to the person's directory within the RESULTS_DIR
    """
    try:
        # Small delay to make sure the results file is fully written
        time.sleep(2)
        
        print(f"[BIO_INTEGRATION] Starting bio generation for: {person_dir}")
        
        # Initialize the bio generator
        generator = BioGenerator()
        
        # Process the directory
        bio_file = generator.process_result_directory(person_dir)
        
        if bio_file:
            print(f"[BIO_INTEGRATION] Bio generation complete: {bio_file}")
        else:
            print(f"[BIO_INTEGRATION] Bio generation failed for: {person_dir}")
    
    except Exception as e:
        print(f"[BIO_INTEGRATION] Error generating bio: {e}")


# Patch to enable direct integration into the controller
def integrate_with_controller():
    """Add this to controller.py to activate bio generation"""
    # Import and patch FaceUpload
    add_bio_generator_to_faceupload()


if __name__ == "__main__":
    # For testing the integration
    add_bio_generator_to_faceupload()