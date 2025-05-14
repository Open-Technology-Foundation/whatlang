#!/usr/bin/env python3
"""
Pytest configuration for whatlang tests.

This module defines fixtures and common utilities for testing the whatlang tool.
"""

import os
import sys
import pytest

# Add parent directory and tests directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tests_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)
sys.path.insert(0, tests_dir)

# Import the mock_whatlang module
import mock_whatlang as whatlang

# Replace the module in sys.modules
sys.modules['whatlang'] = whatlang

@pytest.fixture
def sample_texts():
    """
    Fixture providing sample texts in different languages.
    
    Returns:
        dict: A dictionary mapping language codes to sample texts
    """
    return {
        'en': 'The quick brown fox jumps over the lazy dog. This is a sample text in English.',
        'es': 'España es un país con una rica historia cultural, arquitectura impresionante y una gastronomía diversa.',
        'fr': 'La France est connue pour sa riche histoire culturelle, ses monuments célèbres et sa gastronomie exquise.',
        'id': 'Indonesia adalah negara yang kaya akan budaya dan tradisi.',
        'ru': 'Россия - самая большая страна в мире. Она известна своей богатой историей, литературой и культурой.',
        'zh': '臺灣是太平洋中的一個島嶼，有豐富的自然景觀和多元文化。從高山到海岸，臺灣提供了各種不同的體驗。',
        'ur': 'پاکستان ایشیا میں واقع ایک خوبصورت ملک ہے۔ یہ اپنے تاریخی مقامات، متنوع ثقافت اور لذیذ کھانوں کے لیے مشہور ہے۔',
        'sw': 'Kenya ni nchi iliyoko Afrika Mashariki, inajulikana kwa vivutio vyake vya wanyamapori na fukwe nzuri.',
        'ar': 'مصر هي دولة عربية تقع في شمال أفريقيا، وهي موطن لواحدة من أقدم الحضارات في العالم.',
        'hi': 'भारत एक विविधता से भरा देश है, जिसमें अनेक भाषाएँ, संस्कृतियाँ और परंपराएँ हैं।',
        'pt': 'Portugal é um país localizado no sudoeste da Europa, conhecido por suas belas praias e arquitetura histórica.',
        'bn': 'বাংলাদেশ দক্ষিণ এশিয়ার একটি দেশ, যা তার সবুজ প্রাকৃতিক সৌন্দর্য, সমৃদ্ধ সাংস্কৃতিক ঐতিহ্য এবং সুস্বাদু খাবারের জন্য পরিচিত।',
        'ja': '日本は東アジアに位置する島国で、美しい自然景観、伝統文化、そして革新的な技術で知られています。',
        'de': 'Deutschland ist ein Land in Mitteleuropa, bekannt für seine reiche Geschichte, beeindruckende Architektur und vielfältige Kultur.',
        'tr': 'Türkiye, Asya ve Avrupa\'yı birbirine bağlayan, zengin tarihi, çeşitli kültürü ve lezzetli mutfağıyla tanınan bir ülkedir.',
        'vi': 'Việt Nam là một quốc gia nằm ở Đông Nam Á, nổi tiếng với cảnh quan thiên nhiên tuyệt đẹp và di sản văn hóa phong phú.',
        'ko': '한국은 동아시아에 위치한 나라로, 아름다운 자연 경관, 풍부한 문화 유산, 그리고 맛있는 음식으로 유명합니다.',
        'it': 'L\'Italia è un paese situato nell\'Europa meridionale, conosciuto per la sua ricca storia e architettura impressionante.',
        'th': 'ประเทศไทยตั้งอยู่ในเอเชียตะวันออกเฉียงใต้ เป็นที่รู้จักจากวัฒนธรรมที่หลากหลาย อาหารรสเลิศ และภูมิทัศน์ธรรมชาติที่สวยงาม',
        'fa': 'ایران کشوری است در غرب آسیا، با تاریخی غنی، معماری چشمگیر و فرهنگ متنوع.',
        'he': 'ישראל היא מדינה במזרח התיכון, הידועה בהיסטוריה העשירה שלה, במקומות הקדושים ובחדשנות הטכנולוגית.',
        'el': 'Η Ελλάδα είναι μια χώρα στη νοτιοανατολική Ευρώπη, γνωστή για την πλούσια ιστορία της και την εντυπωσιακή αρχιτεκτονική.',
        'ms': 'Malaysia adalah sebuah negara di Asia Tenggara yang terkenal dengan pantai yang indah dan hutan hujan yang kaya.',
        'ta': 'தமிழ்நாடு இந்தியாவின் தென்பகுதியில் உள்ள ஒரு மாநிலம், இது அதன் பண்டைய கோவில்கள், வளமான கலாச்சாரம் மற்றும் சுவையான உணவிற்கு பெயர் பெற்றது.',
        'unknown': 'Nai tiruvantel ar varyuvantel i Valar tielyanna nu vilya.'  # Elvish
    }

