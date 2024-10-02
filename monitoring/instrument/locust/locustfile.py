import os
from locust import HttpUser, task, between
import random

class NSFWUser(HttpUser):
    # Define wait time between tasks (simulates real user activity)
    wait_time = between(1, 5)

    @task
    def post_nsfw_det(self):
        # Path to a sample image file to be uploaded
        image_path = os.path.join(os.getcwd(), "receipt.jpg")
        
        # Ensure the image exists before sending
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                files = {
                    'file': ('receipt.jpg', image_file, 'image/jpg')
                }
                # Send the image as a POST request to the /nsfw_detection endpoint
                response = self.client.post("/nsfw_detection", files=files)
                
                # Log the response status and content
                if response.status_code == 200:
                    print(f"Success: {response.status_code}")
                else:
                    print(f"Failed: {response.status_code}")
        else:
            print("Image file not found!")

