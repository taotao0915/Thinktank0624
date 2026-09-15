#这个文件当中就是把各种配置全部变成配置类，后期我们只需要在这个文件当中写一遍dotenv即可
#后期哪个文件当中用到相关的配置，只需要把相关的配置类导进来获取配置项即可
import os

from dotenv import load_dotenv
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(dotenv_path=env_path, override=True)

class MinerUConfig:
    mineru_token = os.getenv('MINERU_TOKEN')

class LLMConfig:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    openai_api_base = os.getenv('OPENAI_API_BASE')
    llm_default_model = os.getenv('LLM_DEFAULT_MODEL')
    llm_default_temperature = float(os.getenv('LLM_DEFAULT_TEMPERATURE'))
    vl_model = os.getenv('VL_MODEL')
    item_model = os.getenv('ITEM_MODEL')

class MinioConfig:
    minio_endpoint = os.getenv('MINIO_ENDPOINT')
    minio_access_key = os.getenv('MINIO_ACCESS_KEY')
    minio_secret_key = os.getenv('MINIO_SECRET_KEY')
    minio_bucket_name = os.getenv('MINIO_BUCKET_NAME')
    minio_img_dir = os.getenv('MINIO_IMG_DIR')