@pytest.fixture
def sample_filepath(tmp_path, sample_texts):
    """
    Fixture for creating temporary sample files for testing.
    
    Args:
        tmp_path: pytest built-in fixture that provides a temporary directory
        sample_texts: our custom fixture with sample texts
        
    Returns:
        function: A function that creates a file with specified language content
    """
    def _create_file(lang_code='en'):
        if lang_code not in sample_texts:
            raise ValueError(f"No sample text available for language code: {lang_code}")
            
        filepath = tmp_path / f"test.{lang_code}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sample_texts[lang_code])
            
        return str(filepath)
        
    return _create_file

@pytest.fixture
def empty_file(tmp_path):
    """
    Fixture for creating an empty file for testing edge cases.
    
    Args:
        tmp_path: pytest built-in fixture that provides a temporary directory
        
    Returns:
        str: Path to an empty file
    """
    filepath = tmp_path / "empty.txt"
    with open(filepath, 'w', encoding='utf-8') as f:
        pass  # Create empty file
    return str(filepath)

@pytest.fixture
def short_file(tmp_path):
    """
    Fixture for creating a file with text too short for reliable detection.
    
    Args:
        tmp_path: pytest built-in fixture that provides a temporary directory
        
    Returns:
        str: Path to a file with very short content
    """
    filepath = tmp_path / "short.txt"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("Hi")  # Very short text
    return str(filepath)

@pytest.fixture
def stdin_redirect(monkeypatch):
    """
    Fixture for redirecting stdin for CLI testing.
    
    Args:
        monkeypatch: pytest built-in fixture for modifying functions/attributes
        
    Returns:
        function: A function that sets up stdin with specified content
    """
    from io import StringIO
    
    def _set_stdin(content):
        monkeypatch.setattr('sys.stdin', StringIO(content))
        # Make stdin.isatty() return False to simulate piped input
        monkeypatch.setattr('sys.stdin.isatty', lambda: False)
        
    return _set_stdin

@pytest.fixture
def stdout_capture(monkeypatch):
    """
    Fixture for capturing stdout for CLI testing.
    
    Args:
        monkeypatch: pytest built-in fixture for modifying functions/attributes
        
    Returns:
        tuple: A function to set up capture and a function to get captured output
    """
    from io import StringIO
    
    captured_output = StringIO()
    
    def _setup_capture():
        monkeypatch.setattr('sys.stdout', captured_output)
        
    def _get_captured():
        return captured_output.getvalue()
        
    return _setup_capture, _get_captured

@pytest.fixture
def stderr_capture(monkeypatch):
    """
    Fixture for capturing stderr for CLI testing.
    
    Args:
        monkeypatch: pytest built-in fixture for modifying functions/attributes
        
    Returns:
        tuple: A function to set up capture and a function to get captured output
    """
    from io import StringIO
    
    captured_error = StringIO()
    
    def _setup_capture():
        monkeypatch.setattr('sys.stderr', captured_error)
        
    def _get_captured():
        return captured_error.getvalue()
        
    return _setup_capture, _get_captured