import logging
import numpy as np
from ultralytics import YOLO
from config import MODEL_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("detection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("detection")

class ObjectDetector:
    """Class for handling object detection using YOLO model."""
    
    def __init__(self, model_path=None, confidence_threshold=None):
        """Initialize the object detector.
        
        Args:
            model_path (str, optional): Path to the YOLO model file
            confidence_threshold (float, optional): Minimum confidence threshold for detections
        """
        self.model_path = model_path or MODEL_CONFIG['model_path']
        self.confidence_threshold = confidence_threshold or MODEL_CONFIG['confidence_threshold']
        self._model = None
        self._load_model()
    
    def _load_model(self):
        """Load the YOLO model."""
        try:
            logger.info(f"Loading model from {self.model_path}")
            self._model = YOLO(self.model_path)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    @property
    def model(self):
        """Get the YOLO model instance, loading it if necessary."""
        if self._model is None:
            self._load_model()
        return self._model
    
    def detect_objects(self, image_path):
        """Detect objects in an image.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Dictionary with detected objects and their counts
            list: List of detailed detection results
        """
        try:
            logger.info(f"Detecting objects in {image_path}")
            results = self.model(image_path, conf=self.confidence_threshold)
            
            # Simple object counts
            detected_objects = {}
            
            # Detailed detection results
            detailed_results = []
            
            for result in results:
                for i, box in enumerate(result.boxes.data):
                    # Extract box data
                    x1, y1, x2, y2, confidence, class_id = box.tolist()
                    class_id = int(class_id)
                    label = self.model.names[class_id]
                    
                    # Update object count
                    detected_objects[label] = detected_objects.get(label, 0) + 1
                    
                    # Add detailed detection
                    detailed_results.append({
                        'label': label,
                        'confidence': confidence,
                        'box': [x1, y1, x2, y2],
                        'width': x2 - x1,
                        'height': y2 - y1,
                        'area': (x2 - x1) * (y2 - y1)
                    })
            
            logger.info(f"Detected {len(detailed_results)} objects in {image_path}")
            return detected_objects, detailed_results
            
        except Exception as e:
            logger.error(f"Error detecting objects: {e}")
            return {}, []
    
    def compare_images(self, planogram_path, shelf_path):
        """Compare a planogram image with a shelf image.
        
        Args:
            planogram_path (str): Path to the planogram image
            shelf_path (str): Path to the shelf image
            
        Returns:
            dict: Comparison results including adherence score and detailed metrics
        """
        try:
            # Detect objects in both images
            planogram_objects, planogram_details = self.detect_objects(planogram_path)
            shelf_objects, shelf_details = self.detect_objects(shelf_path)
            
            # Calculate basic adherence score
            total_expected = sum(planogram_objects.values())
            matches = sum(min(planogram_objects.get(obj, 0), shelf_objects.get(obj, 0)) 
                         for obj in planogram_objects)
            
            adherence_score = (matches / total_expected) * 100 if total_expected > 0 else 0
            
            # Calculate detailed metrics
            missing_items = {}
            extra_items = {}
            
            # Find missing items (in planogram but not in shelf or fewer in shelf)
            for item, count in planogram_objects.items():
                shelf_count = shelf_objects.get(item, 0)
                if shelf_count < count:
                    missing_items[item] = count - shelf_count
            
            # Find extra items (in shelf but not in planogram or more in shelf)
            for item, count in shelf_objects.items():
                planogram_count = planogram_objects.get(item, 0)
                if count > planogram_count:
                    extra_items[item] = count - planogram_count
            
            return {
                'adherence_score': adherence_score,
                'total_expected': total_expected,
                'total_matched': matches,
                'planogram_objects': planogram_objects,
                'shelf_objects': shelf_objects,
                'missing_items': missing_items,
                'extra_items': extra_items
            }
            
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            return {
                'error': str(e),
                'adherence_score': 0
            }

# Create a singleton instance
detector = ObjectDetector()

# Convenience functions that use the singleton
def detect_objects(image_path):
    """Detect objects in an image using the singleton detector."""
    return detector.detect_objects(image_path)

def compare_images(planogram_path, shelf_path):
    """Compare images using the singleton detector."""
    return detector.compare_images(planogram_path, shelf_path)
