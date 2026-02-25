import os
import sys
import hmac
from hashlib import sha1
import httpx

from src.Utils.Logger import logger

API_HOST = "https://api.dogecloud.com"

def generate_auth_token(access_key, secret_key, request_uri, body=""):
    """Generate Authorization Token for DogeCloud API."""
    sign_str = f"{request_uri}\n{body}"
    signed_data = hmac.new(
        secret_key.encode(),
        sign_str.encode('utf-8'),
        sha1
    )
    sign = signed_data.digest().hex()
    access_token = f"{access_key}:{sign}"
    return f"TOKEN {access_token}"

def upload_file(access_key, secret_key, bucket, key, file_path, public_url):
    """Uploads a file to DogeCloud OSS and returns the custom public URL."""
    request_uri = f"/oss/upload/put.json?bucket={bucket}&key={key}"

    with open(file_path, "rb") as f:
        file_content = f.read()

    headers = {
        "Authorization": generate_auth_token(access_key, secret_key, request_uri, ""),
        "Content-Type": "application/octet-stream"
    }

    try:
        with httpx.Client() as client:
            response = client.put(
                f"{API_HOST}{request_uri}",
                headers=headers,
                content=file_content,
                timeout=300
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 200:
                logger.error(
                    f"Error: Upload failed with code {result.get('code')}: {result.get('msg')}"
                )
                sys.exit(1)

            # 使用传入的公共URL替换多吉云默认的URL
            # 多吉云返回的URL格式通常是 https://bucket.oss.dogecloud.com/key
            # 我们需要替换为 https://your-custom-domain.com/key
            final_url = f"{public_url}/{key}"
            return final_url

    except httpx.HTTPStatusError as e:
        logger.error(f"Error: HTTP Status Error: {e.response.status_code}")
        logger.error(f"Response body: {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
