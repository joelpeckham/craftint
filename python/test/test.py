# test.py
# This utility runs all the lox files in the testCode directory first with jlox and the with pylox.
# It then compares the output of each to see if they are the same.
# Written by: Joel Peckham.
# Last Modified: 2022-03-18

import os, sys, subprocess, filecmp, difflib

# Assume the testCode directory is in the same directory as this file.
thisDir = os.path.dirname(os.path.realpath(__file__))
testDir = os.path.join(thisDir, "testCode")

JLOX_PATH = "/Users/joel/Documents/School/OPL/craftint/clox"
PYLOX_PATH = "/Users/joel/Documents/School/OPL/craftint/pylox"

categories = [(cat, [os.path.join(os.path.join(testDir, cat),fileName) for fileName in os.listdir(os.path.join(testDir, cat))]) for cat in os.listdir(testDir)]

failedTests = []
for category, filePaths in categories:
    if category == "benchmark":
        continue
    for filePath in filePaths:
        # Run the file with jlox.
        result = subprocess.run([JLOX_PATH, filePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        jloxOutput = result.stdout.decode("utf-8")
        jloxErrors = result.stderr.decode("utf-8")
        # Run the file with pylox.
        result = subprocess.run([PYLOX_PATH, filePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pyloxOutput = result.stdout.decode("utf-8")
        pyloxErrors = result.stderr.decode("utf-8")
        # Compare the outputs.
        fileName = os.path.basename(filePath)
        
        if jloxOutput != pyloxOutput:
            print( "❌ Test failed: " + fileName + " in " + category + ".")
            failedTests.append({"filename": fileName, "category": category, "jlox": jloxOutput, "pylox": pyloxOutput, "jloxError": jloxErrors, "pyloxError": pyloxErrors})
        else:
            print( "✅ Test passed: " + fileName + " in " + category + ".")
        
if len(failedTests) > 0:
    with open("failures.txt", "w") as f:
        for test in failedTests:
            f.write("❌ Test failed: " + test["filename"] + " in " + test["category"] + "\n")
            f.write("Jlox output:\n" + test["jlox"] + "\n")
            f.write("Pylox output:\n" + test["pylox"] + "\n")
            f.write("Jlox error output:\n" + test["jloxError"] + "\n")
            f.write("Pylox error output:\n" + test["pyloxError"] + "\n")
            f.write("\n")
