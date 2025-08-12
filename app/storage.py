import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class StorageManager:
    """Manage file storage and generate signed URLs"""
    
    def __init__(self):
        self.s3_client = None
        self.local_storage_path = "./storage/reports"
        
        # Initialize S3 client if credentials are available
        if (settings.aws_access_key_id and settings.aws_secret_access_key):
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
                logger.info("S3 client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize S3 client: {e}")
                self.s3_client = None
        
        # Ensure local storage directory exists
        os.makedirs(self.local_storage_path, exist_ok=True)
    
    def store_pdf(self, pdf_content: bytes, filename: str) -> str:
        """Store PDF content and return a URL"""
        
        if self.s3_client:
            return self._store_in_s3(pdf_content, filename)
        else:
            return self._store_locally(pdf_content, filename)
    
    def _store_in_s3(self, pdf_content: bytes, filename: str) -> str:
        """Store PDF in S3 and return signed URL"""
        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=settings.s3_bucket_name,
                Key=f"reports/{filename}",
                Body=pdf_content,
                ContentType="application/pdf"
            )
            
            # Generate signed URL (expires in 1 hour)
            signed_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.s3_bucket_name,
                    'Key': f"reports/{filename}"
                },
                ExpiresIn=3600  # 1 hour
            )
            
            logger.info(f"PDF stored in S3: {filename}")
            return signed_url
            
        except ClientError as e:
            logger.error(f"Error storing PDF in S3: {e}")
            # Fallback to local storage
            return self._store_locally(pdf_content, filename)
    
    def _store_locally(self, pdf_content: bytes, filename: str) -> str:
        """Store PDF locally and return file path"""
        try:
            file_path = os.path.join(self.local_storage_path, filename)
            
            with open(file_path, 'wb') as f:
                f.write(pdf_content)
            
            # Return a local file URL (for development)
            local_url = f"file://{os.path.abspath(file_path)}"
            
            logger.info(f"PDF stored locally: {file_path}")
            return local_url
            
        except Exception as e:
            logger.error(f"Error storing PDF locally: {e}")
            raise
    
    def get_signed_url(self, filename: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a signed URL for an existing file"""
        
        if self.s3_client:
            try:
                signed_url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.s3_bucket_name,
                        'Key': f"reports/{filename}"
                    },
                    ExpiresIn=expires_in
                )
                return signed_url
            except ClientError as e:
                logger.error(f"Error generating signed URL: {e}")
                return None
        else:
            # For local storage, return the file path
            file_path = os.path.join(self.local_storage_path, filename)
            if os.path.exists(file_path):
                return f"file://{os.path.abspath(file_path)}"
            return None
    
    def delete_file(self, filename: str) -> bool:
        """Delete a stored file"""
        
        if self.s3_client:
            try:
                self.s3_client.delete_object(
                    Bucket=settings.s3_bucket_name,
                    Key=f"reports/{filename}"
                )
                logger.info(f"File deleted from S3: {filename}")
                return True
            except ClientError as e:
                logger.error(f"Error deleting file from S3: {e}")
                return False
        else:
            try:
                file_path = os.path.join(self.local_storage_path, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"File deleted locally: {filename}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Error deleting local file: {e}")
                return False
    
    def list_files(self) -> list:
        """List all stored files"""
        
        if self.s3_client:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=settings.s3_bucket_name,
                    Prefix="reports/"
                )
                
                files = []
                if 'Contents' in response:
                    for obj in response['Contents']:
                        files.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified']
                        })
                
                return files
                
            except ClientError as e:
                logger.error(f"Error listing S3 files: {e}")
                return []
        else:
            try:
                files = []
                for filename in os.listdir(self.local_storage_path):
                    file_path = os.path.join(self.local_storage_path, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        files.append({
                            'key': filename,
                            'size': stat.st_size,
                            'last_modified': stat.st_mtime
                        })
                
                return files
                
            except Exception as e:
                logger.error(f"Error listing local files: {e}")
                return []
    
    def get_file_size(self, filename: str) -> Optional[int]:
        """Get the size of a stored file"""
        
        if self.s3_client:
            try:
                response = self.s3_client.head_object(
                    Bucket=settings.s3_bucket_name,
                    Key=f"reports/{filename}"
                )
                return response['ContentLength']
            except ClientError:
                return None
        else:
            try:
                file_path = os.path.join(self.local_storage_path, filename)
                if os.path.exists(file_path):
                    return os.path.getsize(file_path)
                return None
            except Exception:
                return None 