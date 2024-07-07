import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import sys

def get_aplitude_to_db(audio_file, duration):
    y, sr = librosa.load(audio_file, sr=None)
    
    print("loading done")
    # Extract first `sample_duration` seconds
    y = y[:int(sr * duration)]
    
    # Calculate spectrogram
    D = np.abs(librosa.stft(y))

    print("calculations complete")

    return librosa.amplitude_to_db(D, ref=np.max), sr


#does the lowest level of the rating system
def rateFrequency( a, b, factor):
    v = pow(a * b, 1) * factor

    v -= pow(abs(a-b)*factor, 3) * 0.8

    return v

#gos through full song
def plot_spectrogram(audio_file1, audio_file2, sample_duration=1.0):

    first, sr1 = get_aplitude_to_db(audio_file1, sample_duration)
    second, sr2 = get_aplitude_to_db(audio_file2, sample_duration)

    if sr1 != sr2:
        print("audio file sample rates not the same aborting")
        return

    rating = np.copy(first)

    print("for loop")

    xLen = min(len(first), len(second))
    yLen = min(len(first[0]), len(second[0]))

    loudness1 = [0] * yLen
    loudness2 = [0] * yLen

    maxRating = 0

    sampleCount = 1
    totalValue = 0
    
    print(len(first), "   ", len(second))
    print(len(first[0]), "   ", len(second[0]))

    print("x ", xLen, "  y ", yLen)
    
    for x in range(xLen):
        print("%.2f" % ((x/1024) * 100), "%")
        for y in range(yLen):
            
            # print(x, "  ", y)
            a = pow(first[x][y] / 80 + 1, 2)
            b = pow(second[x][y] / 80 + 1, 2)

            loudness1[y] += a
            loudness2[y] += b

            



            factor = 1

            if x > 20:
                factor = max(1 - (x-20)/30 ,0)
            
            maxRating += rateFrequency(a, a, factor)

            v = rateFrequency(a, b, factor)
            rating[x][y] = v
            first[x][y] = pow(a, 1) * factor
            second[x][y] = pow(b, 1) * factor
            totalValue += v 
            sampleCount += 1
    
    score = 0

    totalLoudness = 0
    for i in range(len(loudness1)):
        totalLoudness += abs(loudness1[i] - loudness2[i])
    

    print(totalLoudness/len(loudness1))

    # totalValue*= (totalValue/0.0019265993)

    totalValue = (totalValue / maxRating) * 100

    totalLoudness /= len(loudness1)
    totalLoudness *= -100000

    print("total value ", totalValue)
    print("total loudness ", totalLoudness/ sampleCount)

    score = totalLoudness / sampleCount + totalValue

    print("samples ", sampleCount, " score: ", score)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(first, sr=sr1, x_axis='time', y_axis='log')
    plt.title(audio_file1)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(second, sr=sr1, x_axis='time', y_axis='log')
    plt.title(audio_file2)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(rating, sr=sr1, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('rating ' + str(score))
    plt.show()

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("not enough arguments, program.exe song1.mp3 song2.mp3 <seconds>")
        exit()
    
    audio_file1 = sys.argv[1]  # Replace with your audio file path
    audio_file2 = sys.argv[2] # Replace with your audio file path
    plot_spectrogram(audio_file1, audio_file2, int(sys.argv[3]))
