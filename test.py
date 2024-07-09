import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import sys
import matplotlib
import signal

def get_aplitude_to_db(audio_file, duration=0):
    y, sr = librosa.load(audio_file, sr=None)
    
    print("loading done")
    # Extract first `sample_duration` seconds

    if duration != 0:
        y = y[:int(sr * duration)]
    
    # Calculate spectrogram
    D = np.abs(librosa.stft(y))

    print("calculations complete")

    return librosa.amplitude_to_db(D, ref=np.max), sr


totalNegative = 0

#does the lowest level of the rating system
def rateFrequency( a, b, factor):
    v = pow(a * b, 1) * factor

    s = pow(abs(a-b)*factor, 3) * 0.8
    # s = 0

    v -= s

    global totalNegative
    totalNegative += s

    return v

#gos through full song
def plot_spectrogram(audio_file1, audio_file2, sample_duration=0):

    first, sr1 = get_aplitude_to_db(audio_file1, sample_duration)
    second, sr2 = get_aplitude_to_db(audio_file2, sample_duration)

    if sr1 != sr2:
        print("audio file sample rates not the same aborting")
        return


    print("for loop")


    xLen = min(len(first), len(second))
    yLen = min(len(first[0]), len(second[0]))


    # maxFreq = 80
    # first = first[:maxFreq, :yLen]
    # second = second[:maxFreq, :yLen]

    # print("length ", len(first), "  xLen ", xLen)


    # xLen = maxFreq

    loudness1 = [0] * yLen
    loudness2 = [0] * yLen

    sampleCount = 1

    maxRating = 0
    
    print(len(first), "   ", len(second))
    print(len(first[0]), "   ", len(second[0]))

    print("x ", xLen, "  y ", yLen)

    rating_arr = np.copy(first)
    rating = 0

    # first = np.divide(first, 80)
    # second = np.divide(second, 80)

    # first = np.add(first, 1)
    # second = np.add(second, 1)

    # first = np.pow(first, 2)
    # second = np.pow(second, 2)

    # rating_arr = np.multiply(first, second)
    # rating_arr = np.subtract(rating_arr, np.multiply(np.pow(np.abs(np.subtract(first,second)), 3), 0.8))
    # rating = np.sum(rating_arr)

    # maxRating = np.multiply(first,first)
    # maxRating = np.subtract(maxRating, np.multiply(np.pow(np.abs(np.subtract(first,first)), 3), 0.8))
    # maxRating = np.sum(maxRating)


    
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
            rating_arr[x][y] = v
            first[x][y] = pow(a, 1) * factor
            second[x][y] = pow(b, 1) * factor
            rating += v 
            sampleCount += 1
    
    score = 0

    totalLoudness = 0
    for i in range(len(loudness1)):
        totalLoudness += abs(loudness1[i] - loudness2[i])
    

    print(totalLoudness/len(loudness1))

    # rating*= (rating/0.0019265993)
    global totalNegative
    rating = (rating / maxRating) * 100
    totalNegative = (totalNegative / maxRating) * 100

    totalLoudness /= len(loudness1)
    totalLoudness *= -100000

    print("total value ", rating)
    print("total loudness ", totalLoudness/ sampleCount)
    print("total panelty ", totalNegative)

    score = totalLoudness / sampleCount + rating

    # figure, axis = plt.subplots(2, 2)
    print("samples ", sampleCount, " score: ", score)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(rating_arr, sr=sr1, x_axis='time', y_axis='log', fmin=0, fmax=1000)
    plt.title('rating ' + str(score))
    plt.colorbar(format='%+2.0f dB')
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(first, sr=sr1, x_axis='time', y_axis='log', fmin=0, fmax=1000)
    plt.title(audio_file1)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(second, sr=sr1, x_axis='time', y_axis='log', fmin=0, fmax=1000)
    plt.title(audio_file2)
    plt.show()

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("not enough arguments, program.exe song1.mp3 song2.mp3 <seconds> (optional)")
        exit()
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # matplotlib.use('TkAgg')
    audio_file1 = sys.argv[1]  # Replace with your audio file path
    audio_file2 = sys.argv[2] # Replace with your audio file path

    duration = 0
    if len(sys.argv) == 4:
        duration = int(sys.argv[3])
    plot_spectrogram(audio_file1, audio_file2, duration)
