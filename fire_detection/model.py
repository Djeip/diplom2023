import os
import logging

import torch
from PIL import Image
from label_studio_ml.model import LabelStudioMLBase
from label_studio_ml.utils import get_image_size, get_single_tag_keys
from label_studio.core.utils.io import json_load, get_data_dir
from label_studio.core.settings.base import DATA_UNDEFINED_NAME
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

yolov5_repo_dir = r"yolov5"
pretrained_model_path = r"yolov5\real.pt"


class Invoice_Model(LabelStudioMLBase):
    """Load a YOLOv5 model by torch-hub from local"""

    def __init__(self, yolov5_repo_dir=yolov5_repo_dir, pretrained_model_path=pretrained_model_path, train_output=None,
                 **kwargs):
        super(Invoice_Model, self).__init__(**kwargs)

        upload_dir = os.path.join(get_data_dir(), 'media', 'upload')
        self.image_dir = upload_dir
        logger.debug(f'{self.__class__.__name__}  reads image from {self.image_dir}')

        # create a label map
        self.label_map = {}
        self.model = torch.hub.load(yolov5_repo_dir, "custom", path=pretrained_model_path, source="local")

        self.from_name, self.to_name, self.value, self.labels_in_config = get_single_tag_keys(
            self.parsed_label_config, 'RectangleLabels', 'Image'
        )
        print(self.value)
        schema = list(self.parsed_label_config.values())[0]
        self.labels_in_config = set(self.labels_in_config)

        # collect label ,aps from "predcited_values="invoice no, invoice date attribute in <Label> tag
        self.label_attrs = schema.get('labels_attrs')
        if self.label_attrs:
            for label_name, label_attrs in self.label_attrs.items():
                for predicted_value in label_attrs.get('predicted_values', '').split(','):
                    self.label_map[predicted_value] = label_name

    def _get_image_url(self, task):
        # image_url = task['data'].get(self.value) or task['data'].get(DATA_UNDEFINED_NAME)
        image_url = task['data'][self.value]
        return image_url

    def predict(self, tasks, **kwargs):

        results = []
        all_scores = []
        print("LABELS IN CONFIG:", self.labels_in_config)
        for task in tasks:
            image_url = self._get_image_url(task)
            image_path = self.get_local_path(image_url, project_dir=self.image_dir)
            img = Image.open(image_path)
            img_width, img_height = get_image_size(image_path)
            preds = self.model(img, size=img_width)
            preds_df = preds.pandas().xyxy[0]
            for x_min, y_min, x_max, y_max, confidence, class_, name_ in zip(preds_df['xmin'], preds_df['ymin'],
                                                                             preds_df['xmax'], preds_df['ymax'],
                                                                             preds_df['confidence'], preds_df['class'],
                                                                             preds_df['name']):
                # add label name from label_map
                output_label = self.label_map.get(name_, name_)
                print("--" * 20)
                print(f"Output Label {output_label}")
                if output_label not in self.labels_in_config:
                    print(output_label + ' label not found in project config.')
                    continue

                results.append({
                    'from_name': self.from_name,
                    'to_name': self.to_name,
                    "original_width": img_width,
                    "original_heoght": img_height,
                    'type': 'rectanglelabels',
                    'value': {
                        'rectanglelabels': name_,
                        'x': x_min / img_width * 100,
                        'y': y_min / img_height * 100,
                        'width': (x_max - x_min) / img_width * 100,
                        'height': (y_max - y_min) / img_height * 100
                    },
                    'score': confidence
                })
                all_scores.append(confidence)
                print(results)

        avg_score = sum(all_scores) / max(len(all_scores), 1)

        return [{
            'result': results,
            'score': avg_score
        }]