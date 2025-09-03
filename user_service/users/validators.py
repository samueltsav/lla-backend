import os
from PIL import Image
from django.core.exceptions import ValidationError


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_FORMATS = {"JPEG", "PNG", "GIF"}


# Custom validator class for reusability
class ImageValidator:
    def __init__(
        self,
        allowed_extensions=None,
        allowed_formats=None,
        max_size_mb=5,
        max_width=4000,
        max_height=4000,
    ):
        self.allowed_extensions = ALLOWED_EXTENSIONS
        self.allowed_formats = ALLOWED_FORMATS
        self.max_size_mb = max_size_mb
        self.max_width = max_width
        self.max_height = max_height

    def __call__(self, file):  # Make the class callable as a validator"""
        if not file:
            raise ValidationError("No file provided")

        # Extension check
        if hasattr(file, "name"):
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in self.allowed_extensions:
                raise ValidationError(
                    f"Unsupported file extension: {ext}. "
                    f"Allowed: {', '.join(self.allowed_extensions)}"
                )

        # Format and integrity check
        try:
            file.seek(0)
            with Image.open(file) as img:
                if img.format not in self.allowed_formats:
                    raise ValidationError(
                        f"Unsupported format: {img.format}. "
                        f"Allowed: {', '.join(self.allowed_formats)}"
                    )

                # Size check
                width, height = img.size
                if width > self.max_width or height > self.max_height:
                    raise ValidationError(
                        f"Image too large: {width}x{height}. "
                        f"Max: {self.max_width}x{self.max_height}"
                    )

                img.verify()

            file.seek(0)

            if hasattr(file, "size"):  # Check file size
                max_bytes = self.max_size_mb * 1024 * 1024
                if file.size > max_bytes:
                    raise ValidationError(
                        f"File too large: {file.size / (1024 * 1024):.2f}MB. "
                        f"Max: {self.max_size_mb}MB"
                    )

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Invalid image: {str(e)}")

        return True
