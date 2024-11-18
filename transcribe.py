import torch
from pathlib import Path
from transformers import WhisperProcessor, WhisperForConditionalGeneration, WhisperTokenizer
from transformers import pipeline
import json
import time
from logzero import logger

if __name__ == "__main__":
    # file_path = Path("D://Python_stuff//DigitalAvatar//transcribe_sample")
    
    file_paths = [Path("D://Python_stuff//DigitalAvatar//processed_audio_2"), Path("D://Python_stuff//DigitalAvatar//DeepFilterNet2_result"), Path("D://Python_stuff//DigitalAvatar//DeepFilterNet_result")]
    # output_json = Path("D://Python_stuff//DigitalAvatar//transcribed_results//transcribe_1.json")
    # files = [str(os.path.join(file_path, f)) for f in os.listdir(file_path) if f.endswith('.wav')]

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    processor = WhisperProcessor.from_pretrained("openai/whisper-base")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
    tokenizer = WhisperTokenizer.from_pretrained("openai/whisper-base")
    model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="english", task="transcribe")

    pipe = pipeline(
  "automatic-speech-recognition",
  tokenizer = tokenizer,
  model=model,
  feature_extractor=processor.feature_extractor,
  device=device,
#   language ="en"
)

    # transcriptions = [{"file_name": ds[i]["file"], "transcription": decoded[i]} for i in range(len(decoded))]
    
    start_time = time.time()
    logger.debug(f"transcription starting")
    for folder in file_paths:
        result = []
        logger.debug(f"transcription starting for {folder.name}")
        output_json = Path(f"D://Python_stuff//DigitalAvatar//transcribed_results//transcribe_{folder.name}.json")
        for file in folder.glob("*.wav"):
            transcription = pipe(str(file))
            result.append({"file_name":file.name, "transcription":transcription['text']})
        
        with open(output_json, "w") as outfile:
            json.dump(result, outfile, indent=4)

    end_time = time.time()
    logger.debug(f"The time taken for processing is {end_time - start_time}")
    
    # with open(output_json, "w") as outfile:
    #     json.dump(result, outfile, indent=4)
    
    # end_time = time.time()
    # logger.debug(f"The time taken for json dump is {end_time - start_time}")
    
    # for item in result:
    #     print(item)