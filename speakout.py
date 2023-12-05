import pygame

def play_audio(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        pygame.mixer.quit()
        pygame.quit()

if __name__ == "__main__":
    audio_file_path = "audio.wav"  # Change this to your audio file path
    play_audio(audio_file_path)
