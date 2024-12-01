from inference_sdk import InferenceHTTPClient


class ClientProcessingImage:
    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key="1nned9R042vZm3Lgm2vH"
    )

    mapping = {
        'T033': 'Дуб',
        'T068': 'Тополь',
        'T074': 'Береза',
        'T045': 'Береза',
        'T030': 'Ель',
        'T057': 'Хвойное растение',
        'T089': 'Сосна',
        'T050': 'Куст'
    }

    async def make_generator_tree_data_by_image(self, image):
        result = self.CLIENT.infer(image, model_id="tree-dataset-2023/8")
        for data_tree in result['predictions']:
            yield {
                'x_point': data_tree['x'],
                'y_point': data_tree['y'],
                'width': data_tree['width'],
                'height': data_tree['height'],
                'confidence': data_tree['confidence'],
                'tree_type': self.mapping.get(data_tree['class'], 'растение не распознано'),
            }
