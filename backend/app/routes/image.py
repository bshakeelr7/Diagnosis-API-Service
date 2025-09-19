import shutil, tempfile, os
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from backend.app.models.image_model import TimmChestModel, UltralyticsYOLOModel, TFChestModel, TFAlzheimerModel
from backend.app.utils.mapping import chest_mapping, brain_mapping, alzheimer_mapping

router = APIRouter()

_chest_models = {}
_brain_model = None
_alz_model = None

def get_chest_model(name: str) -> TimmChestModel:
    if name not in _chest_models:
        if name == "tf_efficientnetv2_b0":
            _chest_models[name] = TimmChestModel("tf_efficientnetv2_b0.pt", "tf_efficientnetv2_b0")
        elif name == "swin_tiny_patch4_window7_224":
            _chest_models[name] = TimmChestModel("swin_tiny_patch4_window7_224.pt", "swin_tiny_patch4_window7_224")
        elif name == "best_chest_xray_model.h5":
            _chest_models[name] = TFChestModel("best_chest_xray_model.h5")    
        else:
            raise HTTPException(status_code=400, detail="Unknown chest model")
    return _chest_models[name]


def get_brain_model() -> UltralyticsYOLOModel:
    global _brain_model
    if _brain_model is None:
        _brain_model = UltralyticsYOLOModel(
            "brain_best.pt",
            ["glioma_tumor", "meningioma_tumor", "no_tumor", "pituitary_tumor"]
        )
    return _brain_model


def get_alz_model():
    global _alz_model
    if _alz_model is None:
        _alz_model = UltralyticsYOLOModel(
            "alz_best.pt",
            ["MildDemented", "VeryMildDemented", "ModerateDemented", "NoDemented"]
        )
    return _alz_model



@router.post("/image/predict")
async def predict_image(
    disease: str = Form(...),
    model_name: str = Form(...),
    file: UploadFile = File(...)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        if disease.lower() == "chest":
            model = get_chest_model(model_name)
            pred_class, conf = model.predict_from_path(tmp_path)
            return JSONResponse({
                "result": chest_mapping(pred_class),
                "predicted_class": pred_class,
                "confidence": conf
            })

        elif disease.lower() == "brain":
            model = get_brain_model()
            pred_class, conf = model.predict_from_path(tmp_path)
            return JSONResponse({
                "result": brain_mapping(pred_class),
                "predicted_class": pred_class,
                "confidence": conf
            })
        elif disease.lower() == "alzheimer":
            if model_name == "alz_cnn_model.keras":  
                print("Inference with Alzheimer model")
                model = TFAlzheimerModel(
                    "alzheimer_model.keras"
                   # ["MildImpairment", "VeryMildImpairment", "ModerateImpairment", "NoImpairment"]
                )
                pred_class, conf = model.predict_from_path(tmp_path)
                return JSONResponse({
                    "result": alzheimer_mapping(pred_class),
                    "predicted_class": pred_class,
                    "confidence": conf
                })
            else:  # default to Ultralytics YOLO model
                model = get_alz_model()
                print("default model running")
                pred_class, conf = model.predict_from_path(tmp_path)
                return JSONResponse({
                    "result": alzheimer_mapping(pred_class),
                    "predicted_class": pred_class,
                    "confidence": conf
                })

        # elif disease.lower() == "alzheimer":
        #     model = get_alz_model()
        #     pred_class, conf = model.predict_from_path(tmp_path)
        #     return JSONResponse({
        #         "result": alzheimer_mapping(pred_class),
        #         "predicted_class": pred_class,
        #         "confidence": conf
        #     })

        raise HTTPException(status_code=400, detail="Unsupported disease type")

    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


