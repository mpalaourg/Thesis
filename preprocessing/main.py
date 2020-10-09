import pandas
import numpy as np
import os

from helpers import exportData, checkData, copyData, normData, splitMixedSessions 
from dataStats import dataStats

if __name__ == "__main__":
    #exportData(VM=True)
    #checkData(VM=True)
    #copyData()
    #splitMixedSessions()
    dataStats()