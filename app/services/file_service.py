from fastapi import UploadFile
import os
import uuid
import aiofiles

from app.core.config import settings


class FileService:
    def __init__(self, upload_base_path: str) -> None:
        self.upload_base_path = upload_base_path
        os.makedirs(self.upload_base_path, exist_ok=True)
    async def save_task_image(self, file: UploadFile):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Format .{ext} not allowed")

        filename = f"task_{uuid.uuid4().hex[:8]}.{ext}"
        save_path = os.path.join(self.upload_base_path, filename)

        async with aiofiles.open(save_path, 'wb') as f:
            while content:= await file.read(1024*1024):
                await f.write(content)
        return filename

async def get_file_service() -> FileService:
    return FileService(upload_base_path=settings.UPLOAD_DIR)

