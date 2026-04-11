"""
Background Tasks
Handles cleanup and background processing
"""

import os
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def cleanup_old_files(upload_folder='uploads', output_folder='outputs', max_age_hours=24):
    """
    Clean up old files from upload and output folders
    
    Args:
        upload_folder: Path to uploads folder
        output_folder: Path to outputs folder
        max_age_hours: Maximum age of files in hours
    """
    try:
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        folders = [upload_folder, output_folder]
        
        for folder in folders:
            if not os.path.exists(folder):
                continue
            
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    
                    if file_age > max_age_seconds:
                        try:
                            os.remove(filepath)
                            logger.info(f"Cleaned up old file: {filepath}")
                        except Exception as e:
                            logger.error(f"Failed to delete {filepath}: {str(e)}")
        
        logger.info("Cleanup task completed")
    
    except Exception as e:
        logger.error(f"Cleanup task error: {str(e)}")


def process_conversion_task(input_path, target_format, options=None):
    """
    Process conversion task in background
    This is a placeholder for Celery or similar queue system
    
    Args:
        input_path: Path to input file
        target_format: Target format
        options: Conversion options
        
    Returns:
        dict: Conversion result
    """
    from utils.converter import UniversalConverter
    
    try:
        converter = UniversalConverter()
        result = converter.convert(input_path, target_format, options or {})
        return result
    except Exception as e:
        logger.error(f"Background conversion error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def schedule_periodic_cleanup():
    """
    Schedule periodic cleanup task
    This would typically be implemented with Celery Beat or APScheduler
    """
    import threading
    
    def cleanup_worker():
        while True:
            cleanup_old_files()
            # Run every 6 hours
            time.sleep(6 * 3600)
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    logger.info("Periodic cleanup scheduled")