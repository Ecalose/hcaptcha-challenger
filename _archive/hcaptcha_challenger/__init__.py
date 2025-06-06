# -*- coding: utf-8 -*-
# Time       : 2022/2/15 17:43
# Author     : QIN2DIM
# GitHub     : https://github.com/QIN2DIM
# Description:
from __future__ import annotations

from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from hcaptcha_challenger.models import QuestionResp, Answers, Status, CaptchaResponse
from hcaptcha_challenger.onnx.modelhub import ModelHub
from hcaptcha_challenger.onnx.resnet import ResNetControl
from hcaptcha_challenger.onnx.yolo import YOLOv8
from hcaptcha_challenger.onnx.yolo import YOLOv8Seg
from hcaptcha_challenger.tools.image_label_area_select import AreaSelector
from hcaptcha_challenger.tools.image_label_binary import Classifier as BinaryClassifier
from hcaptcha_challenger.tools.image_label_binary import LocalBinaryClassifier
from hcaptcha_challenger.tools.prompt_handler import (
    label_cleaning,
    diagnose_task,
    regularize_prompt_message,
    prompt2task,
    handle,
)
from hcaptcha_challenger.tools.zero_shot_image_classifier import (
    ZeroShotImageClassifier,
    DataLake,
    register_pipline,
)
from hcaptcha_challenger.utils import init_log

__all__ = [
    "BinaryClassifier",
    "LocalBinaryClassifier",
    "ZeroShotImageClassifier",
    "register_pipline",
    "DataLake",
    "AreaSelector",
    "QuestionResp",
    "Answers",
    "Status",
    "CaptchaResponse",
    "label_cleaning",
    "diagnose_task",
    "regularize_prompt_message",
    "prompt2task",
    "handle",
    "ModelHub",
    "ResNetControl",
    "YOLOv8",
    "YOLOv8Seg",
    "install",
]

LOG_DIR = Path(__file__).parent.joinpath("logs", "{time:YYYY-MM-DD}")
init_log(
    runtime=LOG_DIR.joinpath("runtime.log"),
    error=LOG_DIR.joinpath("error.log"),
    serialize=LOG_DIR.joinpath("serialize.log"),
)


def install(
    upgrade: bool | None = False,
    flush_yolo: bool | Iterable[str] = False,
    pypi: bool = False,
    clip: bool = False,
    username: str = "QIN2DIM",
    repo: str = "hcaptcha-challenger",
    conf_="objects2024.yaml",
    **kwargs,
):
    if pypi is True:
        from hcaptcha_challenger.utils import PyPI

        PyPI("hcaptcha-challenger").install()

    modelhub = ModelHub.from_github_repo(username=username, repo=repo, conf_=conf_)
    modelhub.pull_objects(upgrade=upgrade)
    modelhub.assets.flush_runtime_assets(upgrade=upgrade)

    if clip is True:
        from hcaptcha_challenger.tools.zero_shot_image_classifier import register_pipline

        register_pipline(modelhub, install_only=True)

    if flush_yolo is not None:
        modelhub.parse_objects()

        if isinstance(flush_yolo, bool) and flush_yolo:
            flush_yolo = [modelhub.circle_segment_model]
        if isinstance(flush_yolo, Iterable):
            pending_models = []
            for model_name in flush_yolo:
                if model_name in modelhub.ashes_of_war:
                    modelhub.match_net(model_name, install_only=True)
                    pending_models.append(model_name)
            return pending_models


def set_reverse_proxy(https_cdn: str):
    parser = urlparse(https_cdn)
    if parser.netloc and parser.scheme.startswith("https"):
        ModelHub.CDN_PREFIX = https_cdn
