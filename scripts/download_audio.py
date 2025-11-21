#!/usr/bin/env python3
"""
Classicap Dataset Audio Download Script
========================================
Downloads audio segments from YouTube based on metadata CSV file.

Usage:
    python download_audio.py --metadata download_metadata.csv --output audio/
    python download_audio.py --metadata download_metadata.csv --output audio/ --workers 4
    python download_audio.py --metadata download_metadata.csv --output audio/ --piece-ids id1,id2,id3

Requirements:
    - yt-dlp: pip install yt-dlp
    - ffmpeg: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import shutil

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check_dependencies():
    """Check if required tools are installed"""
    print(f"{Colors.HEADER}Checking dependencies...{Colors.ENDC}")
    
    # Check yt-dlp
    try:
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, timeout=5)
        print(f"{Colors.OKGREEN}✓ yt-dlp found: {result.stdout.strip()}{Colors.ENDC}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"{Colors.FAIL}✗ yt-dlp not found. Install: pip install yt-dlp{Colors.ENDC}")
        return False
    
    # Check ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        version_line = result.stdout.split('\n')[0]
        print(f"{Colors.OKGREEN}✓ ffmpeg found: {version_line}{Colors.ENDC}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"{Colors.FAIL}✗ ffmpeg not found. Install: brew install ffmpeg (macOS) or apt install ffmpeg (Linux){Colors.ENDC}")
        return False
    
    return True

def download_and_extract(piece_id, youtube_url, start_time, end_time, output_path, audio_filename):
    """
    Download YouTube video and extract audio segment
    
    Args:
        piece_id: Unique piece identifier
        youtube_url: YouTube video URL
        start_time: Start timestamp in seconds
        end_time: End timestamp in seconds
        output_path: Output directory path
        audio_filename: Target audio filename
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        output_file = output_path / audio_filename
        
        # Skip if already exists
        if output_file.exists():
            return (True, f"{Colors.WARNING}Already exists{Colors.ENDC}")
        
        # Create temporary directory for this download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Step 1: Download best audio using yt-dlp
            download_cmd = [
                'yt-dlp',
                '-f', 'bestaudio',  # Download best audio format
                '--output', str(temp_path / 'full_audio.%(ext)s'),
                '--no-playlist',
                '--quiet',
                '--no-warnings',
                youtube_url
            ]
            
            result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                return (False, f"{Colors.FAIL}Download failed: {result.stderr[:100]}{Colors.ENDC}")
            
            # Find the downloaded audio file (webm, m4a, etc.)
            audio_files = list(temp_path.glob('full_audio.*'))
            
            if not audio_files:
                return (False, f"{Colors.FAIL}No audio file found after download{Colors.ENDC}")
            
            full_audio_path = audio_files[0]
            
            # Step 2: Extract segment using ffmpeg
            duration = float(end_time) - float(start_time)
            
            # First extract the segment without fade
            temp_output = temp_path / 'temp_nofade.wav'
            extract_cmd = [
                'ffmpeg',
                '-i', str(full_audio_path),
                '-ss', str(start_time),
                '-t', str(duration),
                '-ar', '48000',  # 48kHz sample rate
                '-ac', '2',      # Stereo
                '-y',
                '-loglevel', 'error',
                str(temp_output)
            ]
            
            result = subprocess.run(extract_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                return (False, f"{Colors.FAIL}Extraction failed: {result.stderr[:100]}{Colors.ENDC}")
            
            # Step 3: Apply 100ms fade-in and fade-out to prevent audio pops/clicks
            fade_duration = 0.1  # 100ms
            fade_cmd = [
                'ffmpeg',
                '-i', str(temp_output),
                '-af', f'afade=t=in:st=0:d={fade_duration},afade=t=out:st={duration-fade_duration}:d={fade_duration}',
                '-y',
                '-loglevel', 'error',
                str(output_file)
            ]
            
            result = subprocess.run(fade_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return (False, f"{Colors.FAIL}Extraction failed: {result.stderr[:100]}{Colors.ENDC}")
            
            # Verify output file exists and has reasonable size
            if not output_file.exists():
                return (False, f"{Colors.FAIL}Output file not created{Colors.ENDC}")
            
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            if file_size < 0.1:
                output_file.unlink()  # Remove too-small file
                return (False, f"{Colors.FAIL}Output file too small ({file_size:.2f} MB){Colors.ENDC}")
            
            return (True, f"{Colors.OKGREEN}Success ({file_size:.1f} MB){Colors.ENDC}")
    
    except subprocess.TimeoutExpired:
        return (False, f"{Colors.FAIL}Timeout{Colors.ENDC}")
    except Exception as e:
        return (False, f"{Colors.FAIL}Error: {str(e)[:100]}{Colors.ENDC}")

def process_entry(row, output_path, index, total):
    """Process a single metadata entry"""
    piece_id = row['piece_id']
    youtube_url = row['youtube_url']
    start_time = row['start_time']
    end_time = row['end_time']
    audio_filename = row['audio_filename']
    movement = row['movement']
    
    print(f"[{index}/{total}] Processing: {piece_id} - {movement[:50]}...")
    
    success, message = download_and_extract(
        piece_id, youtube_url, start_time, end_time, 
        output_path, audio_filename
    )
    
    status = "✓" if success else "✗"
    print(f"  {status} {message}")
    
    return {
        'piece_id': piece_id,
        'success': success,
        'message': message,
        'movement': movement
    }

def main():
    parser = argparse.ArgumentParser(
        description='Download Classicap dataset audio from YouTube',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all audio files
  python download_audio.py --metadata download_metadata.csv --output audio/
  
  # Download with 4 parallel workers (faster)
  python download_audio.py --metadata download_metadata.csv --output audio/ --workers 4
  
  # Download specific pieces only
  python download_audio.py --metadata download_metadata.csv --output audio/ --piece-ids id1,id2,id3
  
  # Continue interrupted download (skips existing files)
  python download_audio.py --metadata download_metadata.csv --output audio/
        """
    )
    
    parser.add_argument('--metadata', required=True, 
                       help='Path to download_metadata.csv file')
    parser.add_argument('--output', required=True,
                       help='Output directory for audio files')
    parser.add_argument('--workers', type=int, default=1,
                       help='Number of parallel download workers (default: 1)')
    parser.add_argument('--piece-ids', type=str,
                       help='Comma-separated list of piece IDs to download (optional)')
    
    args = parser.parse_args()
    
    # Print header
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Classicap Dataset Audio Downloader{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    # Check dependencies
    if not check_dependencies():
        print(f"\n{Colors.FAIL}Please install missing dependencies and try again.{Colors.ENDC}")
        sys.exit(1)
    
    print()
    
    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_path.absolute()}\n")
    
    # Read metadata
    metadata_path = Path(args.metadata)
    if not metadata_path.exists():
        print(f"{Colors.FAIL}Error: Metadata file not found: {metadata_path}{Colors.ENDC}")
        sys.exit(1)
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Filter by piece IDs if specified
    if args.piece_ids:
        piece_id_list = [pid.strip() for pid in args.piece_ids.split(',')]
        rows = [row for row in rows if row['piece_id'] in piece_id_list]
        print(f"Filtered to {len(rows)} pieces based on --piece-ids\n")
    
    print(f"Total entries to process: {len(rows)}\n")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    # Process entries
    results = []
    
    if args.workers == 1:
        # Sequential processing
        for i, row in enumerate(rows, 1):
            result = process_entry(row, output_path, i, len(rows))
            results.append(result)
    else:
        # Parallel processing
        print(f"Using {args.workers} parallel workers\n")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(process_entry, row, output_path, i, len(rows)): row
                for i, row in enumerate(rows, 1)
            }
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Download Summary{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"✓ Successful: {Colors.OKGREEN}{successful}/{len(results)}{Colors.ENDC}")
    print(f"✗ Failed: {Colors.FAIL}{failed}/{len(results)}{Colors.ENDC}")
    
    if failed > 0:
        print(f"\n{Colors.WARNING}Failed downloads:{Colors.ENDC}")
        for r in results:
            if not r['success']:
                print(f"  - {r['piece_id']}: {r['movement'][:50]}...")
                print(f"    Reason: {r['message']}")
    
    # Integrity check: verify all expected files exist
    if not args.piece_ids:  # Only do full check if downloading all files
        print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}Integrity Check{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
        
        missing_files = []
        for row in rows:
            audio_file = output_path / row['audio_filename']
            if not audio_file.exists():
                missing_files.append(row['piece_id'])
        
        if missing_files:
            print(f"{Colors.WARNING}⚠️  Found {len(missing_files)} missing files!{Colors.ENDC}")
            print(f"\nAttempting to download missing files...\n")
            
            # Retry missing files
            retry_results = []
            for i, piece_id in enumerate(missing_files, 1):
                row = next(r for r in rows if r['piece_id'] == piece_id)
                print(f"[{i}/{len(missing_files)}] Retrying: {piece_id}...")
                result = process_entry(row, output_path, i, len(missing_files))
                retry_results.append(result)
            
            retry_success = sum(1 for r in retry_results if r['success'])
            print(f"\nRetry results: {Colors.OKGREEN}{retry_success}/{len(missing_files)} successful{Colors.ENDC}")
            
            # Final check
            still_missing = [r['piece_id'] for r in retry_results if not r['success']]
            if still_missing:
                print(f"\n{Colors.FAIL}Still missing {len(still_missing)} files after retry:{Colors.ENDC}")
                for piece_id in still_missing:
                    print(f"  - {piece_id}")
            else:
                print(f"\n{Colors.OKGREEN}✓ All missing files successfully downloaded!{Colors.ENDC}")
        else:
            print(f"{Colors.OKGREEN}✓ All {len(rows)} files verified present!{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}Download complete! Audio files saved to: {output_path.absolute()}{Colors.ENDC}\n")

if __name__ == '__main__':
    main()
