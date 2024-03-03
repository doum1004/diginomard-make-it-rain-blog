import fiftyone as fo
import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.rpn import AnchorGenerator
import glob

def load_model():
    # Load pre-trained Faster R-CNN model
    model = fasterrcnn_resnet50_fpn(pretrained=True)
    # Replace the classifier with a new one, since we're using a different number of classes
    num_classes = 91  # COCO dataset contains 91 classes
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model

def get_coco_labels(dataset):
    # Get COCO class names from the dataset
    return dataset.classes

def caption_image(image_path, model, coco_labels):
    # Transform the image
    transform = transforms.Compose([transforms.ToTensor()])
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0)
    
    # Pass the image through the model
    model.eval()
    with torch.no_grad():
        predictions = model(image_tensor)
    
    # Get prediction labels
    labels = predictions[0]['labels']
    
    # Print the top 3 prediction labels
    for label in labels[:3]:
        label_id = label.item()
        label_name = coco_labels[label_id]
        print(f"Label: {label_name}")

# Load COCO 2017 dataset
dataset = fo.zoo.load_zoo_dataset("coco-2017")

# Load the model
model = load_model()

# Get COCO labels from the dataset
coco_labels = get_coco_labels(dataset)

# Test images in a folder
folderPath = '/Users/alex.lee/Downloads/Test/'
image_files = [f for f in glob.glob(folderPath + "**/*.jpg", recursive=True)]

# Generate descriptions for each image
for image_file in image_files:
    print(f"Processing image: {image_file}")
    caption_image(image_file, model, coco_labels)
    print()  # Add a line break between images
