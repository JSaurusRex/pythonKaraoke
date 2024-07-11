import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import sys
import matplotlib
import signal
import math


QUALITY = 2048*4

def get_aplitude_to_db(audio_file, duration=0):
    y, sr = librosa.load(audio_file, sr=None)
    
    print("loading done")
    # Extract first `sample_duration` seconds

    if duration != 0:
        y = y[:int(sr * duration)]
    
    global QUALITY
    
    # Calculate spectrogram
    D = np.abs(librosa.stft(y, n_fft=QUALITY))

    print("calculations complete")

    return librosa.amplitude_to_db(D, ref=np.max), sr


totalNegative = 0

def scaleRating(a, max):

    a = (a/max)

    print("pre scale ", a*100, "%")
    
    a = 1-a
    power = 1
    if a > 0:
        power = 1.7
    a = 1-pow(a,power)
    return a*100

def filter(a):
    return pow(a / 80 + 1, 3)

def factor(x):
    global QUALITY
    scaler = QUALITY/2048
    if x > 20*scaler:
        return max(1 - (x-20*scaler)/(30*scaler) ,0)
    return 1

#does the lowest level of the rating system
def rateFrequency( a, b, factor, giveNegative=False):
    v = pow(a * b, 1) * factor

    s = pow(abs(a-b)*factor, 3) * 0.8
    # s = 0

    v -= s

    if giveNegative:
        return v,s
    return v

#gos through full song
def plot_spectrogram(audio_file1, audio_file2, sample_duration=0):
    matplotlib.use('TkAgg')

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

    rating_arr = np.zeros((xLen, yLen))

    global QUALITY

    xLen = int(50*QUALITY/2048)

    print("x ", xLen, "  y ", yLen)

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

    global totalNegative


    xRange = range(xLen)
    yRange = range(yLen)
    for x in xRange:
        print("%.2f" % ((x/xLen) * 100), "%    ", x)
        low_rating = 0
        middle_rating = 0
        high_rating = 0

        low_penalty = 0
        middle_penalty = 0
        high_penalty = 0
        for y in yRange:
            
            # print(x, "  ", y)

            f = first[x][y]
            s = second[x][y]
            a = filter(f)
            b = filter(s)

            loudness1[y] += a
            loudness2[y] += b
            
            maxRating += rateFrequency(a, a, factor(x))

            m, s = rateFrequency(a, b, factor(x), True)
            highestRating = m

            middle_rating += m
            middle_penalty += s

            if x < xLen / 2 -1:
                v, s = rateFrequency(filter(first[x*2][y]), filter(second[x][y]), factor(x*2), True)
                highestRating = max(v, highestRating)
                high_rating += v
                high_penalty += s

            if x > 5:
                v, s = rateFrequency(filter(first[int(x/2)][y]), filter(second[x][y]), factor(x), True)
                highestRating = max(v, highestRating)
                low_rating += v
                low_penalty += s

            # rating_arr[x][y] = a*b + a * 0.5 + b * 0.5
            if abs(highestRating) < 0.1:
                highestRating = m
            rating_arr[x][y] = highestRating * 100
            # first[x][y] = (a * factor(x) - 1)*80 
            # second[x][y] = (b * factor(x) - 1) * 80
            sampleCount += 1

        if abs(low_rating) < 0.1:
            low_rating = -999
        if abs(high_rating) < 0.1:
            high_rating = -999
        print(low_rating, middle_rating, high_rating)

        p = middle_penalty
        r = middle_rating

        if r < low_rating:
            p = low_penalty
            r = low_rating
        
        if r < high_rating:
            p = high_penalty
            r = high_rating

        print("rating added ", r, "  penalty ", p)
        rating += r
        totalNegative += p
    score = 0

    totalLoudness = 0
    for i in range(len(loudness1)):
        totalLoudness += abs(loudness1[i] - loudness2[i])
    

    print(totalLoudness/len(loudness1))

    # rating*= (rating/0.0019265993)
    print(rating)
    rating = scaleRating(rating, maxRating)
    totalNegative = scaleRating(rating, maxRating)

    totalLoudness /= len(loudness1)
    totalLoudness *= -100000

    print("total value ", rating)
    print("total loudness ", totalLoudness/ sampleCount)
    print("total panelty ", totalNegative)

    score = totalLoudness / sampleCount + rating

    sr1 *= 2

    # figure, axis = plt.subplots(2, 2)
    print("samples ", sampleCount, " score: ", score)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(rating_arr, sr=sr1, x_axis='time', y_axis='log', n_fft=QUALITY)
    plt.title('rating ' + str(score))
    plt.colorbar(format='%+2.0f dB')
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(first, sr=sr1, x_axis='time', y_axis='log', n_fft=QUALITY)
    plt.title(audio_file1)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(second, sr=sr1, x_axis='time', y_axis='log', n_fft=QUALITY)
    plt.title(audio_file2)
    plt.show()

    return score

# Example usage
# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("not enough arguments, program.exe song1.mp3 song2.mp3 <seconds> (optional)")
#         exit()
    
#     signal.signal(signal.SIGINT, signal.SIG_DFL)
#     audio_file1 = sys.argv[1]  # Replace with your audio file path
#     audio_file2 = sys.argv[2] # Replace with your audio file path

#     duration = 0
#     if len(sys.argv) == 4:
#         duration = int(sys.argv[3])
#     plot_spectrogram(audio_file1, audio_file2, duration)
