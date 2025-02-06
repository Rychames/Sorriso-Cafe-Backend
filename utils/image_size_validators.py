from io import BytesIO
from PIL import Image
from django.core.files import File

def compress_image(image, max_size_kb=300, quality=75):
    """
    Comprime a imagem para não ultrapassar `max_size_kb` (em kilobytes).
    Reduz a qualidade e/ou redimensiona a imagem se necessário.
    """
    img = Image.open(image)
    
    # Converte para RGB se for PNG com transparência
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    output = BytesIO()
    
    # Salva a imagem com qualidade ajustada
    img.save(output, format='JPEG', quality=quality, optimize=True)
    
    # Verifica se o tamanho está dentro do limite
    while output.tell() > max_size_kb * 1024 and quality > 10:
        quality -= 5
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
    
    # Redimensiona se ainda estiver acima do limite (opcional)
    if output.tell() > max_size_kb * 1024:
        width, height = img.size
        new_size = (int(width * 0.8), int(height * 0.8))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
    
    compressed_file = File(output, name=image.name)
    return compressed_file