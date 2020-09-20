import pandas
import os
import pickle
from statistics import mean 
import matplotlib.pyplot as plt

if __name__ == "__main__":
    current_directory = os.getcwd()
    
    #allStdUsage = pickle.load( open( "Usage.pickle", "rb" ) )
    #allStdRAM = pickle.load( open( "RAM.pickle", "rb" ) )
    roughUsage = pickle.load( open( "roughUsage.pickle", "rb" ) )
    roughRAM = pickle.load( open( "roughRAM.pickle", "rb" ) )
    #for sample in roughUsage:
    #    print(mean(sample))
    for sample in roughRAM:
        print(mean(sample))
    
    '''
    for idx, (stdUsage, stdRAM) in enumerate( zip(allStdUsage, allStdRAM) ):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(19.20,9.83))
    
        fig.suptitle(f"Window size = {(idx+1)*10}")
        ax1.hist(stdUsage, density=True, histtype='bar', facecolor='b', alpha=0.5)
        ax1.set_xlabel("Standard Deviation of CPU Usage")
        ax1.set_ylabel("Probability")
        
        ax2.hist(stdRAM, density=True, histtype='bar', facecolor='b', alpha=0.5)
        ax2.set_xlabel("Standard Deviation of Available RAM")
        ax2.set_ylabel("Probability")
        #plt.show()
        plt.savefig(f"std_{(idx+1)*10}.png", format='png')
    ''' 
    '''
    lengths = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    for length in lengths:
        windowFiles = f"{current_directory}//windowFiles_{length}"
        fileName = windowFiles + "//" + "ad896f37958c4b3b84ef8a0c1d792eb0-2020-08-06_11-25-31.csv"
        df = pandas.read_csv(fileName)
        usage = df.usage
        RAM = df.RAM

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(19.20,9.83))
        fig.suptitle(f"Window size = {length}")
        ax1.plot(usage)
        ax1.set_xlabel("Sample")
        ax1.set_ylabel("CPU Usage [%]")
        
        ax2.plot(RAM)
        ax2.set_xlabel("Sample")
        ax2.set_ylabel("Available RAM [%]")
        #plt.show()
        plt.savefig(f"usage_{length}.png", format='png')
    '''