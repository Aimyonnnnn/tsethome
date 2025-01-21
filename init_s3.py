# init_s3.py
import boto3
import os
from botocore.exceptions import ClientError

# AWS S3 설정
S3_BUCKET = os.environ.get('AWS_BUCKET_NAME')
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

# SVG 이미지 목록
svg_images = [
    '11.svg', '12.svg', '41.svg', '42.svg', 
    '43.svg', '44.svg', '45.svg', '415.svg', '452.svg'
]

# PNG 이미지 목록 (나머지 이미지들)
png_images = [
    '4.png', '5.png', '6.png', '7.png', '31.png', '32.png', '32png.png',
    '33.png', '34.png', '35.png', '36.png', '44.png', '45.png', '55.png',
    'bag-icon.png', 'login.png', 'kt1.png', 'kt2.png', 'kt3.png',
    'main1.png', 'main2.png', 'main3.png', 'promo1.png', 'promo2.png',
    'promo3.png', 'sale1.png', 'sale2.png', 'sale3.png', 'sale4.png',
    'shop1.png', 'shop2.png', 'kakao.png'
]

def upload_file_to_s3(file_name, content_type):
    try:
        file_path = f'img/{file_name}'
        if os.path.exists(file_path):
            s3_client.upload_file(
                file_path,
                S3_BUCKET,
                f'img/{file_name}',
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': content_type
                }
            )
            print(f"Uploaded {file_name} successfully")
        else:
            print(f"File not found: {file_path}")
    except ClientError as e:
        print(f"Error uploading {file_name}: {e}")

def upload_initial_images():
    # SVG 파일 업로드
    for image in svg_images:
        upload_file_to_s3(image, 'image/svg+xml')
    
    # PNG 파일 업로드
    for image in png_images:
        upload_file_to_s3(image, 'image/png')

if __name__ == '__main__':
    upload_initial_images()