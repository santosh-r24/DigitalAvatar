import webrtcvad
import torchaudio
import numpy as np
import torch
from pathlib import Path
from logzero import logger
import os 

def load_audio(filename, target_sample_rate=16000):
    waveform, sample_rate = torchaudio.load(filename)
    logger.debug("Audio loaded with sample rate %d and shape %s", sample_rate, waveform.shape)
    
    # Resample if sample rate is not 16000
    if sample_rate != target_sample_rate:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
        waveform = resampler(waveform)
        sample_rate = target_sample_rate
        logger.debug("Resampled audio to %d Hz", sample_rate)
    
    return waveform.squeeze().numpy(), sample_rate

def convert_to_pcm16(audio):
    return (audio * 32767).astype(np.int16)

def vad_split(audio, sample_rate, frame_duration_ms=30, aggressiveness=3):
    vad = webrtcvad.Vad(aggressiveness)
    frame_size = int(sample_rate * frame_duration_ms / 1000)  # Frame size in samples
    num_frames = len(audio) // frame_size

    segments = []
    current_segment = []
    for i in range(num_frames):
        frame = audio[i * frame_size:(i + 1) * frame_size]
        is_speech = vad.is_speech(convert_to_pcm16(frame).tobytes(), sample_rate)
        
        if is_speech:
            current_segment.append(frame)
        elif current_segment:
            segments.append(np.concatenate(current_segment))
            current_segment = []

    if current_segment:
        segments.append(np.concatenate(current_segment))

    logger.debug("Total segments created: %d", len(segments))
    return segments

def adjust_segments(segments, sample_rate, min_duration=3, max_duration=10):
    min_samples = min_duration * sample_rate
    max_samples = max_duration * sample_rate

    adjusted_segments = []
    buffer = []

    for segment in segments:
        segment_length = len(segment)

        if segment_length < min_samples:
            buffer.extend(segment)
            if len(buffer) >= min_samples:
                adjusted_segments.append(np.array(buffer[:max_samples]))
                buffer = buffer[max_samples:]
        elif segment_length > max_samples:
            while len(segment) > max_samples:
                adjusted_segments.append(segment[:max_samples])
                segment = segment[max_samples:]
            if len(segment) >= min_samples:
                adjusted_segments.append(segment)
        else:
            adjusted_segments.append(segment)

    logger.debug("Adjusted segments count: %d", len(adjusted_segments))
    return adjusted_segments

def save_audio_chunks(segments, sample_rate, output_dir="processed_audio"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, segment in enumerate(segments):
        filename = f"{output_dir}/chunk_{i}.wav"
        torchaudio.save(filename, torch.from_numpy(segment).unsqueeze(0), sample_rate)
        logger.debug("Saved chunk %d to %s", i, filename)

if __name__ == "__main__":
    output_folder = "processed_audio_3_agg3"
    input_file = Path("D://Python_stuff//DigitalAvatar//audio//vegeta_38mins.wav")
    
    logger.debug("Starting processing for %s", input_file)
    audio, sr = load_audio(input_file)
    audio = audio.mean(axis=0)  # Convert to mono by averaging channels
    vad_segments = vad_split(audio, sr, aggressiveness=3)  # Try setting aggressiveness to 2 or 3 for testing
    if vad_segments:
        logger.debug("VAD segments created: %d", len(vad_segments))
        adjusted_segments = adjust_segments(vad_segments, sr)
        save_audio_chunks(adjusted_segments, sr, output_folder)
    else:
        logger.debug("No speech segments detected.")
