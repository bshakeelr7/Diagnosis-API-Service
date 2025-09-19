CHEST_CLASSES = ["normal", "pneumonia_bacteria", "pneumonia_virus"]
CHEST_CLASSES_H5 = ["normal", "pneumonia"]
BRAIN_CLASSES = ["glioma_tumor", "meningioma_tumor", "no_tumor", "pituitary_tumor"]
ALZHEIMER_CLASSES = ["MildDemented", "VeryMildDemented", "ModerateDemented", "NoDemented"]
ALZHEIMER_CLASSES_CNN = ["MildImpairment", "VeryMildImpairment", "ModerateImpairment", "NoImpairment"]


def chest_mapping(pred_class: str) -> str:
    return "No" if pred_class.lower() == "normal" else "Yes"

def chest_mapping_h5(pred_class: str) -> str:
    return "No" if pred_class.lower() == "normal" else "Yes"

def brain_mapping(pred_class: str) -> str:
    return "No" if pred_class.lower() in ("no_tumor", "no_tumour") else "Yes"

def alzheimer_mapping(pred_class: str) -> str:
    return "No" if pred_class.lower() in ("nondemented", "no_demented", "nodemented") else "Yes"
