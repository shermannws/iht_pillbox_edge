from inference import InferencePipeline
from inference.core.interfaces.stream.sinks import UDPSink, render_boxes

from dotenv import dotenv_values

import warnings
warnings.filterwarnings('ignore')

config = dotenv_values(".env")
ROBOFLOW_API_KEY = config["ROBOFLOW_API_KEY"]

udp_sink = UDPSink.init(ip_address="127.0.0.1", port=12345)

# create an inference pipeline object
pipeline = InferencePipeline.init(
    model_id="ai-drug-analysis-service/3",
    video_reference=0,
    on_prediction=udp_sink.send_predictions, #render_boxes, #
    api_key=ROBOFLOW_API_KEY,
)

# start the pipeline
pipeline.start()
# wait for the pipeline to finish
pipeline.join()
