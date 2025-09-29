import os
from PIL import Image
import pillow_heif
import sys
from multiprocessing import Pool, cpu_count
from functools import partial
import time

def convert_single_image(filepath, directory):
    """단일 HEIC 이미지를 PNG로 변환하는 함수"""
    filename = os.path.basename(filepath)
    
    # HEIC 파일인지 확인
    if not filename.lower().endswith(".heic"):
        return f"Skipped (not HEIC): {filename}"
    
    print(f"Converting: {filepath}")
    
    try:
        # HEIC 파일 읽기
        heif_file = pillow_heif.read_heif(filepath)
        
        # PIL Image로 변환
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
        )
        
        # PNG 파일명 생성
        new_filename = os.path.splitext(filename)[0] + ".png"
        new_filepath = os.path.join(directory, new_filename)
        
        # PNG로 저장
        image.save(new_filepath, "PNG")
        
        return f"Success: {filename} -> {new_filename}"
        
    except Exception as e:
        # 실제 HEIC가 아닌 경우 확장자만 변경
        try:
            image = Image.open(filepath)
            new_filename = os.path.splitext(filename)[0] + ".png"
            new_filepath = os.path.join(directory, new_filename)
            image.save(new_filepath, "PNG")
            return f"Converted (non-HEIC): {filename} -> {new_filename}"
        except:
            return f"Error: {filename} - {str(e)}"

def convert_heic_to_png_parallel(directory, num_workers=None):
    """병렬처리로 디렉토리 내 모든 HEIC 파일을 PNG로 변환"""
    
    # 워커 수 설정 (기본: CPU 코어 수)
    if num_workers is None:
        num_workers = cpu_count()
    
    print(f"Using {num_workers} workers for parallel processing")
    print(f"Processing directory: {directory}")
    print("-" * 50)
    
    # HEIC 파일 목록 가져오기
    heic_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(".heic"):
            filepath = os.path.join(directory, filename)
            heic_files.append(filepath)
    
    if not heic_files:
        print("No HEIC files found in the directory.")
        return
    
    print(f"Found {len(heic_files)} HEIC files to convert")
    print("-" * 50)
    
    # 시작 시간 기록
    start_time = time.time()
    
    # 병렬처리 실행
    with Pool(processes=num_workers) as pool:
        # partial을 사용하여 directory 파라미터 고정
        convert_func = partial(convert_single_image, directory=directory)
        
        # 병렬로 변환 실행
        results = pool.map(convert_func, heic_files)
    
    # 결과 출력
    print("\n" + "=" * 50)
    print("Conversion Results:")
    print("=" * 50)
    
    success_count = 0
    error_count = 0
    
    for result in results:
        print(result)
        if result.startswith("Success") or result.startswith("Converted"):
            success_count += 1
        elif result.startswith("Error"):
            error_count += 1
    
    # 소요 시간 계산
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 50)
    print(f"Conversion completed in {elapsed_time:.2f} seconds")
    print(f"Successfully converted: {success_count} files")
    if error_count > 0:
        print(f"Errors: {error_count} files")
    print(f"Average time per file: {elapsed_time/len(heic_files):.2f} seconds")
    print("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python heic-to-png.py <directory_path> [num_workers]")
        print("Example: python heic-to-png.py ./heic_img")
        print("Example with workers: python heic-to-png.py ./heic_img 4")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    # 디렉토리 존재 확인
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a directory.")
        sys.exit(1)
    
    # 워커 수 옵션 (선택사항)
    num_workers = None
    if len(sys.argv) >= 3:
        try:
            num_workers = int(sys.argv[2])
            if num_workers < 1:
                print("Warning: num_workers must be at least 1. Using default.")
                num_workers = None
        except ValueError:
            print("Warning: Invalid num_workers value. Using default (CPU count).")
    
    # 변환 실행
    convert_heic_to_png_parallel(directory, num_workers)