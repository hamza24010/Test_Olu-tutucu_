import pytest
import os
from PIL import Image
from unittest.mock import MagicMock
from src.core.pdf_processor import PDFProcessor

def test_convert_pdf_to_images(mocker, tmp_path):
    """Test PDF conversion calls underlying library correctly."""
    mock_convert = mocker.patch("src.core.pdf_processor.convert_from_path")
    
    # Mock return list of PIL Images
    mock_img = MagicMock()
    # Mock 'save' method of PIL Image
    mock_img.save = MagicMock()
    
    # Simulate 2 pages
    mock_convert.return_value = [mock_img, mock_img]
    
    # Use tmp_path for output
    processor = PDFProcessor(output_dir=str(tmp_path))
    
    paths = processor.convert_pdf_to_images("dummy.pdf")
    
    assert len(paths) == 2
    assert mock_convert.called
    # Expect 2 saves
    assert mock_img.save.call_count == 2

def test_convert_pdf_exception(mocker):
    """Test exception handling during conversion."""
    mock_convert = mocker.patch("src.core.pdf_processor.convert_from_path")
    mock_convert.side_effect = Exception("Poppler error")
    
    processor = PDFProcessor()
    paths = processor.convert_pdf_to_images("bad.pdf")
    
    assert paths == []

def test_crop_question(tmp_path):
    """Test image cropping logic with coordinate calculation."""
    # Create a dummy image (1000x1000 for easy calc)
    img_path = tmp_path / "test_page.png"
    img = Image.new("RGB", (1000, 1000), color="white")
    img.save(img_path)
    
    processor = PDFProcessor(output_dir=str(tmp_path))
    
    # Crop center: ymin=250, xmin=250, ymax=750, xmax=750
    # Expected size: 500x500 pixels (since image is 1000x1000 and coords are 0-1000 normalized)
    coords = [250, 250, 750, 750]
    out_path = tmp_path / "cropped.png"
    
    # Use 0 padding for exact math check
    result = processor.crop_question(str(img_path), coords, str(out_path), padding=0)
    
    assert result is not None
    assert os.path.exists(result)
    
    # Check dimensions of cropped image
    with Image.open(result) as c_img:
        w, h = c_img.size
        # Tolerance of +/- 1 pixel due to float rounding
        assert 499 <= w <= 501
        assert 499 <= h <= 501
