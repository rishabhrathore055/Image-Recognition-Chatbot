from transformers import BlipProcessor, BlipForConditionalGeneration

def load_captioning_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

def generate_caption(processor, model, image):
    inputs = processor(image, return_tensors="pt")
    caption_output = model.generate(**inputs)
    caption = processor.decode(caption_output[0], skip_special_tokens=True)
    return caption
