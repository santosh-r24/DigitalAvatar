# import subprocess
from pathlib import Path
import os
from pydub import AudioSegment
import torchaudio
import seaborn as sns
import matplotlib.pyplot as plt
from logzero import logger

def download_yt_video(url, output_audio_name="audio.wav"):
  """Takes in a url and output audio name, and extracts audio from video and downloads it using yt-dlp.

     args:
      url: url of the video to be downloaded
      output_video_name: name of the output video file

    example:
      download_yt_video('https://www.youtube.com/watch?v=ysLiABvVos8', 'output_audio.wav')
  """
  extension = Path(output_audio_name).suffix.lstrip('.').lower()
  command = [
        'yt-dlp',
        '-x',  # Extract audio only
        '--audio-quality', '64K',
        '--audio-format', extension,  # Choose the format you want (mp3, wav, etc.)
        '-o', f'{output_audio_name}',  # Output file name
        url  # Video URL
    ]
  try:
    # Execute the command
    subprocess.run(command, check=True)
    print(f"Audio downloaded and saved as {output_audio_name}")
  except subprocess.CalledProcessError as e:
    print(f"Error occurred: {e}")

  return output_audio_name

# Function to split the audio into chunks of roughly 10 MB each
def split_audio_into_chunks(input_file, output_folder, chunk_size_mb=10):
    # Load audio file
    audio = AudioSegment.from_file(input_file)
    
    # Calculate number of bytes per millisecond (since pydub works in ms)
    bytes_per_ms = len(audio.raw_data) / len(audio)

    # Calculate the size in bytes for each chunk (10MB -> 10 * 1024 * 1024)
    chunk_size_bytes = chunk_size_mb * 1024 * 1024

    # Calculate the duration in milliseconds for each chunk
    chunk_duration_ms = chunk_size_bytes / bytes_per_ms

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through the audio and export chunks
    for i in range(0, len(audio), int(chunk_duration_ms)):
        chunk = audio[i:i + int(chunk_duration_ms)]
        chunk_name = os.path.join(output_folder, f"chunk_{i // int(chunk_duration_ms) + 1}.mp3")
        print(f"Exporting {chunk_name}")
        chunk.export(chunk_name, format="wav")

def visualise_distribution_chunk_length(folder):
  chunk_duration = []
  audio_files = list(folder.glob("*.wav"))
  for file_path in audio_files:
    waveform, sample_rate = torchaudio.load(file_path)
    duration_seconds = waveform.shape[1] / sample_rate
    chunk_duration.append(duration_seconds)

  plt.figure(figsize=(10, 6))
  sns.histplot(chunk_duration, bins=20, kde=True, color='skyblue')
  plt.xlabel('Length of Audio Chunks (seconds)')
  plt.ylabel('Density')
  plt.title(f'Distribution of Length of Audio Chunks {folder}')

  output_plot_path = f"{folder}_chunk_length_distribution.png"
  plt.savefig(output_plot_path, format="png", dpi=300)
  print(f"Plot saved as {output_plot_path}")

if __name__ == "__main__":
  folders = ["processed_audio_2", "processed_audio_3", "processed_audio_3_agg3"]
  # folders = ["processed_audio"]
  for folder in folders:
    logger.debug(f"processing for {folder}")
    input_file = Path(folder)
    visualise_distribution_chunk_length(input_file)




    # input_file = Path("processed_audio")
  # input_file = Path("vegeta_quotes2.wav")
  # output_folder = "output_audio_chunks"
  # split_audio_into_chunks(input_file, output_folder)
#   download_yt_video("https://youtu.be/j5ROvCUArEg?si=NWg__4vUzbN_qqqr", "vegeta_quotes_with_bgmusic.wav") # Vegeta Quotes
#   download_yt_video("https://www.youtube.com/watch?v=Udu0Qc1zcR4&list=PLT7YQtwNLtQ0a3jwCM1g1S6V1TkuZTNvW&index=2&t=298s", "vegeta_quotes2.wav")
#   download_yt_video("https://youtu.be/ejfIISzou7c?si=-a6_Ds64W2IvIUAF", "vegeta_38mins.wav")