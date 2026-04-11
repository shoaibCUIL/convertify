"""
Video Engine
Handles all video and audio operations using FFmpeg
"""

import os
import uuid
import subprocess
import json


class VideoEngine:
    """Engine for video and audio operations"""
    
    def convert_format(self, input_path, target_format, quality, output_folder):
        """
        Convert video to different format
        
        Args:
            input_path: Video file path
            target_format: Target format (mp4, avi, mov, etc.)
            quality: Quality level (low, medium, high)
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            output_filename = f"converted_{uuid.uuid4()}.{target_format}"
            output_path = os.path.join(output_folder, output_filename)
            
            # Quality presets
            quality_settings = {
                'low': {'crf': '28', 'preset': 'fast'},
                'medium': {'crf': '23', 'preset': 'medium'},
                'high': {'crf': '18', 'preset': 'slow'}
            }
            
            settings = quality_settings.get(quality, quality_settings['medium'])
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-crf', settings['crf'],
                '-preset', settings['preset'],
                '-c:a', 'aac',
                '-b:a', '192k',
                '-y',  # Overwrite output
                output_path
            ]
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'FFmpeg error: {result.stderr}'
                }
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_audio(self, input_path, audio_format, output_folder):
        """
        Extract audio from video
        
        Args:
            input_path: Video file path
            audio_format: Output audio format (mp3, wav, aac, etc.)
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            output_filename = f"audio_{uuid.uuid4()}.{audio_format}"
            output_path = os.path.join(output_folder, output_filename)
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vn',  # No video
                '-acodec', self._get_audio_codec(audio_format),
                '-ab', '192k',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'FFmpeg error: {result.stderr}'
                }
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def convert_audio_format(self, input_path, target_format, output_folder):
        """
        Convert audio format
        
        Args:
            input_path: Audio file path
            target_format: Target format (mp3, wav, etc.)
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            output_filename = f"converted_{uuid.uuid4()}.{target_format}"
            output_path = os.path.join(output_folder, output_filename)
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', self._get_audio_codec(target_format),
                '-ab', '192k',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'FFmpeg error: {result.stderr}'
                }
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def change_resolution(self, input_path, width, height, output_folder):
        """
        Change video resolution
        
        Args:
            input_path: Video file path
            width: Target width
            height: Target height
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            ext = os.path.splitext(input_path)[1]
            output_filename = f"resized_{uuid.uuid4()}{ext}"
            output_path = os.path.join(output_folder, output_filename)
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', f'scale={width}:{height}',
                '-c:a', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'FFmpeg error: {result.stderr}'
                }
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def trim_video(self, input_path, start_time, end_time, output_folder):
        """
        Trim video
        
        Args:
            input_path: Video file path
            start_time: Start time (seconds or HH:MM:SS)
            end_time: End time (seconds or HH:MM:SS)
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            ext = os.path.splitext(input_path)[1]
            output_filename = f"trimmed_{uuid.uuid4()}{ext}"
            output_path = os.path.join(output_folder, output_filename)
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ss', str(start_time),
                '-to', str(end_time),
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'FFmpeg error: {result.stderr}'
                }
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def merge_videos(self, input_paths, output_folder):
        """
        Merge multiple videos
        
        Args:
            input_paths: List of video file paths
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            # Create file list for FFmpeg
            list_file = os.path.join(output_folder, f"filelist_{uuid.uuid4()}.txt")
            with open(list_file, 'w') as f:
                for path in input_paths:
                    f.write(f"file '{path}'\n")
            
            ext = os.path.splitext(input_paths[0])[1]
            output_filename = f"merged_{uuid.uuid4()}{ext}"
            output_path = os.path.join(output_folder, output_filename)
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up list file
            os.remove(list_file)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'FFmpeg error: {result.stderr}'
                }
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_video_info(self, input_path):
        """
        Get video metadata
        
        Args:
            input_path: Video file path
            
        Returns:
            dict: Video information
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                input_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': 'Failed to get video info'
                }
            
            info = json.loads(result.stdout)
            
            return {
                'success': True,
                'info': info
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_audio_codec(self, format_name):
        """Get appropriate audio codec for format"""
        codec_map = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'aac': 'aac',
            'ogg': 'libvorbis',
            'm4a': 'aac'
        }
        return codec_map.get(format_name, 'copy')