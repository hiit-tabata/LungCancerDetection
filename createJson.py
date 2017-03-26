#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 19:20:50 2017

@author: holman
"""

fileList = [
        "c1673993c070080c1d65aca6799c66f8",
        "c0f0eb84e70b19544943bed0ea6bd374",
        "c0625c79ef5b37e293b5753d20b00c89",
        "c05acf3bd59f5570783138c01b737c3d",
        "c020f5c28fc03aed3c125714f1c3cf2a",
        "be2be08151ef4d3aebd3ea4fcd5d364b",
        "bda661b08ad77afb79bd35664861cd62",
        "d81704ee56c124cc1434640918a3299c",
        "d7e5640b52c8e092ec277febc81478da",
        "d7aa27d839b1ecb03dbf011af4bcb092",
        "d777a77cc7a2ec2f1eed68799cc9075c",
        "d7713d80767cfdaad5e3db537849d8d0",
        "0015ceb851d7251b8f399e39779d1e7d",
        "006b96310a37b36cccb2ab48d10b49a3",
        "008464bb8521d09a42985dd8add3d0d2",
        "00edff4f51a893d80dae2d42a7f45ad1",
        "0257df465d9e4150adef13303433ff1e",
        "02801e3bbcc6966cb115a962012c35df",
        "04a8c47583142181728056310759dea1",
        "07bca4290a2530091ce1d5f200d9d526",
        "059d8c14b2256a2ba4e38ac511700203",
        "0708c00f6117ed977bbe1b462b56848c",
        "05609fdb8fa0895ac8a9be373144dac7",
        "07349deeea878c723317a1ce42cc7e58",
        "064366faa1a83fdcb18b2538f1717290",
        "028996723faa7840bb57f57e28275e4c",
        "0acbebb8d463b4b9ca88cf38431aac69",
        "09d7c4a3e1076dcfcae2b0a563a28364",
        "081f4a90f24ac33c14b61b97969b7f81",
        "0c0de3749d4fe175b7a5098b060982a1",
        "0c37613214faddf8701ca41e6d43f56e",
        "2a2300103f80aadbfac57516d9a95365",
        "28a9b77a9113ce491433d3ea47fa8fc9",
        "243e69389ae5738d3f89386b0efddbcd",
        "2619ed1e4eca954af4dcbc4436ef8467",
        "ac00af80df36484660203d5816d697aa",
        "ac4c6d832509d4cee3c7ac93a9227075",
        "b5de57869d863bdc1b84b0194e79a9d3",
        "b6d8dd834f2ff1ed7a5154e658460699",
        "b17cb533d71d63d548ce47b48b34c23c",
        "b83ce5267f3fd41c7029b4e56724cd08",
        "b84c43bed6c51182d7536619b747343a",
        "b7045ebff6dbb0023087e0399d00b873"
        ]

for i in range(len(fileList)):
    filePath = "./stage1_jpg/"+ fileList[i]+"/"+fileList[i]+".json"
    with open(filePath,"w+") as f:
        f.write("[]")


