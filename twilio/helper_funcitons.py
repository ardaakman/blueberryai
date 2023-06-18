import requests
import boto3
import requests
import os

# access-key= MICPMAWAWF2KI1CRWU0B
# secret-key= DkLNyYz0uP1EJINhAizYIlRLzAgWMZSHzbH11RZY


def upload_file_to_wasabi(file_path, bucket_name):
    s3 = boto3.client('s3',
                      endpoint_url='https://s3.us-west-1.wasabisys.com',  # Use the correct endpoint URL for your Wasabi region
                      aws_access_key_id='MICPMAWAWF2KI1CRWU0B',  # Replace with your access key
                      aws_secret_access_key='DkLNyYz0uP1EJINhAizYIlRLzAgWMZSHzbH11RZY')  # Replace with your secret key

    file_name = os.path.basename(file_path)

    try:
        s3.upload_file(file_path, bucket_name, file_name)
        print(f"File uploaded to Wasabi successfully!")
    except Exception as e:
        print("Something went wrong: ", e)


def get_url_recording(url):
    response = requests.get(url, stream=True)
    print("creating a response")

    # Ensure the request is successful
    if response.status_code == 200:
        # Open the file in write-binary mode and write the response content to it
        with open('output.mp3', 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
    else:
        print('Failed to download the file.')



def count_files_in_directory(directory):
    return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])