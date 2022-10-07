#By Minmode
#Special thanks: Chrrox, korenkonder, BlueSkyth, Brolijah, samyuu
from inc_noesis import *
from vmd import Vmd
import noesis
import rapi
import os.path
import math
import ast
import copy
from collections import MutableMapping as Map

#Write vmd file (required for a3da)
exportVmd = False
pmxScale = 12.5

#Options
vc2 = False #Use vertex colour 2 instead of 1 (bin format only)
h2v = True #Convert horizontal FOV to vertical
printMatInfo = False #Print extra material info
debug = False #Print debug log

def registerNoesisTypes():
    handle = noesis.register("Fates/Grand Order Model", ".bin")
    noesis.setHandlerTypeCheck(handle, objectSetFgoCheckType)
    noesis.setHandlerLoadModel(handle, objectSetFgoLoadModel)

    handle = noesis.register("Project Diva Model", ".bin")
    noesis.setHandlerTypeCheck(handle, objectSetCheckType)
    noesis.setHandlerLoadModel(handle, objectSetLoadModel)

    handle = noesis.register("Project Diva Model", ".osd")
    noesis.setHandlerTypeCheck(handle, osdCheckType)
    noesis.setHandlerLoadModel(handle, osdLoadModel)

    handle = noesis.register("Soul Reverse Model", ".bin")
    noesis.setHandlerTypeCheck(handle, objectSetSrCheckType)
    noesis.setHandlerLoadModel(handle, objectSetSrLoadModel)

    handle = noesis.register("Project Diva Texture", ".bin")
    noesis.setHandlerTypeCheck(handle, txpCheckType)
    noesis.setHandlerLoadRGBA(handle, txpLoadRGBA)

    handle = noesis.register("Project Diva Texture", ".txd")
    noesis.setHandlerTypeCheck(handle, txdCheckType)
    noesis.setHandlerLoadRGBA(handle, txdLoadRGBA)

    handle = noesis.register("Soul Reverse Texture", ".bin")
    noesis.setHandlerTypeCheck(handle, txpSrCheckType)
    noesis.setHandlerLoadRGBA(handle, txpSrLoadRGBA)

    handle = noesis.register("Fates/Grand Order Texture", ".bin")
    noesis.setHandlerTypeCheck(handle, txpFgoCheckType)
    noesis.setHandlerLoadRGBA(handle, txpFgoLoadRGBA)

    handle = noesis.register("Project Diva Sprite", ".bin")
    noesis.setHandlerTypeCheck(handle, spriteCheckType)
    noesis.setHandlerLoadRGBA(handle, spriteLoadRGBA)

    handle = noesis.register("Project Diva Sprite", ".spr")
    noesis.setHandlerTypeCheck(handle, sprCheckType)
    noesis.setHandlerLoadRGBA(handle, sprLoadRGBA)

    handle = noesis.register("Project Diva Ibl", ".ibl")
    noesis.setHandlerTypeCheck(handle, iblCheckType)
    noesis.setHandlerLoadRGBA(handle, iblLoadRGBA)

    handle = noesis.register("Project Diva Emcs", ".emcs")
    noesis.setHandlerTypeCheck(handle, emcsCheckType)
    noesis.setHandlerLoadRGBA(handle, emcsLoadRGBA)

    handle = noesis.register("Project Diva Motion", ".bin")
    noesis.setHandlerTypeCheck(handle, motBinCheckType)
    noesis.setHandlerLoadModel(handle, motBinLoadModel)

    handle = noesis.register("Project Diva Motion", ".mot")
    noesis.setHandlerTypeCheck(handle, motCheckType)
    noesis.setHandlerLoadModel(handle, motLoadModel)

    #handle = noesis.register("Project Diva Script", ".dsc")
    #noesis.setHandlerTypeCheck(handle, noeCheckGeneric)
    #noesis.setHandlerLoadModel(handle, dscLoadScript)

    #handle = noesis.register("Project Diva Expression Script", ".bin")
    #noesis.setHandlerTypeCheck(handle, expBinCheckType)
    #noesis.setHandlerLoadModel(handle, expLoadScript)

    #handle = noesis.register("Project Diva Expression Script", ".dex")
    #noesis.setHandlerTypeCheck(handle, expDexCheckType)
    #noesis.setHandlerLoadModel(handle, expLoadScript)

    handle = noesis.register("Project Diva 3D Animation", ".a3da")
    noesis.setHandlerTypeCheck(handle, a3daCheckType)
    noesis.setHandlerLoadModel(handle, a3daLoadModel)
    return 1

def objectSetCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readUInt()
    if magic != 0x05062500:
        return 0
    return 1

def osdCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "MOSD":
        return 0
    return 1

def osiCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "MOSI":
        return 0
    return 1

def objectSetSrCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readUInt()
    if magic != 0x804C444D:
        return 0
    return 1

def objectSetFgoCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readUInt()
    if magic != 0x05062500:
        return 0
    bs.seek(0x08, NOESEEK_REL)
    test = bs.readUInt()
    if test != 0x00:
        return 0
    return 1

def txpCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readUInt()
    if magic != 0x03505854:
        return 0
    return 1

def txdCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "MTXD":
        return 0
    return 1

def txiCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "MTXI":
        return 0
    return 1

def txpSrCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 5:
        return 0
    magic = bs.readUInt()
    if magic != 0x80584554:
        return 0
    return 1

def txpFgoCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    tCount = bs.readUShort()
    nSize = bs.readUByte()
    try:
        tName =  bs.readBytes(nSize).decode("ASCII").split('_',1)[0]
    except:
        return 0
    test = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName())).split('_',1)[0]
    if tName != test:
        return 0
    return 1

def spriteCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    if not rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName())).startswith("spr_"):
        return 0
    return 1

def sprCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "SPRC":
        return 0
    return 1

def spiCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "SPDB":
        return 0
    return 1

def iblCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 7:
        return 0
    magic = bs.readBytes(7).decode("ASCII")
    if magic != "VF5_IBL":
        return 0
    return 1

def emcsCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "EMCS":
        return 0
    return 1

def motBinCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    if not rapi.getLocalFileName(rapi.getLastCheckedName()).startswith("mot_"):
        return 0
    return 1

def motCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "MOTC":
        return 0
    return 1

def expBinCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readUInt()
    if magic != 0x64:
        return 0
    return 1

def expDexCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "EXPC":
        return 0
    return 1

def a3daCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic = bs.readBytes(4).decode("ASCII")
    if magic != "#A3D" and magic != 'A3DA':
        return 0
    return 1

def objectSetLoadModel(data, mdlList, fileName=None, fileDir=None, isMot=False):
    ctx = rapi.rpgCreateContext()
    if not fileName:
        fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))[:-4]
        fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    texDbData = getFileData(fileDir, "tex_db.bin")
    texDb = TexDb(32)
    texDb.readTexDb(NoeBitStream(texDbData))
    texDbMdataData = getFileDataMdata(fileDir, 'tex_db.bin')
    texDbMdata = TexDb(32)
    if texDbMdataData:
        texDbMdata.readTexDb(NoeBitStream(texDbMdataData))
    txpData = getFileData(fileDir, fileName + "_tex.bin")
    test = txpCheckType(txpData)
    if test == 0:
        noesis.messagePrompt("Invalid texture file.")
        return 0
    txp = Txp([], None, False)
    txp.readTxp(NoeBitStream(txpData), fileName)
    boneDataData = getFileData(fileDir, "bone_data.bin")
    boneData = BoneData(32)
    if fileName[:3].upper() != "CMN":
        skel = fileName[:3].upper()
    else:
        skel = None
    boneData.readBoneData(NoeBitStream(boneDataData), skel)
    objDbData = getFileData(fileDir, "obj_db.bin")
    objDb = ObjDb(32)
    objDb.readObjDb(NoeBitStream(objDbData), False)
    objDbMdataData = getFileDataMdata(fileDir, 'obj_db.bin')
    if objDbMdataData:
        objDbMdata = ObjDb(32)
        objDbMdata.readObjDb(NoeBitStream(objDbMdataData), False)
        if fileName.upper() in objDbMdata.db:
            objDb = objDbMdata
    objectSetDb = {}
    if fileName.upper() in objDb.db:
        objectSetDb = objDb.db[fileName.upper()]
    obj = ObjectSet(mdlList, txp.texList, objectSetDb, texDb, boneData, 32, None, texDbMdata)
    obj.readObjSet(NoeBitStream(data), data)
    if fileName.startswith("stg") and "pv" in fileName and "hrc" not in fileName and (len(fileName) == 11 or len(fileName) == 13):
        txp2Data = getFileData(fileDir, fileName[:-3] + "_tex.bin")
        test = txpCheckType(txp2Data)
        if test == 0:
            noesis.messagePrompt("Invalid texture file.")
            return 0
        txp2 = Txp([], None, False)
        txp2.readTxp(NoeBitStream(txp2Data), fileName[:-3])
        texObjData = getFileData(fileDir, fileName[:-3] + "_obj.bin")
        test = objectSetCheckType(texObjData)
        if test == 0:
            noesis.messagePrompt("Invalid object file.")
            return 0
        texObj = ObjectSet([], txp2.texList, objectSetDb, texDb, boneData, 32, None, texDbMdata)
        texObj.readObjSet(NoeBitStream(texObjData), texObjData)
        for i in range(len(mdlList[0].modelMats.texList)):
            mdlList[0].modelMats.texList[i] = texObj.texList[texObj.texDict[mdlList[0].modelMats.texList[i].name]]
    if isMot:
        return obj
    return 1

def osdLoadModel(data, mdlList, fileName=None, fileDir=None, isMot=False):
    ctx = rapi.rpgCreateContext()
    if not fileName:
        fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
        fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    txiData = getFileData(fileDir, fileName + ".txi")
    test = txiCheckType(txiData)
    if test == 0:
        noesis.messagePrompt("Invalid txi file.")
        return 0
    txi = Txi()
    txi.readTxi(NoeBitStream(txiData))
    txdData = getFileData(fileDir, fileName + ".txd")
    test = txdCheckType(txdData)
    if test == 0:
        noesis.messagePrompt("Invalid txd file.")
        return 0
    txd = Txd([])
    txd.readTxd(NoeBitStream(txdData), fileName, txi.texDb)
    boneData, boneDataDir = getBoneData(fileDir, "bone_data.bon", fileName[:3], fileName[-3:] + ".bon")
    if boneData != None:
        bone = Bone()
        boneDataName = rapi.getExtensionlessName(rapi.getLocalFileName(boneDataDir))
        if boneDataName != "bone_data":
            skel = boneDataName.upper()
        elif fileName[:3].upper() != "CMN":
            skel = fileName[:3].upper()
        else:
            skel = None
        bone.readBone(NoeBitStream(boneData), skel)
    else:
        bone = Bone()
        bone.boneData = BoneData(32)
    osiData = getFileData(fileDir, fileName + ".osi")
    test = osiCheckType(osiData)
    if test == 0:
        noesis.messagePrompt("Invalid osi file.")
        return 0
    osi = Osi()
    osi.readOsi(NoeBitStream(osiData))
    osd = Osd(mdlList, txd.texList, bone.boneData)
    osd.readOsd(data, osi.objDb.db[fileName.upper()], txi.texDb)
    if fileName.startswith("stg") and "pv" in fileName and "hrc" not in fileName and (len(fileName) == 11 or len(fileName) == 13):
        txi2Data = getFileData(fileDir, fileName[:-3] + ".txi")
        test = txiCheckType(txi2Data)
        if test == 0:
            noesis.messagePrompt("Invalid txi file.")
            return 0
        txi2 = Txi()
        txi2.readTxi(NoeBitStream(txi2Data))
        txd2Data = getFileData(fileDir, fileName[:-3] + ".txd")
        test = txdCheckType(txd2Data)
        if test == 0:
            noesis.messagePrompt("Invalid txd file.")
            return 0
        txd2 = Txd([])
        txd2.readTxd(NoeBitStream(txd2Data), fileName, txi2.texDb)
        mdlList[0].modelMats.texList = txd2.texList
    if isMot:
        return osd
    return 1

def objectSetSrLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))[4:]
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    txpData = getFileData(fileDir, "tex_" + fileName + ".bin")
    test = txpSrCheckType(txpData)
    if test == 0:
        noesis.messagePrompt("Invalid texture file.")
        return 0
    txp = Txp([], None, False)
    txp.readTxpSr(NoeBitStream(txpData))
    obj = ObjectSetSr()
    obj.readObjSet(NoeBitStream(data), mdlList, txp.texList)
    return 1

def objectSetFgoLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))[:-4]
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    txpData = getFileData(fileDir, fileName + "_tex.bin")
    test = txpFgoCheckType(txpData)
    if test == 0:
        noesis.messagePrompt("Invalid texture file.")
        return 0
    txp = Txp([], None, False)
    txp.readTxpFgo(NoeBitStream(txpData), fileName)
    obj = ObjectSetFgo()
    obj.readObjSet(NoeBitStream(data), data, mdlList, txp.texList)
    return 1

def txpLoadRGBA(data, texList):
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))[:-4]
    txp = Txp(texList, None, False)
    txp.readTxp(NoeBitStream(data), fileName)
    return 1

def txdLoadRGBA(data, texList):
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    txiData = getFileData(fileDir, fileName + ".txi")
    test = txiCheckType(txiData)
    if test == 0:
        noesis.messagePrompt("Invalid txi file.")
        return 0
    txi = Txi()
    txi.readTxi(NoeBitStream(txiData))
    txd = Txd(texList)
    txd.readTxd(NoeBitStream(data), fileName, txi.texDb)
    return 1

def txpSrLoadRGBA(data, texList):
    txp = Txp(texList, None, False)
    txp.readTxpSr(NoeBitStream(data))
    return 1

def txpFgoLoadRGBA(data, texList):
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))[:-4]
    txp = Txp(texList, None, False)
    txp.readTxpFgo(NoeBitStream(data), fileName)
    return 1

def spriteLoadRGBA(data, texList):
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    sprDbData = getFileData(fileDir, 'spr_db.bin')
    sprDb = SprDb(32)
    sprDb.readSprDb(NoeBitStream(sprDbData))
    sprDbMdataData = getFileDataMdata(fileDir, 'spr_db.bin')
    if sprDbMdataData:
        sprDbMdata = SprDb(32)
        sprDbMdata.readSprDb(NoeBitStream(sprDbMdataData))
        if fileName + '.bin' in sprDbMdata.db:
            sprDb = sprDbMdata
    spr = Sprite(texList, fileName + '.bin', sprDb.db, 32)
    spr.readSpr(NoeBitStream(data), data, None)
    return 1

def sprLoadRGBA(data, texList):
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    spiData = getFileData(fileDir, fileName + ".spi")
    test = spiCheckType(spiData)
    if test == 0:
        noesis.messagePrompt("Invalid spi file.")
        return 0
    spi = Spi()
    spi.readSpi(NoeBitStream(spiData))
    spr = Spr(texList)
    spr.readSpr(data, fileName, spi.sprDb.db)
    return 1

def iblLoadRGBA(data, texList):
    ctx = rapi.rpgCreateContext()
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    ibl = Ibl(fileName, texList)
    ibl.readIbl(NoeBitStream(data))
    return 1

def emcsLoadRGBA(data, texList):
    ctx = rapi.rpgCreateContext()
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    emcs = Emcs(fileName, texList)
    emcs.readEmcs(NoeBitStream(data))
    return 1

def motBinLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    modelPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open Model File", "Select a model file to open.", noesis.getSelectedFile(), None)
    if isinstance(modelPath, str):
        fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))[:-4]
        fileDir = rapi.getDirForFilePath(modelPath)
        objData = rapi.loadIntoByteArray(modelPath)
        testBin = objectSetCheckType(objData)
        testOsd = osdCheckType(objData)
        if testBin:
            fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))[:-4]
            obj = objectSetLoadModel(objData, mdlList, fileName, fileDir, True)
        elif testOsd:
            fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))
            obj = osdLoadModel(objData, mdlList, fileName, fileDir, True)
        else:
            noesis.messagePrompt("Invalid model file.")
            return 0
    else:
        noesis.messagePrompt("Invalid input.")
        return 0
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))[4:]
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    motDbData = getFileData(fileDir, "mot_db.bin")
    motDb = MotDb()
    motDb.readDb(NoeBitStream(motDbData))
    motDbMdataData = getFileDataMdata(fileDir, 'mot_db.bin')
    if motDbMdataData:
        motDbMdata = MotDb()
        motDbMdata.readDb(NoeBitStream(motDbMdataData))
        if fileName in motDbMdata.db:
            motDb = motDbMdata
    mot = Motion(motDb, obj.boneData, obj.boneList[0], obj.boneDict[0])
    mot.readMotion(NoeBitStream(data), fileName)
    mdlList[0].setAnims(mot.animList)
    rapi.setPreviewOption("setAnimSpeed", "60")
    if exportVmd:
        vmdExport(mot.names, mot.frameCounts, mot.animList, None, "diva.bone", "diva.morph")
    return 1

def motLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    modelPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open Model File", "Select a model file to open.", noesis.getSelectedFile(), None)
    if isinstance(modelPath, str):
        fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))[:-4]
        fileDir = rapi.getDirForFilePath(modelPath)
        objData = rapi.loadIntoByteArray(modelPath)
        testBin = objectSetCheckType(objData)
        testOsd = osdCheckType(objData)
        if testOsd:
            fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))
            obj = osdLoadModel(objData, mdlList, fileName, fileDir, True)
        elif testBin:
            fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))[:-4]
            obj = objectSetLoadModel(objData, mdlList, fileName, fileDir, True)
        else:
            noesis.messagePrompt("Invalid model file.")
            return 0
    else:
        noesis.messagePrompt("Invalid input.")
        return 0
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    mot = Motc()
    mot.readMotc(data, obj.boneData, obj.boneList[0], obj.boneDict[0], fileName, fileDir)
    mdlList[0].setAnims(mot.animList)
    rapi.setPreviewOption("setAnimSpeed", "60")
    if exportVmd:
        vmdExport(mot.names, mot.frameCounts, mot.animList, None, "diva.bone", "diva.morph")
    return 1

def a3daLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    a3da = A3da(mdlList)
    a3da.readA3da(data)
    rapi.setPreviewOption("setAnimSpeed", "60")
    if exportVmd:
        vmdExport(a3da.names, a3da.frameCounts, a3da.animList, None, "diva.bone", "diva.morph")
    return 1

def dscLoadScript(data, mdlList):
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    mdlList.append(NoeModel())
    game = noesis.userPrompt(noesis.NOEUSERVAL_STRING, "Choose a Game.", "DT, DT2, DTE, F, F2, X, AC, ACFT, FT, MM", "FT", isGame)
    if game == None:
        return 1
    else:
        game = game.upper()
    if game == "F":
        robTblData = getFileData(fileDir, "/mothead/rob_mot_tbl.bin")
        robTbl = RobTbl()
        robTbl.readTbl(NoeBitStream(robTblData[0x40:]), game)
        motDbData = getFileData(fileDir, "/rob/mot_db.bin")
        motDb = MotDb()
        motDb.readDb(NoeBitStream(motDbData))
    elif game == "F2":
        robTblData = getFileData(fileDir, "/rob/rob_mot_tbl.bin")
        robTbl = RobTbl()
        robTbl.readTbl(NoeBitStream(robTblData), game)
        motDb = MotDb()
        motDb.motDict = initF2XHashDict()
    elif game == "X":
        robTblData = getFileData(fileDir, "/rob/rob_mot_tbl.bin")
        robTbl = RobTbl()
        robTbl.readTbl(NoeBitStream(robTblData[0x20:]), game)
        motDb = MotDb()
        motDb.motDict = initF2XHashDict()
    else:
        robTblData = getFileData(fileDir, "/rob/rob_mot_tbl.bin")
        robTbl = RobTbl()
        robTbl.readTbl(NoeBitStream(robTblData[0x40:]), game)
        motDbData = getFileData(fileDir, "/rob/mot_db.bin")
        motDb = MotDb()
        motDb.readDb(NoeBitStream(motDbData))
    dsc = Dsc()
    if game == "F2":
        dsc.readDsc(NoeBitStream(data[0x40:], 1), game, robTbl, motDb)
    elif game == "X":
        dsc.readDsc(NoeBitStream(data[0x40:]), game, robTbl, motDb)
    else:
        dsc.readDsc(NoeBitStream(data), game, robTbl, motDb)
    if exportVmd:
        outDir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Choose a output directory.", "Choose a directory to output your vmd files.", rapi.getDirForFilePath(rapi.getLastCheckedName()), isFolder)
        if outDir == None:
            print("Write vmd failed.")
            return 0
        if not outDir.endswith("\\"):
            outDir += "\\"
        for i in range(len(dsc.performers)):
            vmd = Vmd(fileName[:6].upper() + "_P" + str(i) + "_" + dsc.performers[i], [], dsc.morphs[i])
            vmd.wrtieVmd(outDir)
    return 1

def expLoadScript(data, mdlList):
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    mdlList.append(NoeModel())
    game = noesis.userPrompt(noesis.NOEUSERVAL_STRING, "Choose a Game.", "F, F2, X, ACFT, FT, MM", "FT", isGameExp)
    if game == None:
        return 1
    else:
        game = game.upper()
    if game == "F":
        robTblData = getFileData(fileDir, "/mothead/rob_mot_tbl.bin")
        robTbl = RobTbl()
        robTbl.readTbl(NoeBitStream(robTblData[0x40:]), game)
        motDbData = getFileData(fileDir, "/rob/mot_db.bin")
        motDb = MotDb()
        motDb.readDb(NoeBitStream(motDbData))
    elif game == "F2":
        robTblData = getFileData(fileDir, "/rob/rob_mot_tbl.bin")
        robTbl = RobTbl()
        robTbl.readTbl(NoeBitStream(robTblData), game)
        motDb = MotDb()
        motDb.motDict = initF2XHashDict()
    elif game == "X":
        robTblData = getFileData(fileDir, "/rob/rob_mot_tbl.bin")
        robTbl = RobTbl()
        robTbl.readTbl(NoeBitStream(robTblData[0x20:]), game)
        motDb = MotDb()
        motDb.motDict = initF2XHashDict()
    else:
        robTblData = getFileData(fileDir, "/rob/rob_mot_tbl.bin")
        robTbl = RobTbl()
        robTbl.readTbl(NoeBitStream(robTblData[0x40:]), game)
        motDbData = getFileData(fileDir, "/rob/mot_db.bin")
        motDb = MotDb()
        motDb.readDb(NoeBitStream(motDbData))
    exp = Exp()
    if game == "F2" or game == "X":
        exp.readExp(NoeBitStream(data[0x20:]), game, robTbl, motDb)
    else:
        exp.readExp(NoeBitStream(data), game, robTbl, motDb)
    if exportVmd:
        outDir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Choose a output directory.", "Choose a directory to output your vmd files.", rapi.getDirForFilePath(rapi.getLastCheckedName()), isFolder)
        if outDir == None:
            print("Write vmd failed.")
            return 0
        if not outDir.endswith("\\"):
            outDir += "\\"
        for i in range(len(exp.performers)):
            vmd = Vmd(exp.name[i] + "_" + exp.performers[i], [], exp.morphs[i])
            vmd.wrtieVmd(outDir)
    return 1

def isGame(string):
    games = ["DT", "DT2", "DTE", "F", "F2", "X", "AC", "ACFT", "FT", "MM"]
    if string.upper() not in games:
        return "Invalid game."
    return None

def isGameExp(string):
    games = ["F", "F2", "X", "ACFT", "FT", "MM"]
    if string.upper() not in games:
        return "Invalid game."
    return None

def isPerformer(string):
    performers = ["MIK", "RIN", "LEN", "LUK", "NER", "HAK", "KAI", "MEI", "SAK", "TET"]
    if string.upper() not in performers:
        return "Invalid performer."
    return None

def isPerformerOld(string):
    performers = ["MIK", "RIN", "LEN", "LUK", "NER", "HAK", "KAI", "MEI", "SAK"]
    if string.upper() not in performers:
        return "Invalid performer."
    return None

class ObjDb:
    
    def __init__(self, addressSpace):
        self.db = {}
        self.addressSpace = addressSpace
        
    def readObjDb(self, bs, isOsi):
        if isOsi:
            bs.seek(0x04, NOESEEK_REL)
        objCount = bs.readInt()
        maxId = bs.readUInt()
        objOff = readOff(bs, self.addressSpace)
        meshCount = bs.readInt()
        meshOff = readOff(bs, self.addressSpace)
        bs.seek(objOff, NOESEEK_ABS)
        objDb = {}
        for i in range(objCount):
            objName = getOffString(bs, readOff(bs, self.addressSpace))
            objId = bs.readUInt()
            objFileNameOff = readOff(bs, self.addressSpace)
            texFileNameOff = readOff(bs, self.addressSpace)
            farcFileNameOff = readOff(bs, self.addressSpace)
            bs.seek(0x10, NOESEEK_REL)
            objDb[objId] = objName
            self.db[objName] = {}
        bs.seek(meshOff, NOESEEK_ABS)
        for i in range(meshCount):
            if isOsi:
                meshId = bs.readUInt()
                objId = bs.readUInt()
            else:
                meshId = bs.readUShort()
                objId = bs.readUShort()
            meshName = getOffString(bs, readOff(bs, self.addressSpace))
            self.db[objDb[objId]][meshId] = meshName

class TexDb:
    
    def __init__(self, addressSpace):
        self.db = {}
        self.addressSpace = addressSpace
        self.texHash = []
        
    def readTexDb(self, bs):
        texCount = bs.readInt()
        texDatabaseOff = readOff(bs, self.addressSpace)
        bs.seek(texDatabaseOff, NOESEEK_ABS)
        for i in range(texCount):
            texId = bs.readUInt()
            texName = getOffString(bs, readOff(bs, self.addressSpace))
            self.db[texId] = texName
            self.texHash.append(texId)

class SprDb:
    
    def __init__(self, addressSpace):
        self.db = {}
        self.addressSpace = addressSpace
        
    def readSprDb(self, bs):
        setCount = bs.readInt()
        setDatabaseOff = readOff(bs, self.addressSpace)
        spriteCount = bs.readInt()
        spriteDatabaseOff = readOff(bs, self.addressSpace)
        bs.seek(setDatabaseOff, NOESEEK_ABS)
        setDb = {}
        for i in range(setCount):
            setId = bs.readUInt()
            setName = getOffString(bs, readOff(bs, self.addressSpace))
            fileName = getOffString(bs, readOff(bs, self.addressSpace))
            index = bs.readUInt()
            if self.addressSpace == 64:
                bs.seek(0x04, NOESEEK_REL)
            setDb[index] = fileName
            self.db[fileName] = []
        bs.seek(spriteDatabaseOff, NOESEEK_ABS)
        for i in range(spriteCount):
            spriteId = bs.readUInt()
            spriteName = getOffString(bs,readOff(bs, self.addressSpace))
            info = bs.readUInt()
            if self.addressSpace == 64:
                bs.seek(0x04, NOESEEK_REL)
            index = info & 0xFFFF
            setIndex = (info >> 16) & 0xFFFF
            if setIndex in setDb:
                self.db[setDb[setIndex]].append(spriteName)

class MotDb:
    
    def __init__(self):
        self.db = {}
        self.motDict = {}
        self.boneNames = []
        
    def readDb(self, bs):
        magic = bs.readUInt()
        motSetOff = bs.readUInt()
        motSetIdOff = bs.readUInt()
        motSetCount = bs.readInt()
        boneNamesOff = bs.readUInt()
        boneNamesCount = bs.readUInt()
        bs.seek(motSetOff, NOESEEK_ABS)
        for i in range(motSetCount):
            self.getMotSets(bs)
        self.boneNames = getOffStringList(bs, 32, boneNamesOff, boneNamesCount)

    def getMotSets(self, bs):
        motSet = MotSet()
        name = getOffString(bs, bs.readUInt())
        motNamesOff = bs.readUInt()
        motSet.count = bs.readInt()
        motIdsOff = bs.readUInt()
        motSet.name = getOffStringList(bs, 32, motNamesOff, motSet.count)
        pos = bs.tell()
        bs.seek(motIdsOff, NOESEEK_ABS)
        for i in range(motSet.count):
            motId = bs.readUInt()
            motSet.id.append(motId)
            self.motDict[motId] = motSet.name[i]
        self.db[name] = motSet
        bs.seek(pos, NOESEEK_ABS)

class MotSet:
    
    def __init__(self):
        self.count = 0
        self.name = []
        self.id = []

class RobTbl:
    
    def __init__(self):
        self.db = {}
        
    def readTbl(self, bs, game):
        performers = ["MIK", "RIN", "LEN", "LUK", "NER", "HAK", "KAI", "MEI", "SAK", "TET", "CMN"]
        if game == "F2":
            bs.seek(0x20, NOESEEK_ABS)
        PerformerCount = bs.readUInt()
        animCount = bs.readUInt()
        PerformerOff = bs.readUInt()
        bs.seek(PerformerOff, NOESEEK_ABS)
        for i in range(PerformerCount):
            if game == "X":
                animOff = bs.readUInt64()
                unk = bs.readUInt64()
            else:
                animOff = bs.readUInt()
                unk = bs.readUInt()
            pos = bs.tell()
            bs.seek(animOff, NOESEEK_ABS)
            dataOff = bs.readUInt()
            bs.seek(dataOff, NOESEEK_ABS)
            self.db[performers[i]] = self.getPerformerAnims(bs, animCount)
            bs.seek(pos, NOESEEK_ABS)

    def getPerformerAnims(self, bs, animCount):
        anims = []
        for i in range(animCount):
            idx = bs.readUInt()
            if idx == 0xFFFFFFFF:
                idx = -1
            anims.append(idx)
        return anims

class BoneData:
    
    def __init__(self, addressSpace):
        self.game = 'AFT'
        self.type = {}
        self.boneList = []
        self.boneDict = {}
        self.addressSpace = addressSpace
        
    def readBoneData(self, bs, char):
        magic = bs.readUInt()
        skelCount = bs.readInt()
        skelOff = readOff(bs, self.addressSpace)
        skelNames = getOffStringList(bs, self.addressSpace, readOff(bs, self.addressSpace), skelCount)
        if 'TET' not in skelNames:
            self.game = 'AC'
            if 'RIN' not in skelNames:
                self.game = 'VF5'
                if 'AKI' not in skelNames:
                    self.game = 'MGF'
        bs.seek(skelOff, NOESEEK_ABS)
        for i in range(skelCount):
            off = readOff(bs, self.addressSpace)
            if skelNames[i] == char:
                pos = bs.tell()
                bs.seek(off, NOESEEK_ABS)
                self.readSkel(bs, char)
                bs.seek(pos, NOESEEK_ABS)

    def readSkel(self, bs, char):
        boneOff = readOff(bs, self.addressSpace)
        boneVec3Count = bs.readInt()
        boneVec3Off = readOff(bs, self.addressSpace)
        unk = readOff(bs, self.addressSpace)
        objBoneCount = bs.readInt()
        objBoneNames = getOffStringList(bs, self.addressSpace, readOff(bs, self.addressSpace), objBoneCount)
        motBoneCount = bs.readInt()
        motBoneNames = getOffStringList(bs, self.addressSpace, readOff(bs, self.addressSpace), motBoneCount)
        parentOff = readOff(bs, self.addressSpace)
        bs.seek(boneOff, NOESEEK_ABS)
        self.readBone(bs)
        bs.seek(boneVec3Off, NOESEEK_ABS)
        vec3 = self.readBoneVec3(bs, boneVec3Count)
        bs.seek(parentOff, NOESEEK_ABS)
        parents = self.readBoneParent(bs, motBoneCount, motBoneNames)
        if self.game == 'MGF':
            self.loadSkelMgf(char, vec3, motBoneCount, motBoneNames, parents)
        else:
            self.loadSkel(char, vec3, motBoneCount, motBoneNames, parents)

    def readBone(self, bs):
        while True:
            boneType = bs.readByte()
            hasParent = bs.readBool()
            parentIndex = bs.readByte()
            flag2 = bs.readByte()
            pairIndex = bs.readByte()
            flag4 = bs.readByte()
            bs.seek(0x02, NOESEEK_REL)
            boneName = getOffString(bs, readOff(bs, self.addressSpace))
            if boneName == "End":
                break
            self.type[boneName] = boneType

    def readBoneVec3(self, bs, boneVec3Count):
        vec3 = []
        for i in range(boneVec3Count):
            vec3.append([bs.readFloat(), bs.readFloat(), bs.readFloat()])
        return vec3

    def readBoneParent(self, bs, motBoneCount, motBoneNames):
        parents = []
        for i in range(motBoneCount):
            pIdx = bs.readShort()
            if motBoneNames[pIdx].endswith('_cp') and motBoneNames[pIdx].startswith('e_'):
                pIdx = parents[pIdx]
            parents.append(pIdx)
        return parents

    def loadSkel(self, char, vec3, motBoneCount, motBoneNames, parents):
        if self.game == 'AFT':
            boneTrans, boneRot = baseSkelAFT()
        elif self.game == 'AC':
            boneTrans, boneRot = baseSkelAC()
        elif self.game == 'VF5':
            boneTrans, boneRot = baseSkelVF5()
        else:
            return
        boneTrans = boneTrans[char]
        self.boneList.append(NoeBone(0, 'gblctr', NoeMat43(), None, -1))
        self.boneDict['gblctr'] = 0
        self.boneList.append(NoeBone(1, 'kg_ya_ex', NoeMat43(), None, 0))
        self.boneDict['kg_ya_ex'] = 1
        idx = 0
        ikIdxDict = {}
        for i in range(motBoneCount):
            boneName = motBoneNames[i]
            parent = parents[i]
            pos = NoeVec3((0, 0, 0))
            if boneName in self.type:
                pos = NoeVec3(vec3[idx])
                if self.type[boneName] == 0x04:
                    ikIdxDict[boneName] = idx
                    idx += 1
                elif self.type[boneName] == 0x05 or self.type[boneName] == 0x06:
                    ikIdxDict[boneName] = idx
                    idx += 2
                idx += 1
            mtx = NoeMat43()
            mtx[3] = pos
            if boneName in boneTrans:
                mtx[3] = boneTrans[boneName]
            elif boneName in boneRot and not boneName.startswith('c_kata'):
                mtx2 = NoeAngles([boneRot[boneName][0]*noesis.g_flRadToDeg, boneRot[boneName][1]*noesis.g_flRadToDeg, boneRot[boneName][2]*noesis.g_flRadToDeg]).toMat43_XYZ()
                mtx2[3] = mtx[3]
                mtx = mtx2
            elif boneName == 'e_mune_cp':
                boneName2 = 'cl_mune'
                mtx[3] = NoeVec3(vec3[ikIdxDict[boneName2]+1])
            elif boneName == 'j_mune_wj' or boneName == 'j_kao_wj':
                mtx2 = NoeAngles((0.0, 0.0, 90.0)).toMat43_XYZ()
                mtx2[3] = mtx[3]
                mtx = mtx2
            elif boneName == 'e_kao_cp':
                boneName2 = 'cl_kao'
                mtx[3] = NoeVec3(vec3[ikIdxDict[boneName2]+1])
            elif boneName == 'c_kata_l' or boneName == 'c_kata_r':
                mtx2 = NoeAngles([boneRot[boneName][0]*noesis.g_flRadToDeg, boneRot[boneName][1]*noesis.g_flRadToDeg, boneRot[boneName][2]*noesis.g_flRadToDeg]).toMat43_XYZ()
                mtx2[3] = mtx[3]
                mtx = mtx2
            elif boneName == 'j_kata_l_wj_cu' or boneName == 'j_kata_r_wj_cu':
                boneName2 = 'n_skata_'+boneName[7]+'_wj_cd_ex'
                if boneName2 in boneRot:
                    mtx2 = NoeAngles([boneRot[boneName2][0]*noesis.g_flRadToDeg, boneRot[boneName2][1]*noesis.g_flRadToDeg, boneRot[boneName2][2]*noesis.g_flRadToDeg]).toMat43_XYZ()
                    mtx2[3] = mtx[3]
                    mtx = mtx2
            elif boneName == 'j_ude_l_wj' or boneName == 'j_ude_r_wj':
                boneName2 = 'c_kata_'+boneName[6]
                mtx[3] = NoeVec3(vec3[ikIdxDict[boneName2]+1])
            elif boneName == 'e_ude_l_cp' or boneName == 'e_ude_r_cp':
                boneName2 = 'c_kata_'+boneName[6]
                mtx[3] = NoeVec3(vec3[ikIdxDict[boneName2]+2])
            elif boneName == 'j_momo_l_wj' or boneName == 'j_momo_r_wj':
                mtx2 = NoeAngles((0.0, 0.0, -90.0)).toMat43_XYZ()
                mtx2[3] = mtx[3]
                mtx = mtx2
            elif boneName == 'j_sune_l_wj' or boneName == 'j_sune_r_wj':
                boneName2 = 'cl_momo_'+boneName[7]
                mtx[3] = NoeVec3(vec3[ikIdxDict[boneName2]+1])
            elif boneName == 'e_sune_l_cp' or boneName == 'e_sune_r_cp':
                boneName2 = 'cl_momo_'+boneName[7]
                mtx[3] = NoeVec3(vec3[ikIdxDict[boneName2]+2])
            self.boneList.append(NoeBone(i+2, boneName, mtx, None, parent+2))
            self.boneDict[boneName] = i+2

    def loadSkelMgf(self, char, vec3, motBoneCount, motBoneNames, parents):
        boneRot, boneRotExtra = baseSkelMGF()
        boneRot = boneRot[char[:3]]
        if char in boneRotExtra:
            boneRot.update(boneRotExtra[char])
        self.boneList.append(NoeBone(0, 'gblctr', NoeMat43(), None, -1))
        self.boneDict['gblctr'] = 0
        self.boneList.append(NoeBone(1, 'kg_ya_ex', NoeMat43(), None, 0))
        self.boneDict['kg_ya_ex'] = 1
        idx = 0
        for i in range(motBoneCount):
            boneName = motBoneNames[i]
            parent = parents[i]
            pos = NoeVec3((0, 0, 0))
            if boneName in self.type:
                pos = NoeVec3(vec3[idx])
                idx += 1
            mtx = NoeMat43()
            mtx[3] = pos
            if boneName in boneRot:
                mtx2 = NoeAngles([boneRot[boneName][0]*noesis.g_flRadToDeg, boneRot[boneName][1]*noesis.g_flRadToDeg, boneRot[boneName][2]*noesis.g_flRadToDeg]).toMat43_XYZ()
                mtx2[3] = mtx[3]
                mtx = mtx2
            self.boneList.append(NoeBone(i+2, boneName, mtx, None, parent+2))
            self.boneDict[boneName] = i+2

class Bone:
    
    def __init__(self):
        self.boneData = None
        
    def readBone(self, bs, skel):
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        addressSpace = getAddressSpace(bs, fileSize, dataOff, dataSize)
        self.boneData = BoneData(addressSpace)
        if addressSpace == 32:
            bs.seek(dataOff, NOESEEK_ABS)
            if endian == 0x18000000:
                bs.setEndian(NOE_BIGENDIAN)
            self.boneData.readBoneData(bs, skel)
        elif addressSpace == 64:
            bs.seek(dataOff, NOESEEK_ABS)
            ts = NoeBitStream(bs.readBytes(dataSize))
            if endian == 0x18000000:
                ts.setEndian(NOE_BIGENDIAN)
            self.boneData.readBoneData(ts, skel)

class ObjectSet:
    
    def __init__(self, mdlList, texList, objDb, texDb, boneData, addressSpace, sectionOff, texDbMdata={}):
        self.mdlList = mdlList
        self.texList = texList
        self.objDb = objDb
        self.texDb = texDb
        self.texDbMdata = texDbMdata
        self.boneData = boneData
        self.texDict = {}
        self.texHashDict = {}
        self.boneList =[]
        self.boneDict = []
        self.endian = 0
        self.addressSpace = addressSpace
        self.sectionOff = sectionOff
        self.objId = []
        self.objects = {}
        self.skinBoneName = []
        self.clsWeight = []
        self.clsBoneName = []
        # self.isMot = False
        
    def readObjSet(self, bs, data):
        magic = bs.readUInt()
        objCount = bs.readInt()
        boneCount = bs.readInt()
        objOff = readOff(bs, self.addressSpace)
        SkinOff = readOff(bs, self.addressSpace)
        objNameOff = readOff(bs, self.addressSpace)
        objIdOff = readOff(bs, self.addressSpace)
        texIdOff = readOff(bs, self.addressSpace)
        texIdCount = bs.readInt()
        bs.seek(objIdOff, NOESEEK_ABS)
        self.readObjId(bs, objCount)
        bs.seek(texIdOff, NOESEEK_ABS)
        self.readTexId(bs, texIdCount)
        bs.seek(SkinOff, NOESEEK_ABS)
        self.readSkin(bs, data, objCount)
        bs.seek(objOff, NOESEEK_ABS)
        self.readObject(bs, data, objCount)

    def readObjId(self, bs, objCount):
        for i in range(objCount):
            self.objId.append(bs.readUInt())

    def readTexId(self, bs, texIdCount):
        for i in range(texIdCount):
            texId = bs.readUInt()
            try:
                if texId in self.texDb.db:
                    self.texList[i].name = self.texDb.db[texId]
                else:
                    self.texList[i].name = self.texDbMdata.db[texId]
                self.texDict[self.texList[i].name] = i
                self.texHashDict[texId] = self.texList[i].name
            except:
                self.texList[i].name += "_" + str(i)
                self.texDict[self.texList[i].name] = i
                self.texHashDict[texId] = self.texList[i].name

    def readSkin(self, bs, data, objCount):
        for i in range(objCount):
            self.boneList.append(list(self.boneData.boneList))
            self.boneDict.append(self.boneData.boneDict.copy())
        if self.sectionOff:
            for i in range(objCount):
                if self.sectionOff["OSKN"][i]:
                    skin = Skin(self.boneList[i], self.boneDict[i], self.addressSpace)
                    if self.addressSpace == 32:
                        ts = NoeBitStream(data[self.sectionOff["OSKN"][i]:], self.endian)
                        ts.seek(0x20, NOESEEK_ABS)
                        skin.readSkin(ts, self.boneData.game)
                    elif self.addressSpace == 64:
                        skin.readSkin(NoeBitStream(data[self.sectionOff["OSKN"][i]:], self.endian), self.boneData.game)
                    self.skinBoneName.append(skin.boneName)
                    self.clsWeight.append(skin.clsWeight)
                    self.clsBoneName.append(skin.clsBoneName)
                    if skin.local:
                        self.boneList[i] = list(rapi.multiplyBones(self.boneList[i]))
                        self.resetBoneMtx(i)
                        if skin.gblMtxs:
                            for motName in skin.gblMtxs:
                                self.boneList[i][self.boneDict[i][motName]]._matrix = skin.gblMtxs[motName]
                else:
                    self.skinBoneName.append([])
                    self.clsWeight.append({})
                    self.clsBoneName.append({})
        else:
            for i in range(objCount):
                skinOff = bs.readUInt()
                if skinOff != 0:
                    pos = bs.tell()
                    bs.seek(skinOff, NOESEEK_ABS)
                    skin = Skin(self.boneList[i], self.boneDict[i], self.addressSpace)
                    skin.readSkin(bs, self.boneData.game)
                    bs.seek(pos, NOESEEK_ABS)
                    self.skinBoneName.append(skin.boneName)
                    self.clsWeight.append(skin.clsWeight)
                    self.clsBoneName.append(skin.clsBoneName)
                    if skin.local:
                        self.boneList[i] = list(rapi.multiplyBones(self.boneList[i]))
                        self.resetBoneMtx(i)
                        if skin.gblMtxs:
                            for motName in skin.gblMtxs:
                                self.boneList[i][self.boneDict[i][motName]]._matrix = skin.gblMtxs[motName]
                else:
                    self.skinBoneName.append([])
                    self.clsWeight.append({})
                    self.clsBoneName.append({})

    def readObject(self, bs, data, objCount):
        if objCount == 0:
            mdl = NoeModel()
            mdl.setModelMaterials(NoeModelMaterials(self.texList, []))
            self.mdlList.append(mdl)
            return
        if self.sectionOff:
            for i in range(objCount):
                try:
                    print(self.objDb[self.objId[i]])
                    self.objects[self.objDb[self.objId[i]]] = i
                except:
                    print("Unused object")
                if self.endian == 1:
                    rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
                obj = Object(self.texHashDict, self.boneDict[i], self.skinBoneName[i], self.endian, self.addressSpace, self.sectionOff, i, self.clsWeight[i], self.clsBoneName[i])
                if self.addressSpace == 32:
                    ts = NoeBitStream(data[self.sectionOff["OMDL"][i]:], self.endian)
                    ts.seek(0x20, NOESEEK_ABS)
                    obj.readObject(ts, data)
                elif self.addressSpace == 64:
                    obj.readObject(NoeBitStream(data[self.sectionOff["OMDL"][i]:], self.endian), data)
                try:
                    mdl = rapi.rpgConstructModel()
                except:
                    mdl = NoeModel()
                if i == 0:
                    mdl.setModelMaterials(NoeModelMaterials(self.texList, obj.matList))
                else:
                    mdl.setModelMaterials(NoeModelMaterials([], obj.matList))
                mdl.setBones(self.boneList[i])
                self.mdlList.append(mdl)
                rapi.rpgReset()
        else:
            for i in range(objCount):
                try:
                    print(self.objDb[self.objId[i]])
                    self.objects[self.objDb[self.objId[i]]] = i
                except:
                    print("Unused object")
                objectOff = bs.readUInt()
                obj = Object(self.texHashDict, self.boneDict[i], self.skinBoneName[i], self.endian, self.addressSpace, None, i, self.clsWeight[i], self.clsBoneName[i])
                obj.readObject(NoeBitStream(data[objectOff:]), data)
                try:
                    mdl = rapi.rpgConstructModel()
                except:
                    mdl = NoeModel()
                if i == 0:
                    mdl.setModelMaterials(NoeModelMaterials(self.texList, obj.matList))
                else:
                    mdl.setModelMaterials(NoeModelMaterials([], obj.matList))
                mdl.setBones(self.boneList[i])
                self.mdlList.append(mdl)
                rapi.rpgReset()

    def resetBoneMtx(self, idx):
        ikBones = {}
        for bone in self.boneList[idx]:
            if bone.name.startswith('e_') and bone.name.endswith('_cp'):
                ikBones[bone.name] = {'name': bone.parentName, 'index': bone.parentIndex}
                mtx2 = NoeMat43()
                mtx2[3] = bone._matrix[3]
                bone._matrix = mtx2
                bone.parentName = 'kg_ya_ex'
                bone.parentIndex = 1
            elif bone.parentName in ikBones.keys():
                parent = bone.parentName
                bone.parentName = ikBones[parent]['name']
                bone.parentIndex = ikBones[parent]['index']

class Osd:
    
    def __init__(self, mdlList, texList, boneData):
        self.mdlList = mdlList
        self.texList = texList
        self.boneData = boneData
        self.boneList =[]
        self.boneDict = []
        self.objId = []
        self.objects = {}
        self.sectionOff = {"OMDL":[], "OSKN":[], "OIDX":[], "OVTX":[]}

    def readOsd(self, data, objDb, texDb):
        bs = NoeBitStream(data)
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        bs.seek(dataOff + dataSize, NOESEEK_ABS)
        self.getSectionOff(bs, fileSize)
        addressSpace = getAddressSpace(bs, fileSize, dataOff, dataSize)
        objectSet = ObjectSet(self.mdlList, self.texList, objDb, texDb, self.boneData, addressSpace, self.sectionOff)
        if addressSpace == 32:
            bs.seek(dataOff, NOESEEK_ABS)
            if endian == 0x18000000:
                bs.setEndian(NOE_BIGENDIAN)
                rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
                objectSet.endian = 1
            objectSet.readObjSet(bs, data)
        elif addressSpace == 64:
            bs.seek(dataOff, NOESEEK_ABS)
            newData = bs.readBytes(dataSize)
            ts = NoeBitStream(newData)
            if endian == 0x18000000:
                ts.setEndian(NOE_BIGENDIAN)
                rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
                objectSet.endian = 1
            objectSet.readObjSet(ts, data[dataOff:])
        self.boneList = objectSet.boneList
        self.boneDict = objectSet.boneDict
        self.objects = objectSet.objects

    def getSectionOff(self, bs, fileSize):
        start = 0
        hasOmdl = False
        hasOskn = False
        while start < fileSize:
            start = bs.tell()
            magic = bs.readBytes(4).decode("ASCII")
            fileSize2 = bs.readUInt()
            dataOff = bs.readUInt()
            endian = bs.readUInt()
            unk = bs.readUInt()
            dataSize = bs.readUInt()
            bs.seek(start + dataOff + dataSize, NOESEEK_ABS)
            if magic == "OMDL" or magic == "OSKN" or magic == "OIDX" or magic == "OVTX":
                self.sectionOff[magic].append(start)
            if magic == "OMDL":
                hasOmdl = True
            if magic == "OSKN":
                hasOskn = True
            if magic == "EOFC" and hasOmdl:
                if not hasOskn:
                    self.sectionOff["OSKN"].append(None)
                hasOmdl = False
                hasOskn = False

class Osi:
    
    def __init__(self):
        self.objDb = None
        
    def readOsi(self, bs):
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        addressSpace = getAddressSpace(bs, fileSize, dataOff, dataSize)
        self.objDb = ObjDb(addressSpace)
        if addressSpace == 32:
            bs.seek(dataOff, NOESEEK_ABS)
            if endian == 0x18000000:
                bs.setEndian(NOE_BIGENDIAN)
            self.objDb.readObjDb(bs, True)
        elif addressSpace == 64:
            bs.seek(dataOff, NOESEEK_ABS)
            ts = NoeBitStream(bs.readBytes(dataSize))
            if endian == 0x18000000:
                ts.setEndian(NOE_BIGENDIAN)
            self.objDb.readObjDb(ts, True)

class Skin:
    
    def __init__(self, boneList, boneDict, addressSpace):
        self.boneList = boneList
        self.boneDict = boneDict
        self.addressSpace = addressSpace
        self.local = True
        self.boneMtx = []
        self.boneParent = {}
        self.gblMtxs = {}
        self.clsWeight = {}
        self.clsBoneName = {}
        self.parentRetry = []
        
    def readSkin(self, bs, game):
        boneIdOff = readOff(bs, self.addressSpace)
        boneMtxOff = readOff(bs, self.addressSpace)
        boneNameOff = readOff(bs, self.addressSpace)
        exDataOff = readOff(bs, self.addressSpace)
        boneCount = bs.readInt()
        boneParentOff = readOff(bs, self.addressSpace)
        if boneCount:
            bs.seek(boneMtxOff, NOESEEK_ABS)
            boneMtxs = self.readBoneMtx(bs, boneCount)
            self.boneName = getOffStringList(bs, self.addressSpace, boneNameOff, boneCount)
            bs.seek(boneIdOff, NOESEEK_ABS)
            boneId = self.readBoneId(bs, boneCount)
            boneParents = {}
            if boneParentOff:
                bs.seek(boneParentOff, NOESEEK_ABS)
                boneParents = self.readBoneParent(bs, boneCount, boneId)
            if game == 'MGF' and self.boneList:
                self.local = False
                for bone in self.boneList:
                    if bone.name in self.boneName:
                        bone._matrix = boneMtxs[self.boneName.index(bone.name)]
                    elif bone.index > 1:
                        mtx = copy.deepcopy(self.boneList[bone.parentIndex]._matrix)
                        tmpList = [NoeBone(0, 'tmp1', mtx, None, -1), NoeBone(1, 'tmp2', bone._matrix, None, 0)]
                        tmpList = rapi.multiplyBones(tmpList)
                        bone._matrix = tmpList[1]._matrix
            elif self.boneList:
                if exDataOff:
                    bs.seek(exDataOff, NOESEEK_ABS)
                    self.readExData(bs)
            else:
                self.local = False
                if boneParents:
                    for i in range(boneCount):
                        name = self.boneName[i]
                        self.loadBone(name, None, None, None, None, boneMtxs[i], boneParents[name])
                else:
                    for i in range(boneCount):
                        name = self.boneName[i]
                        self.loadBone(name, None, None, None, None, boneMtxs[i])

    def readBoneId(self, bs, boneCount):
        boneId = {}
        for i in range(boneCount):
            boneId[bs.readUInt()] = i
        return boneId

    def readBoneMtx(self, bs, boneCount):
        mtx = []
        for i in range(boneCount):
            m01, m11, m21, m31 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            m02, m12, m22, m32 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            m03, m13, m23, m33 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            m04, m14, m24, m34 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            boneMtx = NoeMat44([NoeVec4((m01, m02, m03, m04)), NoeVec4((m11, m12, m13, m14)), NoeVec4((m21, m22, m23, m24)), NoeVec4((m31, m32, m33, m34))]).inverse().toMat43()
            mtx.append(boneMtx)
        return mtx

    def readBoneParent(self, bs, boneCount, boneId):
        parent = {}
        for i in range(boneCount):
            parentId = bs.readUInt()
            if parentId != 0xFFFFFFFF:
                parent[self.boneName[i]] = boneId[parentId]
            else:
                parent[self.boneName[i]] = -1
        return parent

    def readExData(self, bs):
        osageNameCount = bs.readInt()
        osageNodeCount = bs.readInt()
        bs.seek(0x04, NOESEEK_REL)
        osageNodeOff = readOff(bs, self.addressSpace)
        osageName = getOffStringList(bs, self.addressSpace, readOff(bs, self.addressSpace), osageNameCount)
        blockOff = readOff(bs, self.addressSpace)
        stringCount = bs.readInt()
        string = getOffStringList(bs, self.addressSpace, readOff(bs, self.addressSpace), stringCount)
        osageSiblingOff = readOff(bs, self.addressSpace)
        clothCount = bs.readInt()
        bs.seek(osageNodeOff, NOESEEK_ABS)
        osageNode = self.readOsageNode(bs, osageNodeCount, string)
        bs.seek(osageSiblingOff, NOESEEK_ABS)
        osageSibling = self.readOsageSibling(bs, string)
        bs.seek(blockOff, NOESEEK_ABS)
        self.readBlock(bs, string, osageNode)
        for bone in self.parentRetry:
            if bone[1] in self.boneDict:
                parent = self.boneDict[bone[1]]
                self.boneList[bone[0]].parentIndex = parent

    def readOsageNode(self, bs, osageNodeCount, string):
        osgNode = []
        for i in range(osageNodeCount):
            name = string[bs.readUInt() & 0x7FFF]
            length = bs.readFloat()
            bs.seek(0x04, NOESEEK_REL)
            osgNode.append([name, length])
        return osgNode

    def readOsageSibling(self, bs, string):
        osgSibling = []
        while True:
            idx = bs.readUInt()
            if idx == 0:
                break
            boneName = string[idx & 0x7FFF]
            siblingName = string[bs.readUInt() & 0x7FFF]
            distance = bs.readFloat()
            osgSibling.append([boneName, siblingName, distance])
        return osgSibling

    def readBlock(self, bs, string, osageNode):
        while True:
            sigOff = readOff(bs, self.addressSpace)
            if sigOff == 0:
                break
            signature = getOffString(bs, sigOff)
            blockOff = readOff(bs, self.addressSpace)
            pos = bs.tell()
            bs.seek(blockOff, NOESEEK_ABS)
            if signature == "EXP":
                self.readExp(bs)
            elif signature == "OSG":
                self.readOsg(bs, string, osageNode)
            elif signature == "MOT":
                self.readMot(bs, string)
            elif signature == "CNS":
                try:
                    self.readCns(bs)
                except:
                    pass
            elif signature == "ITM":
                self.readItm(bs)
            elif signature == "CLS":
                self.readCls(bs)
            bs.seek(pos, NOESEEK_ABS)

    def readExp(self, bs):
        parentName = getOffString(bs, readOff(bs, self.addressSpace))
        pos = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        rot = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        scl = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        name = getOffString(bs, readOff(bs, self.addressSpace))
        count = bs.readInt()
        exp = []
        # print(name)
        for i in range(count):
            exp.append(getOffString(bs, readOff(bs, self.addressSpace)))
            # print(exp[i])
        if name not in self.boneDict:
            self.loadBone(name, parentName, pos, rot, scl)

    def readOsg(self, bs, string, osageNode):
        parentName = getOffString(bs, readOff(bs, self.addressSpace))
        pos = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        rot = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        scl = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        if self.addressSpace == 64:
            bs.seek(0x04, NOESEEK_REL)
        index = bs.readUInt()
        count = bs.readInt()
        externalNameIdx = bs.readUInt() & 0x7FFF
        name = string[externalNameIdx]
        endName = string[bs.readUInt() & 0x7FFF]
        osgNodeOff = bs.readUInt()
        self.loadBone(name, parentName, pos, rot, scl)
        osgParent = name
        osgPos = NoeVec3((0.0, 0.0, 0.0))
        if osgNodeOff:
            bs.seek(osgNodeOff, NOESEEK_ABS)
            osgNodes = []
            osgNameIdx = bs.readUInt()
            if osgNameIdx:
                bs.seek(-4, NOESEEK_REL)
            else:
                for i in range(count):
                    osgName = osageNode[index+i][0]
                    if i:
                        osgPos = NoeVec3((osageNode[index+i-1][1], 0.0, 0.0))
                    if osgName in self.boneDict:
                        osgName = osgName + '_osg'
                    self.loadBone(osgName, osgParent, osgPos)
                    osgParent = osgName
                self.loadBone(endName, osgParent, NoeVec3((osageNode[index+count-1][1], 0.0, 0.0)))
                return
            for i in range(count):
                osgName = string[bs.readUInt() & 0x7FFF]
                length = bs.readFloat()
                osgRot = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
                osgNodes.append([osgName, length, osgRot])
            for i in range(count):
                osgName = osgNodes[i][0]
                if i:
                    osgPos = NoeVec3((osgNodes[i-1][1], 0.0, 0.0))
                if osgName in self.boneDict:
                    osgName = osgName + '_osg'
                self.loadBone(osgName, osgParent, osgPos, osgNodes[i][2])
                osgParent = osgName
            self.loadBone(endName, osgParent, NoeVec3((osgNodes[-1][1], 0.0, 0.0)))
        else:
            for i in range(count):
                osgName = osageNode[index+i][0]
                if i:
                    osgPos = NoeVec3((osageNode[index+i-1][1], 0.0, 0.0))
                if osgName in self.boneDict:
                    osgName = osgName + '_osg'
                self.loadBone(osgName, osgParent, osgPos)
                osgParent = osgName
            self.loadBone(endName, osgParent, NoeVec3((osageNode[index+count-1][1], 0.0, 0.0)))

    def readMot(self, bs, string):
        parentName = getOffString(bs, readOff(bs, self.addressSpace))
        pos = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        rot = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        scl = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        name = getOffString(bs, readOff(bs, self.addressSpace))
        count = bs.readInt()
        boneNameOff = readOff(bs, self.addressSpace)
        boneMtxOff = readOff(bs, self.addressSpace)
        bs.seek(boneNameOff, NOESEEK_ABS)
        boneNames = []
        for i in range(count):
            boneNames.append(string[bs.readUInt() & 0x7FFF])
        bs.seek(boneMtxOff, NOESEEK_ABS)
        boneMtxs = []
        for i in range(count):
            m01, m11, m21, m31 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            m02, m12, m22, m32 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            m03, m13, m23, m33 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            m04, m14, m24, m34 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            boneMtx = NoeMat44([NoeVec4((m01, m02, m03, m04)), NoeVec4((m11, m12, m13, m14)), NoeVec4((m21, m22, m23, m24)), NoeVec4((m31, m32, m33, m34))]).toMat43()
            boneMtxs.append(boneMtx)
        self.loadBone(name, parentName, pos, rot, scl)
        motParent = name
        for i in range(count):
            boneName = boneNames[i]
            if '000' in boneName:
                motParent = name
            self.gblMtxs[boneName] = boneMtxs[i]
            self.loadBone(boneName, motParent, None, None, None, boneMtxs[i])
            motParent = boneName

    def readCns(self, bs):
        parentName = getOffString(bs, readOff(bs, self.addressSpace))
        pos = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        rot = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        scl = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        cnsType = getOffString(bs, readOff(bs, self.addressSpace))
        name = getOffString(bs, readOff(bs, self.addressSpace))
        coupling = bs.readInt()
        sourceName = getOffString(bs, readOff(bs, self.addressSpace))
        self.loadBone(name, parentName, pos, rot, scl)

    def readItm(self, bs):
        parentName = getOffString(bs, readOff(bs, self.addressSpace))
        pos = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        rot = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        scl = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        itmType = getOffString(bs, readOff(bs, self.addressSpace))
        name = getOffString(bs, readOff(bs, self.addressSpace))
        self.loadBone(name, parentName, pos, rot, scl)

    def readCls(self, bs):
        meshName = getOffString(bs, readOff(bs, self.addressSpace))
        backfaceName = getOffString(bs, readOff(bs, self.addressSpace))
        unk1 = bs.readUInt()
        rowCount = bs.readInt()
        columnCount = bs.readInt()
        unk3 = bs.readUInt()
        unk1Off = readOff(bs, self.addressSpace)
        rootNodeOff = readOff(bs, self.addressSpace)
        nodeOff = readOff(bs, self.addressSpace)
        meshVertOff = readOff(bs, self.addressSpace)
        backfaceVertOff = readOff(bs, self.addressSpace)
        bs.seek(rootNodeOff, NOESEEK_ABS)
        rootBoneName = []
        rootWeight = []
        nodeName = []
        usedBone = []
        for i in range(rowCount):
            pos = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
            bs.seek(0x1C, NOESEEK_REL)
            bone1 = self.readClsNodeInfo(bs)
            bone2 = self.readClsNodeInfo(bs)
            bone3 = self.readClsNodeInfo(bs)
            bone4 = self.readClsNodeInfo(bs)
            rootBoneName.append([bone1[0], bone2[0], bone3[0], bone4[0]])
            rootWeight.append([bone1[1], bone2[1], bone3[1], bone4[1]])
            name = meshName + "_" + str(i+1).zfill(2) + "_000"
            mtx = self.loadBone(name, bone1[0], pos)
            nodeName.append(name)
            self.gblMtxs[name] = mtx
            for a in range(4):
                if rootBoneName[i][a] and rootBoneName[i][a] not in usedBone:
                    usedBone.append(rootBoneName[i][a])
        bs.seek(nodeOff, NOESEEK_ABS)
        for i in range(columnCount-1):
            for a in range(rowCount):
                nodeType = bs.readUInt()
                pos = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
                bs.seek(0x1C, NOESEEK_REL)
                name = meshName + "_" + str(a+1).zfill(2) + "_" + str(i+1).zfill(3)
                parent = meshName + "_" + str(a+1).zfill(2) + "_" + str(i).zfill(3)
                mtx = self.loadBone(name, parent, pos)
                nodeName.append(name)
                self.gblMtxs[name] = mtx
        usedBoneDict = {}
        for i in range(len(usedBone)):
            usedBoneDict[usedBone[i]] = len(nodeName) + i
        nodeName.extend(usedBone)
        boneName = nodeName
        self.clsBoneName[meshName] = boneName
        self.clsBoneName[backfaceName] = boneName
        bs.seek(meshVertOff, NOESEEK_ABS)
        self.readClsWeight(bs, meshName, rowCount, rootBoneName, rootWeight, usedBoneDict)
        bs.seek(backfaceVertOff, NOESEEK_ABS)
        self.readClsWeight(bs, backfaceName, rowCount, rootBoneName, rootWeight, usedBoneDict)

    def readClsNodeInfo(self, bs):
        boneName = getOffString(bs, readOff(bs, self.addressSpace))
        weight = bs.readFloat()
        index = bs.readUInt()
        unk = bs.readUInt()
        return [boneName, weight, index, unk]

    def readClsWeight(self, bs, meshName, rowCount, rootBoneName, rootWeight, usedBoneDict):
        vertCount = bs.readShort()
        weight = []
        boneIdx = []
        for i in range(vertCount):
            nodeIdx = bs.readShort()
            if nodeIdx < rowCount:
                weight.extend(rootWeight[nodeIdx])
                for a in range(4):
                    name = rootBoneName[nodeIdx][a]
                    if name:
                        boneIdx.append(usedBoneDict[name])
                    else:
                        boneIdx.append(nodeIdx)
            else:
                weight.extend([1.0, 0.0, 0.0, 0.0])
                boneIdx.extend([nodeIdx] * 4)
        self.clsWeight[meshName] = [weight, boneIdx]

    def loadBone(self, name, parentName, pos, rot=NoeVec3((0.0,0.0,0.0)), scl=NoeVec3((1.0,1.0,1.0)), mtx=None, parentIdx=None):
        if not mtx:
            mtx = NoeAngles([rot[0]*noesis.g_flRadToDeg, rot[1]*noesis.g_flRadToDeg, rot[2]*noesis.g_flRadToDeg]).toMat43_XYZ()
            mtx[0] *= scl[0]
            mtx[1] *= scl[1]
            mtx[2] *= scl[2]
            mtx[3] = NoeVec3((pos[0], pos[1], pos[2]))
        idx = len(self.boneList)
        parent = -1
        if parentName:
            try:
                parent = self.boneDict[parentName]
            except:
                self.parentRetry.append([idx, parentName])
                parent = -1
        elif parentIdx != None:
            parent = parentIdx
        self.boneDict[name] = idx
        self.boneList.append(NoeBone(idx, name, mtx, None, parent))
        return mtx

class Object:
    
    def __init__(self, texHashDict, boneDict, boneName, endian, addressSpace, sectionOff, objIdx, clsWeight, clsBoneName):
        self.texHashDict = texHashDict
        self.boneDict = boneDict
        self.boneName = boneName
        self.endian = endian
        self.addressSpace = addressSpace
        self.sectionOff = sectionOff
        self.objIdx = objIdx
        self.clsWeight = clsWeight
        self.clsBoneName = clsBoneName
        self.matList = []
        self.matDict = {}
        self.uvScale = []
        
    def readObject(self, bs, data):
        if self.addressSpace == 32:
            bs.seek(0x18, NOESEEK_REL)
            meshCount = bs.readInt()
            meshOff = readOff(bs, self.addressSpace)
            matCount = bs.readUInt()
            matOff = readOff(bs, self.addressSpace)
        elif self.addressSpace == 64:
            bs.seek(0x08, NOESEEK_REL)
            meshCount = bs.readInt()
            matCount = bs.readInt()
            bs.seek(0x10, NOESEEK_REL)
            meshOff = readOff(bs, self.addressSpace)
            matOff = readOff(bs, self.addressSpace)
        bs.seek(matOff, NOESEEK_ABS)
        for i in range(matCount):
            self.readMat(bs)
        bs.seek(meshOff, NOESEEK_ABS)
        self.loadMesh(bs, data, meshCount)

    def readMat(self, bs):
        bs.seek(0x04, NOESEEK_REL)
        flags = bs.readUInt()
        shaderName = bs.readBytes(0x08).decode("ASCII").rstrip("\0")
        shaderFlags = bs.readUInt()
        matTex = []
        matBlend = []
        matTexType = []
        for i in range(8):
            texId, uv, blend, texType = self.readMatTex(bs)
            if i == 0:
                self.uvScale.append(uv)
            matTex.append(texId)
            matBlend.append(blend)
            matTexType.append(texType)
        blendFlags = bs.readUInt()
        diffColour = [bs.readFloat(), bs.readFloat(), bs.readFloat(),bs.readFloat()]
        ambiColour = [bs.readFloat(), bs.readFloat(), bs.readFloat(),bs.readFloat()]
        specColour = [bs.readFloat(), bs.readFloat(), bs.readFloat(),bs.readFloat()]
        emiColour = [bs.readFloat(), bs.readFloat(), bs.readFloat(),bs.readFloat()]
        shininess = bs.readFloat()
        intensity = bs.readFloat()
        bs.seek(0x10, NOESEEK_REL)
        matName = bs.readBytes(0x40).decode("ASCII").rstrip("\0")
        bumpDepth = bs.readFloat()
        bs.seek(0x3C, NOESEEK_REL)
        material = NoeMaterial(matName, "")
        for i in range(6):
            try:
                if i == 0 and matTexType[i] == 0x01:
                    material.setTexture(self.texHashDict[matTex[i]])
                elif i == 1 and matTexType[i] == 0x01 and matBlend[i] == 6:
                    material.setOcclTexture(self.texHashDict[matTex[i]])
                elif matTexType[i] == 0x02:
                    material.setNormalTexture(self.texHashDict[matTex[i]])
                elif matTexType[i] == 0x03:
                    material.setSpecularTexture(self.texHashDict[matTex[i]])
                elif i == 5 and matTex[i] != 0xFFFFFFFF and matTex[i] != 0x5A009B23:
                    material.setEnvTexture(self.texHashDict[matTex[i]])
            except:
                pass
        material.setDefaultBlend(blendFlags & 0x01)
        material.setDiffuseColor(diffColour)
        material.setAmbientColor(ambiColour)
        material.setSpecularColor([specColour[0], specColour[1], specColour[2], shininess])
        material.setFlags(None, 1)
        if printMatInfo:
            if emiColour != [0.0, 0.0, 0.0, 1.0] or specColour[3] != 1.0:
                print(matName)
                if specColour[3] != 1.0:
                    print("Reflectivity = " + str(specColour[3]))
                if emiColour != [0.0, 0.0, 0.0, 1.0]:
                    print("Emissive Colour = " + str(emiColour[:3]))
                print()
        self.matList.append(material)
    
    def readMatTex(self, bs):
        flags = bs.readUInt()
        texId = bs.readUInt()
        texFlags = bs.readUInt()
        extraShaderName = bs.readBytes(0x08).decode("ASCII").rstrip("\0")
        weight = bs.readUInt()
        uvX = bs.readFloat()
        bs.seek(0x10, NOESEEK_REL)
        uvY = bs.readFloat()
        bs.seek(0x10, NOESEEK_REL)
        uvZ = bs.readFloat()
        bs.seek(0x34, NOESEEK_REL)
        uv = ([uvX, uvY, uvZ])
        blend = flags >> 5 & 0X1F
        texType = texFlags & 0xF
        return texId, uv, blend, texType

    def loadMesh(self, bs, data, meshCount):
        meshes = []
        for i in range(meshCount):
            meshes.append(self.readMesh(bs))
        for mesh in meshes:
            subMeshes = []
            bs.seek(mesh.subMeshOff, NOESEEK_ABS)
            for i in range(mesh.subMeshCount):
                subMeshes.append(self.readSubMesh(bs))
            if self.sectionOff:
                self.buildMeshFgo(bs, data, mesh, subMeshes)
            else:
                self.buildMesh(bs, mesh, subMeshes)

    def readMesh(self, bs):
        mesh = Mesh()
        bs.seek(0x14, NOESEEK_REL)
        mesh.subMeshCount = bs.readInt()
        mesh.subMeshOff = readOff(bs, self.addressSpace)
        mesh.vertFlags = bs.readUInt()
        mesh.vertSize = bs.readUInt()
        mesh.vertCount = bs.readInt()
        if self.endian and self.addressSpace == 32:
            mesh.vertAttrOff = bs.read(">" + "20I")
        elif self.addressSpace == 32:
            mesh.vertAttrOff = bs.read("20I")
        elif self.endian and self.addressSpace == 64:
            bs.seek(0x04, NOESEEK_REL)
            mesh.vertAttrOff = bs.read(">" + "20Q")
        elif self.addressSpace == 64:
            bs.seek(0x04, NOESEEK_REL)
            mesh.vertAttrOff = bs.read("20Q")
        mesh.meshFlags = bs.readUInt()
        mesh.attrFlags = bs.readUInt()
        bs.seek(0x18, NOESEEK_REL)
        mesh.meshName = bs.readBytes(0x40).decode("ASCII").rstrip("\0")
        return mesh

    def readSubMesh(self, bs):
        subMesh = SubMesh()
        bs.seek(0x14, NOESEEK_REL)
        subMesh.matIndex = bs.readUInt()
        subMesh.texCoordIndicies = bs.read("8B")
        subMesh.boneMapCount = bs.readInt()
        subMesh.boneMap = self.readBoneMap(bs, readOff(bs, self.addressSpace), subMesh.boneMapCount)
        subMesh.bonesPerVertex = bs.readUInt()
        subMesh.faceType = bs.readUInt()
        subMesh.faceFormat = bs.readUInt()
        subMesh.faceCount = bs.readInt()
        subMesh.faceOff = readOff(bs, self.addressSpace)
        subMesh.flags = bs.readUInt()
        if self.sectionOff:
            if self.addressSpace == 32:
                bs.seek(0x30, NOESEEK_REL)
            elif self.addressSpace == 64:
                bs.seek(0x34, NOESEEK_REL)
        else:
            bs.seek(0x1C, NOESEEK_REL)
        return subMesh

    def readBoneMap(self, bs, boneMapOff, boneMapCount):
        boneMap = []
        pos = bs.tell()
        bs.seek(boneMapOff, NOESEEK_ABS)
        if self.sectionOff:
            for i in range(boneMapCount):
                idx = self.boneDict[self.boneName[bs.readUShort()]]
                boneMap.append(idx)
                boneMap.append(idx)
                boneMap.append(idx)
        else:
            for i in range(boneMapCount):
                boneMap.append(self.boneDict[self.boneName[bs.readUShort()]])
        bs.seek(pos, NOESEEK_ABS)
        return boneMap

    def buildMesh(self, bs, mesh, subMeshes):
        if mesh.vertFlags & 0x01:
            bs.seek(mesh.vertAttrOff[0], NOESEEK_ABS)
            vertBuff = bs.readBytes(mesh.vertCount * 0x0C)
            rapi.rpgBindPositionBuffer(vertBuff, noesis.RPGEODATA_FLOAT, 12)
        if mesh.vertFlags & 0x02:
            bs.seek(mesh.vertAttrOff[1], NOESEEK_ABS)
            normalBuff = bs.readBytes(mesh.vertCount * 0x0C)
            rapi.rpgBindNormalBuffer(normalBuff, noesis.RPGEODATA_FLOAT, 12)
        if mesh.vertFlags & 0x04:
            bs.seek(mesh.vertAttrOff[2], NOESEEK_ABS)
            tangentBuff = bs.readBytes(mesh.vertCount * 0x10)
            rapi.rpgBindTangentBuffer(tangentBuff, noesis.RPGEODATA_FLOAT, 16)
        if mesh.vertFlags & 0x10:
            bs.seek(mesh.vertAttrOff[4], NOESEEK_ABS)
            uvBuff = bs.readBytes(mesh.vertCount * 0x08)
            rapi.rpgBindUV1Buffer(uvBuff, noesis.RPGEODATA_FLOAT, 8)
        if mesh.vertFlags & 0x20:
            bs.seek(mesh.vertAttrOff[5], NOESEEK_ABS)
            uv2Buff = bytearray()
            for i in range(mesh.vertCount):
                uv2Buff += struct.pack("f", bs.readFloat())
                uv2Buff += struct.pack("f", bs.readFloat() * -1)
            rapi.rpgBindUV2Buffer(uv2Buff, noesis.RPGEODATA_FLOAT, 8)
        if mesh.vertFlags & 0x40:
            bs.seek(mesh.vertAttrOff[6], NOESEEK_ABS)
            uv3Buff = bytearray()
            for i in range(mesh.vertCount):
                uv3Buff += struct.pack("f", bs.readFloat())
                uv3Buff += struct.pack("f", bs.readFloat() * -1)
            rapi.rpgBindUVXBuffer(uv3Buff, noesis.RPGEODATA_FLOAT, 8, 2, 2)
        if mesh.vertFlags & 0x80:
            bs.seek(mesh.vertAttrOff[7], NOESEEK_ABS)
            uv4Buff = bytearray()
            for i in range(mesh.vertCount):
                uv4Buff += struct.pack("f", bs.readFloat())
                uv4Buff += struct.pack("f", bs.readFloat() * -1)
            rapi.rpgBindUVXBuffer(uv4Buff, noesis.RPGEODATA_FLOAT, 8, 3, 2)
        if mesh.vertFlags & 0x100 and not vc2:
            bs.seek(mesh.vertAttrOff[8], NOESEEK_ABS)
            colourBuff = bs.readBytes(mesh.vertCount * 0x10)
            rapi.rpgBindColorBuffer(colourBuff, noesis.RPGEODATA_FLOAT, 16, 4)
        elif mesh.vertFlags & 0x200:
            bs.seek(mesh.vertAttrOff[9], NOESEEK_ABS)
            colourBuff2 = bs.readBytes(mesh.vertCount * 0x10)
            rapi.rpgBindColorBuffer(colourBuff2, noesis.RPGEODATA_FLOAT, 16, 4)
        if mesh.vertFlags & 0x400:
            bs.seek(mesh.vertAttrOff[10], NOESEEK_ABS)
            weightBuff = bs.readBytes(mesh.vertCount * 0x10)
            rapi.rpgBindBoneWeightBuffer(weightBuff, noesis.RPGEODATA_FLOAT, 16, 4)
        if mesh.vertFlags & 0x800:
            bs.seek(mesh.vertAttrOff[11], NOESEEK_ABS)
            indexBuff = bytearray()
            isOld = False
            if subMeshes[0].boneMapCount < 85:
                isOld = True
            for i in range(mesh.vertCount):
                for a in range(4):
                    idx = bs.readFloat()
                    if isOld and idx == 255.0:
                        idx = 0.0
                    indexBuff += struct.pack("h", int(idx // 3))
            rapi.rpgBindBoneIndexBuffer(indexBuff, noesis.RPGEODATA_SHORT, 8, 4)
        if mesh.meshName in self.clsWeight:
            weightBuff = struct.pack("f" * mesh.vertCount * 4, * self.clsWeight[mesh.meshName][0])
            indexBuff = struct.pack("h" * mesh.vertCount * 4, * self.clsWeight[mesh.meshName][1])
            rapi.rpgBindBoneWeightBuffer(weightBuff, noesis.RPGEODATA_FLOAT, 16, 4)
            rapi.rpgBindBoneIndexBuffer(indexBuff, noesis.RPGEODATA_SHORT, 8, 4)
        cnt = 0
        for subMesh in subMeshes:
            if subMesh.texCoordIndicies[0] == 1 and subMesh.texCoordIndicies[2] == 1 and subMesh.texCoordIndicies[3] == 1:
                self.matList[subMesh.matIndex].setFlags(noesis.NMATFLAG_DIFFUSE_UV1 | noesis.NMATFLAG_NORMAL_UV1 | noesis.NMATFLAG_SPEC_UV1)
            elif subMesh.texCoordIndicies[0] == 1 and subMesh.texCoordIndicies[2] == 1:
                self.matList[subMesh.matIndex].setFlags(noesis.NMATFLAG_DIFFUSE_UV1 | noesis.NMATFLAG_NORMAL_UV1)
            elif subMesh.texCoordIndicies[0] == 1 and subMesh.texCoordIndicies[3] == 1:
                self.matList[subMesh.matIndex].setFlags(noesis.NMATFLAG_DIFFUSE_UV1 | noesis.NMATFLAG_SPEC_UV1)
            elif subMesh.texCoordIndicies[0] == 1:
                self.matList[subMesh.matIndex].setFlags(noesis.NMATFLAG_DIFFUSE_UV1)
            if subMesh.texCoordIndicies[1] == 1:
                self.matList[subMesh.matIndex].setFlags2(noesis.NMATFLAG2_OCCL_UV1 | noesis.NMATFLAG2_OCCL_ISLM)
            if len(subMeshes) > 1:
                rapi.rpgSetName(mesh.meshName + "_" + str(cnt))
                cnt += 1
            else:
                rapi.rpgSetName(mesh.meshName)
            rapi.rpgSetMaterial(self.matList[subMesh.matIndex].name)
            if subMesh.boneMapCount != 0:
                rapi.rpgSetBoneMap(subMesh.boneMap)
            elif mesh.meshName in self.clsWeight:
                boneMap = []
                boneNameList = self.clsBoneName[mesh.meshName]
                for i in range(len(boneNameList)):
                    boneMap.append(self.boneDict[boneNameList[i]])
                rapi.rpgSetBoneMap(boneMap)
            rapi.rpgSetUVScaleBias(NoeVec3((self.uvScale[subMesh.matIndex][0], self.uvScale[subMesh.matIndex][1]*-1, self.uvScale[subMesh.matIndex][2])), None)
            bs.seek(subMesh.faceOff, NOESEEK_ABS)
            if subMesh.faceFormat == 0x00:
                faceBuff = bs.readBytes(subMesh.faceCount * 0x01)
                faceFormat = noesis.RPGEODATA_UBYTE
            elif subMesh.faceFormat == 0x01:
                faceBuff = bs.readBytes(subMesh.faceCount * 0x02)
                faceFormat = noesis.RPGEODATA_USHORT
            elif subMesh.faceFormat == 0x02:
                faceBuff = bs.readBytes(subMesh.faceCount * 0x04)
                faceFormat = noesis.RPGEODATA_UINT
            if subMesh.faceType == 0x04:
                rapi.rpgCommitTriangles(faceBuff, faceFormat, subMesh.faceCount, noesis.RPGEO_TRIANGLE, 1)
            elif subMesh.faceType == 0x05:
                rapi.rpgCommitTriangles(faceBuff, faceFormat, subMesh.faceCount, noesis.RPGEO_TRIANGLE_STRIP, 1)
        rapi.rpgClearBufferBinds()
    
    def buildMeshFgo(self, bs, data, mesh, subMeshes):
        vs = NoeBitStream(data[self.sectionOff["OVTX"][self.objIdx]:], self.endian)
        if self.addressSpace == 32:
            vs.seek(mesh.vertAttrOff[13] + 0x20, NOESEEK_ABS)
        elif self.addressSpace == 64:
            vs.seek(mesh.vertAttrOff[13], NOESEEK_ABS)
        vertBuff = vs.readBytes(mesh.vertSize * mesh.vertCount)
        rapi.rpgBindPositionBufferOfs(vertBuff, noesis.RPGEODATA_FLOAT, mesh.vertSize, 0x00)
        rapi.rpgBindNormalBufferOfs(vertBuff, noesis.RPGEODATA_SHORT, mesh.vertSize, 0x0C)
        rapi.rpgBindTangentBufferOfs(vertBuff, noesis.RPGEODATA_SHORT, mesh.vertSize, 0x14)
        rapi.rpgBindUV1BufferOfs(vertBuff, noesis.RPGEODATA_HALFFLOAT, mesh.vertSize, 0x1C)
        rapi.rpgBindUV2BufferOfs(vertBuff, noesis.RPGEODATA_HALFFLOAT, mesh.vertSize, 0x20)
        if mesh.attrFlags == 0x0A:
            rapi.rpgBindUVXBufferOfs(vertBuff, noesis.RPGEODATA_HALFFLOAT, mesh.vertSize, 2, 2, 0x24)
            rapi.rpgBindUVXBufferOfs(vertBuff, noesis.RPGEODATA_HALFFLOAT, mesh.vertSize, 3, 2, 0x28)
            rapi.rpgBindColorBufferOfs(vertBuff, noesis.RPGEODATA_HALFFLOAT, mesh.vertSize, 0x2C, 4)
        else:
            rapi.rpgBindColorBufferOfs(vertBuff, noesis.RPGEODATA_HALFFLOAT, mesh.vertSize, 0x24, 4)
        if mesh.attrFlags == 0x04:
            rapi.rpgBindBoneWeightBufferOfs(vertBuff, noesis.RPGEODATA_USHORT, mesh.vertSize, 0x2C, 4)
            rapi.rpgBindBoneIndexBufferOfs(vertBuff, noesis.RPGEODATA_UBYTE, mesh.vertSize, 0x34, 4)
        elif mesh.meshName in self.clsWeight:
            if self.endian:
                weightBuff = struct.pack(">" + "f" * mesh.vertCount * 4, * self.clsWeight[mesh.meshName][0])
                indexBuff = struct.pack(">" + "h" * mesh.vertCount * 4, * self.clsWeight[mesh.meshName][1])
            else:
                weightBuff = struct.pack("f" * mesh.vertCount * 4, * self.clsWeight[mesh.meshName][0])
                indexBuff = struct.pack("h" * mesh.vertCount * 4, * self.clsWeight[mesh.meshName][1])
            rapi.rpgBindBoneWeightBuffer(weightBuff, noesis.RPGEODATA_FLOAT, 16, 4)
            rapi.rpgBindBoneIndexBuffer(indexBuff, noesis.RPGEODATA_SHORT, 8, 4)
        cnt = 0
        for subMesh in subMeshes:
            if subMesh.texCoordIndicies[0] == 1 and subMesh.texCoordIndicies[2] == 1 and subMesh.texCoordIndicies[3] == 1:
                self.matList[subMesh.matIndex].setFlags(noesis.NMATFLAG_DIFFUSE_UV1 | noesis.NMATFLAG_NORMAL_UV1 | noesis.NMATFLAG_SPEC_UV1)
            elif subMesh.texCoordIndicies[0] == 1 and subMesh.texCoordIndicies[2] == 1:
                self.matList[subMesh.matIndex].setFlags(noesis.NMATFLAG_DIFFUSE_UV1 | noesis.NMATFLAG_NORMAL_UV1)
            elif subMesh.texCoordIndicies[0] == 1 and subMesh.texCoordIndicies[3] == 1:
                self.matList[subMesh.matIndex].setFlags(noesis.NMATFLAG_DIFFUSE_UV1 | noesis.NMATFLAG_SPEC_UV1)
            elif subMesh.texCoordIndicies[0] == 1:
                self.matList[subMesh.matIndex].setFlags(noesis.NMATFLAG_DIFFUSE_UV1)
            if subMesh.texCoordIndicies[1] == 1:
                self.matList[subMesh.matIndex].setFlags2(noesis.NMATFLAG2_OCCL_UV1 | noesis.NMATFLAG2_OCCL_ISLM)
            if len(subMeshes) > 1:
                rapi.rpgSetName(mesh.meshName + "_" + str(cnt))
                cnt += 1
            else:
                rapi.rpgSetName(mesh.meshName)
            rapi.rpgSetMaterial(self.matList[subMesh.matIndex].name)
            if subMesh.boneMapCount != 0:
                rapi.rpgSetBoneMap(subMesh.boneMap)
            elif mesh.meshName in self.clsWeight:
                boneMap = []
                boneNameList = self.clsBoneName[mesh.meshName]
                for i in range(len(boneNameList)):
                    boneMap.append(self.boneDict[boneNameList[i]])
                rapi.rpgSetBoneMap(boneMap)
            rapi.rpgSetUVScaleBias(NoeVec3((self.uvScale[subMesh.matIndex][0], self.uvScale[subMesh.matIndex][1]*-1, self.uvScale[subMesh.matIndex][2])), None)
            fs = NoeBitStream(data[self.sectionOff["OIDX"][self.objIdx]:], self.endian)
            if self.addressSpace == 32:
                fs.seek(subMesh.faceOff + 0x20, NOESEEK_ABS)
            elif self.addressSpace == 64:
                fs.seek(subMesh.faceOff, NOESEEK_ABS)
            if subMesh.faceFormat == 0x00:
                faceBuff = fs.readBytes(subMesh.faceCount * 0x01)
                faceFormat = noesis.RPGEODATA_UBYTE
            elif subMesh.faceFormat == 0x01:
                faceBuff = fs.readBytes(subMesh.faceCount * 0x02)
                faceFormat = noesis.RPGEODATA_USHORT
            elif subMesh.faceFormat == 0x02:
                faceBuff = fs.readBytes(subMesh.faceCount * 0x04)
                faceFormat = noesis.RPGEODATA_UINT
            if subMesh.faceType == 0x04:
                rapi.rpgCommitTriangles(faceBuff, faceFormat, subMesh.faceCount, noesis.RPGEO_TRIANGLE, 1)
            elif subMesh.faceType == 0x05:
                rapi.rpgCommitTriangles(faceBuff, faceFormat, subMesh.faceCount, noesis.RPGEO_TRIANGLE_STRIP, 1)
        rapi.rpgClearBufferBinds()

class Mesh:
    def __init__(self):
        self.subMeshCount = None
        self.subMeshOff = None
        self.vertFlags = None
        self.vertSize = None
        self.vertCount = None
        self.vertAttrOff = None
        self.meshFlags = None
        self.attrFlags = None
        self.meshName = None

class SubMesh:
    def __init__(self):
        self.matIndex = None
        self.texCoordIndicies = None
        self.boneMapCount = None
        self.boneMapOff = None
        self.bonesPerVertex = None
        self.faceType = None
        self.faceFormat = None
        self.faceCount = None
        self.faceOff = None
        self.flags = None

class ObjectSetSr:
    
    def __init__(self):
        self.objNames = []
        
    def readObjSet(self, bs, mdlList, texList):
        magic = bs.readUInt()
        fileSize = bs.readUInt()
        objCount = bs.readInt()
        texCount = bs.readInt()
        objOff = bs.readUInt64()
        texOff = bs.readUInt64()
        dataOff = bs.readUInt64()
        bs.seek(objOff, NOESEEK_ABS)
        for i in range(objCount):
            objName = getOffString(bs, bs.readUInt64())
            self.objNames.append(objName)
            print(objName)
            objectOff = bs.readUInt64()
            texNameListOff = bs.readUInt64()
            texNameCount = bs.readInt()
            texNameList = getOffStringList(bs, 64, texNameListOff, texNameCount)
            objectDataSize = bs.readUInt()
            bs.seek(0x18, NOESEEK_REL)
            pos = bs.tell()
            bs.seek(objectOff, NOESEEK_ABS)
            objectData = bs.readBytes(objectDataSize)
            bs.seek(pos, NOESEEK_ABS)
            obj = ObjectSr(texNameList)
            obj.readObject(NoeBitStream(objectData))
            try:
                mdl = rapi.rpgConstructModel()
            except:
                mdl = NoeModel()
            if obj.boneList != []:
                obj.boneList = rapi.multiplyBones(obj.boneList)
                # for a in range(len(obj.boneList)):
                #     br = obj.boneList[a]._matrix.inverse()
                #     obj.boneList[a]._matrix[0] = br[0]
                #     obj.boneList[a]._matrix[1] = br[1]
                #     obj.boneList[a]._matrix[2] = br[2]
                mdl.setBones(obj.boneList)
            if i == 0:
                mdl.setModelMaterials(NoeModelMaterials(texList, obj.matList))
            else:
                mdl.setModelMaterials(NoeModelMaterials([], obj.matList))
            mdlList.append(mdl)
            rapi.rpgReset()

class ObjectSr:
    
    def __init__(self, texNameList):
        self.texNameList = texNameList
        self.matList = []
        self.boneList = []
        self.morphList = []
        self.stringList = []
        self.boneMapList = []
        
    def readObject(self, bs):
        bs.seek(0x18, NOESEEK_REL)
        meshCount = bs.readInt()
        matCount = bs.readInt()
        bs.seek(0x30, NOESEEK_REL)
        meshOff = bs.readUInt64()
        matOff = bs.readUInt64()
        skelOff = bs.readUInt64()
        bs.seek(meshOff, NOESEEK_ABS)
        meshList = self.readMesh(bs, meshCount)
        bs.seek(matOff, NOESEEK_ABS)
        self.readMat(bs, matCount)
        if skelOff:
            bs.seek(skelOff, NOESEEK_ABS)
            self.readSkel(bs)
        self.buildMesh(bs, meshList)

    def readMesh(self, bs, meshCount):
        meshList = []
        for i in range(meshCount):
            mesh = MeshSr()
            bs.seek(0x14, NOESEEK_REL)
            mesh.subMeshCount = bs.readInt()
            bs.seek(0x08, NOESEEK_REL)
            mesh.vertCount = bs.readInt()
            bs.seek(0x04, NOESEEK_REL)
            mesh.subMeshOff = bs.readUInt64()
            mesh.vertOff = bs.readUInt64()
            mesh.normOff = bs.readUInt64()
            mesh.tangOff = bs.readUInt64()
            bs.seek(0x08, NOESEEK_REL)
            mesh.uvOff = bs.readUInt64()
            bs.seek(0x28, NOESEEK_REL)
            mesh.weightOff = bs.readUInt64()
            mesh.boneIdxOff = bs.readUInt64()
            bs.seek(0x60, NOESEEK_REL)
            mesh.name = bs.readBytes(0x20).decode("ASCII").rstrip("\0")
            meshList.append(mesh)
        for mesh in meshList:
            self.readSubMesh(bs, mesh)
        return meshList

    def readSubMesh(self, bs, mesh):
        bs.seek(mesh.subMeshOff)
        for i in range(mesh.subMeshCount):
            subMesh = SubMeshSr()
            bs.seek(0x18, NOESEEK_REL)
            subMesh.matIdx = bs.readInt()
            bs.seek(0x24, NOESEEK_REL)
            subMesh.faceType = bs.readUInt()
            bs.seek(0x04, NOESEEK_REL)
            subMesh.faceCount = bs.readInt()
            bs.seek(0x0C, NOESEEK_REL)
            subMesh.faceOff = bs.readUInt64()
            bs.seek(0x18, NOESEEK_REL)
            mesh.subMeshList.append(subMesh)

    def readMat(self, bs, matCount):
        for i in range(matCount):
            bs.seek(0x0C, NOESEEK_REL)
            shaderName = bs.readBytes(0x08).decode("ASCII").rstrip("\0")
            matName = bs.readBytes(0x3C).decode("ASCII").rstrip("\0")
            bs.seek(0x60, NOESEEK_REL)
            material = NoeMaterial(matName, "")
            for a in range(32):
                bs.seek(0x08, NOESEEK_REL)
                texIdx = bs.readInt()
                bs.seek(0x54, NOESEEK_REL)
                if texIdx != -1:
                    if a == 0:
                        material.setTexture(self.texNameList[texIdx])
                    elif a == 4:
                        material.setNormalTexture(self.texNameList[texIdx])
                    elif a == 14:
                        material.setSpecularTexture(self.texNameList[texIdx])
            self.matList.append(material)

    def readSkel(self, bs):
        boneCount = bs.readInt()
        bs.seek(0x0C, NOESEEK_REL)
        boneMtxOff = bs.readUInt64()
        boneParentOff = bs.readUInt64()
        unkOff = bs.readUInt64()
        unkOff = bs.readUInt64()
        boneNameOff = bs.readUInt64()
        bs.seek(boneMtxOff, NOESEEK_ABS)
        for i in range(boneCount):
            quat = NoeQuat.fromBytes(bs.readBytes(0x10))
            pos = NoeVec3.fromBytes(bs.readBytes(0x0C))
            scl = NoeVec3.fromBytes(bs.readBytes(0x0C))
            mtx = NoeMat44.fromBytes(bs.readBytes(0x40)).toMat43().inverse()
            boneMtx = quat.toMat43().inverse()
            boneMtx[3] = pos
            boneMtx[0] *= scl[0]
            boneMtx[1] *= scl[1]
            boneMtx[2] *= scl[2]
            bone = NoeBone(i, str(i), boneMtx, None, -1)
            self.boneList.append(bone)
        bs.seek(boneParentOff, NOESEEK_ABS)
        boneParentList = []
        for i in range(boneCount):
            self.boneList[i].parentIndex = bs.readShort()
        bs.seek(boneNameOff, NOESEEK_ABS)
        for i in range(boneCount):
            self.boneList[i].name = bs.readString()
            padding(bs, 0x04)

    def buildMesh(self, bs, meshList):
        for mesh in meshList:
            bs.seek(mesh.vertOff, NOESEEK_ABS)
            vertBuff = bs.readBytes(mesh.vertCount * 0x0C)
            rapi.rpgBindPositionBuffer(vertBuff, noesis.RPGEODATA_FLOAT, 0x0C)
            if mesh.normOff:
                bs.seek(mesh.normOff, NOESEEK_ABS)
                normBuff = bs.readBytes(mesh.vertCount * 0x06)
                rapi.rpgBindNormalBuffer(normBuff, noesis.RPGEODATA_HALFFLOAT, 0x06)
            if mesh.tangOff:
                bs.seek(mesh.tangOff, NOESEEK_ABS)
                tangBuff = bs.readBytes(mesh.vertCount * 0x08)
                rapi.rpgBindTangentBuffer(tangBuff, noesis.RPGEODATA_HALFFLOAT, 0x08)
            if mesh.uvOff:
                bs.seek(mesh.uvOff, NOESEEK_ABS)
                uvBuff = bs.readBytes(mesh.vertCount * 0x08)
                rapi.rpgBindUV1Buffer(uvBuff, noesis.RPGEODATA_FLOAT, 0x08)
            if mesh.weightOff:
                bs.seek(mesh.weightOff, NOESEEK_ABS)
                weightBuff = bs.readBytes(mesh.vertCount * 0x10)
                rapi.rpgBindBoneWeightBuffer(weightBuff, noesis.RPGEODATA_FLOAT, 0x10, 4)
            if mesh.boneIdxOff:
                bs.seek(mesh.boneIdxOff, NOESEEK_ABS)
                boneIdxBuff = bs.readBytes(mesh.vertCount * 0x04)
                rapi.rpgBindBoneIndexBuffer(boneIdxBuff, noesis.RPGEODATA_UBYTE, 0x04, 4)
            cnt = 0
            for subMesh in mesh.subMeshList:
                if mesh.subMeshCount > 1:
                    rapi.rpgSetName(mesh.name + "_" + str(cnt))
                    cnt += 1
                else:
                    rapi.rpgSetName(mesh.name)
                rapi.rpgSetMaterial(self.matList[subMesh.matIdx].name)
                rapi.rpgSetUVScaleBias(NoeVec3([1, -1, 1]), None)
                bs.seek(subMesh.faceOff, NOESEEK_ABS)
                faceBuff = bs.readBytes(subMesh.faceCount * 0x02)
                if subMesh.faceType == 0x04:
                    rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, subMesh.faceCount, noesis.RPGEO_TRIANGLE, 1)
                else:
                    rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, subMesh.faceCount, noesis.RPGEO_TRIANGLE_STRIP, 1)
            rapi.rpgClearBufferBinds()

class MeshSr:

    def __init__(self):
        self.subMeshCount = None
        self.vertCount = None
        self.subMeshOff = None
        self.vertOff = None
        self.normOff = None
        self.tangOff = None
        self.uvOff = None
        self.weightOff = None
        self.boneIdxOff = None
        self.name = None
        self.subMeshList = []

class SubMeshSr:

    def __init__(self):
        self.matIdx = None
        self.faceType = None
        self.faceCount = None
        self.faceOff = None

class ObjectSetFgo:
    
    def __init__(self):
        self.objNames = []
        
    def readObjSet(self, bs, data, mdlList, texList):
        magic = bs.readUInt()
        objCount = bs.readInt()
        boneCount = bs.readInt()
        self.objNames = getOffStringList(bs, 64, readOff(bs, 64), objCount)
        bs.seek(0x2C, NOESEEK_ABS)
        for i in range(objCount):
            print(self.objNames[i])
            objectOff = bs.readUInt64()
            obj = ObjectFgo()
            obj.readObject(NoeBitStream(data[objectOff:]))
            try:
                mdl = rapi.rpgConstructModel()
            except:
                mdl = NoeModel()
            if obj.boneList != []:
                obj.boneList = rapi.multiplyBones(obj.boneList)
                # for a in range(len(obj.boneList)):
                #     br = obj.boneList[a]._matrix.inverse()
                #     obj.boneList[a]._matrix[0] = br[0]
                #     obj.boneList[a]._matrix[1] = br[1]
                #     obj.boneList[a]._matrix[2] = br[2]
                mdl.setBones(obj.boneList)
            if i == 0:
                mdl.setModelMaterials(NoeModelMaterials(texList, obj.matList))
            else:
                mdl.setModelMaterials(NoeModelMaterials([], obj.matList))
            mdlList.append(mdl)
            rapi.rpgReset()

class ObjectFgo:
    
    def __init__(self):
        self.matList = []
        self.boneList = []
        self.morphList = []
        self.stringList = []
        self.boneMapList = []
        
    def readObject(self, bs):
        bs.seek(0x18, NOESEEK_REL)
        meshCount = bs.readInt64()
        meshOff = bs.readUInt64()
        subMeshCount = bs.readInt64()
        subMeshOff = bs.readUInt64()
        vertSize = bs.readUInt64()
        vertOff = bs.readUInt64()
        faceSize = bs.readUInt64()
        faceOff = bs.readUInt64()
        boneMapOff = bs.readUInt64()
        bs.seek(0x18, NOESEEK_REL)
        matCount = bs.readInt64()
        matOff = bs.readUInt64()
        bs.seek(0x20, NOESEEK_REL)
        seklOff = bs.readUInt64()
        bs.seek(0x08, NOESEEK_REL)
        texOff = bs.readUInt64()
        bs.seek(0x30, NOESEEK_REL)
        morphCount = bs.readInt64()
        morphOff = bs.readUInt64()
        bs.seek(0x30, NOESEEK_REL)
        stringCount = bs.readInt64()
        stringOff = bs.readUInt64()
        bs.seek(stringOff, NOESEEK_ABS)
        self.readString(bs, stringCount)
        bs.seek(meshOff, NOESEEK_ABS)
        meshes = self.readMesh(bs, meshCount)
        bs.seek(subMeshOff, NOESEEK_ABS)
        subMeshes = self.readSubMesh(bs, subMeshCount)
        self.readBoneMap(bs, boneMapOff, subMeshes)
        bs.seek(matOff, NOESEEK_ABS)
        self.readMat(bs, matCount)
        bs.seek(seklOff, NOESEEK_ABS)
        self.readSkel(bs)
        bs.seek(texOff, NOESEEK_ABS)
        self.readTex(bs)
        bs.seek(morphOff, NOESEEK_ABS)
        self.readMorph(bs, morphCount)
        self.buildMesh(bs, vertOff, faceOff, meshes, subMeshes)
        return matCount

    def readMesh(self, bs, meshCount):
        meshes = []
        for i in range(meshCount):
            mesh = MeshFgo()
            mesh.name = self.stringList[bs.readUInt()]
            bs.seek(0x08, NOESEEK_REL)
            mesh.subMeshCount = bs.readInt()
            mesh.subMeshIdx = bs.readUInt()
            bs.seek(0x04, NOESEEK_REL)
            mesh.vertFlags = bs.readUInt()
            mesh.stride = bs.readUInt()
            bs.seek(0x1C, NOESEEK_REL)
            mesh.morphCount = bs.readInt()
            bs.seek(0x10, NOESEEK_REL)
            meshes.append(mesh)
        return meshes

    def readSubMesh(self, bs, subMeshCount):
        subMeshes = []
        for i in range(subMeshCount):
            subMesh = SubMeshFgo()
            bs.seek(0x04, NOESEEK_REL)
            subMesh.vertOff = bs.readUInt()
            subMesh.faceCount = bs.readInt()
            subMesh.faceOff = bs.readUInt()
            subMesh.vertCount = bs.readInt()
            subMesh.matIdx = bs.readUInt()
            bs.seek(0x04, NOESEEK_REL)
            subMesh.uvScaleU = bs.readFloat() * 0xFFFF
            subMesh.uvScaleV = bs.readFloat() * 0xFFFF
            subMesh.uvPosU = bs.readFloat()
            subMesh.uvPosV = bs.readFloat()
            bs.seek(0x30, NOESEEK_REL)
            subMesh.boneMapCount = bs.readInt()
            subMesh.boneMapOff = bs.readUInt()
            bs.seek(0x6C, NOESEEK_REL)
            subMeshes.append(subMesh)
        return subMeshes

    def readBoneMap(self, bs, boneMapOff, subMeshes):
        for subMesh in subMeshes:
            boneMap = []
            bs.seek(boneMapOff + (subMesh.boneMapOff * 0x02), NOESEEK_ABS)
            for i in range(subMesh.boneMapCount):
                boneMap.append(bs.readShort())
            self.boneMapList.append(boneMap)

    def readMat(self, bs, matCount):
        for i in range(matCount):
            matName = self.stringList[bs.readUInt()]
            bs.seek(0x04, NOESEEK_REL)
            material = NoeMaterial(matName, "")
            bs.seek(0xB0, NOESEEK_REL)
            self.matList.append(material)

    def readSkel(self, bs):
        boneCount = bs.readUInt()
        if boneCount != 0:
            skelNameSize = bs.readUInt()
            skelName = bs.readBytes(skelNameSize).decode("ASCII").rstrip("\0")
            padding(bs, 0x04)
            for i in range(boneCount):
                quat = NoeQuat.fromBytes(bs.readBytes(0x10))
                pos = NoeVec3.fromBytes(bs.readBytes(0x0C))
                scl = NoeVec3.fromBytes(bs.readBytes(0x0C))
                mtx = NoeMat44.fromBytes(bs.readBytes(0x40)).toMat43().inverse()
                boneMtx = quat.toMat43().inverse()
                boneMtx[3] = pos
                boneMtx[0] *= scl[0]
                boneMtx[1] *= scl[1]
                boneMtx[2] *= scl[2]
                bone = NoeBone(i, str(i), boneMtx, None, -1)
                self.boneList.append(bone)
            for i in range(boneCount):
                self.boneList[i].parentIndex = bs.readInt()
            boneCount = bs.readInt()
            bs.seek(0x04 * boneCount, NOESEEK_REL)
            for i in range(boneCount):
                nameSize = bs.readUInt()
                name = bs.readBytes(nameSize).decode("ASCII").rstrip("\0")
                padding(bs, 0x04)
                boneID = bs.readInt()
                self.boneList[boneID].name = name

    def readTex(self, bs):
        texMatOff = bs.readUInt64()
        texNameOff = bs.readUInt64()
        texCount = bs.readInt64()
        bs.seek(texNameOff, NOESEEK_ABS)
        texData = []
        for i in range(texCount):
            texName = self.stringList[bs.readUInt()]
            bs.seek(0x04, NOESEEK_REL)
            usageCount = bs.readUInt64()
            texId = bs.readUInt64()
            texData.append([texName, usageCount])
        bs.seek(texMatOff, NOESEEK_ABS)
        unkTex = {}
        for i in range(texCount):
            for a in range(texData[i][1]):
                matIdx = bs.readUInt()
                texType = bs.readUInt()
                if texType == 0x00:
                    self.matList[matIdx].setTexture(texData[i][0])
                elif texType == 0x03:
                    self.matList[matIdx].setSpecularTexture(texData[i][0])
                elif texType == 0x06:
                    self.matList[matIdx].setNormalTexture(texData[i][0])
                else:
                    if self.matList[matIdx].name in unkTex:
                        unkTex[self.matList[matIdx].name].append([str(texType), texData[i][0]])
                    else:
                        unkTex[self.matList[matIdx].name] = [[str(texType), texData[i][0]]]
        for key in unkTex:
            print(key)
            for value in unkTex[key]:
                print("Type: " + str(value[0]) + " Tex: " + value[1])
            print()

    def readMorph(self, bs, morphCount):
        for i in range(morphCount):
            self.morphList.append(self.stringList[bs.readUInt()])
            bs.seek(0x04, NOESEEK_REL)

    def readString(self, bs, stringCount):
        for i in range(stringCount):
            stringSize = bs.readUShort()
            self.stringList.append(bs.readString())

    def buildMesh(self, bs, vertOff, faceOff, meshes, subMeshes):
        morphCnt = 0
        for mesh in meshes:
            cnt = 0
            if mesh.morphCount != 0:
                print(mesh.name)
                for i in range(mesh.morphCount):
                    print(self.morphList[morphCnt])
                    morphCnt += 1
                print()
            for i in range(mesh.subMeshCount):
                subMesh = subMeshes[mesh.subMeshIdx + i]
                if mesh.subMeshCount > 1:
                    rapi.rpgSetName(mesh.name + "_" + str(cnt))
                    cnt += 1
                else:
                    rapi.rpgSetName(mesh.name)
                rapi.rpgSetMaterial(self.matList[subMesh.matIdx].name)
                rapi.rpgSetUVScaleBias(NoeVec3([subMesh.uvScaleU, subMesh.uvScaleV * -1, 1]), NoeVec3([subMesh.uvPosU, 1 - subMesh.uvPosV, 0]))
                if subMesh.boneMapCount != 0:
                    rapi.rpgSetBoneMap(self.boneMapList[mesh.subMeshIdx + i])
                bs.seek(vertOff + subMesh.vertOff, NOESEEK_ABS)
                vertBuff = bs.readBytes(subMesh.vertCount * mesh.stride)
                off = 0
                if mesh.vertFlags & 0x01:
                    rapi.rpgBindPositionBufferOfs(vertBuff, noesis.RPGEODATA_FLOAT, mesh.stride, off)
                    off += 0x0C
                if mesh.vertFlags & 0x02:
                    nmlData = noesis.deinterleaveBytes(vertBuff, off, 0x04, mesh.stride)
                    decodedNormals = rapi.decodeNormals32(nmlData, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindNormalBuffer(decodedNormals, noesis.RPGEODATA_FLOAT, 0x0C)
                    off += 0x04
                if mesh.vertFlags & 0x04:
                    tanData = noesis.deinterleaveBytes(vertBuff, off, 0x04, mesh.stride)
                    decodedTangents = rapi.decodeTangents32(tanData, 4, -10, -10, -10, -2, NOE_LITTLEENDIAN)
                    rapi.rpgBindTangentBuffer(decodedTangents, noesis.RPGEODATA_FLOAT, 0x10)
                    off += 0x04
                if mesh.vertFlags & 0x08:
                    rapi.rpgBindUV1BufferOfs(vertBuff, noesis.RPGEODATA_USHORT, mesh.stride, off)
                    off += 0x04
                if mesh.vertFlags & 0x10:
                    rapi.rpgBindUV2BufferOfs(vertBuff, noesis.RPGEODATA_USHORT, mesh.stride, off)
                    off += 0x04
                if mesh.vertFlags & 0x20:
                    rapi.rpgBindUVXBufferOfs(vertBuff, noesis.RPGEODATA_USHORT, mesh.stride, 2, 2, off)
                    off += 0x04
                if mesh.vertFlags & 0x40:
                    rapi.rpgBindUVXBufferOfs(vertBuff, noesis.RPGEODATA_USHORT, mesh.stride, 3, 2, off)
                    off += 0x04
                if mesh.vertFlags & 0x80:
                    if not vc2:
                        rapi.rpgBindColorBufferOfs(vertBuff, noesis.RPGEODATA_UBYTE, mesh.stride, off, 4)
                    off += 0x04
                if mesh.vertFlags & 0x100:
                    if vc2:
                        rapi.rpgBindColorBufferOfs(vertBuff, noesis.RPGEODATA_UBYTE, mesh.stride, off, 4)
                    off += 0x04
                if mesh.vertFlags & 0x200:
                    rapi.rpgBindBoneWeightBufferOfs(vertBuff, noesis.RPGEODATA_UBYTE, mesh.stride, off, 4)
                    off += 0x04
                elif subMesh.boneMapCount != 0:
                    weightBuff = struct.pack("B" * subMesh.vertCount, * [0xFF] * subMesh.vertCount)
                    rapi.rpgBindBoneWeightBuffer(weightBuff, noesis.RPGEODATA_UBYTE, 0x01, 1)
                if mesh.vertFlags & 0x400:
                    rapi.rpgBindBoneIndexBufferOfs(vertBuff, noesis.RPGEODATA_UBYTE, mesh.stride, off, 4)
                elif subMesh.boneMapCount != 0:
                    indexBuff = struct.pack("B" * subMesh.vertCount, * [0x00] * subMesh.vertCount)
                    rapi.rpgBindBoneIndexBuffer(indexBuff, noesis.RPGEODATA_UBYTE, 0x01, 1)
                if mesh.morphCount != 0:
                    for j in range(mesh.morphCount):
                        off = 0
                        vertBuff = bs.readBytes(subMesh.vertCount * mesh.stride)
                        if mesh.vertFlags & 0x01:
                            rapi.rpgFeedMorphTargetPositionsOfs(vertBuff, noesis.RPGEODATA_FLOAT, mesh.stride, off)
                            off += 0x0C
                        if mesh.vertFlags & 0x02:
                            nmlData = noesis.deinterleaveBytes(vertBuff, off, 0x04, mesh.stride)
                            decodedNormals = rapi.decodeNormals32(nmlData, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                            rapi.rpgFeedMorphTargetNormals(decodedNormals, noesis.RPGEODATA_FLOAT, 0x0C)
                        rapi.rpgCommitMorphFrame(subMesh.vertCount)
                    rapi.rpgCommitMorphFrameSet()
                bs.seek(faceOff + subMesh.faceOff, NOESEEK_ABS)
                faceBuff = bs.readBytes(subMesh.faceCount * 0x02)
                rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, subMesh.faceCount, noesis.RPGEO_TRIANGLE_STRIP, 1)
            rapi.rpgClearBufferBinds()

class MeshFgo:

    def __init__(self):
        self.name = None
        self.subMeshCount = None
        self.subMeshIdx = None
        self.vertFlags = None
        self.vertCount = None
        self.stride = None
        self.morphCount = None

class SubMeshFgo:
    
    def __init__(self):
        self.vertOff = None
        self.faceCount = None
        self.faceOff = None
        self.vertCount = None
        self.matIdx = None
        self.uvScaleU = None
        self.uvScaleV = None
        self.uvPosU = None
        self.uvPosV = None
        self.boneMapCount = None
        self.boneMapOff = None

class Txp:
    
    def __init__(self, texList, texDb, isEmcs):
        self.texList = texList
        self.texDb = texDb
        self.isEmcs = isEmcs
        self.texInfo = []
        self.texRGBAData = []
        self.isOld = True
        
    def readTxp(self, bs, name):
        start = bs.tell()
        magic = bs.readUInt()
        if magic == 0x02505854:
            txpData = self.readTxpData(bs)
            return txpData
        elif magic == 0x03505854:
            self.readTxpSet(bs, start, name)
        elif magic == 0x04505854 or magic == 0x05505854:
            self.readTxpInfo(bs, start, magic, name)

    def readTxpSr(self, bs):
        self.isOld = False
        magic = bs.readUInt()
        fileSize = bs.readUInt()
        texCount = bs.readInt()
        txpOff = bs.readUInt()
        texInfoOff = bs.readUInt64()
        bs.seek(texInfoOff, NOESEEK_ABS)
        for i in range(texCount):
            name = getOffString(bs, bs.readUInt64())
            bs.seek(0x14, NOESEEK_REL)
            txpSize = bs.readUInt()
            txpInfoOff = bs.readUInt64()
            pos = bs.tell()
            bs.seek(txpOff + txpInfoOff, NOESEEK_ABS)
            self.readTxp(bs, name)
            bs.seek(pos, NOESEEK_ABS)

    def readTxpFgo(self, bs, fileName):
        self.isOld = False
        texCount = bs.readShort()
        for i in range(texCount):
            nameSize = bs.readUByte()
            name = bs.readBytes(nameSize).decode("ASCII").rstrip("\0")[len(fileName) + 1:]
            txpInfoOff = bs.readUInt()
            pos = bs.tell()
            bs.seek(txpInfoOff, NOESEEK_ABS)
            self.readTxp(bs, name)
            bs.seek(pos, NOESEEK_ABS)

    def readTxpSet(self, bs, start, name):
        texCount = bs.readInt()
        unk = bs.readUInt()
        for i in range(texCount):
            txpInfoOff = bs.readUInt()
            pos = bs.tell()
            bs.seek(start + txpInfoOff, NOESEEK_ABS)
            self.readTxp(bs, name)
            bs.seek(pos, NOESEEK_ABS)

    def readTxpInfo(self, bs, start, magic, name):
        subTexCount = bs.readInt()
        info = bs.readUInt()
        mipCount = info & 0xFF
        depth = (info >> 8) & 0xFF
        isYCbCr = False
        if (mipCount == 2 and depth == 1) or (mipCount == 3 and depth == 1):
            isYCbCr = True
        if self.isEmcs:
            mipCount += 1
        txpDataOff = []
        for i in range(subTexCount):
            txpDataOff.append(bs.readUInt())
        txpDataList = []
        cnt = 0
        for i in range(depth):
            for a in range(mipCount):
                if a ==0 or ((a == 1 or a == 2) and isYCbCr):
                    bs.seek(start + txpDataOff[cnt], NOESEEK_ABS)
                    txpDataList.append(self.readTxp(bs, name))
                else:
                    txpDataList.append(None)
                cnt += 1
        self.loadTxp(magic, name, mipCount, depth, txpDataList[0][0], txpDataList[0][1], txpDataList[0][2], txpDataList, isYCbCr)

    def readTxpData(self, bs):
        width = bs.readUInt()
        height = bs.readUInt()
        texFormat = bs.readUInt()
        index = bs.readUInt()
        dataSize = bs.readUInt()
        texData = bs.readBytes(dataSize)
        return [width, height, texFormat, texData]

    def loadTxp(self, magic, name, mipCount, depth, width, height, texFormat, txpDataList, isYCbCr):
        texData = bytearray()
        if texFormat == 6:
            texFmt = noesis.NOESISTEX_DXT1
        elif texFormat == 8 or texFormat == 9:
            texFmt = noesis.NOESISTEX_DXT5
        else:
            texFmt = noesis.NOESISTEX_RGBA32
        self.texInfo.append(txpDataList[0])
        for i in range(depth):
            if i == 0:
                if isYCbCr:
                    if mipCount == 2:
                        texData += self.decodeFormat(txpDataList[i][3], width, height, texFormat, magic, texFmt, isYCbCr, txpDataList[i + 1], None)
                    elif mipCount == 3:
                        texData += self.decodeFormat(txpDataList[i][3], width, height, texFormat, magic, texFmt, isYCbCr, txpDataList[i + 1], txpDataList[i + 2])
                else:
                    texData += self.decodeFormat(txpDataList[i*mipCount][3], width, height, texFormat, magic, texFmt, isYCbCr, None, None)
            elif i == 4 and self.isOld:
                texData += self.decodeFormat(txpDataList[5*mipCount][3], width, height, texFormat, magic, texFmt, isYCbCr, None, None)
            elif i == 5 and self.isOld:
                texData += self.decodeFormat(txpDataList[4*mipCount][3], width, height, texFormat, magic, texFmt, isYCbCr, None, None)
            else:
                texData += self.decodeFormat(txpDataList[i*mipCount][3], width, height, texFormat, magic, texFmt, isYCbCr, None, None)
        if self.texDb != None:
            tex = NoeTexture(self.texDb.db[self.texDb.texHash[0]], width, height, texData, texFmt)
            self.texDb.texHash.pop(0)
        else:
            tex = NoeTexture(name, width, height, texData, texFmt)
        if magic == 0x05505854:
            tex.setFlags(noesis.NTEXFLAG_CUBEMAP)
        self.texList.append(tex)

    def decodeFormat(self, texData, width, height, texFormat, magic, texFmt, isYCbCr, txpDataList2, txpDataList3):
        if texFormat == 1:
            texData = rapi.imageDecodeRaw(texData, width, height, "r8g8b8")
        elif texFormat == 2:
            pass
        elif texFormat == 3:
            texData = rapi.imageDecodeRaw(texData, width, height, "r5g5b5")
        elif texFormat == 4:
            texData = rapi.imageDecodeRaw(texData, width, height, "r5g5b5a1")
        elif texFormat == 5:
            texData = rapi.imageDecodeRaw(texData, width, height, "r4g4b4")
        elif texFormat == 6:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT1)
        elif texFormat == 8:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT3)
        elif texFormat == 9:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT5)
        elif texFormat == 10:
            if not isYCbCr:
                texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC4)
            else:
                tex2Data = []
                texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC4, 0.0 , 1)
                mipData = rapi.imageDecodeDXT(txpDataList2[3], txpDataList2[0], txpDataList2[1], noesis.FOURCC_BC4, 0.0 , 1)
                mipData = rapi.imageResampleBox(mipData, txpDataList2[0], txpDataList2[1], width, height)
                mip2Data = rapi.imageDecodeDXT(txpDataList3[3], txpDataList3[0], txpDataList3[1], noesis.FOURCC_BC4, 0.0 , 1)
                mip2Data = rapi.imageResampleBox(mip2Data, txpDataList3[0], txpDataList3[1], width, height)
                lum = [texData[x:x+4] for x in range(0, len(texData),4)]
                cr = [mipData[x:x+4] for x in range(0, len(mipData),4)]
                cb = [mip2Data[x:x+4] for x in range(0, len(mip2Data),4)]
                for a in range(height):
                        off = width * a
                        for b in range(width):
                            vec3 = NoeVec3((lum[off + b][0] / 255.0, (cb[off + b][0] / 255.0) - 0.5, (cr[off + b][0] / 255.0) - 0.5))
                            mat44 = NoeMat44([NoeVec4((1.0, 1.0, 1.0, 0.0)), NoeVec4((0.0, -0.1873, 1.8556, 0.0)), NoeVec4((1.5748, -0.4681, 0.0, 0.0)), NoeVec4((0.0, 0.0, 0.0, 1.0))])
                            vec4 = vec3.toVec4()
                            rgb = mat44.transformVec4(vec4).toVec3()
                            tex2Data.append(int(max(0, min(1, rgb[0])) * 255))
                            tex2Data.append(int(max(0, min(1, rgb[1])) * 255))
                            tex2Data.append(int(max(0, min(1, rgb[2])) * 255))
                            tex2Data.append(lum[off + b][1])
                texData = bytearray(tex2Data)
        elif texFormat == 11:
            if not isYCbCr:
                texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC5)
            else:
                tex2Data = []
                texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC5, 0.0 , 1)
                mipData = rapi.imageDecodeDXT(txpDataList2[3], txpDataList2[0], txpDataList2[1], noesis.FOURCC_BC5, 0.0 , 1)
                mipData = rapi.imageResampleBox(mipData, txpDataList2[0], txpDataList2[1], width, height)
                lum = [texData[x:x+4] for x in range(0, len(texData),4)]
                cbr = [mipData[x:x+4] for x in range(0, len(mipData),4)]
                for a in range(height):
                        off = width * a
                        for b in range(width):
                            vec3 = NoeVec3((lum[off + b][0] / 255.0, (cbr[off + b][0] / 255.0) - 0.5, (cbr[off + b][1] / 255.0) - 0.5))
                            mat44 = NoeMat44([NoeVec4((1.0, 1.0, 1.0, 0.0)), NoeVec4((0.0, -0.1873, 1.8556, 0.0)), NoeVec4((1.5748, -0.4681, 0.0, 0.0)), NoeVec4((0.0, 0.0, 0.0, 1.0))])
                            vec4 = vec3.toVec4()
                            rgb = mat44.transformVec4(vec4).toVec3()
                            tex2Data.append(int(max(0, min(1, rgb[0])) * 255))
                            tex2Data.append(int(max(0, min(1, rgb[1])) * 255))
                            tex2Data.append(int(max(0, min(1, rgb[2])) * 255))
                            tex2Data.append(lum[off + b][1])
                texData = bytearray(tex2Data)
        elif texFormat == 103:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT1)
        elif texFormat == 104:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT1)
        elif texFormat == 109:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT5)
        elif texFormat == 112:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC4)
        elif texFormat == 115:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC5)
        elif texFormat == 130:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
        elif texFormat == 131:
            texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
        if magic == 0x04505854:
            texData = rapi.imageFlipRGBA32(texData, width, height, 0, 1)
        self.texRGBAData.append(texData)
        if texFormat == 6:
            texData = rapi.imageEncodeDXT(texData, 4, width, height, noesis.NOE_ENCODEDXT_BC1)
        elif texFormat == 8:
            texData = rapi.imageEncodeDXT(texData, 4, width, height, noesis.NOE_ENCODEDXT_BC3)
        elif texFormat == 9:
            texData = rapi.imageEncodeDXT(texData, 4, width, height, noesis.NOE_ENCODEDXT_BC3)
        return texData

class Txd:
    
    def __init__(self, texList):
        self.texList = texList
        
    def readTxd(self, bs, fileName, texDb):
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        bs.seek(dataOff, NOESEEK_ABS)
        data = bs.readBytes(dataSize)
        txp = Txp(self.texList, texDb, False)
        txp.readTxp(NoeBitStream(data), fileName)

class Txi:
    
    def __init__(self):
        self.texDb = None
        
    def readTxi(self, bs):
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        addressSpace = getAddressSpace(bs, fileSize, dataOff, dataSize)
        self.texDb = TexDb(addressSpace)
        if addressSpace == 32:
            bs.seek(dataOff, NOESEEK_ABS)
            if endian == 0x18000000:
                bs.setEndian(NOE_BIGENDIAN)
            self.texDb.readTexDb(bs)
        elif addressSpace == 64:
            bs.seek(dataOff, NOESEEK_ABS)
            ts = NoeBitStream(bs.readBytes(dataSize))
            if endian == 0x18000000:
                ts.setEndian(NOE_BIGENDIAN)
            self.texDb.readTexDb(ts)

class Sprite:
    
    def __init__(self, texList, fileName, sprDb, addressSpace):
        self.texList = texList
        self.fileName = fileName
        self.sprDb = sprDb
        self.addressSpace = addressSpace
        self.endian = 0
        
    def readSpr(self, bs, data, txpOff):
        magic = bs.readUInt()
        texOff = bs.readUInt()
        texCount = bs.readInt()
        spriteCount = bs.readInt()
        spriteOff = readOff(bs, self.addressSpace)
        texNameOff = readOff(bs, self.addressSpace)
        spriteNameOff = readOff(bs, self.addressSpace)
        spriteModeOff = readOff(bs, self.addressSpace)
        txp = Txp([], None, False)
        if txpOff == None:
            txp.readTxp(NoeBitStream(data[texOff:], self.endian), self.fileName)
        else:
            txp.readTxp(NoeBitStream(data[txpOff:], self.endian), self.fileName)
        bs.seek(spriteOff, NOESEEK_ABS)
        for i in range(spriteCount):
            tex = self.readSprInfo(bs, txp.texInfo, txp.texRGBAData)
            tex.name = self.sprDb[self.fileName][i]
            self.texList.append(tex)

    def readSprInfo(self, bs, texInfo, texRGBAData):
        index = bs.readUInt()
        unk = bs.readUInt()
        normX = bs.readFloat()
        normY = bs.readFloat()
        normWidth = bs.readFloat()
        normHeight = bs.readFloat()
        x = bs.readFloat()
        y = bs.readFloat()
        width = bs.readFloat()
        height = bs.readFloat()
        tex = self.loadSpr(int(x), int(y), int(width), int(height), texInfo[index], texRGBAData[index])
        return tex

    def loadSpr(self, x, y, width, height, texInfo, texRGBAData):
        if width != texInfo[0] or height != texInfo[1]:
            rgbaData = list(texRGBAData)
            if height != texInfo[1]:
                rgbaData = rgbaData[y*texInfo[0]*4:(y+height)*texInfo[0]*4]
            if width != texInfo[0]:
                rgbaData = [rgbaData[x:x+(texInfo[0]*4)] for x in range(0, len(rgbaData),texInfo[0]*4)]
                texData = []
                for i in range(height):
                    texData.extend(rgbaData[i][x*4:(x+width)*4])
                texData = bytearray(texData)
            else:
                texData = bytearray(rgbaData)
        else:
            texData = texRGBAData
        tex = NoeTexture(self.fileName, width, height, texData, noesis.NOESISTEX_RGBA32)
        return tex

class Spr:
    
    def __init__(self, texList):
        self.texList = texList
        
    def readSpr(self, data, fileName, sprDb):
        bs = NoeBitStream(data)
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        addressSpace = getAddressSpace(bs, fileSize, dataOff, dataSize)
        sprite = Sprite(self.texList, fileName + ".spr", sprDb, addressSpace)
        if addressSpace == 32:
            bs.seek(dataOff, NOESEEK_ABS)
            if endian == 0x18000000:
                bs.setEndian(NOE_BIGENDIAN)
                sprite.endian = 1
            sprite.readSpr(bs, data, dataOff + fileSize + dataOff)
        elif addressSpace == 64:
            bs.seek(dataOff, NOESEEK_ABS)
            ts = NoeBitStream(bs.readBytes(dataSize))
            if endian == 0x18000000:
                ts.setEndian(NOE_BIGENDIAN)
                sprite.endian = 1
            sprite.readSpr(ts, data[dataOff:], fileSize + dataOff)

class Spi:
    
    def __init__(self):
        self.SprDb = None
        
    def readSpi(self, bs):
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        addressSpace = getAddressSpace(bs, fileSize, dataOff, dataSize)
        self.sprDb = SprDb(addressSpace)
        if addressSpace == 32:
            bs.seek(dataOff, NOESEEK_ABS)
            if endian == 0x18000000:
                bs.setEndian(NOE_BIGENDIAN)
            self.sprDb.readSprDb(bs)
        elif addressSpace == 64:
            bs.seek(dataOff, NOESEEK_ABS)
            ts = NoeBitStream(bs.readBytes(dataSize))
            if endian == 0x18000000:
                ts.setEndian(NOE_BIGENDIAN)
            self.sprDb.readSprDb(ts)

class Ibl:
    
    def __init__(self, fileName, texList):
        self.fileName = fileName
        self.texList = texList
        
    def readIbl(self, bs):
        lightMaps = []
        while True:
                header = bs.readline().rstrip("\n")
                if header == "VERSION":
                    version = bs.readline().rstrip("\n")
                elif header == "LIT_DIR":
                    index = bs.readline()
                    direction = bs.readline().rstrip("\n")
                elif header == "LIT_COL":
                    index = bs.readline().rstrip("\n")
                    colour = bs.readline().rstrip("\n")
                elif header == "DIFF_COEF":
                    index = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                    mat = bs.readline().rstrip("\n")
                elif header == "LIGHT_MAP":
                    index = bs.readline().rstrip("\n")
                    dataType = bs.readline().rstrip("\n")
                    dimensions = bs.readline().rstrip("\n")
                    lightMaps.append([dataType, dimensions])
                elif header == "BINARY":
                    break
        for i in range(len(lightMaps)):
                if lightMaps[i][0] != "RGBA16F_CUBE":
                    print("Unknown texture type " + lightMaps[i][0])
                    return 0
                width = int(lightMaps[i][1].split(" ")[0])
                height = int(lightMaps[i][1].split(" ")[1])
                texData = bs.readBytes(width * height * 8 * 6)
                texData = rapi.imageDecodeRaw(texData, width * 6, height * 6, "r#f16g#f16b#f16a#f16")
                texFmt = noesis.NOESISTEX_RGBA32
                if len(lightMaps) == 1:
                    tex = NoeTexture(self.fileName, width, height, texData, texFmt)
                else:
                    tex = NoeTexture(self.fileName + "_" + str(i), width, height, texData, texFmt)
                tex.setFlags(noesis.NTEXFLAG_CUBEMAP)
                self.texList.append(tex)

class Emcs:
    
    def __init__(self, fileName, texList):
        self.fileName = fileName
        self.texList = texList
        
    def readEmcs(self, bs):
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        emshOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        emshSize = bs.readUInt()
        bs.seek(emshOff, NOESEEK_ABS)
        data = bs.readBytes(emshSize)
        self.readEmsh(data)

    def readEmsh(self, data):
        bs = NoeBitStream(data)
        magic = bs.readBytes(4).decode("ASCII")
        unk1 = bs.read("6f")
        unk2 = bs.readUInt()
        texCount = bs.readInt()
        emciOff = bs.readUInt()
        txpInfoOff = bs.readUInt()
        txpOff = bs.readUInt()
        txpInfo = []
        bs.seek(txpInfoOff, NOESEEK_ABS)
        for i in range(texCount):
            txpInfo.append(bs.readUInt())
        self.loadEmcs(data, texCount, txpInfo, txpOff)

    def loadEmcs(self, data, texCount, txpInfo, txpOff):
        for i in range(texCount):
            txp = Txp(self.texList, None, True)
            txp.readTxp(NoeBitStream(data[txpOff + txpInfo[i]:]), self.fileName)

class Motion:
    
    def __init__(self, motDb, boneData, boneList, boneDict):
        self.motDb = motDb
        self.boneData = boneData
        self.boneList = boneList
        self.boneDict = boneDict
        self.animList = []
        self.names = []
        self.frameCounts = []
        self.endian = 0
        self.addressSpace = 32
        
    def readMotion(self, bs, fileName):
        for name in self.motDb.db[fileName].name:
            infoOff = bs.readUInt()
            mapOff = bs.readUInt()
            frameOff = bs.readUInt()
            boneNamesOff = bs.readUInt()
            pos = bs.tell()
            bs.seek(infoOff, NOESEEK_ABS)
            mapSize, frameCount = self.readInfo(bs)
            self.names.append(name)
            self.frameCounts.append(frameCount)
            bs.seek(mapOff, NOESEEK_ABS)
            animMap = self.readMap(bs, mapSize)
            bs.seek(boneNamesOff, NOESEEK_ABS)
            boneNames = self.readBoneNames(bs, int(len(animMap) / 3) - 1)
            bs.seek(frameOff, NOESEEK_ABS)
            self.readAnim(bs, name, frameCount, animMap, boneNames)
            bs.seek(pos, NOESEEK_ABS)

    def readMotionMot(self, bs, fileName, fileDir):
        id = bs.readUInt64()
        name = getOffString(bs, readOff(bs, self.addressSpace))
        infoOff = readOff(bs, self.addressSpace)
        mapOff = readOff(bs, self.addressSpace)
        frameOff = readOff(bs, self.addressSpace)
        boneNamesOff = readOff(bs, self.addressSpace)
        boneIdOff = readOff(bs, self.addressSpace)
        boneCount = bs.readUInt()
        divFrameCount = bs.readUShort()
        divFileCount = bs.readUByte()
        bs.seek(infoOff, NOESEEK_ABS)
        mapSize, frameCount = self.readInfo(bs)
        self.names.append(name)
        self.frameCounts.append(frameCount)
        bs.seek(mapOff, NOESEEK_ABS)
        animMap = self.readMap(bs, mapSize)
        boneNames = getOffStringList(bs, self.addressSpace, boneNamesOff, boneCount)
        bs.seek(frameOff, NOESEEK_ABS)
        divData = [bs]
        for i in range(1, divFileCount):
            div = rapi.loadIntoByteArray(fileDir + fileName + "_div_" + str(i) + ".mot")
            if self.addressSpace == 32:
                ds = NoeBitStream(div)
            elif self.addressSpace == 64:
                ds = NoeBitStream(div)
                ds.seek(0x08, NOESEEK_ABS)
                dataOff = ds.readUInt()
                ds = NoeBitStream(div[dataOff:])
            ds.seek(frameOff, NOESEEK_ABS)
            if self.endian:
                ds.setEndian(NOE_BIGENDIAN)
            divData.append(ds)
        if self.boneData.game == 'MGF':
            self.readAnimMotMgf(name, frameCount, animMap, boneNames, divData)
        else:
            self.readAnimMot(name, frameCount, animMap, boneNames, divData)

    def readInfo(self, bs):
        mapSize = bs.readUShort() & 0x3FFF
        frameCount = bs.readUShort()
        return mapSize, frameCount

    def readMap(self, bs, mapSize):
        animMap = []
        mapByteSize = int(math.ceil(mapSize / 8))
        for i in range(mapByteSize):
            mapSet = bin(bs.readUShort())[2:].zfill(16)
            animMap.append(int(mapSet[14:], 2))
            animMap.append(int(mapSet[12:14], 2))
            animMap.append(int(mapSet[10:12], 2))
            animMap.append(int(mapSet[8:10], 2))
            animMap.append(int(mapSet[6:8], 2))
            animMap.append(int(mapSet[4:6], 2))
            animMap.append(int(mapSet[2:4], 2))
            animMap.append(int(mapSet[:2], 2))
        return animMap[:mapSize]

    def readBoneNames(self, bs, boneCount):
        boneNames = []
        for i in range(boneCount):
            boneNames.append(self.motDb.boneNames[bs.readUShort()])
        return boneNames
    
    def readAnim(self, bs, name, frameCount, animMap, boneNames):
        kfBones = []
        cnt = 0
        for boneName in boneNames:
            if animMap[cnt] == 0x00 and animMap[cnt+1] == 0x00 and animMap[cnt+2] == 0x00:
                cnt += 3
                if boneName in self.boneData.type and self.boneData.type[boneName] == 0x03:
                    cnt += 3
                continue
            xKeyFrames = self.readKeyFrames(bs, animMap[cnt])
            cnt += 1
            yKeyFrames = self.readKeyFrames(bs, animMap[cnt])
            cnt += 1
            zKeyFrames = self.readKeyFrames(bs, animMap[cnt])
            cnt += 1
            if boneName in self.boneData.type and self.boneData.type[boneName] == 0x03:
                cnt += 3
            # if name == 'MIK_KUCHI_A':
            #     print("'"+ boneName +"': NoeVec3(("+str(xKeyFrames.keys[0])+', '+str(yKeyFrames.keys[0])+', '+str(zKeyFrames.keys[0])+')), ')
            boneKey = self.buildAnim(frameCount, boneName, xKeyFrames, yKeyFrames, zKeyFrames)
            kfBones.append(boneKey)
        self.animList.append(NoeKeyFramedAnim(name, self.boneList, kfBones, 1.0))

    def readAnimMot(self, name, frameCount, animMap, boneNames, divData):
        kfBones = []
        cnt = 0
        for boneName in boneNames:
            if animMap[cnt] == 0x00 and animMap[cnt+1] == 0x00 and animMap[cnt+2] == 0x00:
                cnt += 3
                if boneName in self.boneData.type and self.boneData.type[boneName] == 0x03:
                    cnt += 3
                continue
            xKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
            cnt += 1
            yKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
            cnt += 1
            zKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
            cnt += 1
            if boneName in self.boneData.type and self.boneData.type[boneName] == 0x03:
                cnt += 3
            boneKey = self.buildAnim(frameCount, boneName, xKeyFrames, yKeyFrames, zKeyFrames)
            kfBones.append(boneKey)
        self.animList.append(NoeKeyFramedAnim(name, self.boneList, kfBones, 1.0))

    def readAnimMotMgf(self, name, frameCount, animMap, boneNames, divData):
        kfBones = []
        cnt = 0
        for boneName in boneNames:
            if animMap[cnt] == 0x00 and animMap[cnt+1] == 0x00 and animMap[cnt+2] == 0x00 and animMap[cnt+3] == 0x00 and animMap[cnt+4] == 0x00 and animMap[cnt+5] == 0x00:
                if boneName in self.boneData.type and self.boneData.type[boneName] == 0x00:
                    if animMap[cnt+6] == 0x00 and animMap[cnt+7] == 0x00 and animMap[cnt+8]:
                        cnt += 9
                        continue
                else:
                    cnt += 6
                    continue
            xTranKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
            cnt += 1
            yTranKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
            cnt += 1
            zTranKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
            cnt += 1
            xRotKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
            cnt += 1
            yRotKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
            cnt += 1
            zRotKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
            cnt += 1
            if xRotKeyFrames.keys[0] != 0.0 or yRotKeyFrames.keys[0] != 0.0 or zRotKeyFrames.keys[0] != 0.0:
                print("'"+ boneName +"': NoeVec3(("+str(xRotKeyFrames.keys[0])+', '+str(yRotKeyFrames.keys[0])+', '+str(zRotKeyFrames.keys[0])+')), ')
            if boneName in self.boneData.type and self.boneData.type[boneName] == 0x00:
                xSclKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
                cnt += 1
                ySclKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
                cnt += 1
                zSclKeyFrames = self.readKeyFramesMot(divData, animMap[cnt])
                cnt += 1
                boneKey = self.buildAnimMotMgf(frameCount, boneName, xTranKeyFrames, yTranKeyFrames, zTranKeyFrames, xRotKeyFrames, yRotKeyFrames, zRotKeyFrames, xSclKeyFrames, ySclKeyFrames, zSclKeyFrames)
            else:
                boneKey = self.buildAnimMotMgf(frameCount, boneName, xTranKeyFrames, yTranKeyFrames, zTranKeyFrames, xRotKeyFrames, yRotKeyFrames, zRotKeyFrames)
            kfBones.append(boneKey)
        self.animList.append(NoeKeyFramedAnim(name, self.boneList, kfBones, 1.0))

    def readKeyFrames(self, bs, keyType):
        keyFrames = KeyFrames(keyType)
        if keyFrames.keyType == 0x00:
            keyFrames.keys.append(0.0)
            keyFrames.frameList.append(0)
        elif keyFrames.keyType == 0x01:
            keyFrames.keys.append(bs.readFloat())
            keyFrames.frameList.append(0)
        elif keyFrames.keyType == 0x02:
            frameCount = bs.readUShort()
            for i in range(frameCount):
                keyFrames.frameList.append(bs.readUShort())
            padding(bs, 0x04)
            for i in range(frameCount):
                keyFrames.keys.append(bs.readFloat())
                keyFrames.tangents.append(0.0)
        elif keyFrames.keyType == 0x03:
            frameCount = bs.readUShort()
            for i in range(frameCount):
                keyFrames.frameList.append(bs.readUShort())
            padding(bs, 0x04)
            for i in range(frameCount):
                keyFrames.keys.append(bs.readFloat())
                keyFrames.tangents.append(bs.readFloat())
        return keyFrames

    def readKeyFramesMot(self, divData, keyType):
        keyFrames = KeyFrames(keyType)
        prevFrameList = []
        for bs in divData:
            if keyFrames.keyType == 0x00 and not keyFrames.frameList:
                keyFrames.keys.append(0.0)
                keyFrames.frameList.append(0)
            elif keyFrames.keyType == 0x01:
                if keyFrames.frameList:
                    bs.readFloat()
                else:
                    keyFrames.keys.append(bs.readFloat())
                    keyFrames.frameList.append(0)
            elif keyFrames.keyType == 0x02:
                frameCount = bs.readUShort()
                dataType = bs.readUShort()
                keys = []
                frameList = []
                if dataType == 0x00:
                    for i in range(frameCount):
                        keys.append(bs.readFloat())
                elif dataType == 0x01:
                    for i in range(frameCount):
                        keys.append(bs.readHalfFloat())
                    padding(bs, 0x04)
                tmpList = []
                for i in range(frameCount):
                    frame = bs.readUShort()
                    if frame not in prevFrameList:
                        frameList.append(frame)
                        tmpList.append(frame)
                        keyFrames.frameList.append(frame)
                        keyFrames.keys.append(keys[i])
                        keyFrames.tangents.append(0.0)
                prevFrameList.extend(tmpList)
                padding(bs, 0x04)
            elif keyFrames.keyType == 0x03:
                frameCount = bs.readUShort()
                dataType = bs.readUShort()
                keys = []
                tangents = []
                frameList = []
                for i in range(frameCount):
                    tangents.append(bs.readFloat())
                if dataType == 0x00:
                    for i in range(frameCount):
                        keys.append(bs.readFloat())
                elif dataType == 0x01:
                    for i in range(frameCount):
                        keys.append(bs.readHalfFloat())
                    padding(bs, 0x04)
                tmpList = []
                for i in range(frameCount):
                    frame = bs.readUShort()
                    if frame not in prevFrameList:
                        frameList.append(frame)
                        tmpList.append(frame)
                        keyFrames.frameList.append(frame)
                        keyFrames.keys.append(keys[i])
                        keyFrames.tangents.append(tangents[i])
                prevFrameList.extend(tmpList)
                padding(bs, 0x04)
        return keyFrames

    def buildAnim(self, frameCount, boneName, xKeyFrames, yKeyFrames, zKeyFrames):
        boneKey = NoeKeyFramedBone(self.boneDict[boneName])
        if boneName in self.boneData.type:
            if self.boneData.type[boneName] & 0x02:
                if self.boneData.type[boneName] & 0x04:
                    keys = self.loadRotKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, boneName, 1)
                    boneKey.setRotation(keys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
                else:
                    keys = self.loadKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, 1)
                    boneKey.setTranslation(keys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
            else:
                keys = self.loadRotKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, boneName, 1)
                boneKey.setRotation(keys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
        elif boneName.endswith("_cp") or boneName == "gblctr":
            keys = self.loadKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, 1)
            boneKey.setTranslation(keys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
        else:
            keys = self.loadRotKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, boneName, 1)
            boneKey.setRotation(keys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
        return boneKey

    def buildAnimMotMgf(self, frameCount, boneName, xTranKeyFrames, yTranKeyFrames, zTranKeyFrames, xRotKeyFrames, yRotKeyFrames, zRotKeyFrames, xSclKeyFrames = None, ySclKeyFrames = None, zSclKeyFrames = None):
        boneKey = NoeKeyFramedBone(self.boneDict[boneName])
        keys = self.loadKeys(frameCount,  xTranKeyFrames, yTranKeyFrames, zTranKeyFrames, 4)
        boneKey.setTranslation(keys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
        keys = self.loadRotKeys(frameCount, xRotKeyFrames, yRotKeyFrames, zRotKeyFrames, boneName, 4)
        boneKey.setRotation(keys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
        if self.boneData.type[boneName] == 0x00:
            keys = self.loadKeys(frameCount, xSclKeyFrames, ySclKeyFrames, zSclKeyFrames, 4)
            boneKey.setScale(keys, noesis.NOEKF_SCALE_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
        return boneKey

    def loadKeys(self, frameCount, xKeyFrames, yKeyFrames, zKeyFrames, interpType):
        keys = []
        if xKeyFrames.keyType <= 0x01 and yKeyFrames.keyType <= 0x01 and zKeyFrames.keyType <= 0x01:
            keys.append(NoeKeyFramedValue(0, NoeVec3((xKeyFrames.keys[0], yKeyFrames.keys[0], zKeyFrames.keys[0]))))
        else:
            xKey = interpolate(frameCount, xKeyFrames, interpType)
            yKey = interpolate(frameCount, yKeyFrames, interpType)
            zKey = interpolate(frameCount, zKeyFrames, interpType)
            keys = cleanupKeys(frameCount, xKey, yKey, zKey)
        return keys

    def loadRotKeys(self, frameCount, xKeyFrames, yKeyFrames, zKeyFrames, boneName, interpType):
        keys = []
        if xKeyFrames.keyType <= 0x01 and yKeyFrames.keyType <= 0x01 and zKeyFrames.keyType <= 0x01:
            keys.append(NoeKeyFramedValue(0, NoeAngles([xKeyFrames.keys[0]*noesis.g_flRadToDeg, yKeyFrames.keys[0]*noesis.g_flRadToDeg, zKeyFrames.keys[0]*noesis.g_flRadToDeg]).toMat43_XYZ().toQuat()))
        else:
            xKey = interpolate(frameCount, xKeyFrames, interpType)
            yKey = interpolate(frameCount, yKeyFrames, interpType)
            zKey = interpolate(frameCount, zKeyFrames, interpType)
            keys = cleanupRotKeys(frameCount, xKey, yKey, zKey)
        return keys

class Motc:

    def __init__(self):
        self.animList = []
        self.names = []
        self.frameCounts = []

    def readMotc(self, data, boneData, boneList, boneDict, fileName, fileDir):
        bs = NoeBitStream(data)
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        addressSpace = getAddressSpace(bs, fileSize, dataOff, dataSize)
        motion = Motion(None, boneData, boneList, boneDict)
        if addressSpace == 32:
            bs.seek(dataOff, NOESEEK_ABS)
            if endian == 0x18000000:
                bs.setEndian(NOE_BIGENDIAN)
                motion.endian = 1
            motion.readMotionMot(bs, fileName, fileDir)
        elif addressSpace == 64:
            bs.seek(dataOff, NOESEEK_ABS)
            ts = NoeBitStream(bs.readBytes(dataSize))
            if endian == 0x18000000:
                ts.setEndian(NOE_BIGENDIAN)
                motion.endian = 1
            motion.addressSpace = 64
            motion.readMotionMot(ts, fileName, fileDir)
        self.animList = motion.animList
        self.names = motion.names
        self.frameCounts = motion.frameCounts

class KeyFrames:
    def __init__(self, keyType):
        self.keyType = keyType
        self.keys = []
        self.tangents = []
        self.tangents2 = []
        self.frameList = []
        self.interpType = 0
        self.epTypePre = 0
        self.epTypePost = 0

class Dsc: 
    
    def __init__(self):
        self.commands = []
        self.frame = 0
        self.performers = []
        self.morphs = []
        self.close = False
        
    def readDsc(self, bs, game, robTbl, motDb):
        if game == "DT":
            self.initDT()
        elif game == "DT2" or game == "DTE":
            self.initDT2Ex()
        elif game == "F":
            self.initF()
        elif game == "F2":
            self.initF2()
        elif game == "X":
            self.initX()
        elif game == "AC":
            self.initAC()
        elif game == "ACFT" or game == "FT" or game == "MM":
            self.initFT()
        mouthMorphs = []
        expMorphs = []
        eyeBlend = 1.0
        if game != "DT":
            version = bs.readUInt()
        while True:
            idx = bs.readInt()
            opcode = self.opcodes[idx]
            if opcode == "END":
                break
            elif opcode == "TIME":
                self.time(bs)
            elif opcode == "MIKU_DISP":
                self.mikuDisp(bs, game, mouthMorphs, expMorphs)
            elif opcode == "EYE_ANIM":
                self.eyeAnim(bs, game, motDb, expMorphs, eyeBlend)
            elif opcode == "MOUTH_ANIM":
                self.mouthAnim(bs, game, robTbl, motDb, mouthMorphs)
            elif opcode == "HAND_ANIM":
                self.handAnim(bs, game, robTbl, motDb)
            elif opcode == "LOOK_ANIM":
                self.lookAnim(bs, game, robTbl, motDb)
            elif opcode == "EXPRESSION":
                self.expression(bs, game, robTbl, motDb, expMorphs)
            elif opcode == "HAND_SCALE":
                self.handScale(bs)
            else:
                bs.seek(self.dataLength[idx] * 0x04, NOESEEK_REL)
        for i in range(len(self.performers)):
            self.morphs[i].extend(mouthMorphs[i])
            self.morphs[i].extend(expMorphs[i])

    def time(self, bs):
        time = bs.readInt() * 0.00001
        self.frame = int(round(time * 60))
        if debug:
            print("Frame: " + str(self.frame))

    def mikuDisp(self, bs, game, mouthMorphs, expMorphs):
        if game == "DT":
            performer = 0
        else:
            performer = bs.readInt()
        disp = bs.readInt()
        if performer + 1 > len(self.performers):
            if game == "DT" or game == "DT2" or game == "DTE" or game == "AC":
                performer = noesis.userPrompt(noesis.NOEUSERVAL_STRING, "Choose Performer " + str(performer + 1) + ".", "MIK, RIN, LEN, LUK, NER, HAK, KAI, MEI, SAK", "MIK", isPerformerOld)
                if performer == None:
                    return 1
                else:
                    performer = performer.upper()
            else:
                performer = noesis.userPrompt(noesis.NOEUSERVAL_STRING, "Choose Performer " + str(performer + 1) + ".", "MIK, RIN, LEN, LUK, NER, HAK, KAI, MEI, SAK, TET", "MIK", isPerformer)
                if performer == None:
                    return 1
                else:
                    performer = performer.upper()
            self.performers.append(performer)
            self.morphs.append([])
            mouthMorphs.append([])
            expMorphs.append([])
            
    def eyeAnim(self, bs, game, motDb, expMorphs, eyeBlend):
        if game == "DT":
            performer = 0
        else:
            performer = bs.readInt()
        state = bs.readInt()
        frameCount = bs.readInt()
        if frameCount == -1:
            frameCount = 6.0
        else:
            frameCount *= 0.001 * 60
            if frameCount < 0.0:
                frameCount = 6.0
        if performer > len(self.performers) - 1:
            return
        if len(expMorphs[performer]) != 0:
            pMorph = expMorphs[performer][-1]
        else:
            pMorph = Morph(0, "RESET", 1.0)
        if state == 0x01 and not self.close:
            if self.performers[performer] + "_FACE_" + pMorph.name + "_CL" in motDb.motDict.values():
                self.close = True
                name = pMorph.name + "_CL"
                eyeBlend = pMorph.blend
                keyMorph(self.frame, expMorphs[performer], name, int(frameCount), 1.0)
            elif pMorph.name == "RESET":
                self.close = True
                name = "CLOSE"
                eyeBlend = pMorph.blend
                keyMorph(self.frame, expMorphs[performer], name, int(frameCount), 1.0)
            elif pMorph.name == "RESET_OLD":
                self.close = True
                name = "CLOSE_OLD"
                eyeBlend = pMorph.blend
                keyMorph(self.frame, expMorphs[performer], name, int(frameCount), 1.0)
        elif self.close:
            self.close = False
            if pMorph.name == "CLOSE":
                name = "RESET"
                keyMorph(self.frame, expMorphs[performer], name, int(frameCount), eyeBlend)
            elif pMorph.name == "CLOSE_OLD":
                name = "RESET_OLD"
                keyMorph(self.frame, expMorphs[performer], name, int(frameCount), eyeBlend)
            elif pMorph.name.endswith("_CL"):
                name = pMorph.name[:-3]
                keyMorph(self.frame, expMorphs[performer], name, int(frameCount), eyeBlend)
        if debug:
            if state == 0x01:
                print(self.performers[performer] + " Eye Close, Frame count: " + str(frameCount))
            else:
                print(self.performers[performer] + " Eye Open, Frame count: " + str(frameCount))

    def mouthAnim(self, bs, game, robTbl, motDb, mouthMorphs):
        if game == "DT":
            performer = 0
        else:
            performer = bs.readInt()
            unk = bs.readInt()
        idx = bs.readInt()
        frameCount = bs.readInt()
        if frameCount == -1:
            frameCount = 6.0
        else:
            frameCount *= 0.001 * 60
            if frameCount < 0.0:
                frameCount = 6.0
        blend = bs.readInt()
        if blend == -1:
            blend = 1.0
        else:
            blend *= 0.001
            if blend < 0.0 or blend > 1.0:
                blend = 1.0
        if performer > len(self.performers) - 1:
            return
        animId = robTbl.db[self.performers[performer]][self.mouth[idx]]
        if animId == -1:
            name = "NULL"
        else:
            name = motDb.motDict[animId][10:]
        keyMorph(self.frame, mouthMorphs[performer], "M_" + name, int(frameCount), blend)
        if debug:
            print(name + ", Frame count: " + str(frameCount) + ", Blend: " + str(blend))
    
    def handAnim(self, bs, game, robTbl, motDb):
        if game == "DT":
            performer = 0
        else:
            performer = bs.readInt()
        hand = bs.readInt()
        idx = bs.readInt()
        frameCount = bs.readInt()
        if frameCount == -1:
            frameCount = 0.0
        else:
            frameCount *= 0.001 * 60
            if frameCount < 0.0:
                frameCount = 0.0
        blend = bs.readInt()
        if blend == -1:
            blend = 1.0
        else:
            blend *= 0.001
            if blend < 0.0 or blend > 1.0:
                blend = 1.0
        if performer > len(self.performers) - 1:
            return
        animId = robTbl.db[self.performers[performer]][self.hand[idx]]
        if animId == -1:
            name = "NULL"
        else:
            name = motDb.motDict[animId]
        if debug:
            if hand == 0x00:
                print(self.performers[performer] + " " + name + " (Left), Frame count: " + str(frameCount) + ", Blend: " + str(blend))
            elif hand == 0x01:
                print(self.performers[performer] + " " + name + " (Right), Frame count: " + str(frameCount) + ", Blend: " + str(blend))

    def lookAnim(self, bs, game, robTbl, motDb):
        if game == "DT":
            performer = 0
        else:
            performer = bs.readInt()
        idx = bs.readInt()
        frameCount = bs.readInt()
        if frameCount == -1:
            frameCount = 6.0
        else:
            frameCount *= 0.001 * 60
            if frameCount < 0.0:
                frameCount = 6.0
        blend = bs.readInt()
        if blend == -1:
            blend = 1.0
        else:
            blend *= 0.001
            if blend < 0.0 or blend > 1.0:
                blend = 1.0
        if performer > len(self.performers) - 1:
            return
        animId = robTbl.db[self.performers[performer]][self.look[idx]]
        if animId == -1:
            name = "NULL"
        else:
            name = motDb.motDict[animId]
        if debug:
            print(name + ", Frame count: " + str(frameCount) + ", Blend: " + str(blend))

    def expression(self, bs, game, robTbl, motDb, expMorphs):
        if game == "DT":
            performer = 0
        else:
            performer = bs.readInt()
        idx = bs.readInt()
        frameCount = bs.readInt()
        if frameCount == -1:
            frameCount = 0.0
        else:
            frameCount *= 0.001 * 60
            if frameCount < 0.0:
                frameCount = 0.0
        blend = bs.readInt()
        if blend == -1:
            blend = 1.0
        else:
            blend *= 0.001
            if blend < 0.0 or blend > 1.0:
                blend = 1.0
        if performer > len(self.performers) - 1:
            return
        animId = robTbl.db[self.performers[performer]][self.exp[idx]]
        if animId == -1:
            name = "NULL"
        else:
            name = motDb.motDict[animId][9:]
        if self.close:
            self.close = False
        keyMorph(self.frame, expMorphs[performer], name, int(frameCount), blend)
        if debug:
            print(name + ", Frame count: " + str(frameCount) + ", Blend: " + str(blend))

    def handScale(self, bs):
        performer = bs.readInt()
        hand = bs.readInt()
        scale = bs.readInt() * 0.001
        if debug:
            if hand == 0x00:
                print(self.performers[performer] + " Hand scale (Left), Scale: " + str(scale))
            elif hand == 0x01:
                print(self.performers[performer] + " Hand scale (Right), Scale: " + str(scale))

    def initDT(self):
        self.opcodes = ["END", "TIME", "MIKU_MOVE", "MIKU_ROT", "MIKU_DISP", "MIKU_SHADOW", "TARGET", "SET_MOTION", "SET_PLAYDATA", "EFFECT", "FADEIN_FIELD", "EFFECT_OFF", "SET_CAMERA", "DATA_CAMERA", "CHANGE_FIELD",
        "HIDE_FIELD", "MOVE_FIELD", "FADEOUT_FIELD", "EYE_ANIM", "MOUTH_ANIM", "HAND_ANIM", "LOOK_ANIM", "EXPRESSION", "LOOK_CAMERA", "LYRIC", "MUSIC_PLAY", "MODE_SELECT", "EDIT_MOTION", "BAR_TIME_SET",
        "SHADOWHEIGHT", "EDIT_FACE", "MOVE_CAMERA", "PV_END", "SHADOWPOS", "NEAR_CLIP", "CLOTH_WET"]
        self.dataLength = [0, 1, 3, 1, 1, 1, 7, 3, 1, 5, 2, 1, 6, 2, 1, 1, 3, 2, 2, 3, 4, 3, 3, 4, 1, 0, 1, 2, 2, 1, 2, 19, 0, 2, 2, 1]
        self.mouth = [0x31, 0x34, 0x35, 0x37, 0x36, 0x38, 0x30, 0x32, 0x33]
        self.hand = [0x3C, 0x3D, 0x3B, 0x3E, 0x42, 0x3F, 0x40, 0x3A, 0x41, 0x43, 0x44]
        self.look = [0x27, 0x28, 0x2A, 0x29, 0x2C, 0x2B, 0x2E, 0x2D, 0x26]
        self.exp = [0x08, 0x09, 0x14, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x07, 0x15]

    def initDT2Ex(self):
        self.opcodes = ["END", "TIME", "MIKU_MOVE", "MIKU_ROT", "MIKU_DISP", "MIKU_SHADOW", "TARGET", "SET_MOTION", "SET_PLAYDATA", "EFFECT", "FADEIN_FIELD", "EFFECT_OFF", "SET_CAMERA", "DATA_CAMERA", "CHANGE_FIELD",
        "HIDE_FIELD", "MOVE_FIELD", "FADEOUT_FIELD", "EYE_ANIM", "MOUTH_ANIM", "HAND_ANIM", "LOOK_ANIM", "EXPRESSION", "LOOK_CAMERA", "LYRIC", "MUSIC_PLAY", "MODE_SELECT", "EDIT_MOTION", "BAR_TIME_SET",
        "SHADOWHEIGHT", "EDIT_FACE", "MOVE_CAMERA", "PV_END", "SHADOWPOS", "EDIT_LYRIC", "EDIT_TARGET", "EDIT_MOUTH", "SET_CHARA", "EDIT_MOVE", "EDIT_SHADOW", "EDIT_EYELID", "EDIT_EYE", "EDIT_ITEM", "EDIT_EFFECT",
        "EDIT_DISP", "EDIT_HAND_ANIM", "AIM", "HAND_ITEM", "EDIT_BLUSH", "NEAR_CLIP", "CLOTH_WET", "LIGHT_ROT", "SCENE_FADE", "TONE_TRANS", "SATURATE", "FADE_MODE", "AUTO_BLINK", "PARTS_DISP", "TARGET_FLYING_TIME",
        "CHARA_SIZE", "CHARA_HEIGHT_ADJUST", "ITEM_ANIM", "CHARA_POS_ADJUST", "SCENE_ROT"]
        self.dataLength = [0, 1, 4, 2, 2, 2, 7, 4, 2, 6, 2, 1, 6, 2, 1, 1, 3, 2, 3, 5, 5, 4, 4, 5, 2, 0, 2, 4, 2, 2, 1, 21, 0, 3, 2, 5, 1, 1, 7, 1, 1, 2, 1, 2, 1, 2, 3, 3, 1, 2, 2, 3, 6, 6, 1, 1, 2, 3, 1, 2, 2, 4,
        4, 1]
        self.mouth = [0x31, 0x34, 0x35, 0x37, 0x36, 0x38, 0x5D, 0x5E, 0x30, 0x2F, 0x32, 0x33]
        self.hand = [0x3C, 0x3D, 0x3B, 0x3E, 0x42, 0x3F, 0x40, 0x5F, 0x60, 0x39, 0x41, 0x61, 0x43, 0x44, 0x3A]
        self.look = [0x27, 0x28, 0x2A, 0x29, 0x2C, 0x2B, 0x2E, 0x2D, 0x26, 0x25, 0x67]
        self.exp = [0x08, 0x09, 0x14, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x4F, 0x07, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x07, 0x15, 0x06, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B, 0x4C,
        0x4D, 0x4E]

    def initF(self):
        self.opcodes = ["END", "TIME", "MIKU_MOVE", "MIKU_ROT", "MIKU_DISP", "MIKU_SHADOW", "TARGET", "SET_MOTION", "SET_PLAYDATA", "EFFECT", "FADEIN_FIELD", "EFFECT_OFF", "SET_CAMERA", "DATA_CAMERA", "CHANGE_FIELD",
        "HIDE_FIELD", "MOVE_FIELD", "FADEOUT_FIELD", "EYE_ANIM", "MOUTH_ANIM", "HAND_ANIM", "LOOK_ANIM", "EXPRESSION", "LOOK_CAMERA", "LYRIC", "MUSIC_PLAY", "MODE_SELECT", "EDIT_MOTION", "BAR_TIME_SET",
        "SHADOWHEIGHT", "EDIT_FACE", "MOVE_CAMERA", "PV_END", "SHADOWPOS", "EDIT_LYRIC", "EDIT_TARGET", "EDIT_MOUTH", "SET_CHARA", "EDIT_MOVE", "EDIT_SHADOW", "EDIT_EYELID", "EDIT_EYE", "EDIT_ITEM", "EDIT_EFFECT",
        "EDIT_DISP", "EDIT_HAND_ANIM", "AIM", "HAND_ITEM", "EDIT_BLUSH", "NEAR_CLIP", "CLOTH_WET", "LIGHT_ROT", "SCENE_FADE", "TONE_TRANS", "SATURATE", "FADE_MODE", "AUTO_BLINK", "PARTS_DISP", "TARGET_FLYING_TIME",
        "CHARA_SIZE", "CHARA_HEIGHT_ADJUST", "ITEM_ANIM", "CHARA_POS_ADJUST", "SCENE_ROT", "EDIT_MOT_SMOOTH_LEN", "PV_BRANCH_MODE", "DATA_CAMERA_START", "MOVIE_PLAY", "MOVIE_DISP", "WIND", "OSAGE_STEP",
        "OSAGE_MV_CCL", "CHARA_COLOR", "SE_EFFECT", "EDIT_MOVE_XYZ", "EDIT_EYELID_ANIM", "EDIT_INSTRUMENT_ITEM", "EDIT_MOTION_LOOP", "EDIT_EXPRESSION", "EDIT_EYE_ANIM", "EDIT_MOUTH_ANIM", "EDIT_CAMERA",
        "EDIT_MODE_SELECT", "PV_END_FADEOUT"]
        self.dataLength = [0, 1, 4, 2, 2, 2, 11, 4, 2, 6, 2, 1, 6, 2, 1, 1, 3, 2, 3, 5, 5, 4, 4, 5, 2, 0, 2, 4, 2, 2, 1, 21, 0, 3, 2, 5, 1, 1, 7, 1, 1, 2, 1, 2, 1, 2, 3, 3, 1, 2, 2, 3, 6, 6, 1, 1, 2, 3, 1, 2, 2, 4,
        4, 1, 2, 1, 2, 1, 1, 3, 3, 3, 2, 1, 9, 3, 2, 4, 2, 3, 2, 24, 1, 2]
        self.mouth = [0x76, 0x79, 0x7A, 0x7C, 0x7B, 0x7D, 0x7E, 0x7F, 0x75, 0x74, 0x77, 0x78, 0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8A]
        self.hand = [0x9C, 0x9D, 0x9B, 0x9E, 0xA2, 0x9F, 0xA0, 0xA3, 0xA4, 0x99, 0xA1, 0xA5, 0xA5, 0xA5, 0x9A]
        self.look = [0x8D, 0x8E, 0x90, 0x8F, 0x92, 0x91, 0x94, 0x93, 0x8C, 0x8C, 0x8B]
        self.exp = [0x28, 0x2A, 0x40, 0x2C, 0x62, 0x30, 0x32, 0x34, 0x36, 0x38, 0x3A, 0x3C, 0x3E, 0x44, 0x26, 0x46, 0x48, 0x4A, 0x4C, 0x4E, 0x50, 0x26, 0x42, 0x25, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2,
        0xB3, 0xB4, 0x52, 0x54, 0x56, 0x58, 0x5A, 0x5C, 0x5E, 0x60, 0x62, 0x64, 0x66, 0x68, 0x6A, 0x6C, 0x6E, 0x70, 0x72]

    def initF2(self):
        self.opcodes = ["END", "TIME", "MIKU_MOVE", "MIKU_ROT", "MIKU_DISP", "MIKU_SHADOW", "TARGET", "SET_MOTION", "SET_PLAYDATA", "EFFECT", "FADEIN_FIELD", "EFFECT_OFF", "SET_CAMERA", "DATA_CAMERA", "CHANGE_FIELD",
        "HIDE_FIELD", "MOVE_FIELD", "FADEOUT_FIELD", "EYE_ANIM", "MOUTH_ANIM", "HAND_ANIM", "LOOK_ANIM", "EXPRESSION", "LOOK_CAMERA", "LYRIC", "MUSIC_PLAY", "MODE_SELECT", "EDIT_MOTION", "BAR_TIME_SET",
        "SHADOWHEIGHT", "EDIT_FACE", "MOVE_CAMERA", "PV_END", "SHADOWPOS", "EDIT_LYRIC", "EDIT_TARGET", "EDIT_MOUTH", "SET_CHARA", "EDIT_MOVE", "EDIT_SHADOW", "EDIT_EYELID", "EDIT_EYE", "EDIT_ITEM", "EDIT_EFFECT",
        "EDIT_DISP", "EDIT_HAND_ANIM", "AIM", "HAND_ITEM", "EDIT_BLUSH", "NEAR_CLIP", "CLOTH_WET", "LIGHT_ROT", "SCENE_FADE", "TONE_TRANS", "SATURATE", "FADE_MODE", "AUTO_BLINK", "PARTS_DISP", "TARGET_FLYING_TIME",
        "CHARA_SIZE", "CHARA_HEIGHT_ADJUST", "ITEM_ANIM", "CHARA_POS_ADJUST", "SCENE_ROT", "EDIT_MOT_SMOOTH_LEN", "PV_BRANCH_MODE", "DATA_CAMERA_START", "MOVIE_PLAY", "MOVIE_DISP", "WIND", "OSAGE_STEP",
        "OSAGE_MV_CCL", "CHARA_COLOR", "SE_EFFECT", "EDIT_MOVE_XYZ", "EDIT_EYELID_ANIM", "EDIT_INSTRUMENT_ITEM", "EDIT_MOTION_LOOP", "EDIT_EXPRESSION", "EDIT_EYE_ANIM", "EDIT_MOUTH_ANIM", "EDIT_CAMERA",
        "EDIT_MODE_SELECT", "PV_END_FADEOUT", "RESERVE", "RESERVE", "RESERVE", "RESERVE", "PV_AUTH_LIGHT_PRIORITY", "PV_CHARA_LIGHT", "PV_STAGE_LIGHT", "TARGET_EFFECT", "FOG", "BLOOM", "COLOR_CORRECTION", "DOF",
        "CHARA_ALPHA", "AUTO_CAPTURE_BEGIN", "MANUAL_CAPTURE", "TOON_EDGE", "SHIMMER", "ITEM_ALPHA", "MOVIE_CUT", "EDIT_CAMERA_BOX", "EDIT_STAGE_PARAM", "EDIT_CHANGE_FIELD", "MIKUDAYO_ADJUST", "LYRIC_2", "LYRIC_READ",
        "LYRIC_READ_2", "ANNOTATION"]
        self.dataLength = [0, 1, 4, 2, 2, 2, 12, 4, 2, 6, 2, 1, 6, 2, 2, 1, 3, 2, 3, 5, 5, 4, 4, 5, 2, 0, 2, 4, 2, 2, 1, 21, 0, 3, 2, 5, 1, 1, 7, 1, 1, 2, 1, 2, 1, 2, 3, 3, 1, 2, 2, 3, 6, 6, 1, 1, 2, 3, 1, 2, 2, 4,
        4, 1, 2, 1, 2, 1, 1, 3, 3, 3, 2, 1, 9, 3, 2, 4, 2, 3, 2, 22, 1, 2, 1, 6, 1, 9, 2, 3, 3, 11, 3, 2, 3, 3, 4, 1, 1, 3, 3, 4, 1, 112, 1, 1, 7, 2, 2, 2, 5]
        self.mouth = [0x5A, 0x5D, 0x5E, 0x66, 0x5F, 0x63, 0x64, 0x60, 0x61, 0x62, 0x65, 0x67, 0x68, 0x69, 0x59, 0x58, 0x5B, 0x5C, 0x6A, 0x6B, 0x6C, 0x6E, 0x6F, 0x70, 0x71, 0x72, 0x73, 0x74,
        0x75, 0x6D, 0x76]
        self.hand = [0x93, 0x94, 0x92, 0x95, 0x99, 0x96, 0x97, 0x9A, 0x9B, 0x90, 0x98, 0x9C, 0x9C, 0x9C, 0x91, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xAB]
        self.look = [0x7A, 0x7B, 0x7D, 0x7C, 0x7F, 0x7E, 0x81, 0x80, 0x79, 0x86, 0x87, 0x88, 0x89, 0x8A, 0x8B, 0x8D, 0x8C, 0x8E, 0x8F, 0x79, 0x78]
        self.exp = [0x04, 0x06, 0x1C, 0x08, 0x41, 0x0C, 0x0E, 0x10, 0x12, 0x14, 0x16, 0x18, 0x1A, 0x20, 0x02, 0x22, 0x24, 0x26, 0x28, 0x2A, 0x2C, 0x02, 0x1E, 0x01, 0xAC, 0xAD, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2, 0xB3,
        0xB4, 0xB5, 0x2E, 0x30, 0x35, 0x37, 0x39, 0x3B, 0x3D, 0x3F, 0x41, 0x43, 0x45, 0x47, 0x49, 0x4B, 0x4D, 0x4F, 0x51, 0x54, 0x55, 0x56, 0x57, 0x32, 0x33, 0x34, 0x53]

    def initX(self):
        self.opcodes = ["END", "TIME", "MIKU_MOVE", "MIKU_ROT", "MIKU_DISP", "MIKU_SHADOW", "TARGET", "SET_MOTION", "SET_PLAYDATA", "EFFECT", "FADEIN_FIELD", "EFFECT_OFF", "SET_CAMERA", "DATA_CAMERA", "CHANGE_FIELD",
        "HIDE_FIELD", "MOVE_FIELD", "FADEOUT_FIELD", "EYE_ANIM", "MOUTH_ANIM", "HAND_ANIM", "LOOK_ANIM", "EXPRESSION", "LOOK_CAMERA", "LYRIC", "MUSIC_PLAY", "MODE_SELECT", "EDIT_MOTION", "BAR_TIME_SET",
        "SHADOWHEIGHT", "EDIT_FACE", "DUMMY", "PV_END", "SHADOWPOS", "EDIT_LYRIC", "EDIT_TARGET", "EDIT_MOUTH", "SET_CHARA", "EDIT_MOVE", "EDIT_SHADOW", "EDIT_EYELID", "EDIT_EYE", "EDIT_ITEM", "EDIT_EFFECT",
        "EDIT_DISP", "EDIT_HAND_ANIM", "AIM", "HAND_ITEM", "EDIT_BLUSH", "NEAR_CLIP", "CLOTH_WET", "LIGHT_ROT", "SCENE_FADE", "TONE_TRANS", "SATURATE", "FADE_MODE", "AUTO_BLINK", "PARTS_DISP", "TARGET_FLYING_TIME",
        "CHARA_SIZE", "CHARA_HEIGHT_ADJUST", "ITEM_ANIM", "CHARA_POS_ADJUST", "SCENE_ROT", "EDIT_MOT_SMOOTH_LEN", "PV_BRANCH_MODE", "DATA_CAMERA_START", "MOVIE_PLAY", "MOVIE_DISP", "WIND", "OSAGE_STEP",
        "OSAGE_MV_CCL", "CHARA_COLOR", "SE_EFFECT", "CHARA_SHADOW_QUALITY", "STAGE_SHADOW_QUALITY", "COMMON_LIGHT", "TONE_MAP", "IBL_COLOR", "REFLECTION", "CHROMATIC_ABERRATION", "STAGE_SHADOW", "REFLECTION_QUALITY",
        "PV_END_FADEOUT", "CREDIT_TITLE", "BAR_POINT", "BEAT_POINT", "RESERVE", "PV_AUTH_LIGHT_PRIORITY", "PV_CHARA_LIGHT", "PV_STAGE_LIGHT", "TARGET_EFFECT", "FOG", "BLOOM", "COLOR_CORRECTION", "DOF", "CHARA_ALPHA",
        "AUTO_CAPTURE_BEGIN", "MANUAL_CAPTURE", "TOON_EDGE", "SHIMMER", "ITEM_ALPHA", "MOVIE_CUT", "EDIT_CAMERA_BOX", "EDIT_STAGE_PARAM", "EDIT_CHANGE_FIELD", "MIKUDAYO_ADJUST", "LYRIC_2", "LYRIC_READ",
        "LYRIC_READ_2", "ANNOTATION", "STAGE_EFFECT", "SONG_EFFECT", "SONG_EFFECT_ATTACH", "LIGHT_AUTH", "FADE", "SET_STAGE_EFFECT_ENV", "RESERVE", "COMMON_EFFECT_AET_FRONT", "COMMON_EFFECT_AET_FRONT_LOW",
        "COMMON_EFFECT_PARTICLE", "SONG_EFFECT_ALPHA_SORT", "LOOK_CAMERA_FACE_LIMIT", "ITEM_LIGHT", "CHARA_EFFECT", "MARKER", "CHARA_EFFECT_CHARA_LIGHT", "ENABLE_COMMON_LIGHT_TO_CHARA", "ENABLE_FXAA",
        "ENABLE_TEMPORAL_AA", "ENABLE_REFLECTION", "BANK_BRANCH", "BANK_END", "", "", "", "", "", "", "", "", "VR_LIVE_MOVIE", "VR_CHEER", "VR_CHARA_PSMOVE", "VR_MOVE_PATH", "VR_SET_BASE", "VR_TECH_DEMO_EFFECT",
        "VR_TRANSFORM", "GAZE", "TECH_DEMO_GESUTRE", "VR_CHEMICAL_LIGHT_COLOR", "VR_LIVE_MOB", "VR_LIVE_HAIR_OSAGE", "VR_LIVE_LOOK_CAMERA", "VR_LIVE_CHEER", "VR_LIVE_GESTURE", "VR_LIVE_CLONE", "VR_LOOP_EFFECT",
        "VR_LIVE_ONESHOT_EFFECT", "VR_LIVE_PRESENT", "VR_LIVE_TRANSFORM", "VR_LIVE_FLY", "VR_LIVE_CHARA_VOICE"]
        self.dataLength = [0, 1, 4, 2, 2, 2, 12, 4, 2, 6, 2, 1, 6, 2, 2, 1, 3, 2, 3, 5, 5, 4, 4, 5, 2, 0, 2, 4, 2, 2, 1, 21, 0, 3, 2, 5, 1, 1, 7, 1, 1, 2, 1, 2, 1, 2, 3, 3, 1, 2, 2, 3, 6, 6, 1, 1, 2, 3, 1, 2, 2, 4,
        4, 1, 2, 1, 2, 1, 1, 3, 3, 3, 2, 1, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 1, 1, 1, 0, 2, 3, 3, 11, 3, 2, 3, 3, 4, 1, 1, 3, 3, 4, 1, 112, 1, 1, 7, 2, 2, 2, 5, 2, 3, 3, 2, 2, 2, 2, 2, 2, 2, 3, 5, 3, 3, 2, 3, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 9, 9, 5, 3, 7, 7, 6, 9, 5, 5, 2]
        self.mouth = [0x5A, 0x5D, 0x5E, 0x66, 0x5F, 0x63, 0x64, 0x60, 0x61, 0x62, 0x65, 0x67, 0x68, 0x69, 0x59, 0x58, 0x5B, 0x5C, 0x6A, 0x6B, 0x6C, 0x6E, 0x6F, 0x70, 0x71, 0x72, 0x73, 0x74,
        0x75, 0x6D, 0x76]
        self.hand = [0x93, 0x94, 0x92, 0x95, 0x99, 0x96, 0x97, 0x9A, 0x9B, 0x90, 0x98, 0x9C, 0x9C, 0x9C, 0x91, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xAB]
        self.look = [0x7A, 0x7B, 0x7D, 0x7C, 0x7F, 0x7E, 0x81, 0x80, 0x79, 0x86, 0x87, 0x88, 0x89, 0x8A, 0x8B, 0x8D, 0x8C, 0x8E, 0x8F, 0x79, 0x78]
        self.exp = [0x04, 0x06, 0x1C, 0x08, 0x41, 0x0C, 0x0E, 0x10, 0x12, 0x14, 0x16, 0x18, 0x1A, 0x20, 0x02, 0x22, 0x24, 0x26, 0x28, 0x2A, 0x2C, 0x02, 0x1E, 0x01, 0xAC, 0xAD, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2, 0xB3,
        0xB4, 0xB5, 0x2E, 0x30, 0x35, 0x37, 0x39, 0x3B, 0x3D, 0x3F, 0x41, 0x43, 0x45, 0x47, 0x49, 0x4B, 0x4D, 0x4F, 0x51, 0x54, 0x55, 0x56, 0x57, 0x32, 0x33, 0x34, 0x53]

    def initAC(self):
        self.opcodes = ["END", "TIME", "MIKU_MOVE", "MIKU_ROT", "MIKU_DISP", "MIKU_SHADOW", "TARGET", "SET_MOTION", "SET_PLAYDATA", "EFFECT", "FADEIN_FIELD", "EFFECT_OFF", "SET_CAMERA", "DATA_CAMERA", "CHANGE_FIELD",
        "HIDE_FIELD", "MOVE_FIELD", "FADEOUT_FIELD", "EYE_ANIM", "MOUTH_ANIM", "HAND_ANIM", "LOOK_ANIM", "EXPRESSION", "LOOK_CAMERA", "LYRIC", "MUSIC_PLAY", "MODE_SELECT", "EDIT_MOTION", "BAR_TIME_SET",
        "SHADOWHEIGHT", "EDIT_FACE", "MOVE_CAMERA", "PV_END", "SHADOWPOS", "EDIT_LYRIC", "EDIT_TARGET", "EDIT_MOUTH", "SET_CHARA", "EDIT_MOVE", "EDIT_SHADOW", "EDIT_EYELID", "EDIT_EYE", "EDIT_ITEM", "EDIT_EFFECT",
        "EDIT_DISP", "EDIT_HAND_ANIM", "AIM", "HAND_ITEM", "EDIT_BLUSH", "NEAR_CLIP", "CLOTH_WET", "LIGHT_ROT", "SCENE_FADE", "TONE_TRANS", "SATURATE", "FADE_MODE", "AUTO_BLINK", "PARTS_DISP", "TARGET_FLYING_TIME",
        "CHARA_SIZE", "CHARA_HEIGHT_ADJUST", "ITEM_ANIM", "CHARA_POS_ADJUST", "SCENE_ROT", "MOT_SMOOTH", "PV_BRANCH_MODE", "DATA_CAMERA_START", "MOVIE_PLAY", "MOVIE_DISP", "WIND", "OSAGE_STEP", "OSAGE_MV_CCL",
        "CHARA_COLOR", "SE_EFFECT", "EDIT_MOVE_XYZ", "EDIT_EYELID_ANIM", "EDIT_INSTRUMENT_ITEM", "EDIT_MOTION_LOOP", "EDIT_EXPRESSION", "EDIT_EYE_ANIM", "EDIT_MOUTH_ANIM", "EDIT_CAMERA", "EDIT_MODE_SELECT",
        "PV_END_FADEOUT", "TARGET_FLAG", "ITEM_ANIM_ATTACH", "SHADOW_RANGE"]
        self.dataLength = [0, 1, 4, 2, 2, 2, 7, 4, 2, 6, 2, 1, 6, 2, 1, 1, 3, 2, 3, 5, 5, 4, 4, 5, 2, 0, 2, 4, 2, 2, 1, 21, 0, 3, 2, 5, 1, 1, 7, 1, 1, 2, 1, 2, 1, 2, 3, 3, 1, 2, 2, 3, 6, 6, 1, 1, 2, 3, 1, 2, 2, 4,
        4, 1, 2, 1, 2, 1, 1, 3, 3, 3, 2, 1, 9, 3, 2, 4, 2, 3, 2, 24, 1, 2, 1, 3, 1]
        self.mouth = [0x31, 0x34, 0x35, 0x37, 0x36, 0x38, 0x5D, 0x5E, 0x30, 0x2F, 0x32, 0x33]
        self.hand = [0x3C, 0x3D, 0x3B, 0x3E, 0x42, 0x3F, 0x40, 0x5F, 0x60, 0x39, 0x41, 0x61, 0x43, 0x44, 0x3A]
        self.look = [0x27, 0x28, 0x2A, 0x29, 0x2C, 0x2B, 0x2E, 0x2D, 0x26, 0x25, 0x67]
        self.exp = [0x08, 0x09, 0x14, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x4F, 0x07, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x07, 0x15, 0x06, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B, 0x4C,
        0x4D, 0x4E]

    def initFT(self):
        self.opcodes = ["END", "TIME", "MIKU_MOVE", "MIKU_ROT", "MIKU_DISP", "MIKU_SHADOW", "TARGET", "SET_MOTION", "SET_PLAYDATA", "EFFECT", "FADEIN_FIELD", "EFFECT_OFF", "SET_CAMERA", "DATA_CAMERA", "CHANGE_FIELD",
        "HIDE_FIELD", "MOVE_FIELD", "FADEOUT_FIELD", "EYE_ANIM", "MOUTH_ANIM", "HAND_ANIM", "LOOK_ANIM", "EXPRESSION", "LOOK_CAMERA", "LYRIC", "MUSIC_PLAY", "MODE_SELECT", "EDIT_MOTION", "BAR_TIME_SET",
        "SHADOWHEIGHT", "EDIT_FACE", "MOVE_CAMERA", "PV_END", "SHADOWPOS", "EDIT_LYRIC", "EDIT_TARGET", "EDIT_MOUTH", "SET_CHARA", "EDIT_MOVE", "EDIT_SHADOW", "EDIT_EYELID", "EDIT_EYE", "EDIT_ITEM", "EDIT_EFFECT",
        "EDIT_DISP", "EDIT_HAND_ANIM", "AIM", "HAND_ITEM", "EDIT_BLUSH", "NEAR_CLIP", "CLOTH_WET", "LIGHT_ROT", "SCENE_FADE", "TONE_TRANS", "SATURATE", "FADE_MODE", "AUTO_BLINK", "PARTS_DISP", "TARGET_FLYING_TIME",
        "CHARA_SIZE", "CHARA_HEIGHT_ADJUST", "ITEM_ANIM", "CHARA_POS_ADJUST", "SCENE_ROT", "MOT_SMOOTH", "PV_BRANCH_MODE", "DATA_CAMERA_START", "MOVIE_PLAY", "MOVIE_DISP", "WIND", "OSAGE_STEP", "OSAGE_MV_CCL",
        "CHARA_COLOR", "SE_EFFECT", "EDIT_MOVE_XYZ", "EDIT_EYELID_ANIM", "EDIT_INSTRUMENT_ITEM", "EDIT_MOTION_LOOP", "EDIT_EXPRESSION", "EDIT_EYE_ANIM", "EDIT_MOUTH_ANIM", "EDIT_CAMERA", "EDIT_MODE_SELECT",
        "PV_END_FADEOUT", "TARGET_FLAG", "ITEM_ANIM_ATTACH", "SHADOW_RANGE", "HAND_SCALE", "LIGHT_POS", "FACE_TYPE", "SHADOW_CAST", "EDIT_MOTION_F", "FOG", "BLOOM", "COLOR_COLLE", "DOF", "CHARA_ALPHA", "AOTO_CAP",
        "MAN_CAP", "TOON", "SHIMMER", "ITEM_ALPHA", "MOVIE_CUT_CHG", "CHARA_LIGHT", "STAGE_LIGHT", "AGEAGE_CTRL", "PSE"]
        self.dataLength = [0, 1, 4, 2, 2, 2, 7, 4, 2, 6, 2, 1, 6, 2, 1, 1, 3, 2, 3, 5, 5, 4, 4, 5, 2, 0, 2, 4, 2, 2, 1, 21, 0, 3, 2, 5, 1, 1, 7, 1, 1, 2, 1, 2, 1, 2, 3, 3, 1, 2, 2, 3, 6, 6, 1, 1, 2, 3, 1, 2, 2, 4,
        4, 1, 2, 1, 2, 1, 1, 3, 3, 3, 2, 1, 9, 3, 2, 4, 2, 3, 2, 24, 1, 2, 1, 3, 1, 3, 4, 1, 2, 6, 3, 2, 3, 3, 4, 1, 1, 3, 3, 4, 1, 3, 3, 8, 2]
        self.mouth = [0x86, 0x8C, 0x8E, 0x92, 0x90, 0x94, 0x96, 0x98, 0x84, 0x83, 0x88, 0x8A, 0x9A, 0x9B, 0x9C, 0x9D, 0x9E, 0x9F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0x97, 0x87, 0x8F, 0x93, 0x91, 0x85, 0x89, 0x8B, 0x8D,
        0x95, 0x99, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFB, 0xFC]
        self.hand = [0xC3, 0xC4, 0xC2, 0xC5, 0xC9, 0xC6, 0xC7, 0xCA, 0xCB, 0xC0, 0xC8, 0xCC, 0xCC, 0xCC, 0xC1]
        self.look = [0xA8, 0xAA, 0xAE, 0xAC, 0xB2, 0xB0, 0xB6, 0xB4, 0xA6, 0xA5, 0xE0, 0xA9, 0xAB, 0xAF, 0xAD, 0xB3, 0xB1, 0xB7, 0xB5, 0xA7]
        self.exp = [0x0B, 0x0F, 0x39, 0x13, 0x17, 0x19, 0x1D, 0x21, 0x25, 0x29, 0x2D, 0x31, 0x35, 0x41, 0x07, 0x45, 0x49, 0x4D, 0x51, 0x55, 0x59, 0x07, 0x3D, 0x06, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xDB, 0xDC, 0xDD,
        0xDE, 0xDF, 0x5D, 0x5F, 0x61, 0x63, 0x65, 0x67, 0x69, 0x6B, 0x6D, 0x6F, 0x71, 0x73, 0x75, 0x77, 0x79, 0x7B, 0x7D, 0x7F, 0x0D, 0x15, 0x1F, 0x27, 0x2B, 0x2F, 0x33, 0x37, 0x43, 0x47, 0x4F, 0x53, 0x81, 0x3B,
        0x11, 0x5B, 0x1B, 0x57, 0x23, 0x4B, 0x09, 0x3F, 0xEC, 0xEE, 0xF0, 0xF2]

class Exp: 
    
    def __init__(self):
        self.performers = []
        self.name = []
        self.morphs = []
        
    def readExp(self, bs, game, robTbl, motDb):
        if game == "F":
            self.initF()
        elif game == "F2":
            self.initF2()
        elif game == "X":
            self.initX()
        elif game == "ACFT" or game == "FT" or game == "MM":
            self.initFT()
        magic = bs.readInt()
        performerCount = bs.readInt()
        for i in range(performerCount):
            performer = noesis.userPrompt(noesis.NOEUSERVAL_STRING, "Choose Performer " + str(i + 1) + ".", "MIK, RIN, LEN, LUK, NER, HAK, KAI, MEI, SAK, TET", "MIK", isPerformer)
            if performer == None:
                return 1
            else:
                performer = performer.upper()
            self.performers.append(performer)
            self.morphs.append([])
        if game == "X":
            subHeaderOff = bs.readUInt64()
            bs.seek(subHeaderOff, NOESEEK_ABS)
            for i in range(performerCount):
                expressionOff = bs.readUInt64()
                eyeAnimOff = bs.readUInt64()
                pos = bs.tell()
                self.readScript(bs, robTbl, motDb, expressionOff, eyeAnimOff, i)
                bs.seek(pos, NOESEEK_ABS)
            for i in range(performerCount):
                name = getOffString(bs, bs.readUInt64())
                self.name.append(name)
        else:
            subHeaderOff = bs.readUInt()
            bs.seek(subHeaderOff, NOESEEK_ABS)
            for i in range(performerCount):
                expressionOff = bs.readUInt()
                eyeAnimOff = bs.readUInt()
                pos = bs.tell()
                self.readScript(bs, robTbl, motDb, expressionOff, eyeAnimOff, i)
                bs.seek(pos, NOESEEK_ABS)
            for i in range(performerCount):
                name = getOffString(bs, bs.readUInt())
                self.name.append(name)

    def readScript(self, bs, robTbl, motDb, expressionOff, eyeAnimOff, performer):
        expressions = []
        eyeAnims = []
        bs.seek(expressionOff, NOESEEK_ABS)
        while True:
            expKey = ExpKey()
            expKey.frame = int(round(bs.readFloat()))
            expKey.type = bs.readShort()
            if expKey.type == -1:
                break
            expKey.idx = bs.readShort()
            expKey.blend = bs.readFloat()
            expKey.frameCount = int(round(bs.readFloat()))
            expressions.append(expKey)
        bs.seek(eyeAnimOff, NOESEEK_ABS)
        while True:
            expKey = ExpKey()
            expKey.frame = int(round(bs.readFloat()))
            expKey.type = bs.readShort()
            if expKey.type == -1:
                break
            expKey.idx = bs.readShort()
            expKey.blend = bs.readFloat()
            expKey.frameCount = int(round(bs.readFloat()))
            eyeAnims.append(expKey)
        expAnims = []
        while len(expressions) != 0 or len(eyeAnims) != 0:
            if len(expressions) != 0 and len(eyeAnims) != 0:
                if expressions[0].frame <= eyeAnims[0].frame:
                    expAnims.append(expressions[0])
                    del expressions[0]
                else:
                    expAnims.append(eyeAnims[0])
                    del eyeAnims[0]
            elif len(expressions) != 0 and len(eyeAnims) == 0:
                expAnims.append(expressions[0])
                del expressions[0]
            elif len(expressions) == 0 and len(eyeAnims) != 0:
                expAnims.append(eyeAnims[0])
                del eyeAnims[0]
        expBlend = 0.0
        close = False
        for expKey in expAnims:
            if expKey.type == 0x00:
                animId = robTbl.db[self.performers[performer]][self.exp[expKey.idx]]
                if animId == -1:
                    name = "NULL"
                else:
                    name = motDb.motDict[animId][9:]
                if self.morphs[performer] != [] and close:
                    if name == "RESET":
                        name = "CLOSE"
                    elif name == "RESET_OLD":
                        name = "CLOSE_OLD"
                    elif self.performers[performer] + "_FACE_" + pMorph.name + "_CL" in motDb.motDict.values():
                        name = name + "_CL"
                    keyMorph(expKey.frame, self.morphs[performer], name, expKey.frameCount, expKey.blend)
                else:
                    keyMorph(expKey.frame, self.morphs[performer], name, expKey.frameCount, expKey.blend)
            elif expKey.type == 0x01:
                pMorph = self.morphs[performer][-1]
                if expKey.blend == 0.0:
                    close = True
                    if pMorph.name == "CLOSE":
                        name = "RESET"
                        keyMorph(expKey.frame, self.morphs[performer], name, expKey.frameCount, expBlend)
                    elif pMorph.name == "CLOSE_OLD":
                        name = "RESET_OLD"
                        keyMorph(expKey.frame, self.morphs[performer], name, expKey.frameCount, expBlend)
                    elif pMorph.name.endswith("_CL"):
                        name = pMorph.name[:-3]
                        keyMorph(expKey.frame, self.morphs[performer], name, expKey.frameCount, expBlend)
                elif (pMorph.name == "CLOSE" or pMorph.name == "CLOSE_OLD" or pMorph.name.endswith("_CL")) and expKey.blend > 0.0:
                    keyMorph(expKey.frame, self.morphs[performer], pMorph.name, expKey.frameCount, expKey.blend)
                else:
                    close = True
                    if pMorph.name == "RESET":
                        name = "CLOSE"
                        keyMorph(expKey.frame, self.morphs[performer], name, expKey.frameCount, expKey.blend)
                    elif pMorph.name == "RESET_OLD":
                        name = "CLOSE_OLD"
                        keyMorph(expKey.frame, self.morphs[performer], name, expKey.frameCount, expKey.blend)
                    if self.performers[performer] + "_FACE_" + pMorph.name + "_CL" in motDb.motDict.values():
                        name = pMorph.name + "_CL"
                        keyMorph(expKey.frame, self.morphs[performer], name, expKey.frameCount, expKey.blend)

    def initF(self):
        self.exp = [0x28, 0x2A, 0x40, 0x2C, 0x62, 0x30, 0x32, 0x34, 0x36, 0x38, 0x3A, 0x3C, 0x3E, 0x44, 0x26, 0x46, 0x48, 0x4A, 0x4C, 0x4E, 0x50, 0x26, 0x42, 0x25, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2,
        0xB3, 0xB4, 0x52, 0x54, 0x56, 0x58, 0x5A, 0x5C, 0x5E, 0x60, 0x62, 0x64, 0x66, 0x68, 0x6A, 0x6C, 0x6E, 0x70, 0x72]

    def initF2(self):
        self.exp = [0x04, 0x06, 0x1C, 0x08, 0x41, 0x0C, 0x0E, 0x10, 0x12, 0x14, 0x16, 0x18, 0x1A, 0x20, 0x02, 0x22, 0x24, 0x26, 0x28, 0x2A, 0x2C, 0x02, 0x1E, 0x01, 0xAC, 0xAD, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2, 0xB3,
        0xB4, 0xB5, 0x2E, 0x30, 0x35, 0x37, 0x39, 0x3B, 0x3D, 0x3F, 0x41, 0x43, 0x45, 0x47, 0x49, 0x4B, 0x4D, 0x4F, 0x51, 0x54, 0x55, 0x56, 0x57, 0x32, 0x33, 0x34, 0x53]

    def initX(self):
        self.exp = [0x04, 0x06, 0x1C, 0x08, 0x41, 0x0C, 0x0E, 0x10, 0x12, 0x14, 0x16, 0x18, 0x1A, 0x20, 0x02, 0x22, 0x24, 0x26, 0x28, 0x2A, 0x2C, 0x02, 0x1E, 0x01, 0xAC, 0xAD, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2, 0xB3,
        0xB4, 0xB5, 0x2E, 0x30, 0x35, 0x37, 0x39, 0x3B, 0x3D, 0x3F, 0x41, 0x43, 0x45, 0x47, 0x49, 0x4B, 0x4D, 0x4F, 0x51, 0x54, 0x55, 0x56, 0x57, 0x32, 0x33, 0x34, 0x53]

    def initFT(self):
        self.exp = [0x0B, 0x0F, 0x39, 0x13, 0x17, 0x19, 0x1D, 0x21, 0x25, 0x29, 0x2D, 0x31, 0x35, 0x41, 0x07, 0x45, 0x49, 0x4D, 0x51, 0x55, 0x59, 0x07, 0x3D, 0x06, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xDB, 0xDC, 0xDD,
        0xDE, 0xDF, 0x5D, 0x5F, 0x61, 0x63, 0x65, 0x67, 0x69, 0x6B, 0x6D, 0x6F, 0x71, 0x73, 0x75, 0x77, 0x79, 0x7B, 0x7D, 0x7F, 0x0D, 0x15, 0x1F, 0x27, 0x2B, 0x2F, 0x33, 0x37, 0x43, 0x47, 0x4F, 0x53, 0x81, 0x3B,
        0x11, 0x5B, 0x1B, 0x57, 0x23, 0x4B, 0x09, 0x3F, 0xEC, 0xEE, 0xF0, 0xF2]

class ExpKey: 
    
    def __init__(self):
        self.frame = 0
        self.type = 0
        self.idx = 0
        self.blend = 0
        self.frameCount = 0

class Morph:

    def __init__(self, frame, name, blend):
        self.frame = frame
        self.name = name
        self.blend = blend

class A3da:

    def __init__(self, mdlList):
        self.mdlList = mdlList
        self.animList = []
        self.names = []
        self.frameCounts = []

    def readA3da(self, data):
        bs = NoeBitStream(data)
        magic = bs.readBytes(4).decode("ASCII")
        if magic == 'A3DA':
            fileSize = bs.readUInt()
            dataOff = bs.readUInt()
            endian = bs.readUInt()
            unk = bs.readUInt()
            dataSize = bs.readUInt()
            bs.seek(dataOff, NOESEEK_ABS)
            data2 = bs.readBytes(dataSize)
            bs = NoeBitStream(data2)
        bs.seek(0x00, NOESEEK_ABS)
        magic = bs.readBytes(5).decode("ASCII")
        if magic == '#A3DA':
            a3daDict = self.loadA3daDict(data, {})
            self.readA3daDict(a3daDict)
        elif magic == '#A3DC':
            a3daDict, a3daBs = self.loadA3dcDict(bs)
            self.readA3daDict(a3daDict, a3daBs)

    def loadA3daDict(self, data, a3daDict):
        lines = data.decode('utf-8').splitlines()
        for line in lines:
            if not line.startswith('#'):
                sline = line.split('=')
                dsline = sline[0].split('.')
                newDict = current = {}
                for itm in dsline:
                    if itm == dsline[-1]:
                        try:
                            current[itm] = ast.literal_eval(sline[1])
                        except:
                            current[itm] = sline[1]
                    else:
                        current[itm] = {}
                    current = current[itm]
                nested_update(a3daDict, newDict)
        return a3daDict

    def loadA3dcDict(self, bs):
        a3daDict = {}
        bs.seek(0x18, NOESEEK_ABS)
        bs.setEndian(NOE_BIGENDIAN)
        headerOff = bs.readUInt()
        count = bs.readShort()
        stride = bs.readUShort()
        bs.setEndian(NOE_LITTLEENDIAN)
        bs.seek(headerOff, NOESEEK_ABS)
        subType = bs.readUInt()
        bs.setEndian(NOE_BIGENDIAN)
        stringOff = bs.readUInt()
        stringSize = bs.readUInt()
        bs.setEndian(NOE_LITTLEENDIAN)
        bs.seek(headerOff + stride, NOESEEK_ABS)
        subType = bs.readUInt()
        bs.setEndian(NOE_BIGENDIAN)
        binaryOff = bs.readUInt()
        binarySize = bs.readUInt()
        bs.setEndian(NOE_LITTLEENDIAN)
        bs.seek(stringOff, NOESEEK_ABS)
        stringData = bs.readBytes(stringSize)
        a3daDict = self.loadA3daDict(stringData, {})
        bs.seek(binaryOff, NOESEEK_ABS)
        a3daBs = NoeBitStream(bs.readBytes(binarySize))
        return a3daDict, a3daBs
        
    def readA3daDict(self, a3daDict, bs=None):
        compress = 0
        if 'compress_f16' in a3daDict['_']:
            compress = a3daDict['_']['compress_f16']
        begin = a3daDict['play_control']['begin']
        fps = a3daDict['play_control']['fps']
        size = a3daDict['play_control']['size']

        if 'objhrc' in a3daDict:
            objMdlList = []
            modelPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open Model File", "Select a model file to open.", noesis.getSelectedFile(), None)
            if isinstance(modelPath, str):
                fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))[:-4]
                fileDir = rapi.getDirForFilePath(modelPath)
                objData = rapi.loadIntoByteArray(modelPath)
                testBin = objectSetCheckType(objData)
                testOsd = osdCheckType(objData)
                if testBin:
                    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))[:-4]
                    obj = objectSetLoadModel(objData, objMdlList, fileName, fileDir, True)
                elif testOsd:
                    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))
                    obj = osdLoadModel(objData, objMdlList, fileName, fileDir, True)
                else:
                    noesis.messagePrompt("Invalid model file.")
                    return 0
            else:
                noesis.messagePrompt("Invalid input.")
                return 0
            self.readObjhrc(a3daDict['objhrc'], bs, objMdlList, obj, size, compress)

    def readObjhrc(self, a3daDict, bs, objMdlList, obj, size, compress):
        for i in range(a3daDict['length']):
            uidName = a3daDict[str(i)]['uid_name']
            name = a3daDict[str(i)]['name']
            objIdx = obj.objects[uidName]
            mdl = objMdlList[objIdx]
            anim, newBoneList = self.readNode(a3daDict[str(i)]['node'], bs, name, size, compress, obj.boneList[objIdx], obj.boneDict[objIdx])
            mdl.setBones(newBoneList)
            mdl.setAnims([anim])
            self.mdlList.append(mdl)
            self.animList.append(anim)
            self.frameCounts.append(size)
            self.names.append(name)

    def readNode(self, a3daDict, bs, name, size, compress, boneList, boneDict):
        kfBones = []
        for i in range(a3daDict['length']):
            if 'model_transform' in a3daDict[str(i)]:
                binOff = a3daDict[str(i)]['model_transform']['bin_offset']
                self.readModelTransform(a3daDict[str(i)], bs, compress, binOff)
            boneName = a3daDict[str(i)]['name']
            xTranKeyFrames, yTranKeyFrames, zTranKeyFrames = self.readKeysXYZ(a3daDict[str(i)]['trans'])
            tranKeys = self.loadKeysXYZ(size, xTranKeyFrames, yTranKeyFrames, zTranKeyFrames)
            xRotKeyFrames, yRotKeyFrames, zRotKeyFrames = self.readKeysXYZ(a3daDict[str(i)]['rot'])
            rotKeys = self.loadRotKeysXYZ(size, xRotKeyFrames, yRotKeyFrames, zRotKeyFrames)
            xSclKeyFrames, ySclKeyFrames, zSclKeyFrames = self.readKeysXYZ(a3daDict[str(i)]['scale'])
            sclKeys = self.loadKeysXYZ(size, xSclKeyFrames, ySclKeyFrames, zSclKeyFrames)
            visKeyFrames = self.readKeyData(a3daDict[str(i)]['visibility'])
            visKeys = self.loadKeys(size, visKeyFrames)
            if boneName not in boneDict:
                idx = len(boneList)
                boneDict[boneName] = idx
                parentIdx = a3daDict[str(i)]['parent']
                if parentIdx == -1:
                    parent = -1
                    mtx = NoeMat43()
                else:
                    parent = boneDict[a3daDict[str(parentIdx)]['name']]
                    mtx = copy.deepcopy(boneList[parent]._matrix)
                    if boneName.startswith('n_') and boneName != 'n_hara':
                        if 'j'+boneName[1:]+'_wj' in boneDict:
                            print(boneName)
                            mtx = copy.deepcopy(boneList[boneDict['j'+boneName[1:]+'_wj']]._matrix)
                        elif 'j'+boneName[1:-1]+'wj' in boneDict:
                            print(boneName)
                            mtx = copy.deepcopy(boneList[boneDict['j'+boneName[1:-1]+'wj']]._matrix)
                        elif xTranKeyFrames.keyType <= 0x01 and yTranKeyFrames.keyType <= 0x01 and zTranKeyFrames.keyType <= 0x01:
                            if xRotKeyFrames.keyType <= 0x01 and yRotKeyFrames.keyType <= 0x01 and zRotKeyFrames.keyType <= 0x01:
                                mtx2 = NoeAngles([xRotKeyFrames.keys[0]*noesis.g_flRadToDeg, yRotKeyFrames.keys[0]*noesis.g_flRadToDeg, zRotKeyFrames.keys[0]*noesis.g_flRadToDeg]).toMat43_XYZ()
                                mtx2[3] = NoeVec3((xTranKeyFrames.keys[0], yTranKeyFrames.keys[0], zTranKeyFrames.keys[0]))
                                tmpList = [NoeBone(0, 'tmp1', mtx, None, -1), NoeBone(1, 'tmp2', mtx2, None, 0)]
                                tmpList = rapi.multiplyBones(tmpList)
                                mtx = tmpList[1]._matrix
                            else:
                                mtx2 = NoeMat43()
                                mtx2[3] = NoeVec3((xTranKeyFrames.keys[0], yTranKeyFrames.keys[0], zTranKeyFrames.keys[0]))
                                tmpList = [NoeBone(0, 'tmp1', mtx, None, -1), NoeBone(1, 'tmp2', mtx2, None, 0)]
                                tmpList = rapi.multiplyBones(tmpList)
                                mtx = tmpList[1]._matrix
                    elif xTranKeyFrames.keyType <= 0x01 and yTranKeyFrames.keyType <= 0x01 and zTranKeyFrames.keyType <= 0x01:
                        if xRotKeyFrames.keyType <= 0x01 and yRotKeyFrames.keyType <= 0x01 and zRotKeyFrames.keyType <= 0x01:
                            mtx2 = NoeAngles([xRotKeyFrames.keys[0]*noesis.g_flRadToDeg, yRotKeyFrames.keys[0]*noesis.g_flRadToDeg, zRotKeyFrames.keys[0]*noesis.g_flRadToDeg]).toMat43_XYZ()
                            mtx2[3] = NoeVec3((xTranKeyFrames.keys[0], yTranKeyFrames.keys[0], zTranKeyFrames.keys[0]))
                            tmpList = [NoeBone(0, 'tmp1', mtx, None, -1), NoeBone(1, 'tmp2', mtx2, None, 0)]
                            tmpList = rapi.multiplyBones(tmpList)
                            mtx = tmpList[1]._matrix
                        else:
                            mtx2 = NoeMat43()
                            mtx2[3] = NoeVec3((xTranKeyFrames.keys[0], yTranKeyFrames.keys[0], zTranKeyFrames.keys[0]))
                            tmpList = [NoeBone(0, 'tmp1', mtx, None, -1), NoeBone(1, 'tmp2', mtx2, None, 0)]
                            tmpList = rapi.multiplyBones(tmpList)
                            mtx = tmpList[1]._matrix
                boneList.append(NoeBone(idx, boneName, mtx, None, parent))
            else:
                parentIdx = a3daDict[str(i)]['parent']
                if parentIdx == -1:
                    parent = -1
                else:
                    parent = boneDict[a3daDict[str(parentIdx)]['name']]
                if not boneName.endswith('_mot'):
                    boneList[boneDict[boneName]].parentName = boneList[parent].name
                    boneList[boneDict[boneName]].parentIndex = parent
            boneKey = NoeKeyFramedBone(boneDict[boneName])
            boneKey.setTranslation(tranKeys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
            boneKey.setRotation(rotKeys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
            boneKey.setScale(sclKeys, noesis.NOEKF_SCALE_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
            kfBones.append(boneKey)
        return NoeKeyFramedAnim(name, boneList, kfBones, 1.0), boneList

    def readModelTransform(self, a3daDict, bs, compress, binOff):
        bs.seek(binOff, NOESEEK_ABS)
        offsets = []
        for i in range(10):
            offsets.append(bs.readUInt())
        a3daDict['scale'] = {'x': self.readBinKey(bs, compress, offsets[0])}
        a3daDict['scale']['y'] = self.readBinKey(bs, compress, offsets[1])
        a3daDict['scale']['z'] = self.readBinKey(bs, compress, offsets[2])
        a3daDict['rot'] = {'x': self.readBinKey(bs, compress, offsets[3], True)}
        a3daDict['rot']['y'] = self.readBinKey(bs, compress, offsets[4], True)
        a3daDict['rot']['z'] = self.readBinKey(bs, compress, offsets[5], True)
        a3daDict['trans'] = {'x': self.readBinKey(bs, compress, offsets[6])}
        a3daDict['trans']['y'] = self.readBinKey(bs, compress, offsets[7])
        a3daDict['trans']['z'] = self.readBinKey(bs, compress, offsets[8])
        a3daDict['visibility'] = self.readBinKey(bs, compress, offsets[9])

    def readBinKey(self, bs, compress, off, isRot=False):
        mtDict = {}
        if off == 0xFFFFFFFF:
            mtDict['type'] = 1
            mtDict['value'] = 1
            return mtDict
        bs.seek(off, NOESEEK_ABS)
        keyType = bs.readByte()
        mtDict['type'] = keyType
        if keyType == 0x00:
            return mtDict
        elif keyType == 0x01:
            bs.seek(0x03, NOESEEK_REL)
            mtDict['value'] = bs.readFloat()
            return mtDict
        else:
            epType = bs.readByte()
            if epType:
                epTypePre = epType & 0x0F
                if epTypePre:
                    mtDict['ep_type_pre'] = epTypePre
                epTypePost = (epType & 0xF0) >> 4
                if epTypePost:
                    mtDict['ep_type_post'] = epTypePost
            bs.seek(0x06, NOESEEK_REL)
            mtDict['max'] = int(bs.readFloat())
            keyLength = bs.readUInt()
            mtDict['key'] = {'length': keyLength}
            if isRot and compress == 1:
                for i in range(keyLength):
                    mtDict['key'][str(i)] = {'type': 3}
                    frame = bs.readUShort()
                    value = bs.readHalfFloat()
                    tan1 = bs.readFloat()
                    tan2 = bs.readFloat()
                    mtDict['key'][str(i)]['data'] = (frame, value, tan1, tan2)
            elif isRot and compress == 2:
                for i in range(keyLength):
                    mtDict['key'][str(i)] = {'type': 3}
                    frame = bs.readUShort()
                    value = bs.readHalfFloat()
                    tan1 = bs.readHalfFloat()
                    tan2 = bs.readHalfFloat()
                    mtDict['key'][str(i)]['data'] = (frame, value, tan1, tan2)
            else:
                for i in range(keyLength):
                    mtDict['key'][str(i)] = {'type': 3}
                    frame = int(bs.readFloat())
                    value = bs.readFloat()
                    tan1 = bs.readFloat()
                    tan2 = bs.readFloat()
                    mtDict['key'][str(i)]['data'] = (frame, value, tan1, tan2)
        return mtDict

    def readKeysXYZ(self, a3daDict):
        xKeyFrames = self.readKeyData(a3daDict['x'])
        yKeyFrames = self.readKeyData(a3daDict['y'])
        zKeyFrames = self.readKeyData(a3daDict['z'])
        return xKeyFrames, yKeyFrames, zKeyFrames

    def readKeyData(self, a3daDict):
        keyFrames = KeyFrames(a3daDict['type'])
        if 'ep_type_pre' in a3daDict:
            keyFrames.epTypePre == a3daDict['ep_type_pre']
        if 'ep_type_post' in a3daDict:
            keyFrames.epTypePost == a3daDict['ep_type_post']
        if keyFrames.keyType == 0x00:
            keyFrames.frameList.append(0)
            keyFrames.keys.append(0.0)
        elif keyFrames.keyType == 0x01:
            keyFrames.frameList.append(0)
            keyFrames.keys.append(a3daDict['value'])
        elif keyFrames.keyType == 0x02 or keyFrames.keyType == 0x04:
            keyFrames.interpType = keyFrames.keyType
            if 'raw_data' in a3daDict:
                rawKeys = a3daDict["raw_data"]["value_list"]
                for i in range(0, a3daDict["raw_data"]["value_list_size"], 2):
                    keyFrames.frameList.append(rawKeys[i])
                    keyFrames.keys.append(rawKeys[i+1])
            else:
                for i in range(a3daDict['key']['length']):
                    subType = a3daDict['key'][str(i)]['type']
                    if subType == 0x00:
                        keyFrames.frameList.append(a3daDict['key'][str(i)]['data'])
                        keyFrames.keys.append(0.0)
                    else:
                        key = a3daDict['key'][str(i)]['data']
                        keyFrames.frameList.append(key[0])
                        keyFrames.keys.append(key[1])
        elif keyFrames.keyType == 0x03:
            keyFrames.interpType = keyFrames.keyType
            if 'raw_data' in a3daDict:
                subType = a3daDict['raw_data_key_type']
                rawKeys = a3daDict["raw_data"]["value_list"]
                if subType == 0x02:
                    for i in range(0, a3daDict["raw_data"]["value_list_size"], 3):
                        keyFrames.frameList.append(rawKeys[i])
                        keyFrames.keys.append(rawKeys[i+1])
                        keyFrames.tangents.append(rawKeys[i+2])
                        keyFrames.tangents2.append(rawKeys[i+2])
                elif subType == 0x03:
                    for i in range(0, a3daDict["raw_data"]["value_list_size"], 4):
                        keyFrames.frameList.append(rawKeys[i])
                        keyFrames.keys.append(rawKeys[i+1])
                        keyFrames.tangents.append(rawKeys[i+2])
                        keyFrames.tangents2.append(rawKeys[i+3])
            else:
                for i in range(a3daDict['key']['length']):
                    subType = a3daDict['key'][str(i)]['type']
                    if subType == 0x00:
                        keyFrames.frameList.append(a3daDict['key'][str(i)]['data'])
                        keyFrames.keys.append(0.0)
                        keyFrames.tangents.append(0.0)
                        keyFrames.tangents2.append(0.0)
                    elif subType == 0x01:
                        key = a3daDict['key'][str(i)]['data']
                        keyFrames.frameList.append(key[0])
                        keyFrames.keys.append(key[1])
                        keyFrames.tangents.append(0.0)
                        keyFrames.tangents2.append(0.0)
                    elif subType == 0x02:
                        key = a3daDict['key'][str(i)]['data']
                        keyFrames.frameList.append(key[0])
                        keyFrames.keys.append(key[1])
                        keyFrames.tangents.append(key[2])
                        keyFrames.tangents2.append(key[2])
                    elif subType == 0x03:
                        key = a3daDict['key'][str(i)]['data']
                        keyFrames.frameList.append(key[0])
                        keyFrames.keys.append(key[1])
                        keyFrames.tangents.append(key[2])
                        keyFrames.tangents2.append(key[3])
        return keyFrames

    def loadKeys(self, frameCount, keyFrames):
        keys = []
        if keyFrames.keyType <= 0x01:
            keys.append(NoeKeyFramedValue(0, NoeVec3((keyFrames.keys[0], 0.0, 0.0))))
        else:
            key = interpolate(frameCount, keyFrames, keyFrames.interpType)
            keys = cleanupKeys(frameCount, key, [0.0]*frameCount, [0.0]*frameCount)
        return keys

    def loadKeysXYZ(self, frameCount, xKeyFrames, yKeyFrames, zKeyFrames):
        keys = []
        if xKeyFrames.keyType <= 0x01 and yKeyFrames.keyType <= 0x01 and zKeyFrames.keyType <= 0x01:
            keys.append(NoeKeyFramedValue(0, NoeVec3((xKeyFrames.keys[0], yKeyFrames.keys[0], zKeyFrames.keys[0]))))
        else:
            xKey = interpolate(frameCount, xKeyFrames, xKeyFrames.interpType)
            yKey = interpolate(frameCount, yKeyFrames, yKeyFrames.interpType)
            zKey = interpolate(frameCount, zKeyFrames, zKeyFrames.interpType)
            keys = cleanupKeys(frameCount, xKey, yKey, zKey)
        return keys

    def loadRotKeysXYZ(self, frameCount, xKeyFrames, yKeyFrames, zKeyFrames):
        keys = []
        if xKeyFrames.keyType <= 0x01 and yKeyFrames.keyType <= 0x01 and zKeyFrames.keyType <= 0x01:
            keys.append(NoeKeyFramedValue(0, NoeAngles([xKeyFrames.keys[0]*noesis.g_flRadToDeg, yKeyFrames.keys[0]*noesis.g_flRadToDeg, zKeyFrames.keys[0]*noesis.g_flRadToDeg]).toMat43_XYZ().toQuat()))
        else:
            xKey = interpolate(frameCount, xKeyFrames, xKeyFrames.interpType)
            yKey = interpolate(frameCount, yKeyFrames, yKeyFrames.interpType)
            zKey = interpolate(frameCount, zKeyFrames, zKeyFrames.interpType)
            keys = cleanupRotKeys(frameCount, xKey, yKey, zKey)
        return keys

def vmdExport(nameList, frameCountList, animList, morphList, boneDictName, morphDictName):
    outDir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Choose a output directory.", "Choose a directory to output your vmd files.", rapi.getDirForFilePath(rapi.getLastCheckedName()), isFolder)
    if outDir == None:
        print("Write vmd failed.")
        return 0
    if not outDir.endswith("\\"):
        outDir += "\\"
    if morphList and animList:
        for i in range(len(animList)):
            vmd = Vmd(nameList[i], frameCountList[i], animList[i], morphList[i], boneDictName, morphDictName, pmxScale, ["Camera_Fov"])
            vmd.wrtieVmd(outDir)
    elif animList:
        for i in range(len(animList)):
            vmd = Vmd(nameList[i], frameCountList[i], animList[i], [], boneDictName, morphDictName, pmxScale, ["Camera_Fov"])
            vmd.wrtieVmd(outDir)
    elif morphList:
        for i in range(len(animList)):
            vmd = Vmd(nameList[i], frameCountList[i], [], morphList[i], boneDictName, morphDictName, pmxScale, ["Camera_Fov"])
            vmd.wrtieVmd(outDir)

def getFileData(path, name):
    parent1Dir = os.path.dirname(os.path.dirname(path))
    parent2Dir = os.path.dirname(parent1Dir)
    parent3Dir = os.path.dirname(parent2Dir)
    if rapi.checkFileExists(path + name):
        fileDir = path + name
    elif rapi.checkFileExists(parent1Dir + "/" + name):
        fileDir = parent1Dir + "/" + name
    elif rapi.checkFileExists(parent2Dir + "/" + name):
        fileDir = parent2Dir + "/" + name
    elif rapi.checkFileExists(parent3Dir + "/" + name):
        fileDir = parent3Dir + "/" + name
    elif rapi.checkFileExists(path + "mdata_" + name):
        fileDir = path + "mdata_" + name
    elif rapi.checkFileExists(parent1Dir + "/mdata_" + name):
        fileDir = parent1Dir + "/mdata_" + name
    elif rapi.checkFileExists(parent2Dir + "/mdata_" + name):
        fileDir = parent2Dir + "/mdata_" + name
    elif rapi.checkFileExists(parent3Dir + "/mdata_" + name):
        fileDir = parent3Dir + "/mdata_" + name
    elif rapi.checkFileExists(path + "tex" + name):
        fileDir = path + "tex" + name
    elif rapi.checkFileExists(parent1Dir + "/tex/" + name):
        fileDir = parent1Dir + "/tex/" + name
    else:
        fileDir = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open " + name, "Unable to locate " + name, noesis.getSelectedFile(), None)
    data = rapi.loadIntoByteArray(fileDir)
    return data

def getFileDataMdata(path, name):
    parent1Dir = os.path.dirname(os.path.dirname(path))
    parent2Dir = os.path.dirname(parent1Dir)
    parent3Dir = os.path.dirname(parent2Dir)
    if rapi.checkFileExists(path + "mdata_" + name):
        fileDir = path + "mdata_" + name
    elif rapi.checkFileExists(parent1Dir + "/mdata_" + name):
        fileDir = parent1Dir + "/mdata_" + name
    elif rapi.checkFileExists(parent2Dir + "/mdata_" + name):
        fileDir = parent2Dir + "/mdata_" + name
    elif rapi.checkFileExists(parent3Dir + "/mdata_" + name):
        fileDir = parent3Dir + "/mdata_" + name
    else:
        return None
    data = rapi.loadIntoByteArray(fileDir)
    return data

def getBoneData(path, name, char, charId):
    parent1Dir = os.path.dirname(os.path.dirname(path)) 
    parent2Dir = os.path.dirname(parent1Dir)
    parent3Dir = os.path.dirname(parent2Dir)
    if rapi.checkFileExists(path + name):
        fileDir = path + name
    elif rapi.checkFileExists(parent1Dir + "/" + name):
        fileDir = parent1Dir + "/" + name
    elif rapi.checkFileExists(parent2Dir + "/" + name):
        fileDir = parent2Dir + "/" + name
    elif rapi.checkFileExists(parent3Dir + "/" + name):
        fileDir = parent3Dir + "/" + name
    elif rapi.checkFileExists(path + char + "_" + charId):
        fileDir = path + char + "_" + charId
    elif rapi.checkFileExists(parent1Dir + "/" + char + "_" + charId):
        fileDir = parent1Dir + "/" + char + "_" + charId
    elif rapi.checkFileExists(parent2Dir + "/" + char + "_" + charId):
        fileDir = parent2Dir + "/" + char + "_" + charId
    elif rapi.checkFileExists(parent3Dir + "/" + char + "_" + charId):
        fileDir = parent3Dir + "/" + char + "_" + charId
    elif rapi.checkFileExists(path + char + "_002.bon"):
        fileDir = path + char + "_002.bon"
    elif rapi.checkFileExists(parent1Dir + "/" + char + "_002.bon"):
        fileDir = parent1Dir + "/" + char + "_002.bon"
    elif rapi.checkFileExists(parent2Dir + "/" + char + "_002.bon"):
        fileDir = parent2Dir + "/" + char + "_002.bon"
    elif rapi.checkFileExists(parent3Dir + "/" + char + "_002.bon"):
        fileDir = parent3Dir + "/" + char + "_002.bon"
    elif rapi.checkFileExists(path + char + "_001.bon"):
        fileDir = path + char + "_001.bon"
    elif rapi.checkFileExists(parent1Dir + "/" + char + "_001.bon"):
        fileDir = parent1Dir + "/" + char + "_001.bon"
    elif rapi.checkFileExists(parent2Dir + "/" + char + "_001.bon"):
        fileDir = parent2Dir + "/" + char + "_001.bon"
    elif rapi.checkFileExists(parent3Dir + "/" + char + "_001.bon"):
        fileDir = parent3Dir + "/" + char + "_001.bon"
    else:
        return None, None
    data = rapi.loadIntoByteArray(fileDir)
    return data, fileDir

def isFolder(path):
    if os.path.isdir(path):
        return None
    else:
        return "Directory does not exists."

def getAddressSpace(bs, fileSize, dataOff, dataSize):
    addressSpace = 32
    start = 0
    bs.seek(dataOff + dataSize, NOESEEK_ABS)
    while start < fileSize:
        start = bs.tell()
        magic = bs.readBytes(4).decode("ASCII")
        fileSize2 = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        bs.seek(start + dataOff + dataSize, NOESEEK_ABS)
        if magic == "POF1":
            addressSpace = 64
        elif magic == "EOFC":
            break
    return addressSpace

def readOff(bs, addressSpace):
    if addressSpace == 32:
        off = bs.readUInt()
    elif addressSpace == 64:
        offFix = bs.tell()
        while offFix%0x08 != 0:
            bs.seek(0x01, NOESEEK_REL)
            offFix = bs.tell()
        off = bs.readUInt64()
    return off

def getOffString(bs, off):
    pos = bs.tell()
    bs.seek(off, NOESEEK_ABS)
    string = bs.readString()
    bs.seek(pos, NOESEEK_ABS)
    return string

def getOffStringList(bs, addressSpace, off, count):
    string = []
    pos = bs.tell()
    bs.seek(off, NOESEEK_ABS)
    for i in range(count):
        if addressSpace == 32:
            stringOff = bs.readUInt()
        elif addressSpace == 64:
            stringOff = bs.readUInt64()
        pos2 = bs.tell()
        bs.seek(stringOff, NOESEEK_ABS)
        string.append(bs.readString())
        bs.seek(pos2, NOESEEK_ABS)
    bs.seek(pos, NOESEEK_ABS)
    return string

def padding(bs, pad):
    offFix = bs.tell()
    while offFix%pad != 0:
        bs.seek(0x01, NOESEEK_REL)
        offFix = bs.tell()

def keyMorph(frame, morphs, name, frameCount, blend):
    if frameCount == 0:
        initFrameCount = -1
    else:
        initFrameCount = 0
    if morphs == []:
        if frame == 0 and initFrameCount == -1:
            newMorph = Morph(frame, name, blend)
            morphs.append(newMorph)
        else:
            key = addMorphKey(frame, name, initFrameCount, frameCount, 0.0, blend)
            morphs.extend(key)
    else:
        if frame == 0 and initFrameCount == -1:
            newMorph = Morph(frame, name, blend)
            del morphs[-1]
            morphs.append(newMorph)
        else:
            pMorph = morphs[-1]
            if name == pMorph.name:
                if len(morphs) >= 5:
                    p2Morph = morphs[-3]
                    if p2Morph.frame >= frame + initFrameCount:
                        p2InitMorph = morphs[-4]
                        newBlend = interpLinear(frame + initFrameCount, p2InitMorph.frame, p2Morph.frame, p2InitMorph.blend, p2Morph.blend)
                        p2Key = addMorphKey(frame, p2Morph.name, initFrameCount, frameCount, newBlend, 0.0)
                        morphs[-3] = p2Key[0]
                if pMorph.frame < frame + initFrameCount:
                    key = addMorphKey(frame, name, initFrameCount, frameCount, pMorph.blend, blend)
                else:
                    pInitMorph = morphs[-2]
                    newBlend = interpLinear(frame + initFrameCount, pInitMorph.frame, pMorph.frame, pInitMorph.blend, pMorph.blend)
                    key = addMorphKey(frame, name, initFrameCount, frameCount, newBlend, blend)
                    del morphs[-1]
                if len(morphs) >= 5 and p2Morph.frame >= frame + initFrameCount:
                    morphs.extend(p2Key)
                morphs.extend(key)
            else:
                if len(morphs) >= 5:
                    p2Morph = morphs[-3]
                    if p2Morph.frame >= frame + initFrameCount:
                        p2InitMorph = morphs[-4]
                        newBlend = interpLinear(frame + initFrameCount, p2InitMorph.frame, p2Morph.frame, p2InitMorph.blend, p2Morph.blend)
                        p2Key = addMorphKey(frame, p2Morph.name, initFrameCount, frameCount, newBlend, 0.0)
                        morphs[-3] = p2Key[0]
                if pMorph.frame < frame + initFrameCount:
                    pKey = addMorphKey(frame, pMorph.name, initFrameCount, frameCount, pMorph.blend, 0.0)
                else:
                    pInitMorph = morphs[-2]
                    newBlend = interpLinear(frame + initFrameCount, pInitMorph.frame, pMorph.frame, pInitMorph.blend, pMorph.blend)
                    pKey = addMorphKey(frame, pMorph.name, initFrameCount, frameCount, newBlend, 0.0)
                    del morphs[-1]
                if len(morphs) >= 5 and p2Morph.frame >= frame + initFrameCount:
                    morphs.extend(p2Key)
                morphs.extend(pKey)
                key = addMorphKey(frame, name, initFrameCount, frameCount, 0.0, blend)
                morphs.extend(key)

def addMorphKey(frame, name, initFrameCount, frameCount, initBlend, blend):
    initMorph = Morph(frame + initFrameCount, name, initBlend)
    newMorph = Morph(frame + frameCount, name, blend)
    return [initMorph, newMorph]

def interpolate(frameCount, keyFrames, interpType):
    keys = []
    idx = 0
    if keyFrames.frameList[0] == -1:
        keyFrames.frameList.pop(0)
        keyFrames.keys.pop(0)
        if keyFrames.tangents:
            keyFrames.tangents.pop(0)
        if keyFrames.tangents2:
            keyFrames.tangents2.pop(0)
    firstFrame = keyFrames.frameList[0]
    lastFrame = keyFrames.frameList[-1]
    frameDelta = lastFrame - firstFrame
    keyDelta = keyFrames.keys[-1] - keyFrames.keys[0]
    if interpType == 0:
        for i in range(frameCount):
            keys.append(keyFrames.keys[0])
    elif interpType == 1:
        for i in range(frameCount):
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1 and keyFrames.frameList[idx + 1] == i:
                keyFrames.frameList.pop(idx)
                keyFrames.keys.pop(idx)
                keyFrames.tangents.pop(idx)
            keys.append(interpolateMot(i, keyFrames, idx))
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1:
                idx += 1
    elif interpType == 2:
        for i in range(frameCount):
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1 and keyFrames.frameList[idx + 1] == i:
                keyFrames.frameList.pop(idx)
                keyFrames.keys.pop(idx)
            keys.append(interpolateLinear(i, keyFrames, idx))
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1:
                idx += 1
        if keyFrames.epTypePre >= 1 and keyFrames.epTypePre <= 3:
            for i in range(0, frameCount):
                keys[i] = inerpolateA3daEpPre(i, keyFrames.epTypePre, keys, firstFrame, lastFrame, frameDelta, keyDelta)
        if keyFrames.epTypePost >= 1 and keyFrames.epTypePost <= 3:
            for i in range(lastFrame + 1, frameCount):
                keys[i] = inerpolateA3daEpPost(i, keyFrames.epTypePost, keys, firstFrame, lastFrame, frameDelta, keyDelta)
    elif interpType == 3:
        firstTan = keyFrames.tangents[0]
        lastTan = keyFrames.tangents2[-1]
        for i in range(frameCount):
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1 and keyFrames.frameList[idx + 1] == i:
                keyFrames.frameList.pop(idx)
                keyFrames.keys.pop(idx)
                keyFrames.tangents.pop(idx)
                keyFrames.tangents2.pop(idx)
            keys.append(interpolateA3da(i, keyFrames, idx))
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1:
                idx += 1
        if keyFrames.epTypePre >= 1 and keyFrames.epTypePre <= 3:
            for i in range(0, frameCount):
                keys[i] = inerpolateA3daEpPre(i, keyFrames.epTypePre, keys, firstFrame, lastFrame, frameDelta, keyDelta, firstTan)
        if keyFrames.epTypePost >= 1 and keyFrames.epTypePost <= 3:
            for i in range(lastFrame + 1, frameCount):
                keys[i] = inerpolateA3daEpPost(i, keyFrames.epTypePost, keys, firstFrame, lastFrame, frameDelta, keyDelta, lastTan)
    elif interpType == 4:
        for i in range(frameCount):
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1 and keyFrames.frameList[idx + 1] == i:
                keyFrames.frameList.pop(idx)
                keyFrames.keys.pop(idx)
            keys.append(interpolateHold(i, keyFrames, idx))
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1:
                idx += 1
        if keyFrames.epTypePre >= 1 and keyFrames.epTypePre <= 3:
            for i in range(0, frameCount):
                keys[i] = inerpolateA3daEpPre(i, keyFrames.epTypePre, keys, firstFrame, lastFrame, frameDelta, keyDelta)
        if keyFrames.epTypePost >= 1 and keyFrames.epTypePost <= 3:
            for i in range(lastFrame + 1, frameCount):
                keys[i] = inerpolateA3daEpPost(i, keyFrames.epTypePost, keys, firstFrame, lastFrame, frameDelta, keyDelta)
    return keys

def interpolateLinear(frame, keyFrames, idx):
    if frame <= keyFrames.frameList[0]:
        return keyFrames.keys[0]
    elif frame >= keyFrames.frameList[-1]:
        return keyFrames.keys[-1]
    cf = keyFrames.frameList[idx-1]
    nf = keyFrames.frameList[idx]
    cv = keyFrames.keys[idx-1]
    nv = keyFrames.keys[idx]
    if frame > cf and frame < nf:
        t = (frame - cf) / (nf - cf)
        return (1.0 - t) * cv + t * nv
    elif frame <= cf:
        return cv
    else:
        return nv

def interpolateMot(frame, keyFrames, idx):
    if frame <= keyFrames.frameList[0]:
        return keyFrames.keys[0]
    elif frame >= keyFrames.frameList[-1]:
        return keyFrames.keys[-1]
    cf = keyFrames.frameList[idx-1]
    nf = keyFrames.frameList[idx]
    cv = keyFrames.keys[idx-1]
    nv = keyFrames.keys[idx]
    ct = keyFrames.tangents[idx-1]
    nt = keyFrames.tangents[idx]
    if frame > cf and frame < nf:
        df = frame - cf
        t = df / (nf - cf)
        t_1 = t - 1.0
        return cv + t * t * (3.0 - 2.0 * t) * (nv - cv) + (t_1 * ct + t * nt) * df * t_1
    elif frame <= cf:
        return cv
    else:
        return nv

def interpolateA3da(frame, keyFrames, idx):
    if frame <= keyFrames.frameList[0]:
        return keyFrames.keys[0]
    elif frame >= keyFrames.frameList[-1]:
        return keyFrames.keys[-1]
    cf = keyFrames.frameList[idx-1]
    nf = keyFrames.frameList[idx]
    cv = keyFrames.keys[idx-1]
    nv = keyFrames.keys[idx]
    ct = keyFrames.tangents2[idx-1]
    nt = keyFrames.tangents[idx]
    if frame > cf and frame < nf:
        df = frame - cf
        t = df / (nf - cf)
        t_1 = t - 1.0
        return cv + t * t * (3.0 - 2.0 * t) * (nv - cv) + (t_1 * ct + t * nt) * df * t_1
    elif frame <= cf:
        return cf
    else:
        return nv

def interpolateHold(frame, keyFrames, idx):
    if frame <= keyFrames.frameList[0]:
        return keyFrames.keys[0]
    elif frame >= keyFrames.frameList[-1]:
        return keyFrames.keys[-1]
    cf = keyFrames.frameList[idx-1]
    nf = keyFrames.frameList[idx]
    cv = keyFrames.keys[idx-1]
    nv = keyFrames.keys[idx]
    if frame >= cf and frame < nf:
        return cv
    else:
        return nv

def inerpolateA3daEpPre(frame, epType, keys, firstFrame, lastFrame, frameDelta, keyDelta, tan=0.0):
    ep = 0.0
    df = firstFrame - frame
    if epType == 1:
        return firstFrame - df * tan
    f = int(lastFrame - df % frameDelta)
    if epType == 3:
        ep = -float(int(df / frameDelta) + 1) * keyDelta
    return keys[f] + ep

def inerpolateA3daEpPost(frame, epType, keys, firstFrame, lastFrame, frameDelta, keyDelta, tan=0.0):
    ep = 0.0
    df = frame - lastFrame
    if epType == 1:
        return lastFrame + df * tan
    f = int(firstFrame + df % frameDelta)
    if epType == 3:
        ep = float(int(df / frameDelta) + 1) * keyDelta
    return keys[f] + ep

def interpLinear(frame, initFrame, endFrame, initKey, endKey):
    t = (frame - initFrame) / (endFrame - initFrame)
    key = (1.0 - t) * initKey + t * endKey
    return key

def cleanupKeys(frameCount, xKey, yKey, zKey):
    keys = []
    keys.append(NoeKeyFramedValue(0, [xKey[0], yKey[0], zKey[0]]))
    for i in range(1, frameCount - 1):
        if [xKey[i], yKey[i], zKey[i]] == [xKey[i-1], yKey[i-1], zKey[i-1]] and [xKey[i], yKey[i], zKey[i]] == [xKey[i+1], yKey[i+1], zKey[i+1]]:
            continue
        else:
            keys.append(NoeKeyFramedValue(i, NoeVec3((xKey[i], yKey[i], zKey[i]))))
    keys.append(NoeKeyFramedValue(frameCount - 1, NoeVec3((xKey[frameCount - 1], yKey[frameCount - 1], zKey[frameCount - 1]))))
    return keys

def cleanupRotKeys(frameCount, xKey, yKey, zKey):
    keys = []
    keys.append(NoeKeyFramedValue(0, NoeAngles([xKey[0]*noesis.g_flRadToDeg, yKey[0]*noesis.g_flRadToDeg, zKey[0]*noesis.g_flRadToDeg]).toMat43_XYZ().toQuat()))
    for i in range(1, frameCount - 1):
        if [xKey[i], yKey[i], zKey[i]] == [xKey[i-1], yKey[i-1], zKey[i-1]] and [xKey[i], yKey[i], zKey[i]] == [xKey[i+1], yKey[i+1], zKey[i+1]]:
            continue
        else:
            keys.append(NoeKeyFramedValue(i, NoeAngles([xKey[i]*noesis.g_flRadToDeg, yKey[i]*noesis.g_flRadToDeg, zKey[i]*noesis.g_flRadToDeg]).toMat43_XYZ().toQuat()))
    keys.append(NoeKeyFramedValue(frameCount - 1, NoeAngles([xKey[-1]*noesis.g_flRadToDeg, yKey[-1]*noesis.g_flRadToDeg, zKey[-1]*noesis.g_flRadToDeg]).toMat43_XYZ().toQuat()))
    return keys

def nested_update(d, v):
        for key in v:
            if key in d and isinstance(d[key], Map) and isinstance(v[key], Map):
                nested_update(d[key], v[key])
            else:
                d[key] = v[key]

def baseSkelAFT():
    boneTrans = {'MIK': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'KAI': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'LEN': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))},
    'LUK': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'MEI': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'RIN': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))},
    'HAK': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'NER': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'SAK': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))},
    'TET': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}}
    boneRot = {'n_hara': NoeVec3((0.0, 1.570796012878418, 0.0)), 'n_mune_b': NoeVec3((0.0, -1.570796012878418, -1.570796012878418)), 'n_kao': NoeVec3((1.570796012878418, 0.0, -3.1415929794311523)), 
    'face_root': NoeVec3((1.570796012878418, 0.0, 1.570796012878418)), 'n_waki_l': NoeVec3((1.570796012878418, 0.0, 1.570796012878418)), 'c_kata_l': NoeVec3((-1.570796012878418, -1.570796012878418, -1.570796012878418)), 
    'n_hito_l_ex': NoeVec3((0.0, 0.0, -0.15707960724830627)), 'n_ko_l_ex': NoeVec3((-0.13962629437446594, 0.0, 0.27925270795822144)), 'n_kusu_l_ex': NoeVec3((0.0, 0.0, 0.15707960724830627)), 
    'n_naka_l_ex': NoeVec3((0.0, 0.0, -0.01745329052209854)), 'n_oya_l_ex': NoeVec3((1.3089970350265503, 0.2094395011663437, -0.4188790023326874)), 'n_skata_l_wj_cd_ex': NoeVec3((0.0, 0.48869219422340393, 0.01745329052209854)), 
    'n_skata_b_l_wj_cd_cu_ex': NoeVec3((8.317972088889292e-08, 0.0, 0.0)), 'n_skata_c_l_wj_cd_cu_ex': NoeVec3((8.363255687982019e-08, 0.0, 0.0)), 'n_waki_r': NoeVec3((1.570796012878418, 0.0, 1.570796012878418)), 
    'c_kata_r': NoeVec3((-1.570796012878418, 1.570796012878418, 1.570796012878418)), 'n_hito_r_ex': NoeVec3((0.0, 0.0, -0.15707960724830627)), 'n_ko_r_ex': NoeVec3((0.13962629437446594, 0.0, 0.27925270795822144)), 
    'n_kusu_r_ex': NoeVec3((0.0, 0.0, 0.15707960724830627)), 'n_naka_r_ex': NoeVec3((0.0, 0.0, -0.01745329052209854)), 'n_oya_r_ex': NoeVec3((-1.3089970350265503, -0.2094395011663437, -0.4188790023326874)), 
    'n_skata_r_wj_cd_ex': NoeVec3((0.0, -0.48869219422340393, 0.01745329052209854)), 'n_skata_b_r_wj_cd_cu_ex': NoeVec3((-1.5131250563626963e-07, 0.0, 0.0)), 'n_skata_c_r_wj_cd_cu_ex': NoeVec3((7.524719336515773e-08, 0.0, 0.0))}
    return boneTrans, boneRot

def baseSkelAC():
    boneTrans = {'MIK': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'KAI': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'LEN': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))},
    'LUK': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'MEI': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'RIN': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))},
    'HAK': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'NER': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}, 'SAK': {'n_hara_cp': NoeVec3((0.0, 1.0549999475479126, 0.0))}}
    boneRot = {'n_hara': NoeVec3((0.0, 1.570796012878418, 0.0)), 'n_mune_b': NoeVec3((-0.7853981852531433, -1.570796012878418, -0.7853981852531433)), 'n_kao': NoeVec3((1.570796012878418, 0.0, -3.1415929794311523)), 
    'face_root': NoeVec3((1.570796012878418, 0.0, 1.570796012878418)), 'n_waki_l': NoeVec3((1.570796012878418, 0.0, 1.570796012878418)), 'c_kata_l': NoeVec3((-1.570796012878418, -1.570796012878418, -1.570796012878418)), 
    'nl_oya_l_wj': NoeVec3((-1.570796012878418, 0.0, -0.5235987901687622)), 'nl_oya_b_l_wj': NoeVec3((0.0, -0.5235987901687622, 0.0)), 'n_skata_l_wj_cd_ex': NoeVec3((0.005010894034057856, 0.4882011115550995, 0.02011800929903984)), 
    'n_skata_b_l_wj_cd_cu_ex': NoeVec3((-0.0004955081967636943, 0.0, 0.0)), 'n_skata_c_l_wj_cd_cu_ex': NoeVec3((-0.0017838289495557547, 0.0, 0.0)), 'n_waki_r': NoeVec3((1.570796012878418, 0.0, 1.570796012878418)), 
    'c_kata_r': NoeVec3((-1.570796012878418, 1.570796012878418, 1.570796012878418)), 'nl_oya_r_wj': NoeVec3((1.570796012878418, 0.0, -0.5235987901687622)), 'nl_oya_b_r_wj': NoeVec3((0.0, 0.5235987901687622, 0.0)), 
    'n_skata_r_wj_cd_ex': NoeVec3((-0.005010895896703005, -0.4882011115550995, 0.02011800929903984)), 'n_skata_b_r_wj_cd_cu_ex': NoeVec3((0.0004955081967636943, 0.0, 0.0)), 
    'n_skata_c_r_wj_cd_cu_ex': NoeVec3((0.0017838289495557547, 0.0, 0.0)), 'n_momo_l_cd_ex': NoeVec3((0.012819809839129448, 0.0, 0.0)), 'n_momo_r_cd_ex': NoeVec3((-0.012819809839129448, 0.0, 0.0))}
    return boneTrans, boneRot

def baseSkelVF5():
    boneTrans = {'AKI': {'n_hara_cp': NoeVec3((0.0, 1.0579999685287476, 0.0))}, 'AOI': {'n_hara_cp': NoeVec3((0.0, 1.0670000314712524, 0.0))}, 'BRA': {'n_hara_cp': NoeVec3((0.0, 1.1039999723434448, 0.0))}, 
    'DUR': {'n_hara_cp': NoeVec3((0.0, 1.1759999990463257, 0.0))}, 'GOH': {'n_hara_cp': NoeVec3((0.0, 1.055999994277954, 0.0))}, 'JAK': {'n_hara_cp': NoeVec3((0.0, 1.159999966621399, 0.0))},
    'JEF': {'n_hara_cp': NoeVec3((0.0, 1.1759999990463257, 0.0))}, 'KAG': {'n_hara_cp': NoeVec3((0.0, 1.065999984741211, 0.0))}, 'KRT': {'n_hara_cp': NoeVec3((0.0, 1.2070000171661377, 0.0))},
    'LAU': {'n_hara_cp': NoeVec3((0.0, 1.1109999418258667, 0.0))}, 'LEI': {'n_hara_cp': NoeVec3((0.0, 1.1109999418258667, 0.0))}, 'LIO': {'n_hara_cp': NoeVec3((0.0, 1.1349999904632568, 0.0))},
    'MON': {'n_hara_cp': NoeVec3((0.0, 1.034000039100647, 0.0))}, 'MSK': {'n_hara_cp': NoeVec3((0.0, 0.9449999928474426, 0.0))}, 'PAI': {'n_hara_cp': NoeVec3((0.0, 1.065000057220459, 0.0))},
    'SAR': {'n_hara_cp': NoeVec3((0.0, 1.13100004196167, 0.0))}, 'SHU': {'n_hara_cp': NoeVec3((0.0, 0.9890000224113464, 0.0))}, 'TAK': {'n_hara_cp': NoeVec3((0.0, 1.1399999856948853, 0.0))},
    'VAN': {'n_hara_cp': NoeVec3((0.0, 1.1759999990463257, 0.0))}, 'WOL': {'n_hara_cp': NoeVec3((0.0, 1.1759999990463257, 0.0))}}
    boneRot = {'n_hara': NoeVec3((0.0, 1.570796012878418, 0.0)), 'n_mune_b': NoeVec3((-0.7853981852531433, -1.570796012878418, -0.7853981852531433)), 'n_kao': NoeVec3((-1.570796012878418, -3.1415929794311523, 0.0)), 
    'face_root': NoeVec3((1.570796012878418, 0.0, 1.570796012878418)), 'n_waki_l': NoeVec3((1.570796012878418, 0.0, 1.570796012878418)), 'c_kata_l': NoeVec3((-1.570796012878418, -1.570796012878418, -1.570796012878418)), 
    'nl_oya_l_wj': NoeVec3((-1.570796012878418, 0.0, -0.5235987901687622)), 'nl_oya_b_l_wj': NoeVec3((0.0, -0.5235987901687622, 0.0)), 'n_hiji_l_wj_ex': NoeVec3((0.0, 0.0, -0.004363323096185923)), 
    'n_waki_r': NoeVec3((1.570796012878418, 0.0, 1.570796012878418)), 'c_kata_r': NoeVec3((-1.570796012878418, 1.570796012878418, 1.570796012878418)), 'nl_oya_r_wj': NoeVec3((1.570796012878418, 0.0, -0.5235987901687622)), 
    'nl_oya_b_r_wj': NoeVec3((0.0, 0.5235987901687622, 0.0)), 'n_hiji_r_wj_ex': NoeVec3((0.0, 0.0, -0.004363323096185923)), 'kl_asi_l_wj_co': NoeVec3((0.0, 0.0, -0.008726612664759159)), 
    'n_hiza_l_wj_ex': NoeVec3((0.0, 0.0, 0.004363323096185923)), 'kl_asi_r_wj_co': NoeVec3((0.0, 0.0, -0.008726646192371845)), 'n_hiza_r_wj_ex': NoeVec3((0.0, 0.0, 0.004363323096185923)), }
    return boneTrans, boneRot

def baseSkelMGF():
    boneRot = {'ARH': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.2094395011663437, -1.570796012878418)), 
    'skirt_a_02_wj': NoeVec3((0.0, 0.10471980273723602, 0.0)), 'skirt_b_01_wj': NoeVec3((-0.593411922454834, -0.15707960724830627, -1.2566369771957397)), 'skirt_b_02_wj': NoeVec3((0.0, 0.06981316953897476, 0.0)), 
    'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.09599310904741287, -1.1693710088729858)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_d_01_wj': NoeVec3((-2.4434609413146973, 0.3665192127227783, -1.2566369771957397)), 
    'skirt_d_02_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.652899980545044, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.15707960724830627, 0.0)), 'skirt_f_01_wj': NoeVec3((2.4434609413146973, 0.3665192127227783, -1.8849560022354126)), 
    'skirt_f_02_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.09599310904741287, -1.9722219705581665)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.593411922454834, -0.15707960724830627, -1.8849560022354126)), 'skirt_h_02_wj': NoeVec3((0.0, 0.06981316953897476, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hairside_l_01_wj': NoeVec3((-0.3490658104419708, 0.27925270795822144, -1.0471980571746826)), 'hairside_l_02_wj': NoeVec3((0.0, 0.0, -0.2967059910297394)), 'hairside_l_03_wj': NoeVec3((0.0, 0.0, -0.0872664600610733)), 'hairside_l_04_wj': NoeVec3((0.0, 0.0, -0.10471980273723602)), 
    'hairside_l_05_wj': NoeVec3((0.0, 0.0, -0.06981316953897476)), 'hairside_l_06_wj': NoeVec3((0.0, 0.0, -0.06981316953897476)), 'hairside_r_01_wj': NoeVec3((0.3490658104419708, 0.27925270795822144, -2.0943949222564697)), 'hairside_r_02_wj': NoeVec3((0.0, 0.0, 0.2967059910297394)), 
    'hairside_r_03_wj': NoeVec3((0.0, 0.0, 0.0872664600610733)), 'hairside_r_04_wj': NoeVec3((0.0, 0.0, 0.10471980273723602)), 'hairside_r_05_wj': NoeVec3((0.0, 0.0, 0.06981316953897476)), 'hairside_r_06_wj': NoeVec3((0.0, 0.0, 0.06981316953897476)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'hairback_c_04_wj': NoeVec3((0.0, 0.15707960724830627, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.495820999145508, 0.2094395011663437, -1.4311699867248535)), 'hairback_l_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 
    'hairback_l_03_wj': NoeVec3((0.0, 0.0872664600610733, 0.0872664600610733)), 'hairback_l_04_wj': NoeVec3((0.0, 0.3490658104419708, 0.0)), 'hairback_r_01_wj': NoeVec3((2.495820999145508, 0.2094395011663437, -1.7104229927062988)), 
    'hairback_r_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 'hairback_r_03_wj': NoeVec3((0.0, 0.0872664600610733, -0.0872664600610733)), 'hairback_r_04_wj': NoeVec3((0.0, 0.3490658104419708, 0.0))}, 
    'ARI': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.18325960636138916, -1.570796012878418)), 
    'skirt_a_02_wj': NoeVec3((0.0, 0.024434609338641167, 0.0)), 'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.08028514683246613, -1.1693710088729858)), 'skirt_b_02_wj': NoeVec3((0.0, 0.05235987901687622, -0.0872664600610733)), 
    'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.13089969754219055, -1.0471980571746826)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_d_01_wj': NoeVec3((-2.268928050994873, 0.3141593039035797, -1.2042770385742188)), 
    'skirt_d_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.792526960372925, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.022689279168844223, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.268928050994873, 0.3141593039035797, -1.9373149871826172)), 'skirt_f_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.13089969754219055, -2.0943949222564697)), 
    'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.08028514683246613, -1.9722219705581665)), 'skirt_h_02_wj': NoeVec3((0.0, 0.05235987901687622, 0.0872664600610733)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, 0.03490658104419708, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.7853981852531433, 0.01745329052209854, -1.570796012878418)), 
    'hair_r_01_wj': NoeVec3((0.7853981852531433, 0.01745329052209854, -1.570796012878418)), 'hairside_l_01_wj': NoeVec3((0.0, -0.1221729964017868, -1.570796012878418)), 'hairside_l_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.10471980273723602)), 
    'hairside_l_03_wj': NoeVec3((0.0, -0.01745329052209854, 0.06981316953897476)), 'hairside_l_04_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 'hairside_l_05_wj': NoeVec3((0.0, 0.22689279913902283, -0.2967059910297394)), 
    'hairside_r_01_wj': NoeVec3((0.0, -0.1221729964017868, -1.570796012878418)), 'hairside_r_02_wj': NoeVec3((0.0, -0.1745329052209854, -0.10471980273723602)), 'hairside_r_03_wj': NoeVec3((0.0, -0.01745329052209854, -0.06981316953897476)), 
    'hairside_r_04_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 'hairside_r_05_wj': NoeVec3((0.0, 0.22689279913902283, 0.2967059910297394)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'hairback_c_04_wj': NoeVec3((0.0, 0.15707960724830627, 0.0)), 
    'hairback_l_01_wj': NoeVec3((-2.495820999145508, 0.2094395011663437, -1.4311699867248535)), 'hairback_l_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 'hairback_l_03_wj': NoeVec3((0.0, 0.0872664600610733, 0.0872664600610733)), 
    'hairback_l_04_wj': NoeVec3((0.0, 0.3490658104419708, 0.0)), 'hairback_r_01_wj': NoeVec3((2.495820999145508, 0.2094395011663437, -1.7104229927062988)), 'hairback_r_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 
    'hairback_r_03_wj': NoeVec3((0.0, 0.0872664600610733, -0.0872664600610733)), 'hairback_r_04_wj': NoeVec3((0.0, 0.3490658104419708, 0.0))}, 
    'ART': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_a_02_wj': NoeVec3((0.0, 0.03490658104419708, 0.0)), 'skirt_b_01_wj': NoeVec3((-0.9599310755729675, 0.0, -1.326449990272522)), 'skirt_b_02_wj': NoeVec3((0.0, -0.03490658104419708, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0872664600610733, -1.291543960571289)), 
    'skirt_c_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 'skirt_d_01_wj': NoeVec3((-2.268928050994873, 0.2967059910297394, -1.3613569736480713)), 'skirt_d_02_wj': NoeVec3((0.0, 0.06981316953897476, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8274331092834473, 1.570796012878418)), 
    'skirt_e_02_wj': NoeVec3((0.0, 0.05235987901687622, 0.0)), 'skirt_f_01_wj': NoeVec3((2.268928050994873, 0.2967059910297394, -1.780236005783081)), 'skirt_f_02_wj': NoeVec3((0.0, 0.06981316953897476, 0.0)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0872664600610733, -1.8500490188598633)), 'skirt_g_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.9599310755729675, 0.0, -1.815142035484314)), 'skirt_h_02_wj': NoeVec3((0.0, -0.03490658104419708, 0.0)), 
    'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.13962629437446594, 0.2617993950843811, -2.268928050994873)), 
    'hair_ponytail_01_wj': NoeVec3((0.0, 0.3839724063873291, -1.570796012878418)), 'hair_ponytail_02_wj': NoeVec3((0.0, -0.2967059910297394, 0.0)), 'hair_ponytail_03_wj': NoeVec3((0.0, -0.06981316953897476, 0.0)), 'hair_ponytail_04_wj': NoeVec3((0.0, -0.13962629437446594, 0.0)), 
    'hair_ponytail_05_wj': NoeVec3((0.0, -0.1745329052209854, 0.0)), 'hair_r_01_wj': NoeVec3((-0.3490658104419708, 0.0872664600610733, -2.0420351028442383)), 'hairside_l_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.6057029962539673)), 
    'hairside_l_02_wj': NoeVec3((0.0, -0.4188790023326874, 0.19198620319366455)), 'hairside_l_03_wj': NoeVec3((0.0, 0.3490658104419708, 0.05235987901687622)), 'hairside_l_04_wj': NoeVec3((0.0, 0.1745329052209854, -0.1745329052209854)), 
    'hairside_l_05_wj': NoeVec3((0.0, 0.13962629437446594, -0.13962629437446594)), 'hairside_r_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.535889983177185)), 'hairside_r_02_wj': NoeVec3((0.0, -0.4188790023326874, -0.19198620319366455)), 
    'hairside_r_03_wj': NoeVec3((0.0, 0.3490658104419708, -0.05235987901687622)), 'hairside_r_04_wj': NoeVec3((0.0, 0.1745329052209854, 0.1745329052209854)), 'hairside_r_05_wj': NoeVec3((0.0, 0.13962629437446594, 0.13962629437446594)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'hairback_c_04_wj': NoeVec3((0.0, 0.15707960724830627, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.495820999145508, 0.2094395011663437, -1.4311699867248535)), 'hairback_l_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 'hairback_l_03_wj': NoeVec3((0.0, 0.0872664600610733, 0.0872664600610733)), 
    'hairback_l_04_wj': NoeVec3((0.0, 0.3490658104419708, 0.0)), 'hairback_r_01_wj': NoeVec3((2.495820999145508, 0.2094395011663437, -1.7104229927062988)), 'hairback_r_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 'hairback_r_03_wj': NoeVec3((0.0, 0.0872664600610733, -0.0872664600610733)), 
    'hairback_r_04_wj': NoeVec3((0.0, 0.3490658104419708, 0.0))},
    'G5A': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((-4.768378971675702e-07, -0.028681350871920586, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.6454681158065796, -0.0037875559646636248, -1.2750450372695923)), 'skirt_b_02_wj': NoeVec3((-0.0026594980154186487, 0.10391999781131744, -0.05169770121574402)), 'skirt_c_01_wj': NoeVec3((-1.5124499797821045, 0.2100415974855423, -1.1360629796981812)), 
    'skirt_c_02_wj': NoeVec3((0.0, 0.1745329052209854, -0.0872664600610733)), 'skirt_d_01_wj': NoeVec3((-2.4197421073913574, 0.5604689121246338, -1.2464569807052612)), 'skirt_d_02_wj': NoeVec3((-4.768378857988864e-06, 0.3490658104419708, -0.03490832820534706)), 
    'skirt_e_01_wj': NoeVec3((4.768378971675702e-07, 2.5172879695892334, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.3023433983325958, 0.0)), 'skirt_f_01_wj': NoeVec3((2.4197421073913574, 0.5604689121246338, -1.89513099193573)), 
    'skirt_f_02_wj': NoeVec3((5.858948043169221e-06, 0.3490658104419708, 0.03490832820534706)), 'skirt_g_01_wj': NoeVec3((1.5124499797821045, 0.2100415974855423, -2.0055229663848877)), 'skirt_g_02_wj': NoeVec3((0.0, 0.1745329052209854, 0.08726593852043152)), 
    'skirt_h_01_wj': NoeVec3((0.6454681158065796, -0.0037872770335525274, -1.8665419816970825)), 'skirt_h_02_wj': NoeVec3((0.0026589040644466877, 0.10392089933156967, 0.05169770121574402)), 'spine_wj': NoeVec3((0.0, -0.19305090606212616, 1.5702730417251587)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((-0.001871446962468326, -1.344391942024231, -3.1415929794311523)), 'breast_r_wj': NoeVec3((-0.001871446962468326, -1.344391942024231, -3.1415929794311523)), 
    'face_root': NoeVec3((-0.0007658819085918367, -0.17080259323120117, 0.004495671018958092)), 'hair_chara_root': NoeVec3((-0.0007683131261728704, -0.1882563978433609, 0.004509266931563616)), 'hairaccessories_a_01_wj': NoeVec3((6.946217763470486e-05, -0.05494314059615135, 3.137578010559082)), 
    'hairaccessories_a_02_wj': NoeVec3((0.0, -0.003193953074514866, 0.0)), 'hairaccessories_b_01_wj': NoeVec3((6.946217763470486e-05, -0.05494314059615135, 3.137578010559082)), 'hairaccessories_b_02_wj': NoeVec3((-1.7453290638513863e-05, -0.0006108651868999004, -0.00043633230961859226)), 
    'hairaho_01_wj': NoeVec3((-0.019633209332823753, -0.48825061321258545, -1.6760799884796143)), 'hairaho_02_wj': NoeVec3((0.0, 0.0, -0.6356313824653625)), 'hairfront_a_01_wj': NoeVec3((0.008380337618291378, -0.1310953050851822, 2.6446969509124756)), 
    'hairfront_b_01_wj': NoeVec3((0.011147580109536648, -0.17975670099258423, 2.459588050842285)), 'hairfront_b_02_wj': NoeVec3((-0.04257626086473465, 0.6271054744720459, -0.23209740221500397)), 'hairside_l_01_wj': NoeVec3((-0.0017048110021278262, 0.00916739460080862, -3.0441160202026367)), 
    'hairside_l_02_wj': NoeVec3((0.0104370703920722, 0.02666863054037094, -0.4035550057888031)), 'hairside_r_01_wj': NoeVec3((0.002109142951667309, 0.0061197178438305855, 3.020134925842285)), 'hairside_r_02_wj': NoeVec3((-0.010175270028412342, 0.0316777303814888, 0.4481481909751892)), 
    'hair_root': NoeVec3((0.15334460139274597, -0.0007504916284233332, -1.5664160251617432)), 'hairback_c_01_wj': NoeVec3((0.0059515731409192085, 3.106215000152588, 1.5708839893341064)), 'hairback_c_02_wj': NoeVec3((-0.027174780145287514, -0.05347688868641853, 0.0019373149843886495)), 
    'hairback_c_03_wj': NoeVec3((0.09208357334136963, -0.023247789591550827, -0.00874409917742014)), 'hairback_c_04_wj': NoeVec3((-0.10304419696331024, -0.09009390324354172, 0.019128810614347458)), 'hairback_l_01_wj': NoeVec3((-1.592421054840088, 0.01846558041870594, -1.5254000425338745)), 
    'hairback_l_02_wj': NoeVec3((-0.2920460104942322, -0.05499532073736191, 0.03015929087996483)), 'hairback_l_03_wj': NoeVec3((-0.06455972790718079, -0.05431465059518814, 0.010297439992427826)), 'hairback_l_04_wj': NoeVec3((0.002495785942301154, -0.22535690665245056, -0.0009599223849363625)), 
    'hairback_r_01_wj': NoeVec3((1.5924040079116821, 0.01846558041870594, -1.6162270307540894)), 'hairback_r_02_wj': NoeVec3((0.2920284867286682, -0.05499532073736191, -0.03015929087996483)), 'hairback_r_03_wj': NoeVec3((0.07162830978631973, -0.056670840829610825, -0.01160643994808197)), 
    'hairback_r_04_wj': NoeVec3((-0.009895982220768929, -0.22533950209617615, 0.0037873650435358286))}, 
    'G5K': {'lskirt_a_01_wj': NoeVec3((0.0, 0.0024434609804302454, -1.570796012878418)), 'lskirt_a_02_wj': NoeVec3((0.0, 0.036023590713739395, 0.0)), 'lskirt_a_03_wj': NoeVec3((0.0, -0.0037175510078668594, 0.0)), 'lskirt_b_01_wj': NoeVec3((-0.5795888900756836, 0.06609562039375305, -1.470229983329773)), 
    'lskirt_b_02_wj': NoeVec3((0.0, -0.013369220308959484, -0.11309730261564255)), 'lskirt_b_03_wj': NoeVec3((0.0, -0.01160643994808197, 0.005637412890791893)), 'lskirt_c_01_wj': NoeVec3((-2.214858055114746, 0.13821260631084442, -1.389333963394165)), 
    'lskirt_c_02_wj': NoeVec3((0.3770608901977539, 0.1739221066236496, -0.021851519122719765)), 'lskirt_c_03_wj': NoeVec3((0.11107280105352402, 0.005742133129388094, -0.005811946000903845)), 'lskirt_d_01_wj': NoeVec3((-2.6118149757385254, 0.38095301389694214, -1.3564180135726929)), 
    'lskirt_d_02_wj': NoeVec3((0.4991990923881531, 0.39248961210250854, -0.025342179462313652)), 'lskirt_d_03_wj': NoeVec3((-0.00031415928970091045, -1.7453290638513863e-05, 1.7453290638513863e-05)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.668555974960327, 1.570796012878418)), 
    'lskirt_e_02_wj': NoeVec3((0.0, 0.39360669255256653, 0.0)), 'lskirt_e_03_wj': NoeVec3((0.0, 0.05464626103639603, 0.0)), 'lskirt_f_01_wj': NoeVec3((2.6118500232696533, 0.38091808557510376, -1.785140037536621)), 'lskirt_f_02_wj': NoeVec3((-0.499460905790329, 0.39247220754623413, 0.025342179462313652)), 
    'lskirt_f_03_wj': NoeVec3((0.0008377581252716482, -5.2359879191499203e-05, -3.4906581277027726e-05)), 'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.13821260631084442, -1.7522579431533813)), 'lskirt_g_02_wj': NoeVec3((-0.001989674987271428, 0.1258208006620407, 0.12234760075807571)), 
    'lskirt_g_03_wj': NoeVec3((-3.4906581277027726e-05, 0.003944444004446268, 0.007190756034106016)), 'lskirt_h_01_wj': NoeVec3((1.570796012878418, 0.06607816368341446, -1.6713800430297852)), 'lskirt_h_02_wj': NoeVec3((0.00062831852119416, 0.08724901080131531, 0.07332128286361694)), 
    'lskirt_h_03_wj': NoeVec3((-0.00010471980203874409, -0.005672319792211056, 0.01162389013916254)), 'skirt_a_01_wj': NoeVec3((-4.768378971675702e-07, -0.11449480056762695, -1.570796012878418)), 'skirt_a_02_wj': NoeVec3((1.6021900250962062e-07, 0.06923965364694595, 0.0)), 
    'skirt_b_01_wj': NoeVec3((-0.6457229256629944, -0.02627227082848549, -1.2581080198287964)), 'skirt_b_02_wj': NoeVec3((-0.0026564609725028276, 0.1010081022977829, -0.051676228642463684)), 'skirt_c_01_wj': NoeVec3((-1.514515995979309, 0.2100888043642044, -1.1459189653396606)), 
    'skirt_c_02_wj': NoeVec3((0.0036839889362454414, 0.1868060976266861, -0.0872664600610733)), 'skirt_d_01_wj': NoeVec3((-2.4318718910217285, 0.5383433103561401, -1.2696939706802368)), 'skirt_d_02_wj': NoeVec3((-0.00015830989286769181, 0.2807047963142395, -0.035501569509506226)), 
    'skirt_e_01_wj': NoeVec3((3.1415929794311523, 0.6243042945861816, -1.570796012878418)), 'skirt_e_02_wj': NoeVec3((-4.768378971675702e-07, 0.3023433983325958, 0.0)), 'skirt_f_01_wj': NoeVec3((2.4318718910217285, 0.5383433103561401, -1.871901035308838)), 
    'skirt_f_02_wj': NoeVec3((0.0001597202935954556, 0.28070300817489624, 0.03550191968679428)), 'skirt_g_01_wj': NoeVec3((1.514515995979309, 0.21008700132369995, -1.995661973953247)), 'skirt_g_02_wj': NoeVec3((-0.003684530034661293, 0.18507120013237, 0.08726576715707779)), 
    'skirt_h_01_wj': NoeVec3((0.6457229256629944, -0.026272090151906013, -1.883471965789795)), 'skirt_h_02_wj': NoeVec3((0.002657559933140874, 0.10100830346345901, 0.051676228642463684)), 'spine_wj': NoeVec3((0.0, -0.19305090606212616, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((-4.3441590946713404e-07, -1.3443750143051147, -3.1415929794311523)), 'breast_r_wj': NoeVec3((-4.3441590946713404e-07, -1.3443750143051147, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.0, 1.0552030005328561e-07)), 
    'eye_root': NoeVec3((0.0, 0.00027792449691332877, 0.0)), 'hair_chara_root': NoeVec3((-0.00027792449691332877, 1.7094630493375007e-06, -1.570796012878418)), 'hair_b_l_01_wj': NoeVec3((0.0003137683088425547, 0.8886867761611938, -0.7333176136016846)), 
    'hair_b_r_01_wj': NoeVec3((-0.0001917139015858993, 0.6384589076042175, -2.17455792427063)), 'hair_c_01_wj': NoeVec3((0.00010471590212546289, 0.011466809548437595, -1.1543430089950562)), 'hair_l_01_wj': NoeVec3((0.0001743579050526023, 0.39210569858551025, -0.9351997971534729)), 
    'hair_l_side_01_wj': NoeVec3((-8.725267252884805e-05, 0.05216788873076439, -1.8722319602966309)), 'hair_l_side_02_wj': NoeVec3((0.006335493177175522, -0.1540950983762741, -0.12170179933309555)), 'hair_r_01_wj': NoeVec3((-3.491356983431615e-05, -0.07051129639148712, -1.6766159534454346)), 
    'hair_r_side_01_wj': NoeVec3((6.980654143262655e-05, 0.03015929087996483, -1.322052001953125)), 'hair_r_side_02_wj': NoeVec3((-0.004275986924767494, -0.2010270059108734, 0.14161600172519684)), 'hair_root': NoeVec3((-0.00027792449691332877, 1.7094630493375007e-06, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((0.022078419104218483, 2.87001895904541, 1.576712965965271)), 'hairback_c_02_wj': NoeVec3((0.0, 0.315189003944397, -0.007278022821992636)), 'hairback_c_03_wj': NoeVec3((-0.0001396235020365566, -0.005550147034227848, -0.020315630361437798)), 
    'hairback_c_04_wj': NoeVec3((1.7453639884479344e-05, 0.004956734832376242, -0.020577430725097656)), 'hairback_l_01_wj': NoeVec3((-1.867885947227478, 0.0823795422911644, -1.3090840578079224)), 'hairback_l_02_wj': NoeVec3((0.0, 0.25021040439605713, 0.028850290924310684)), 
    'hairback_l_03_wj': NoeVec3((0.0, 0.02958332933485508, 0.010175270028412342)), 'hairback_l_04_wj': NoeVec3((0.0, 0.01679006963968277, 0.008621926419436932)), 'hairback_r_01_wj': NoeVec3((1.9522379636764526, 0.1074075996875763, -1.8313390016555786)), 
    'hairback_r_02_wj': NoeVec3((0.0, 0.24408429861068726, -0.044767700135707855)), 'hairback_r_03_wj': NoeVec3((0.0, 0.03132865950465202, -0.008063421584665775)), 'hairback_r_04_wj': NoeVec3((0.0, 0.017505649477243423, -0.009267698042094707))},
    'G5M': {'lskirt_a_01_wj': NoeVec3((0.0, 0.0059166657738387585, -1.570796012878418)), 'lskirt_a_02_wj': NoeVec3((0.0, -0.0008726646192371845, 0.0)), 'lskirt_b_01_wj': NoeVec3((-0.11952020227909088, 0.023631760850548744, -1.376505970954895)), 
    'lskirt_b_02_wj': NoeVec3((-0.03726277872920036, 0.007312930189073086, -0.00195476901717484)), 'lskirt_c_01_wj': NoeVec3((-1.9006459712982178, 0.14014990627765656, -1.183385968208313)), 'lskirt_c_02_wj': NoeVec3((-0.07440338283777237, 0.06363470107316971, 0.027663469314575195)), 
    'lskirt_d_01_wj': NoeVec3((-2.5189640522003174, 0.3948458135128021, -1.3013520240783691)), 'lskirt_d_02_wj': NoeVec3((-0.05593780055642128, 0.11934559792280197, 0.021868979558348656)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.626283884048462, 1.570796012878418)), 
    'lskirt_e_02_wj': NoeVec3((0.0, 0.1131846010684967, 0.0)), 'lskirt_f_01_wj': NoeVec3((2.5174460411071777, 0.39646899700164795, -1.8420549631118774)), 'lskirt_f_02_wj': NoeVec3((0.05672319978475571, 0.12166690081357956, -0.022183140739798546)), 
    'lskirt_g_01_wj': NoeVec3((1.9012049436569214, 0.14018480479717255, -1.957666039466858)), 'lskirt_g_02_wj': NoeVec3((0.07393214851617813, 0.06312856078147888, -0.027488939464092255)), 'lskirt_h_01_wj': NoeVec3((1.6903339624404907, 0.023631760850548744, -1.765086054801941)), 
    'lskirt_h_02_wj': NoeVec3((0.03722786903381348, 0.00195476901717484, -0.007312930189073086)), 'skirt_a_01_wj': NoeVec3((3.028984110642341e-06, -0.028681350871920586, -1.570796012878418)), 'skirt_b_01_wj': NoeVec3((-0.6452500224113464, -0.011757849715650082, -1.295261025428772)), 
    'skirt_b_02_wj': NoeVec3((-0.002659322926774621, 0.03544728830456734, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.5119999647140503, 0.2049645036458969, -1.1345839500427246)), 'skirt_c_02_wj': NoeVec3((0.0241530891507864, 0.14758920669555664, -0.030548499897122383)), 
    'skirt_d_01_wj': NoeVec3((-2.421173095703125, 0.5534247159957886, -1.2491999864578247)), 'skirt_d_02_wj': NoeVec3((0.0011977249523624778, 0.23975589871406555, -0.030189480632543564)), 'skirt_e_01_wj': NoeVec3((3.1415929794311523, 0.6397852897644043, -1.570796012878418)), 
    'skirt_e_02_wj': NoeVec3((-9.536740890325746e-07, 0.244637593626976, 0.0)), 'skirt_f_01_wj': NoeVec3((2.421173095703125, 0.5534247159957886, -1.8923909664154053)), 'skirt_f_02_wj': NoeVec3((-0.0011963850120082498, 0.23975589871406555, 0.03018965944647789)), 
    'skirt_g_01_wj': NoeVec3((1.5120010375976562, 0.2049645036458969, -2.0070059299468994)), 'skirt_g_02_wj': NoeVec3((-0.024154139682650566, 0.14758910238742828, 0.030549539253115654)), 'skirt_h_01_wj': NoeVec3((0.6452516913414001, -0.011757319793105125, -1.846331000328064)), 
    'skirt_h_02_wj': NoeVec3((0.00265970709733665, 0.0354483388364315, 0.0)), 'spine_wj': NoeVec3((0.0, -0.24893629550933838, 1.5700629949569702)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, 3.1415929794311523)), 
    'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'hair_chara_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((0.0, -0.10744249820709229, -1.3654580116271973)), 'hair_l_02_wj': NoeVec3((-0.04731588065624237, -0.030246559530496597, -0.4528082013130188)), 
    'hair_l_03_wj': NoeVec3((-0.04029965028166771, -0.14814350008964539, -0.312204509973526)), 'hair_r_01_wj': NoeVec3((2.6660780906677246, -0.10744249820709229, -1.7761340141296387)), 'hair_r_02_wj': NoeVec3((0.008220500312745571, 0.22907449305057526, -0.3951948881149292)), 
    'hair_r_03_wj': NoeVec3((0.03436553105711937, 0.2737025022506714, -0.211952805519104)), 'hairfront_l_01_wj': NoeVec3((0.0, -0.5876349210739136, -1.433351993560791)), 'hairfront_l_02_wj': NoeVec3((-0.012339480221271515, 0.5897293090820312, -0.022252950817346573)), 
    'hairfront_l_03_wj': NoeVec3((1.7453290638513863e-05, 0.30087730288505554, -0.008587020449340343)), 'hairfront_r_01_wj': NoeVec3((0.0, -0.5876349210739136, -1.7082409858703613)), 'hairfront_r_02_wj': NoeVec3((0.012322019785642624, 0.5897293090820312, 0.022235490381717682)), 
    'hairfront_r_03_wj': NoeVec3((-1.7453290638513863e-05, 0.30085989832878113, 0.008587020449340343)), 'hairside_l_01_wj': NoeVec3((0.0, -0.069673553109169, -1.9006110429763794)), 'hairside_l_02_wj': NoeVec3((0.001797689008526504, -0.20277230441570282, 0.024783670902252197)), 
    'hairside_l_03_wj': NoeVec3((0.024836039170622826, -0.3222750127315521, 0.07655014097690582)), 'hairside_l_04_wj': NoeVec3((0.05291837826371193, 0.0008377581252716482, 0.07859216630458832)), 'hairside_r_01_wj': NoeVec3((0.0, -0.069673553109169, -1.2409809827804565)), 
    'hairside_r_02_wj': NoeVec3((-0.001797689008526504, -0.20277230441570282, -0.024766219779849052)), 'hairside_r_03_wj': NoeVec3((-0.024836039170622826, -0.3222750127315521, -0.07656759768724442)), 'hairside_r_04_wj': NoeVec3((-0.05291837826371193, 0.0008377581252716482, -0.07859216630458832)), 
    'hair_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((-3.087678909301758, 0.017941990867257118, -1.5698360204696655)), 'hairback_c_02_wj': NoeVec3((-0.06312856078147888, -0.05331981182098389, 0.004502948839217424)), 
    'hairback_c_03_wj': NoeVec3((0.08906415104866028, -0.023369960486888885, -0.008482299745082855)), 'hairback_c_04_wj': NoeVec3((-0.09498082101345062, -0.05600761994719505, 0.01441641990095377)), 'hairback_l_01_wj': NoeVec3((-1.5933279991149902, 0.0010297440458089113, -1.5253829956054688)), 
    'hairback_l_02_wj': NoeVec3((-0.29195868968963623, -0.05499532073736191, 0.03015929087996483)), 'hairback_l_03_wj': NoeVec3((-0.07159339636564255, -0.056670840829610825, 0.0115889897570014)), 'hairback_l_04_wj': NoeVec3((-0.031154129654169083, -0.06325074285268784, 0.007051129825413227)), 
    'hairback_r_01_wj': NoeVec3((0.022514749318361282, 3.1405630111694336, 1.5253829956054688)), 'hairback_r_02_wj': NoeVec3((0.03729768097400665, -0.003839723998680711, 0.05691519007086754)), 'hairback_r_03_wj': NoeVec3((0.4660727083683014, -0.07742281258106232, 0.05017821118235588)), 
    'hairback_r_04_wj': NoeVec3((-0.11140439659357071, 0.02546435035765171, 0.05291837826371193))}, 
    'G5Y': {'lskirt_a_01_wj': NoeVec3((0.0, 0.005899212788790464, -1.570796012878418)), 'lskirt_a_02_wj': NoeVec3((0.0, -0.0008726646192371845, 0.0)), 'lskirt_b_01_wj': NoeVec3((-0.7935140132904053, 0.0008726646192371845, -1.5403579473495483)), 
    'lskirt_b_02_wj': NoeVec3((-0.028605949133634567, 0.0218864306807518, 0.00568977277725935)), 'lskirt_c_01_wj': NoeVec3((-1.534703016281128, 0.14254100620746613, -1.3218599557876587)), 'lskirt_c_02_wj': NoeVec3((-0.03380703181028366, 0.21582740545272827, -0.13901549577713013)), 
    'lskirt_d_01_wj': NoeVec3((-2.6669681072235107, 0.35445889830589294, -1.3943259716033936)), 'lskirt_d_02_wj': NoeVec3((0.4075517952442169, 0.3344050943851471, -0.028047440573573112)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.6700220108032227, 1.570796012878418)), 
    'lskirt_e_02_wj': NoeVec3((0.0, 0.37159809470176697, 0.0)), 'lskirt_e_03_wj': NoeVec3((0.0, 0.06400121748447418, 0.0)), 'lskirt_f_01_wj': NoeVec3((2.6670379638671875, 0.3544763922691345, -1.7472490072250366)), 'lskirt_f_02_wj': NoeVec3((-0.40748199820518494, 0.3344050943851471, 0.028047440573573112)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.1425585001707077, -1.8196979761123657)), 'lskirt_g_02_wj': NoeVec3((-0.00251327408477664, 0.22066199779510498, 0.1311091035604477)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, 0.000855211284942925, -1.6012170314788818)), 
    'lskirt_h_02_wj': NoeVec3((0.0, 0.021921329200267792, -0.005532694049179554)), 'skirt_a_01_wj': NoeVec3((1.120841943702544e-06, -0.028681350871920586, -1.570796012878418)), 'skirt_a_02_wj': NoeVec3((-6.19888578512473e-06, 0.04594649001955986, -4.768378971675702e-07)), 
    'skirt_b_01_wj': NoeVec3((-0.6452500224113464, -0.011757849715650082, -1.295261025428772)), 'skirt_b_02_wj': NoeVec3((-0.0026588519103825092, 0.06449061632156372, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.5119999647140503, 0.2049645036458969, -1.1345839500427246)), 
    'skirt_c_02_wj': NoeVec3((0.0241530891507864, 0.14758920669555664, -0.030548499897122383)), 'skirt_d_01_wj': NoeVec3((-2.421173095703125, 0.5534247159957886, -1.2491999864578247)), 'skirt_d_02_wj': NoeVec3((0.0014882549876347184, 0.27352631092071533, -0.029043149203062057)), 
    'skirt_e_01_wj': NoeVec3((2.3841889174036623e-07, 2.5018069744110107, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((-9.536740890325746e-07, 0.244637593626976, 0.0)), 'skirt_f_01_wj': NoeVec3((2.421173095703125, 0.5534247159957886, -1.8923909664154053)), 
    'skirt_f_02_wj': NoeVec3((-0.0014863009564578533, 0.27352631092071533, 0.029043149203062057)), 'skirt_g_01_wj': NoeVec3((1.5120010375976562, 0.2049645036458969, -2.0070059299468994)), 'skirt_g_02_wj': NoeVec3((-0.024154139682650566, 0.14758910238742828, 0.030549539253115654)), 
    'skirt_h_01_wj': NoeVec3((0.6452516913414001, -0.011757319793105125, -1.846331000328064)), 'skirt_h_02_wj': NoeVec3((0.002659427933394909, 0.06449130922555923, 0.0)), 'spine_wj': NoeVec3((0.0, -0.24893629550933838, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 3.549353877474459e-08)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'hair_chara_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 
    'hair_a_l_side_01_wj': NoeVec3((0.0, -0.33646461367607117, -1.967702031135559)), 'hair_a_r_side_01_wj': NoeVec3((0.0, -0.33485889434814453, -1.1958470344543457)), 'hair_b_l_side_01_wj': NoeVec3((0.0, -0.7013431191444397, -0.9386032223701477)), 
    'hair_b_r_side_01_wj': NoeVec3((0.0, -0.7013257145881653, -2.202971935272217)), 'hair_c_01_wj': NoeVec3((0.0, 0.0, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((0.0, 0.12891000509262085, -1.2407200336456299)), 'hair_r_01_wj': NoeVec3((0.0, 0.13465219736099243, -1.8045660257339478)), 
    'hair_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((3.1415929794311523, -0.23198920488357544, -1.6387590169906616)), 'hairback_c_02_wj': NoeVec3((0.0, -0.17575469613075256, -0.06892304867506027)), 'hairback_c_03_wj': NoeVec3((0.0, -0.0521329902112484, -0.0008203046745620668)), 
    'hairback_c_04_wj': NoeVec3((0.0, -0.029705500230193138, -0.00047123889089562)), 'hairback_l_01_wj': NoeVec3((-2.356194019317627, -0.009843656793236732, -1.5854220390319824)), 'hairback_l_02_wj': NoeVec3((0.06354743987321854, 0.35243430733680725, 0.3183828890323639)), 
    'hairback_l_03_wj': NoeVec3((0.0, -0.4770508110523224, -0.4314629137516022)), 'hairback_l_04_wj': NoeVec3((0.0, -0.010716320015490055, -0.010733770206570625)), 'hairback_r_01_wj': NoeVec3((2.356194019317627, -0.010681410320103168, -1.5031650066375732)), 
    'hairback_r_02_wj': NoeVec3((-0.052499499171972275, 0.2877523899078369, -0.2514669895172119)), 'hairback_r_03_wj': NoeVec3((0.0, -0.4533666968345642, 0.39817941188812256)), 'hairback_r_04_wj': NoeVec3((0.0, -1.7453290638513863e-05, -1.7453290638513863e-05))}, 
    'GCC': {'lskirt_a_01_wj': NoeVec3((0.0, -0.013919070363044739, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7799859046936035, -0.04340285062789917, -1.4525049924850464)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.040142569690942764, -1.3065530061721802)), 
    'lskirt_d_01_wj': NoeVec3((-2.328356981277466, 0.22371980547904968, -1.343775987625122)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.825547933578491, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.328356981277466, 0.22371980547904968, -1.7978110313415527)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.040142569690942764, -1.8350390195846558)), 'lskirt_h_01_wj': NoeVec3((0.7799859046936035, -0.04340285062789917, -1.689087986946106)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'ribbon_chara_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 'ribbon_l_01_wj': NoeVec3((0.0, 2.727268934249878, 1.7142620086669922)), 'ribbon_r_01_wj': NoeVec3((0.0, 2.727268934249878, 1.4273300170898438)), 'ribbonring_l_01_wj': NoeVec3((-2.9382619857788086, 0.3464479148387909, -1.0250320434570312)), 
    'ribbonring_r_01_wj': NoeVec3((2.9382619857788086, 0.3464479148387909, -2.116560935974121)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'hair_l_01_wj': NoeVec3((0.0, 0.10983359813690186, -1.4872299432754517)), 'hair_l_02_wj': NoeVec3((0.038693949580192566, -0.20493659377098083, -0.3588047921657562)), 'hair_r_01_wj': NoeVec3((0.0, 0.13754940032958984, -1.6441349983215332)), 
    'hairside_l_01_wj': NoeVec3((0.0, -0.615769624710083, -1.8749899864196777)), 'hairside_r_01_wj': NoeVec3((0.0, -0.10473719984292984, -1.3647600412368774)), 'hairside_r_02_wj': NoeVec3((-0.00015707960119470954, -0.08628907799720764, -0.0015358900418505073)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((3.1415929794311523, -0.4689874053001404, -1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.5562539100646973, 0.0)), 
    'hairback_l_01_wj': NoeVec3((-2.482556104660034, -0.256912499666214, -1.7896610498428345)), 'hairback_l_02_wj': NoeVec3((0.0, -0.4893204867839813, 0.0)), 'hairback_r_01_wj': NoeVec3((2.482556104660034, -0.256912499666214, -1.3519320487976074)), 'hairback_r_02_wj': NoeVec3((0.0, -0.4893204867839813, 0.0))},
    'GCG': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.02094395086169243, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.3577924966812134, -0.027925269678235054, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.535889983177185, 0.11780969798564911, -1.326449990272522)), 'skirt_c_02_wj': NoeVec3((0.0, 0.06981316953897476, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.7052600383758545, 0.2705259919166565, -1.4660769701004028)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8448870182037354, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.7052600383758545, 0.2705259919166565, -1.6755160093307495)), 
    'skirt_g_01_wj': NoeVec3((1.535889983177185, 0.11780969798564911, -1.815142035484314)), 'skirt_g_02_wj': NoeVec3((0.0, 0.06981316953897476, 0.0)), 'skirt_h_01_wj': NoeVec3((0.3577924966812134, -0.027925269678235054, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((-0.003490658011287451, 0.05585053935647011, -1.623155951499939)), 'hair_l_01_wj': NoeVec3((-0.3769910931587219, 0.13788099586963654, -1.5149459838867188)), 
    'hair_r_01_wj': NoeVec3((0.4363322854042053, 0.0052359881810843945, -1.5882500410079956)), 'hairside_l_01_wj': NoeVec3((-0.0013089970452710986, -0.06283185631036758, -1.761036992073059)), 'hairside_r_01_wj': NoeVec3((0.0008726646192371845, -0.12740899622440338, -1.3857909440994263)), 
    'twintail_l_01_wj': NoeVec3((-0.14660769701004028, -1.1868239641189575, -1.9547690153121948)), 'twintail_l_02_wj': NoeVec3((0.09773843735456467, 0.2967059910297394, -0.1745329052209854)), 'twintail_l_03_wj': NoeVec3((0.23736479878425598, 0.48869219422340393, 0.471238911151886)), 
    'twintail_r_01_wj': NoeVec3((0.14660769701004028, -1.1868239641189575, -1.1868239641189575)), 'twintail_r_02_wj': NoeVec3((-0.09773843735456467, 0.2094395011663437, 0.1745329052209854)), 'twintail_r_03_wj': NoeVec3((-0.2565633952617645, 0.6126105785369873, -0.5078908205032349)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 
    'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'GCM': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0027038820553570986, -0.021863220259547234, -1.5769870281219482)), 
    'skirt_b_01_wj': NoeVec3((-0.3573648929595947, -0.028413090854883194, -1.4709789752960205)), 'skirt_c_01_wj': NoeVec3((-1.535889983177185, 0.11780969798564911, -1.326449990272522)), 'skirt_c_02_wj': NoeVec3((0.0, 0.06981316953897476, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.704580068588257, 0.2713620066642761, -1.4670560359954834)), 'skirt_e_01_wj': NoeVec3((0.0, 2.847172975540161, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.704580068588257, 0.2713620066642761, -1.674536943435669)), 
    'skirt_g_01_wj': NoeVec3((1.535889983177185, 0.11780969798564911, -1.815142035484314)), 'skirt_g_02_wj': NoeVec3((0.0, 0.06981316953897476, 0.0)), 'skirt_h_01_wj': NoeVec3((0.35736140608787537, -0.028413090854883194, -1.6706130504608154)), 
    'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.4363322854042053, 0.03576179966330528, -1.570796012878418)), 
    'hair_r_01_wj': NoeVec3((0.4363322854042053, 0.03576179966330528, -1.570796012878418)), 'hairside_l_01_wj': NoeVec3((0.0, -0.01745329052209854, -1.8500490188598633)), 'hairside_r_01_wj': NoeVec3((0.0, -0.01745329052209854, -1.291543960571289)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 
    'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'GCR': {'lskirt_a_01_wj': NoeVec3((0.0, -0.013919070363044739, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7799859046936035, -0.04340285062789917, -1.4525049924850464)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.040142569690942764, -1.3065530061721802)), 
    'lskirt_d_01_wj': NoeVec3((-2.328356981277466, 0.22371980547904968, -1.343775987625122)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.825547933578491, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.328356981277466, 0.22371980547904968, -1.7978110313415527)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.040142569690942764, -1.8350390195846558)), 'lskirt_h_01_wj': NoeVec3((0.7799859046936035, -0.04340285062789917, -1.689087986946106)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'ribbon_chara_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 'ribbon_l_01_wj': NoeVec3((0.0, 2.727268934249878, 1.7142620086669922)), 'ribbon_r_01_wj': NoeVec3((0.0, 2.727268934249878, 1.4273300170898438)), 
    'ribbonring_l_01_wj': NoeVec3((-2.9382619857788086, 0.3464479148387909, -1.0250320434570312)), 'ribbonring_r_01_wj': NoeVec3((2.9382619857788086, 0.3464479148387909, -2.116560935974121)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, 0.057595860213041306, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((0.0, 0.3901718854904175, -1.372527003288269)), 'hair_l_02_wj': NoeVec3((0.0, -0.45902159810066223, -0.7574728727340698)), 
    'hair_r_01_wj': NoeVec3((0.0, 0.3901683986186981, -1.7690659761428833)), 'hair_r_02_wj': NoeVec3((0.0, -0.45902159810066223, 0.7574728727340698)), 'hair_twintail_l_01_wj': NoeVec3((0.0, 0.10297439992427826, -1.5489799976348877)), 
    'hair_twintail_l_02_wj': NoeVec3((0.0, 0.02914699912071228, 0.2007129043340683)), 'hair_twintail_l_03_wj': NoeVec3((0.0, -0.22235490381717682, -0.44366270303726196)), 'hair_twintail_r_01_wj': NoeVec3((0.0, 0.10297439992427826, -1.5926129817962646)), 
    'hair_twintail_r_02_wj': NoeVec3((0.0, 0.02914699912071228, -0.2007129043340683)), 'hair_twintail_r_03_wj': NoeVec3((0.0, -0.22235490381717682, 0.44366270303726196)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((3.1415929794311523, -0.4689874053001404, -1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.5562539100646973, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.482556104660034, -0.256912499666214, -1.7896610498428345)), 
    'hairback_l_02_wj': NoeVec3((0.0, -0.4893204867839813, 0.0)), 'hairback_r_01_wj': NoeVec3((2.482556104660034, -0.256912499666214, -1.3519320487976074)), 'hairback_r_02_wj': NoeVec3((0.0, -0.4893204867839813, 0.0))},
    'GCS': {'lskirt_a_01_wj': NoeVec3((0.0, -0.013919070363044739, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7799859046936035, -0.04340285062789917, -1.4525049924850464)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.040142569690942764, -1.3065530061721802)), 
    'lskirt_d_01_wj': NoeVec3((-2.328356981277466, 0.22371980547904968, -1.343775987625122)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.825547933578491, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.328356981277466, 0.22371980547904968, -1.7978110313415527)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.040142569690942764, -1.8350390195846558)), 'lskirt_h_01_wj': NoeVec3((0.7799859046936035, -0.04340285062789917, -1.689087986946106)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 
    'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'ribbon_chara_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 'ribbon_l_01_wj': NoeVec3((0.0, 2.727268934249878, 1.7142620086669922)), 'ribbon_r_01_wj': NoeVec3((0.0, 2.727268934249878, 1.4273300170898438)), 
    'ribbonring_l_01_wj': NoeVec3((-2.9382619857788086, 0.3464479148387909, -1.0250320434570312)), 'ribbonring_r_01_wj': NoeVec3((2.9382619857788086, 0.3464479148387909, -2.116560935974121)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, 0.01837831921875477, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.4948183000087738, 0.0172787606716156, -1.5387870073318481)), 
    'hair_r_01_wj': NoeVec3((0.4497363865375519, -0.0172787606716156, -1.6028059720993042)), 'hairadd_l_01_wj': NoeVec3((-0.4188790023326874, 0.04769985005259514, -1.5810070037841797)), 'hairadd_r_01_wj': NoeVec3((0.4188790023326874, -0.04769985005259514, -1.5605859756469727)), 
    'hairside_l_01_wj': NoeVec3((0.0, -0.13950419425964355, -1.7671979665756226)), 'hairside_l_02_wj': NoeVec3((-0.02569125033915043, -0.1359436959028244, -0.1788787990808487)), 'hairside_r_01_wj': NoeVec3((0.0, -0.13950419425964355, -1.3743770122528076)), 
    'hairside_r_02_wj': NoeVec3((0.02569125033915043, -0.1359436959028244, 0.1788787990808487)), 'hair_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.4583699703216553, 1.570796012878418)), 
    'hairback_c_02_wj': NoeVec3((0.0, -0.39941689372062683, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.4936740398406982, -0.2701491117477417, -1.714298963546753)), 'hairback_l_02_wj': NoeVec3((0.0, -0.5186089277267456, 0.0)), 
    'hairback_r_01_wj': NoeVec3((2.4936740398406982, -0.2701491117477417, -1.4272949695587158)), 'hairback_r_02_wj': NoeVec3((0.0, -0.5186089277267456, 0.0))},
    'GCT': {'lskirt_a_01_wj': NoeVec3((0.0, -0.013919070363044739, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7799859046936035, -0.04340285062789917, -1.4525049924850464)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.040142569690942764, -1.3065530061721802)), 
    'lskirt_d_01_wj': NoeVec3((-2.328356981277466, 0.22371980547904968, -1.343775987625122)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.825547933578491, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.328356981277466, 0.22371980547904968, -1.7978110313415527)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.040142569690942764, -1.8350390195846558)), 'lskirt_h_01_wj': NoeVec3((0.7799859046936035, -0.04340285062789917, -1.689087986946106)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'ribbon_chara_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 'ribbon_l_01_wj': NoeVec3((0.0, 2.727268934249878, 1.7142620086669922)), 'ribbon_r_01_wj': NoeVec3((0.0, 2.727268934249878, 1.4273300170898438)), 
    'ribbonring_l_01_wj': NoeVec3((-2.9382619857788086, 0.3464479148387909, -1.0250320434570312)), 'ribbonring_r_01_wj': NoeVec3((2.9382619857788086, 0.3464479148387909, -2.116560935974121)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.03193952888250351, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((0.01518435962498188, 0.12723450362682343, -1.4521139860153198)), 
    'hair_r_01_wj': NoeVec3((-0.008726646192371845, 0.07504914700984955, -1.6842429637908936)), 'hairside_l_01_wj': NoeVec3((-0.0029670600779354572, 0.06579892337322235, -1.6170480251312256)), 'hairside_l_02_wj': NoeVec3((0.06824237108230591, -0.1745329052209854, -0.3291637897491455)), 
    'hairside_r_01_wj': NoeVec3((0.0029670600779354572, 0.06579892337322235, -1.5245449542999268)), 'hairside_r_02_wj': NoeVec3((-0.06824237108230591, -0.1745329052209854, 0.3291637897491455)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((0.0, 2.953097105026245, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.08377580344676971, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.4869469106197357, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.4434609413146973, 0.13439039885997772, -1.4660769701004028)), 
    'hairback_l_02_wj': NoeVec3((0.0, -0.13613569736480713, 0.0)), 'hairback_l_03_wj': NoeVec3((0.0, 0.5235987901687622, 0.0)), 'hairback_r_01_wj': NoeVec3((2.4434609413146973, 0.13439039885997772, -1.6755160093307495)), 'hairback_r_02_wj': NoeVec3((0.0, -0.13613569736480713, 0.0)), 
    'hairback_r_03_wj': NoeVec3((0.0, 0.5235987901687622, 0.0))},
    'GCY': {'lskirt_a_01_wj': NoeVec3((0.0, -0.013919070363044739, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7799859046936035, -0.04340285062789917, -1.4525049924850464)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.040142569690942764, -1.3065530061721802)), 
    'lskirt_d_01_wj': NoeVec3((-2.328356981277466, 0.22371980547904968, -1.343775987625122)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.825547933578491, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.328356981277466, 0.22371980547904968, -1.7978110313415527)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.040142569690942764, -1.8350390195846558)), 'lskirt_h_01_wj': NoeVec3((0.7799859046936035, -0.04340285062789917, -1.689087986946106)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'ribbon_chara_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 'ribbon_l_01_wj': NoeVec3((0.0, 2.727268934249878, 1.7142620086669922)), 'ribbon_r_01_wj': NoeVec3((0.0, 2.727268934249878, 1.4273300170898438)), 
    'ribbonring_l_01_wj': NoeVec3((-2.9382619857788086, 0.3464479148387909, -1.0250320434570312)), 'ribbonring_r_01_wj': NoeVec3((2.9382619857788086, 0.3464479148387909, -2.116560935974121)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.04363323003053665, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((0.0, -0.03490658104419708, -1.483530044555664)), 
    'hair_r_01_wj': NoeVec3((0.0, -0.03490658104419708, -1.6580630540847778)), 'hairacce_c_01_wj': NoeVec3((1.1170109510421753, 0.01745329052209854, -1.5184359550476074)), 'hairacce_c_02_wj': NoeVec3((0.0, -0.10471980273723602, 0.0)), 
    'hairside_l_01_wj': NoeVec3((-1.6580630540847778, 0.0, -1.6580630540847778)), 'hairside_l_02_wj': NoeVec3((0.0, -0.10471980273723602, -0.0872664600610733)), 'hairside_l_03_wj': NoeVec3((0.0, 0.06981316953897476, -0.5759587287902832)), 
    'hairside_r_01_wj': NoeVec3((1.6057029962539673, 0.0872664600610733, -1.5184359550476074)), 'hairside_r_02_wj': NoeVec3((0.0, -0.09845279902219772, 0.0872664600610733)), 'hairside_r_03_wj': NoeVec3((0.0, 0.04846237972378731, 0.37896859645843506)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((3.1415929794311523, 0.0, -1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 
    'hairback_c_04_wj': NoeVec3((0.0, 0.2617993950843811, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.462398052215576, 0.11277379840612411, -1.6050000190734863)), 'hairback_l_02_wj': NoeVec3((0.0, -0.1745329052209854, -0.0872664600610733)), 'hairback_l_03_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 
    'hairback_l_04_wj': NoeVec3((0.0, 0.4363322854042053, 0.0)), 'hairback_r_01_wj': NoeVec3((2.462398052215576, 0.11277379840612411, -1.5365949869155884)), 'hairback_r_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.0872664600610733)), 'hairback_r_03_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 
    'hairback_r_04_wj': NoeVec3((0.0, 0.4363322854042053, 0.0))},
    'KNA': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'skirt_a_02_wj': NoeVec3((0.0, -0.025307100266218185, 0.0)), 
    'skirt_b_01_wj': NoeVec3((-0.7882360816001892, -0.08088553696870804, -1.4897170066833496)), 'skirt_b_02_wj': NoeVec3((0.0010948049603030086, 0.011426649987697601, -0.00011334779992466792)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.2361290454864502)), 
    'skirt_c_02_wj': NoeVec3((0.0, 0.04814979061484337, 0.0)), 'skirt_d_01_wj': NoeVec3((-2.34437894821167, 0.19759400188922882, -1.3724329471588135)), 'skirt_d_02_wj': NoeVec3((-0.0018062059534713626, 0.045111700892448425, 0.0004355731070972979)), 
    'skirt_e_01_wj': NoeVec3((0.0, 2.878187894821167, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.04861946031451225, 0.0)), 'skirt_f_01_wj': NoeVec3((2.3443610668182373, 0.19759400188922882, -1.7691700458526611)), 
    'skirt_f_02_wj': NoeVec3((0.001807707012630999, 0.045111700892448425, -0.00043593961163423955)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.9054629802703857)), 'skirt_g_02_wj': NoeVec3((0.0, -0.018122969195246696, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.7882273197174072, -0.08088675886392593, -1.6518759727478027)), 'skirt_h_02_wj': NoeVec3((-0.0010847339872270823, 0.011427580378949642, 0.00011230500240344554)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'cardigan_a_01_wj': NoeVec3((-0.7737218737602234, 0.0835627019405365, -3.0510098934173584)), 'cardigan_a_02_wj': NoeVec3((0.0, -0.025747450068593025, 0.0)), 
    'cardigan_b_01_wj': NoeVec3((-1.5394330024719238, 0.17172010242938995, -2.9600090980529785)), 'cardigan_b_02_wj': NoeVec3((0.0, -0.14305570721626282, 0.0)), 'cardigan_c_01_wj': NoeVec3((0.6513218879699707, 2.93723201751709, 0.02305039018392563)), 
    'cardigan_c_02_wj': NoeVec3((0.13305220007896423, -0.2662028968334198, -0.04003069922327995)), 'cardigan_d_01_wj': NoeVec3((0.0, 2.840714931488037, 0.0)), 'cardigan_e_01_wj': NoeVec3((2.4902710914611816, 0.20436759293079376, 3.118536949157715)), 
    'cardigan_e_02_wj': NoeVec3((-0.1330574005842209, -0.2662028968334198, 0.040032271295785904)), 'cardigan_f_01_wj': NoeVec3((1.5394350290298462, 0.17172010242938995, 2.9600090980529785)), 'cardigan_f_02_wj': NoeVec3((0.0, -0.1430577039718628, 0.0)), 
    'cardigan_g_01_wj': NoeVec3((0.7737289071083069, 0.08356322348117828, 3.0510098934173584)), 'cardigan_g_02_wj': NoeVec3((0.0, -0.025746570900082588, 6.668798278042232e-07)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hair_c_01_wj': NoeVec3((-0.007624994032084942, -0.08693362772464752, -1.4831980466842651)), 'hair_l_01_wj': NoeVec3((-0.5425443053245544, 0.365192711353302, -1.3512059450149536)), 'hair_r_01_wj': NoeVec3((1.0902249813079834, 0.03879448026418686, -1.6934479475021362)), 
    'kanzashi_c_01_wj': NoeVec3((-1.436076045036316, 0.010468239895999432, -1.12916898727417)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-1.9784350395202637, 0.15723790228366852, -1.4028279781341553)), 
    'hairback_r_01_wj': NoeVec3((1.9784350395202637, 0.15723790228366852, -1.7387670278549194))},
    'KNC': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.10471980273723602, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.05235987901687622, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3613569736480713)), 'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.19198620319366455, -1.4137170314788818)), 
    'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.19198620319366455, -1.7278759479522705)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.780236005783081)), 
    'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.05235987901687622, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.01745329052209854, 0.0872664600610733, -1.4486229419708252)), 
    'hair_l_01_wj': NoeVec3((-0.811578094959259, 0.4118976891040802, -1.3910269737243652)), 'hair_r_01_wj': NoeVec3((0.820304811000824, 0.3839724063873291, -1.6929689645767212)), 'hairside_l_01_wj': NoeVec3((-1.3962630033493042, 0.16807520389556885, -1.483530044555664)), 
    'hairside_r_01_wj': NoeVec3((1.483530044555664, 0.23038350045681, -1.5428709983825684)), 'twintail_l_01_wj': NoeVec3((-2.4260079860687256, -0.019198620691895485, -1.4590950012207031)), 'twintail_l_02_wj': NoeVec3((0.0052359881810843945, -0.14660769701004028, 0.13439039885997772)), 
    'twintail_l_03_wj': NoeVec3((0.02617993950843811, -0.33510321378707886, -0.07853981852531433)), 'twintail_l_04_wj': NoeVec3((0.0, 0.5585054159164429, 0.0)), 'twintail_r_01_wj': NoeVec3((2.4260079860687256, -0.019198620691895485, -1.6824970245361328)), 
    'twintail_r_02_wj': NoeVec3((-0.0052359881810843945, -0.14660769701004028, -0.13439039885997772)), 'twintail_r_03_wj': NoeVec3((-0.02617993950843811, -0.33510321378707886, 0.07853981852531433)), 'twintail_r_04_wj': NoeVec3((0.0, 0.5585054159164429, 0.0)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 
    'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'KNK': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.15533429384231567, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7923794984817505, -0.111701101064682, -1.3962630033493042)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.239184021949768)), 'skirt_c_02_wj': NoeVec3((0.0, 0.05235987901687622, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3177969455718994, 0.259181410074234, -1.3046339750289917)), 'skirt_d_02_wj': NoeVec3((0.0, 0.05235987901687622, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.782054901123047, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.05235987901687622, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.303834915161133, 0.259181410074234, -1.8369590044021606)), 'skirt_f_02_wj': NoeVec3((0.0, 0.05235987901687622, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.9024089574813843)), 'skirt_g_02_wj': NoeVec3((0.0, 0.05235987901687622, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.7923794984817505, -0.111701101064682, -1.7453290224075317)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.06213371828198433, 0.12566369771957397, -1.1100289821624756)), 
    'hair_l_01_wj': NoeVec3((-1.1344640254974365, 0.5201081037521362, -1.1955510377883911)), 'hair_r_01_wj': NoeVec3((1.3229600191116333, 0.4415682852268219, -1.6266469955444336)), 'hairside_l_01_wj': NoeVec3((0.008377579972147942, -0.10175269842147827, -1.7558009624481201)), 
    'hairside_l_02_wj': NoeVec3((0.0, -0.2998476028442383, 0.17034409940242767)), 'hairside_l_03_wj': NoeVec3((0.0, 0.2094395011663437, 0.18500490486621857)), 'hairside_r_01_wj': NoeVec3((-0.008377579972147942, -0.10175269842147827, -1.3857909440994263)), 
    'hairside_r_02_wj': NoeVec3((0.0, -0.2998476028442383, -0.17034409940242767)), 'hairside_r_03_wj': NoeVec3((0.0, 0.2094395011663437, -0.18500490486621857)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((0.0, 2.9112091064453125, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, 0.008377579972147942, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.14546220004558563, 0.0)), 'hairback_c_04_wj': NoeVec3((0.0, 0.3074274957180023, 0.0)), 
    'hairback_l_01_wj': NoeVec3((-2.530726909637451, 0.24958209693431854, -1.4957469701766968)), 'hairback_l_02_wj': NoeVec3((0.0, -0.02705259993672371, -0.11257369816303253)), 'hairback_l_03_wj': NoeVec3((0.0, 0.19722220301628113, 0.022689279168844223)), 
    'hairback_l_04_wj': NoeVec3((0.0, 0.3141593039035797, 0.04886921867728233)), 'hairback_r_01_wj': NoeVec3((2.530726909637451, 0.24958209693431854, -1.6458460092544556)), 'hairback_r_02_wj': NoeVec3((0.0, -0.02705259993672371, 0.11257369816303253)), 
    'hairback_r_03_wj': NoeVec3((0.0, 0.19722220301628113, -0.022689279168844223)), 'hairback_r_04_wj': NoeVec3((0.0, 0.3141593039035797, -0.04886921867728233)), 'parka_a_01_wj': NoeVec3((-0.3066543936729431, 0.07330383360385895, -3.0124380588531494)), 
    'parka_a_02_wj': NoeVec3((0.0, -0.016755159944295883, 0.08552113175392151)), 'parka_a_03_wj': NoeVec3((0.0, 0.0, 0.07330383360385895)), 'parka_b_01_wj': NoeVec3((1.5742870569229126, 2.919935941696167, 0.19198620319366455)), 'parka_b_02_wj': NoeVec3((0.0, -0.15882499516010284, 0.0)), 
    'parka_c_01_wj': NoeVec3((0.0, 2.8068389892578125, 0.0)), 'parka_c_02_wj': NoeVec3((0.0, -0.16929690539836884, 0.0)), 'parka_d_01_wj': NoeVec3((1.5673060417175293, 0.22165679931640625, 2.949605941772461)), 'parka_d_02_wj': NoeVec3((0.0, -0.15882499516010284, 0.0)), 
    'parka_e_01_wj': NoeVec3((0.3066543936729431, 0.07330383360385895, 3.0124380588531494)), 'parka_e_02_wj': NoeVec3((0.0, -0.016755159944295883, -0.08552113175392151)), 'parka_e_03_wj': NoeVec3((0.0, 0.0, -0.07330383360385895))},
    'KNS': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.13962629437446594, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7941247820854187, -0.09599310904741287, -1.3788100481033325)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.291543960571289)), 'skirt_d_01_wj': NoeVec3((-2.3212881088256836, 0.27925270795822144, -1.3962630033493042)), 
    'skirt_e_01_wj': NoeVec3((0.0, 2.792526960372925, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3212881088256836, 0.27925270795822144, -1.7453290224075317)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.8500490188598633)), 
    'skirt_h_01_wj': NoeVec3((0.7941247820854187, -0.09599310904741287, -1.7627830505371094)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.1745329052209854, -1.570796012878418)), 
    'hair_l_01_wj': NoeVec3((-0.8028513789176941, 0.0, -1.483530044555664)), 'hair_r_01_wj': NoeVec3((0.8028513789176941, 0.0, -1.6580630540847778)), 'hairside_l_01_wj': NoeVec3((0.08203048259019852, -0.33161258697509766, -1.9024089574813843)), 
    'hairside_r_01_wj': NoeVec3((-0.08203048259019852, -0.33161258697509766, -1.239184021949768)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.2114059925079346, 1.570796012878418)), 
    'hairback_c_02_wj': NoeVec3((0.0, -0.3490658104419708, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.0, -1.780236005783081)), 'hairback_l_02_wj': NoeVec3((0.0, -0.3490658104419708, 0.0)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.0, -1.3613569736480713)), 
    'hairback_r_02_wj': NoeVec3((0.0, -0.3490658104419708, 0.0))},
    'KNY': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.13962629437446594, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7941247820854187, -0.09599310904741287, -1.3788100481033325)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.291543960571289)), 'skirt_d_01_wj': NoeVec3((-2.3212881088256836, 0.27925270795822144, -1.3962630033493042)), 
    'skirt_e_01_wj': NoeVec3((0.0, 2.792526960372925, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3212881088256836, 0.27925270795822144, -1.7453290224075317)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.8500490188598633)), 
    'skirt_h_01_wj': NoeVec3((0.7941247820854187, -0.09599310904741287, -1.7627830505371094)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hair_c_01_wj': NoeVec3((-0.0017453290056437254, -0.01745329052209854, -1.4660769701004028)), 'hair_l_01_wj': NoeVec3((-0.7853981852531433, 0.2617993950843811, -1.535889983177185)), 'hair_r_01_wj': NoeVec3((0.7853981852531433, 0.2617993950843811, -1.6057029962539673)), 
    'hairside_l_01_wj': NoeVec3((0.0872664600610733, -0.27925270795822144, -1.9198620319366455)), 'hairside_r_01_wj': NoeVec3((-0.0872664600610733, -0.27925270795822144, -1.3089970350265503)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((0.0, 3.2114059925079346, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.3490658104419708, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.268928050994873, -0.03490658104419708, -1.4486229419708252)), 'hairback_l_02_wj': NoeVec3((0.0, -0.3490658104419708, 0.0)), 
    'hairback_r_01_wj': NoeVec3((2.268928050994873, -0.03490658104419708, -1.6929689645767212)), 'hairback_r_02_wj': NoeVec3((0.0, -0.3490658104419708, 0.0))},
    'MIB': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, 0.0, -1.570796012878418)), 
    'hair_l_01_wj': NoeVec3((-0.7853981852531433, 0.0872664600610733, -1.483530044555664)), 'hair_r_01_wj': NoeVec3((0.7853981852531433, 0.0872664600610733, -1.6580630540847778)), 'hairside_l_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.6580630540847778)), 
    'hairside_l_02_wj': NoeVec3((0.0, -0.2094395011663437, 0.0)), 'hairside_l_03_wj': NoeVec3((0.0, -0.3490658104419708, 0.0)), 'hairside_r_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.483530044555664)), 'hairside_r_02_wj': NoeVec3((0.0, -0.2094395011663437, 0.0)), 
    'hairside_r_03_wj': NoeVec3((0.0, -0.3490658104419708, 0.0)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 
    'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'MIK': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_l1_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.5184359550476074)), 'hair_l2_01_wj': NoeVec3((-0.6108651757240295, 0.0, -1.5184359550476074)), 
    'hair_r1_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.623155951499939)), 'hair_r2_01_wj': NoeVec3((0.6108651757240295, 0.0, -1.623155951499939)), 'hairside_l_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.6580630540847778)), 
    'hairside_l_02_wj': NoeVec3((0.0, 0.0872664600610733, -0.1745329052209854)), 'hairside_r_01_wj': NoeVec3((1.570796012878418, 0.0, -1.483530044555664)), 'hairside_r_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.1745329052209854)), 
    'hairtail_l_01_wj': NoeVec3((-2.4260079860687256, 0.10471980273723602, -1.3613569736480713)), 'hairtair_r_01_wj': NoeVec3((2.4260079860687256, 0.10471980273723602, -1.780236005783081)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((3.1415929794311523, -0.0872664600610733, -1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.530726909637451, -0.06981316953897476, -1.570796012878418)), 'hairback_r_01_wj': NoeVec3((2.530726909637451, -0.06981316953897476, -1.570796012878418))},
    'MIM': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7863126993179321, -0.05095802992582321, -1.4288400411605835)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.483530044555664)), 
    'lskirt_d_01_wj': NoeVec3((-2.3508710861206055, 0.08307766914367676, -1.4905040264129639)), 'lskirt_e_01_wj': NoeVec3((0.0, 3.0019659996032715, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3508710861206055, 0.08307766914367676, -1.651087999343872)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.6580630540847778)), 'lskirt_h_01_wj': NoeVec3((0.7863126993179321, -0.05095802992582321, -1.7127530574798584)), 'skirt_a_01_wj': NoeVec3((0.0, -0.05235987901687622, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.890117883682251, -0.06981316953897476, -1.483530044555664)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.326449990272522)), 'skirt_c_02_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 
    'skirt_d_01_wj': NoeVec3((0.7504916191101074, 3.0717790126800537, 1.6580630540847778)), 'skirt_e_01_wj': NoeVec3((0.0, 2.9845130443573, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3911008834838867, 0.06981316953897476, -1.6580630540847778)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.815142035484314)), 'skirt_g_02_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 'skirt_h_01_wj': NoeVec3((0.890117883682251, -0.06981316953897476, -1.6580630540847778)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.2617993950843811, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((0.0, 0.0872664600610733, -1.2217299938201904)), 'hair_r_01_wj': NoeVec3((0.0, 0.0872664600610733, -1.9198620319366455)), 
    'hairback_c1_01_wj': NoeVec3((0.0, 2.967060089111328, 1.570796012878418)), 'hairdown_c1_03_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'hairdown_c1_04_wj': NoeVec3((0.0, 0.1745329052209854, 0.0)), 'ribbon_l_01_wj': NoeVec3((1.1519169807434082, -0.5148720741271973, -1.038470983505249)), 
    'ribbon_r_01_wj': NoeVec3((-1.1519169807434082, -0.5148720741271973, 1.038470983505249)), 'hairback_l1_01_wj': NoeVec3((-1.570796012878418, 0.0, -0.6981316804885864)), 'hairback_l2_01_wj': NoeVec3((-2.0594890117645264, 0.6981316804885864, -0.6981316804885864)), 
    'hairback_r1_01_wj': NoeVec3((1.570796012878418, 0.0, -2.4434609413146973)), 'hairback_r2_01_wj': NoeVec3((2.0594890117645264, 0.6981316804885864, -2.4434609413146973)), 'hairside_l_01_wj': NoeVec3((-1.2217299938201904, -0.1745329052209854, -2.007128953933716)), 
    'hairside_r_01_wj': NoeVec3((1.2217299938201904, -0.1745329052209854, -1.1344640254974365)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 
    'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'NOM': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.029670599848031998, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7801622152328491, 0.0, -1.4486229419708252)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.06283185631036758, -1.274090051651001)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.268928050994873, 0.3141593039035797, -1.326449990272522)), 'skirt_d_02_wj': NoeVec3((0.0, 0.1221729964017868, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.757620096206665, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.268928050994873, 0.3141593039035797, -1.815142035484314)), 'skirt_f_02_wj': NoeVec3((0.0, 0.1221729964017868, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.06283185631036758, -1.867501974105835)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.7801622152328491, 0.0, -1.6929689645767212)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, 0.033161260187625885, -1.570796012878418)), 
    'hair_l_01_wj': NoeVec3((-0.7853981852531433, 0.1745329052209854, -1.3089970350265503)), 'hair_r_01_wj': NoeVec3((0.7853981852531433, 0.1745329052209854, -1.832595944404602)), 'hairside_l_01_wj': NoeVec3((-1.570796012878418, -0.3665192127227783, -1.8500490188598633)), 
    'hairside_r_01_wj': NoeVec3((1.570796012878418, -0.3665192127227783, -1.291543960571289)), 'hairtop_01_wj': NoeVec3((-1.570796012878418, 0.15707960724830627, 0.9075711965560913)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((0.0, 3.3161261081695557, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.3490658104419708, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, -0.0872664600610733, -1.780236005783081)), 'hairback_l_02_wj': NoeVec3((0.0, -0.471238911151886, 0.0)), 
    'hairback_r_01_wj': NoeVec3((2.5132739543914795, -0.0872664600610733, -1.3613569736480713)), 'hairback_r_02_wj': NoeVec3((0.0, -0.471238911151886, 0.0))},
    'NOR': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.04553563892841339, -1.570796012878418)), 
    'skirt_a_02_wj': NoeVec3((0.0011170109501108527, 0.029094640165567398, 0.024609139189124107)), 'skirt_b_01_wj': NoeVec3((-0.7853981852531433, 0.06478662043809891, -1.3539040088653564)), 'skirt_b_02_wj': NoeVec3((0.002844887087121606, 0.03867650032043457, -0.04623376950621605)), 
    'skirt_c_01_wj': NoeVec3((-1.704906940460205, 0.060388389974832535, -1.1502070426940918)), 'skirt_c_02_wj': NoeVec3((-0.17957690358161926, 0.0768992081284523, 0.0679805725812912)), 'skirt_d_01_wj': NoeVec3((-2.4367239475250244, 0.30885350704193115, -1.3177759647369385)), 
    'skirt_d_02_wj': NoeVec3((-0.35304519534111023, 0.18828609585762024, 0.08299040794372559)), 'skirt_e_01_wj': NoeVec3((0.0, 2.766922950744629, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.1318770945072174, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.33034610748291, 0.36713001132011414, -1.9322019815444946)), 'skirt_f_02_wj': NoeVec3((0.1995784044265747, 0.25588271021842957, -0.05820672959089279)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.19369660317897797, -2.007581949234009)), 
    'skirt_g_02_wj': NoeVec3((-0.011536629870533943, 0.1123816967010498, 0.09119345247745514)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.05372123047709465, -1.8072010278701782)), 'skirt_h_02_wj': NoeVec3((-0.0024260079953819513, 0.17758730053901672, -0.010245080105960369)), 
    'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.15707960724830627, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.820304811000824, -0.01745329052209854, -1.5009829998016357)), 
    'hair_r_01_wj': NoeVec3((0.820304811000824, 0.01745329052209854, -1.6406099796295166)), 'hair_tail_back_l_02_wj': NoeVec3((0.3366740047931671, 2.594413995742798, 1.7509139776229858)), 'hair_tail_back_l_03_wj': NoeVec3((0.1593136042356491, 0.06590362638235092, -0.09307841211557388)), 
    'hair_tail_back_l_04_wj': NoeVec3((-0.044174280017614365, 0.16758650541305542, 0.0172787606716156)), 'hair_tail_back_l_05_wj': NoeVec3((-0.21706660091876984, 0.2978579103946686, 0.011641349643468857)), 'hair_tail_back_l_06_wj': NoeVec3((0.0, 0.44687411189079285, 0.011205010116100311)), 
    'hair_tail_back_r_02_wj': NoeVec3((2.742418050765991, 0.5440714955329895, -1.785768985748291)), 'hair_tail_back_r_03_wj': NoeVec3((-0.0743335708975792, 0.0777893215417862, 0.042987458407878876)), 'hair_tail_back_r_04_wj': NoeVec3((-0.07822565734386444, 0.14350099861621857, 0.0316777303814888)), 
    'hair_tail_back_r_05_wj': NoeVec3((0.0, 0.3358187973499298, -0.05794493108987808)), 'hair_tail_back_r_06_wj': NoeVec3((0.0, 0.40083229541778564, 0.18015289306640625)), 'hair_tail_front_l_02_wj': NoeVec3((-0.31581729650497437, -0.9572781920433044, -1.309730052947998)), 
    'hair_tail_front_l_03_wj': NoeVec3((-0.06195918843150139, 0.08918633311986923, 0.08691740036010742)), 'hair_tail_front_l_04_wj': NoeVec3((-0.03153809905052185, 0.4147076904773712, 0.023265240713953972)), 'hair_tail_front_l_05_wj': NoeVec3((0.26253241300582886, 0.29536208510398865, -0.055798180401325226)), 
    'hair_tail_front_l_06_wj': NoeVec3((0.0, 0.3816685974597931, -0.10154329985380173)), 'hair_tail_front_r_02_wj': NoeVec3((0.3750537931919098, -0.9504889249801636, -1.8808189630508423)), 'hair_tail_front_r_03_wj': NoeVec3((0.024731319397687912, 0.09452704340219498, -0.03471459820866585)), 
    'hair_tail_front_r_04_wj': NoeVec3((0.10534810274839401, 0.40137338638305664, -0.07908085733652115)), 'hair_tail_front_r_05_wj': NoeVec3((-0.5449615716934204, 0.3283661901950836, 0.11393509805202484)), 'hair_tail_front_r_06_wj': NoeVec3((0.0, 0.3606024980545044, 0.124965600669384)), 
    'hairside_l_01_wj': NoeVec3((-1.570796012878418, -0.0872664600610733, -1.535889983177185)), 'hairside_l_02_wj': NoeVec3((-0.101351298391819, 0.39620721340179443, -0.17039650678634644)), 'hairside_r_01_wj': NoeVec3((1.570796012878418, -0.0872664600610733, -1.6755160093307495)), 
    'hairside_r_02_wj': NoeVec3((0.1482831984758377, 0.6040583848953247, 0.16990779340267181)), 'hairtwintail_l_01_wj': NoeVec3((-1.570796012878418, 0.02652899920940399, -1.4872469902038574)), 'hairtwintail_r_01_wj': NoeVec3((1.570796012878418, 0.026406830176711082, -1.6521639823913574)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 2.897247076034546, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.10471980273723602, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.1221729964017868, 0.0)), 
    'hairback_c_04_wj': NoeVec3((0.0, 0.24434609711170197, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.4436349868774414, 0.2967059910297394, -1.3439040184020996)), 'hairback_l_02_wj': NoeVec3((0.0015707960119470954, -0.09433504939079285, -0.0007330382941290736)), 
    'hairback_l_03_wj': NoeVec3((0.00783652812242508, 0.08546877652406693, -0.0031241390388458967)), 'hairback_l_04_wj': NoeVec3((0.168721005320549, 0.2929185926914215, -0.01340413000434637)), 'hairback_r_01_wj': NoeVec3((2.4436349868774414, 0.2967059910297394, -1.7976889610290527)), 
    'hairback_r_02_wj': NoeVec3((-0.0015707960119470954, -0.09433504939079285, 0.0007330382941290736)), 'hairback_r_03_wj': NoeVec3((-0.00783652812242508, 0.08546877652406693, 0.0031241390388458967)), 'hairback_r_04_wj': NoeVec3((-0.168721005320549, 0.2929185926914215, 0.01340413000434637))},
    'NOY': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.6108651757240295, -1.570796012878418)), 'skirt_a_02_wj': NoeVec3((0.0, 0.1745329052209854, 0.0)), 
    'skirt_b_01_wj': NoeVec3((-0.9299113750457764, -0.5005429983139038, -0.9985203146934509)), 'skirt_b_02_wj': NoeVec3((0.0, 0.2617993950843811, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -0.6981316804885864)), 'skirt_c_02_wj': NoeVec3((0.0, 0.2617993950843811, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.1474881172180176, 0.5640711784362793, -0.8862032294273376)), 'skirt_d_02_wj': NoeVec3((0.0, 0.2617993950843811, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.268928050994873, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.3490658104419708, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.1474881172180176, 0.5640711784362793, -2.2553839683532715)), 'skirt_f_02_wj': NoeVec3((0.0, 0.2617993950843811, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -2.4434609413146973)), 'skirt_g_02_wj': NoeVec3((0.0, 0.2617993950843811, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.9299113750457764, -0.5005412101745605, -2.1430718898773193)), 'skirt_h_02_wj': NoeVec3((0.0, 0.2617993950843811, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hair_c_01_wj': NoeVec3((0.0, -0.15707960724830627, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.820304811000824, -0.01745329052209854, -1.5009829998016357)), 'hair_r_01_wj': NoeVec3((0.820304811000824, 0.01745329052209854, -1.6406099796295166)), 
    'hairside_l_01_wj': NoeVec3((-1.570796012878418, -0.0872664600610733, -1.535889983177185)), 'hairside_l_02_wj': NoeVec3((-0.101351298391819, 0.39620721340179443, -0.17039650678634644)), 'hairside_r_01_wj': NoeVec3((1.570796012878418, -0.0872664600610733, -1.6755160093307495)), 
    'hairside_r_02_wj': NoeVec3((0.1482831984758377, 0.6040583848953247, 0.16990779340267181)), 'hairtwintail_l_01_wj': NoeVec3((-1.570796012878418, 0.10471980273723602, -1.239184021949768)), 'hairtwintail_l_02_wj': NoeVec3((-0.03438299149274826, -0.1414414942264557, 0.13459980487823486)), 
    'hairtwintail_l_03_wj': NoeVec3((0.004834562074393034, 0.019582590088248253, 0.005550147034227848)), 'hairtwintail_l_04_wj': NoeVec3((-0.07045894116163254, 0.6283184885978699, -0.36189401149749756)), 'hairtwintail_r_01_wj': NoeVec3((1.570796012878418, 0.10471980273723602, -1.9024089574813843)), 
    'hairtwintail_r_02_wj': NoeVec3((0.03438299149274826, -0.1414414942264557, -0.13459980487823486)), 'hairtwintail_r_03_wj': NoeVec3((-0.004834562074393034, 0.019582590088248253, -0.005550147034227848)), 'hairtwintail_r_04_wj': NoeVec3((0.07045894116163254, 0.6283184885978699, 0.36189401149749756)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 2.897247076034546, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.10471980273723602, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.1221729964017868, 0.0)), 
    'hairback_c_04_wj': NoeVec3((0.0, 0.24434609711170197, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.4436349868774414, 0.2967059910297394, -1.3439040184020996)), 'hairback_l_02_wj': NoeVec3((0.0015707960119470954, -0.09433504939079285, -0.0007330382941290736)), 
    'hairback_l_03_wj': NoeVec3((0.00783652812242508, 0.08546877652406693, -0.0031241390388458967)), 'hairback_l_04_wj': NoeVec3((0.168721005320549, 0.2929185926914215, -0.01340413000434637)), 'hairback_r_01_wj': NoeVec3((2.4436349868774414, 0.2967059910297394, -1.7976889610290527)), 
    'hairback_r_02_wj': NoeVec3((-0.0015707960119470954, -0.09433504939079285, 0.0007330382941290736)), 'hairback_r_03_wj': NoeVec3((-0.00783652812242508, 0.08546877652406693, 0.0031241390388458967)), 'hairback_r_04_wj': NoeVec3((-0.168721005320549, 0.2929185926914215, 0.01340413000434637))},
    'NYC': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.02617993950843811, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.6038839221000671, 0.003490658011287451, -1.3962630033493042)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.06108652055263519, -1.291543960571289)), 'skirt_c_02_wj': NoeVec3((0.0, -0.006283184979110956, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.5010569095611572, 0.3665192127227783, -1.3089970350265503)), 'skirt_d_02_wj': NoeVec3((0.0, 0.09948377311229706, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.7052600383758545, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.09075711667537689, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.5010569095611572, 0.3665192127227783, -1.832595944404602)), 'skirt_f_02_wj': NoeVec3((0.0, 0.09948377311229706, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.06108652055263519, -1.8500490188598633)), 'skirt_g_02_wj': NoeVec3((0.0, -0.006283184979110956, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.6038839221000671, 0.003490658011287451, -1.7453290224075317)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.006108651868999004, 0.03490658104419708, -1.3997540473937988)), 
    'hair_l_01_wj': NoeVec3((-1.0995570421218872, 0.30368730425834656, -1.3962630033493042)), 'hair_r_01_wj': NoeVec3((1.0995570421218872, 0.30368730425834656, -1.7453290224075317)), 'hair_twintail_l_01_wj': NoeVec3((-2.124066114425659, 0.22689279913902283, -1.36484694480896)), 
    'hair_twintail_l_02_wj': NoeVec3((0.0, 0.016057029366493225, -0.02042035013437271)), 'hair_twintail_l_03_wj': NoeVec3((0.0, -0.06178465113043785, -0.08028514683246613)), 'hair_twintail_l_04_wj': NoeVec3((0.0, -0.027925269678235054, -0.006108651868999004)), 
    'hair_twintail_r_01_wj': NoeVec3((2.124066114425659, 0.22689279913902283, -1.7767449617385864)), 'hair_twintail_r_02_wj': NoeVec3((0.0, 0.016057029366493225, 0.02042035013437271)), 'hair_twintail_r_03_wj': NoeVec3((0.0, -0.06178465113043785, 0.08028514683246613)), 
    'hair_twintail_r_04_wj': NoeVec3((0.0, -0.027925269678235054, 0.006108651868999004)), 'hairside_l_01_wj': NoeVec3((0.003490658011287451, -0.10122910141944885, -1.84306800365448)), 'hairside_r_01_wj': NoeVec3((0.003490658011287451, -0.10122910141944885, -1.2985249757766724)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 
    'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'NYN': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.2111847996711731, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.44505900144577026, -0.15358899533748627, -1.3002699613571167)), 'skirt_c_01_wj': NoeVec3((-1.565559983253479, 0.04712389037013054, -1.0035640001296997)), 'skirt_c_02_wj': NoeVec3((0.0, 0.11344639956951141, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.509783983230591, 0.4206242859363556, -1.1868239641189575)), 'skirt_d_02_wj': NoeVec3((0.006981316953897476, 0.179768905043602, 0.040142569690942764)), 'skirt_e_01_wj': NoeVec3((0.0, 2.630211114883423, 1.570796012878418)), 
    'skirt_e_02_wj': NoeVec3((0.0, 0.18849560618400574, 0.0)), 'skirt_f_01_wj': NoeVec3((2.509783983230591, 0.4206242859363556, -1.9547690153121948)), 'skirt_f_02_wj': NoeVec3((0.006981316953897476, 0.179768905043602, -0.040142569690942764)), 
    'skirt_g_01_wj': NoeVec3((1.565559983253479, 0.04712389037013054, -2.1380279064178467)), 'skirt_g_02_wj': NoeVec3((0.0, 0.11344639956951141, 0.0)), 'skirt_h_01_wj': NoeVec3((0.44505900144577026, -0.15358899533748627, -1.8413219451904297)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hair_c_01_wj': NoeVec3((0.0, 0.09767437726259232, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((0.0010048539843410254, 0.04330616071820259, -1.570796012878418)), 'hair_r_01_wj': NoeVec3((-0.0010048559634014964, 0.04330616071820259, -1.570796012878418)), 
    'hairside_l_01_wj': NoeVec3((-0.0009653572924435139, -0.01598108932375908, -1.6493359804153442)), 'hairside_l_02_wj': NoeVec3((-0.03816493973135948, -0.4148840010166168, 0.0890117883682251)), 'hairside_l_03_wj': NoeVec3((-0.01660322956740856, 0.00170920102391392, 0.179768905043602)), 
    'hairside_l_04_wj': NoeVec3((-0.12392059713602066, 0.4710626006126404, -0.10411690175533295)), 'hairside_r_01_wj': NoeVec3((0.0009653589804656804, -0.015981070697307587, -1.492256999015808)), 'hairside_r_02_wj': NoeVec3((0.03816493973135948, -0.4148840010166168, -0.0890117883682251)), 
    'hairside_r_03_wj': NoeVec3((0.01660322956740856, 0.00170920102391392, -0.179768905043602)), 'hairside_r_04_wj': NoeVec3((0.12392059713602066, 0.4710626006126404, 0.10411690175533295)), 'hairtop_01_wj': NoeVec3((1.7505650520324707, 0.16755160689353943, 1.6929689645767212)), 
    'hairtop_02_wj': NoeVec3((0.14419250190258026, 0.4321574866771698, 0.2857086956501007)), 'hairtop_03_wj': NoeVec3((0.2977462112903595, 0.8266630172729492, 0.3958877921104431)), 'hairtop_04_wj': NoeVec3((0.060850560665130615, 0.49440810084342957, 0.1276984065771103)), 
    'hairtop_05_wj': NoeVec3((0.019634079188108444, 0.42486900091171265, 0.049438539892435074)), 'hairtop_06_wj': NoeVec3((-0.12645310163497925, 0.24964669346809387, -0.048882659524679184)), 'hairtop_07_wj': NoeVec3((-0.019541749730706215, 0.37564370036125183, -0.0532224215567112)), 
    'hairtop_08_wj': NoeVec3((0.002782962052151561, 0.5341789722442627, 0.005466004833579063)), 'hair_root': NoeVec3((0.0, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 2.956850051879883, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.0952436625957489, 0.0)), 
    'hairback_c_03_wj': NoeVec3((0.0, 0.11361829936504364, 0.0)), 'hairback_c_04_wj': NoeVec3((0.0, 0.23430870473384857, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.19198620319366455, -1.3788100481033325)), 'hairback_l_02_wj': NoeVec3((0.0, -0.04712389037013054, -0.029670599848031998)), 
    'hairback_l_03_wj': NoeVec3((0.0, -0.04363323003053665, 0.013962630182504654)), 'hairback_l_04_wj': NoeVec3((0.0, 0.1745329052209854, -0.10471980273723602)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.19198620319366455, -1.7627830505371094)), 
    'hairback_r_02_wj': NoeVec3((0.0, -0.04712389037013054, 0.029670599848031998)), 'hairback_r_03_wj': NoeVec3((0.0, -0.04363323003053665, -0.013962630182504654)), 'hairback_r_04_wj': NoeVec3((0.0, 0.1745329052209854, 0.10471980273723602))},
    'NYT': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.13613569736480713, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.6038839221000671, -0.05585053935647011, -1.3543750047683716)), 'skirt_c_01_wj': NoeVec3((-1.5725419521331787, 0.15184369683265686, -1.2269669771194458)), 'skirt_c_02_wj': NoeVec3((0.0, -0.006283184979110956, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.495820999145508, 0.359537810087204, -1.3124879598617554)), 'skirt_d_02_wj': NoeVec3((0.0, 0.09948377311229706, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.6947879791259766, 1.570796012878418)), 
    'skirt_e_02_wj': NoeVec3((0.0, 0.09075711667537689, 0.0)), 'skirt_f_01_wj': NoeVec3((2.495820999145508, 0.359537810087204, -1.829105019569397)), 'skirt_f_02_wj': NoeVec3((0.0, 0.09948377311229706, 0.0)), 'skirt_g_01_wj': NoeVec3((1.5725419521331787, 0.15184369683265686, -1.9146260023117065)), 
    'skirt_g_02_wj': NoeVec3((0.0, -0.006283184979110956, 0.0)), 'skirt_h_01_wj': NoeVec3((0.6038839221000671, -0.05585053935647011, -1.7872170209884644)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hair_c_01_wj': NoeVec3((0.0, -0.05585053935647011, -1.4206980466842651)), 'hair_l_01_wj': NoeVec3((-1.0995570421218872, 0.22165679931640625, -1.3788100481033325)), 'hair_l_side_01_wj': NoeVec3((-1.579522967338562, 0.11588989943265915, -1.4189529418945312)), 
    'hair_ponytail_01_wj': NoeVec3((0.0, 2.9949851036071777, 1.570796012878418)), 'hair_ponytail_02_wj': NoeVec3((0.0, 0.17627820372581482, 0.0)), 'hair_r_01_wj': NoeVec3((1.0995570421218872, 0.22165679931640625, -1.7627830505371094)), 
    'hair_r_side_01_wj': NoeVec3((1.579522967338562, 0.11588989943265915, -1.722640037536621)), 'hairside_l_01_wj': NoeVec3((-0.003490658011287451, -0.19547690451145172, -1.7976889610290527)), 'hairside_r_01_wj': NoeVec3((0.003490658011287451, -0.19547690451145172, -1.3439040184020996)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 
    'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'TSA': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.15707960724830627, -1.570796012878418)), 'skirt_a_02_wj': NoeVec3((0.0, -0.03490658104419708, 0.0)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.13962629437446594, -1.3439040184020996)), 'skirt_b_02_wj': NoeVec3((0.0, -0.03490658104419708, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.05235987901687622, -1.2217299938201904)), 'skirt_c_02_wj': NoeVec3((0.0, -0.15707960724830627, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.303834915161133, 0.2967059910297394, -1.2566369771957397)), 'skirt_e_01_wj': NoeVec3((0.0, 2.792526960372925, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.303834915161133, 0.2967059910297394, -1.8849560022354126)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.05235987901687622, -1.9198620319366455)), 'skirt_g_02_wj': NoeVec3((0.0, -0.15707960724830627, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.13962629437446594, -1.7976889610290527)), 'skirt_h_02_wj': NoeVec3((0.0, -0.03490658104419708, 0.0)), 
    'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.49065899848938, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.1221729964017868, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.6632251143455505, -0.03490658104419708, -1.335176944732666)), 
    'hair_r_01_wj': NoeVec3((0.6632251143455505, 0.03141592815518379, -1.7540559768676758)), 'hair_twintail_l_01_wj': NoeVec3((-1.527163028717041, 0.5235987901687622, -0.3490658104419708)), 'hair_twintail_l_02_wj': NoeVec3((0.0, 0.9250245094299316, 0.0)), 
    'hair_twintail_l_03_wj': NoeVec3((0.0, 0.8290314078330994, 0.0)), 'hair_twintail_r_01_wj': NoeVec3((1.527163028717041, 0.5235987901687622, -2.792526960372925)), 'hair_twintail_r_02_wj': NoeVec3((0.0, 0.9250245094299316, 0.0)), 'hair_twintail_r_03_wj': NoeVec3((0.0, 0.8290314078330994, 0.0)), 
    'hairside_l_01_wj': NoeVec3((0.0, 0.0, -1.6580630540847778)), 'hairside_l_02_wj': NoeVec3((0.0, -0.1745329052209854, -0.05235987901687622)), 'hairside_r_01_wj': NoeVec3((0.0, 0.0, -1.483530044555664)), 'hairside_r_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.05235987901687622)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 
    'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'TSH': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.06632251292467117, -1.570796012878418)), 
    'skirt_a_02_wj': NoeVec3((0.0, -0.06981316953897476, 0.0)), 'skirt_b_01_wj': NoeVec3((-0.6632251143455505, -0.08028514683246613, -1.3788100481033325)), 'skirt_b_02_wj': NoeVec3((0.0, -0.06283185631036758, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.5533430576324463, 0.10471980273723602, -1.1868239641189575)), 
    'skirt_c_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 'skirt_d_01_wj': NoeVec3((-2.3212881088256836, 0.22689279913902283, -1.3089970350265503)), 'skirt_d_02_wj': NoeVec3((0.0, -0.06981316953897476, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8448870182037354, 1.570796012878418)), 
    'skirt_e_02_wj': NoeVec3((0.0, -0.03490658104419708, 0.0)), 'skirt_f_01_wj': NoeVec3((2.3212881088256836, 0.22689279913902283, -1.832595944404602)), 'skirt_f_02_wj': NoeVec3((0.0, -0.06981316953897476, 0.0)), 'skirt_g_01_wj': NoeVec3((1.5533430576324463, 0.10471980273723602, -1.9547690153121948)), 
    'skirt_g_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.6632251143455505, -0.08028514683246613, -1.7627830505371094)), 'skirt_h_02_wj': NoeVec3((0.0, -0.06283185631036758, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_wj': NoeVec3((0.02094395086169243, -0.027925269678235054, -1.274090051651001)), 'hair_l_01_wj': NoeVec3((-0.767944872379303, 0.3665192127227783, -0.9599310755729675)), 
    'hair_l_02_wj': NoeVec3((-0.40142568945884705, 0.3490658104419708, -0.13962629437446594)), 'hair_r_01_wj': NoeVec3((0.5672320127487183, 0.3141593039035797, -2.164207935333252)), 'hair_r_02_wj': NoeVec3((0.33161258697509766, 0.471238911151886, 0.3490658104419708)), 
    'hairside_l_01_wj': NoeVec3((0.0, 0.0, -1.6057029962539673)), 'hairside_l_02_wj': NoeVec3((-0.010471980087459087, -0.111701101064682, -0.10471980273723602)), 'hairside_r_01_wj': NoeVec3((0.0, 0.0, -1.535889983177185)), 'hairside_r_02_wj': NoeVec3((0.010471980087459087, -0.111701101064682, 0.10471980273723602)), 
    'hairtop_01_wj': NoeVec3((0.9773843884468079, -0.2617993950843811, -2.670353889465332)), 'hairtop_02_wj': NoeVec3((-0.06537985801696777, 0.9969965815544128, -0.025604330003261566)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((0.0, 3.0019659996032715, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, 0.0345575213432312, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.05235987901687622, 0.0)), 'hairback_c_04_wj': NoeVec3((0.0, 0.03490658104419708, 0.0)), 
    'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 'hairback_l_03_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'hairback_l_04_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778)), 
    'hairback_r_03_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'hairback_r_04_wj': NoeVec3((0.0, 0.0872664600610733, 0.0))},
    'TSK': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.06632251292467117, -1.570796012878418)), 'skirt_a_02_wj': NoeVec3((0.0, -0.06981316953897476, 0.0)), 
    'skirt_b_01_wj': NoeVec3((-0.6632251143455505, -0.08028514683246613, -1.3788100481033325)), 'skirt_b_02_wj': NoeVec3((0.0, -0.06283185631036758, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.5533430576324463, 0.10471980273723602, -1.1868239641189575)), 'skirt_c_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3212881088256836, 0.22689279913902283, -1.3089970350265503)), 'skirt_d_02_wj': NoeVec3((0.0, -0.06981316953897476, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8448870182037354, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, -0.03490658104419708, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.3212881088256836, 0.22689279913902283, -1.832595944404602)), 'skirt_f_02_wj': NoeVec3((0.0, -0.06981316953897476, 0.0)), 'skirt_g_01_wj': NoeVec3((1.5533430576324463, 0.10471980273723602, -1.9547690153121948)), 'skirt_g_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.6632251143455505, -0.08028514683246613, -1.7627830505371094)), 'skirt_h_02_wj': NoeVec3((0.0, -0.06283185631036758, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'haira_l_01_wj': NoeVec3((-0.16869999468326569, 0.04495863988995552, -1.312798023223877)), 'haira_r_01_wj': NoeVec3((0.16869999468326569, 0.04495863988995552, -1.8287910223007202)), 'hairb_l_01_wj': NoeVec3((-0.8072497248649597, 0.4068728983402252, -1.4254380464553833)), 
    'hairb_r_01_wj': NoeVec3((0.6448416113853455, 0.386775404214859, -1.6916120052337646)), 'hairside_l_01_wj': NoeVec3((0.010506879538297653, -0.15015070140361786, -1.6408710479736328)), 'hairside_l_02_wj': NoeVec3((-0.018308499827980995, 0.1612859070301056, -0.04427900165319443)), 
    'hairside_r_01_wj': NoeVec3((-0.010506879538297653, -0.15015070140361786, -1.500704050064087)), 'hairside_r_02_wj': NoeVec3((0.018308499827980995, 0.1612859070301056, 0.04427900165319443)), 'ribbon_l_01_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'ribbon_r_01_wj': NoeVec3((0.0, 3.2288589477539062, 0.0)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 
    'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'TSY': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_a_02_wj': NoeVec3((0.0, -0.06981316953897476, 0.0)), 'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.05235987901687622, -1.4660769701004028)), 'skirt_b_02_wj': NoeVec3((0.0, -0.05235987901687622, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'skirt_c_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.0)), 'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_d_02_wj': NoeVec3((0.0, -0.13962629437446594, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 
    'skirt_e_02_wj': NoeVec3((0.0, -0.05235987901687622, 0.0)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 'skirt_f_02_wj': NoeVec3((0.0, -0.13962629437446594, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 
    'skirt_g_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.05235987901687622, -1.6755160093307495)), 'skirt_h_02_wj': NoeVec3((0.0, -0.05235987901687622, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.49065899848938, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, 0.2094395011663437, -1.9198620319366455)), 'hair_l_01_wj': NoeVec3((-0.767944872379303, 0.4363322854042053, -1.2217299938201904)), 
    'hair_r_01_wj': NoeVec3((0.767944872379303, 0.4363322854042053, -1.9198620319366455)), 'hairside_l_01_wj': NoeVec3((0.0, -0.13962629437446594, -1.6406099796295166)), 'hairside_r_01_wj': NoeVec3((0.0, -0.13962629437446594, -1.5009829998016357)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 2.8274331092834473, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, 0.2617993950843811, 0.0)), 
    'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.2617993950843811, -1.3089970350265503)), 'hairback_l_02_wj': NoeVec3((0.0, 0.1745329052209854, 0.0)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.2617993950843811, -1.832595944404602)), 
    'hairback_r_02_wj': NoeVec3((0.0, 0.1745329052209854, 0.0))},
    'VIB': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.15707960724830627, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.9250245094299316, -0.013962630182504654, -1.1344640254974365)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.2705259919166565, -0.890117883682251)), 'skirt_c_02_wj': NoeVec3((0.0, 0.06108652055263519, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.4434609413146973, 0.6283184885978699, -1.0471980571746826)), 'skirt_e_01_wj': NoeVec3((0.0, 2.4085540771484375, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.4434609413146973, 0.6283184885978699, -2.0943949222564697)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.2705259919166565, -2.2514750957489014)), 'skirt_g_02_wj': NoeVec3((0.0, 0.06108652055263519, 0.0)), 'skirt_h_01_wj': NoeVec3((0.9250245094299316, -0.01396264974027872, -2.007128953933716)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, 0.3263765871524811, -0.8098328113555908)), 'hair_cap_01_wj': NoeVec3((0.0, 0.40142568945884705, 1.570796012878418)), 'hair_r_01_wj': NoeVec3((0.0, 0.24958209693431854, -1.6807520389556885)), 
    'hairside_l_01_wj': NoeVec3((0.0, 0.059341199696063995, -1.5882500410079956)), 'hairside_l_02_wj': NoeVec3((0.00593411922454834, -0.179768905043602, -0.10122910141944885)), 'hairside_l_03_wj': NoeVec3((-0.03141592815518379, -0.12740899622440338, -0.2617993950843811)), 
    'hairside_r_01_wj': NoeVec3((0.0, 0.059341199696063995, -1.5533430576324463)), 'hairside_r_02_wj': NoeVec3((-0.00593411922454834, -0.179768905043602, 0.10122910141944885)), 'hairside_r_03_wj': NoeVec3((0.03141592815518379, -0.12740899622440338, 0.2617993950843811)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 2.975785970687866, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.1221729964017868, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.2617993950843811, 0.0)), 
    'hairback_l_01_wj': NoeVec3((-2.495820999145508, 0.11519169807434082, -1.4416420459747314)), 'hairback_l_02_wj': NoeVec3((0.0, -0.1221729964017868, 0.0)), 'hairback_l_03_wj': NoeVec3((0.0, 0.2094395011663437, 0.0)), 'hairback_r_01_wj': NoeVec3((2.495820999145508, 0.11519169807434082, -1.6999510526657104)), 
    'hairback_r_02_wj': NoeVec3((0.0, -0.1221729964017868, 0.0)), 'hairback_r_03_wj': NoeVec3((0.0, 0.2094395011663437, 0.0))},
    'VIG': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.15707960724830627, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.9250245094299316, -0.013962630182504654, -1.1344640254974365)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.2705259919166565, -0.890117883682251)), 'skirt_c_02_wj': NoeVec3((0.0, 0.06108652055263519, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.4434609413146973, 0.6283184885978699, -1.0471980571746826)), 'skirt_e_01_wj': NoeVec3((0.0, 2.4085540771484375, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.4434609413146973, 0.6283184885978699, -2.0943949222564697)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.2705259919166565, -2.2514750957489014)), 'skirt_g_02_wj': NoeVec3((0.0, 0.06108652055263519, 0.0)), 'skirt_h_01_wj': NoeVec3((0.9250245094299316, -0.01396264974027872, -2.007128953933716)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hair_c_01_wj': NoeVec3((-0.01054546982049942, 0.25635218620300293, -1.1707969903945923)), 'hair_cap_01_wj': NoeVec3((0.0, 0.4136430025100708, 1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.021374180912971497, 0.4969981908798218, -0.9593585729598999)), 
    'hair_ponytail_01_wj': NoeVec3((-1.575508952140808, 0.24783679842948914, -1.3807300329208374)), 'hair_ponytail_02_wj': NoeVec3((0.0, -0.15707960724830627, -0.18500490486621857)), 'hair_ponytail_03_wj': NoeVec3((-0.008726646192371845, -0.12112580239772797, -0.4757767915725708)), 
    'hair_ponytail_04_wj': NoeVec3((-0.012740899808704853, 0.11780969798564911, -0.6223844289779663)), 'hair_ponytail_05_wj': NoeVec3((-0.18971729278564453, 0.35360369086265564, -0.1802925020456314)), 'hair_ponytail_06_wj': NoeVec3((0.0005235986900515854, -0.26511549949645996, 0.47403138875961304)), 
    'hair_t_01_wj': NoeVec3((-0.008203047327697277, -0.518362820148468, 2.4661500453948975)), 'hairside_l_01_wj': NoeVec3((0.19198620319366455, 0.3665192127227783, -1.4800390005111694)), 'hairside_r_01_wj': NoeVec3((0.04886921867728233, 0.15358899533748627, -1.6929689645767212)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 2.975785970687866, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.495820999145508, 0.11519169807434082, -1.4416420459747314)), 
    'hairback_r_01_wj': NoeVec3((2.495820999145508, 0.11519169807434082, -1.6999510526657104))},
    'VIR': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.15707960724830627, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.9250245094299316, -0.013962630182504654, -1.1344640254974365)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.2705259919166565, -0.890117883682251)), 'skirt_c_02_wj': NoeVec3((0.0, 0.06108652055263519, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.4434609413146973, 0.6283184885978699, -1.0471980571746826)), 'skirt_e_01_wj': NoeVec3((0.0, 2.4085540771484375, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.4434609413146973, 0.6283184885978699, -2.0943949222564697)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.2705259919166565, -2.2514750957489014)), 'skirt_g_02_wj': NoeVec3((0.0, 0.06108652055263519, 0.0)), 'skirt_h_01_wj': NoeVec3((0.9250245094299316, -0.01396264974027872, -2.007128953933716)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, 0.02617993950843811, -1.570796012878418)), 'hair_cap_01_wj': NoeVec3((0.0, 0.39444440603256226, 1.570796012878418)), 'hair_l_01_wj': NoeVec3((0.0, 0.3141593039035797, -1.2217299938201904)), 
    'hair_r_01_wj': NoeVec3((-0.24434609711170197, 0.2617993950843811, -2.0420351028442383)), 'hair_t_01_wj': NoeVec3((0.0, 0.19198620319366455, 1.570796012878418)), 'hairside_l_01_wj': NoeVec3((-0.01117010973393917, 0.27925270795822144, -1.4137170314788818)), 
    'hairside_l_02_wj': NoeVec3((0.0, 0.0, -0.4621562063694)), 'hairside_r_01_wj': NoeVec3((0.0, 0.27925270795822144, -1.7278759479522705)), 'hairside_r_02_wj': NoeVec3((-0.1269986927509308, -0.004980436991900206, 0.4621317982673645)), 
    'hairsideback_l_01_wj': NoeVec3((-0.2792421877384186, 0.29223790764808655, -0.8462350964546204)), 'hairsideback_l_02_wj': NoeVec3((0.0, 0.0, -0.8726645708084106)), 'hairsideback_r_01_wj': NoeVec3((0.2792421877384186, 2.8493549823760986, 0.8462350964546204)), 
    'hairsideback_r_02_wj': NoeVec3((0.0, 0.0, -0.8726645708084106)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((0.0, 3.0979599952697754, 1.3788100481033325)), 
    'hairback_l_02_wj': NoeVec3((-0.007689624093472958, -0.07828255742788315, -0.2928104102611542)), 'hairback_r_01_wj': NoeVec3((3.1415929794311523, 0.04363096132874489, -1.3788100481033325)), 'hairback_r_02_wj': NoeVec3((0.007688647136092186, -0.07828377932310104, 0.29279640316963196))},
    'VIS': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'muffler_l_01_wj': NoeVec3((0.5235987901687622, -0.06981316953897476, 2.4085540771484375)), 
    'muffler_r_01_wj': NoeVec3((-0.5061454772949219, -0.0872664600610733, -2.4085540771484375)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hair_c_01_wj': NoeVec3((-0.03490658104419708, 0.03490658104419708, -1.2217299938201904)), 'hair_l_01_wj': NoeVec3((-0.5180835127830505, 0.460220605134964, -0.8863952159881592)), 'hair_r_01_wj': NoeVec3((0.6632251143455505, 0.541051983833313, -2.164207935333252)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.06981316953897476, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.05235987901687622, 0.0)), 
    'hairback_l_01_wj': NoeVec3((-2.5434510707855225, 0.28763720393180847, -1.529891014099121)), 'hairback_l_02_wj': NoeVec3((0.0, -0.0872664600610733, -0.1745329052209854)), 'hairback_l_03_wj': NoeVec3((0.0, 0.0, -0.1745329052209854)), 
    'hairback_r_01_wj': NoeVec3((2.5434510707855225, 0.28763720393180847, -1.6117019653320312)), 'hairback_r_02_wj': NoeVec3((0.0, -0.0872664600610733, 0.1745329052209854)), 'hairback_r_03_wj': NoeVec3((0.0, 0.0, 0.1745329052209854))},
    'VIY': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.15707960724830627, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.9250245094299316, -0.013962630182504654, -1.1344640254974365)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.2705259919166565, -0.890117883682251)), 'skirt_c_02_wj': NoeVec3((0.0, 0.06108652055263519, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.4434609413146973, 0.6283184885978699, -1.0471980571746826)), 'skirt_e_01_wj': NoeVec3((0.0, 2.4085540771484375, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.4434609413146973, 0.6283184885978699, -2.0943949222564697)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.2705259919166565, -2.2514750957489014)), 'skirt_g_02_wj': NoeVec3((0.0, 0.06108652055263519, 0.0)), 'skirt_h_01_wj': NoeVec3((0.9250245094299316, -0.01396264974027872, -2.007128953933716)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, 0.23561950027942657, -1.58999502658844)), 'hair_cap_01_wj': NoeVec3((0.0, 0.40142568945884705, 1.570796012878418)), 'hair_l_01_wj': NoeVec3((0.0, 0.2111847996711731, -1.4887659549713135)), 
    'hair_r_01_wj': NoeVec3((0.0, 0.5113813877105713, -2.3771378993988037)), 'hairside_l_01_wj': NoeVec3((0.0, -0.1665123999118805, -1.5414750576019287)), 'hairside_l_02_wj': NoeVec3((-0.007155850064009428, -0.6738715767860413, -0.02897246927022934)), 
    'hairside_l_03_wj': NoeVec3((-0.2598794996738434, 0.07138396799564362, -0.25883230566978455)), 'hairside_r_01_wj': NoeVec3((0.0, -0.1665123999118805, -1.6001180410385132)), 'hairside_r_02_wj': NoeVec3((0.007155850064009428, -0.6738715767860413, 0.02897246927022934)), 
    'hairside_r_03_wj': NoeVec3((0.2598794996738434, 0.07138396799564362, 0.25883230566978455)), 'hair_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 2.9234259128570557, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.3577924966812134, 0.0)), 
    'hairback_c_03_wj': NoeVec3((0.0, 0.5078908205032349, 0.0)), 'hairback_c_04_wj': NoeVec3((0.0, 0.35988691449165344, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.499660015106201, 0.13805550336837769, -1.4723600149154663)), 'hairback_l_02_wj': NoeVec3((0.0, -0.3892084062099457, 0.0)), 
    'hairback_l_03_wj': NoeVec3((0.0, 0.518886387348175, 0.0)), 'hairback_l_04_wj': NoeVec3((0.0, 0.33772119879722595, 0.0)), 'hairback_r_01_wj': NoeVec3((2.499660015106201, 0.13805550336837769, -1.669232964515686)), 'hairback_r_02_wj': NoeVec3((0.0, -0.3892084062099457, 0.0)), 
    'hairback_r_03_wj': NoeVec3((0.0, 0.518886387348175, 0.0)), 'hairback_r_04_wj': NoeVec3((0.0, 0.33772119879722595, 0.0))},
    'WG1': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.21816620230674744, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.8028513789176941, -0.22689279913902283, -1.3439040184020996)), 'skirt_b_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.1519169807434082)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.2863810062408447, 0.34033921360969543, -1.2042770385742188)), 'skirt_d_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.6616270542144775, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.16580629348754883, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.2863810062408447, 0.34033921360969543, -1.9373149871826172)), 'skirt_f_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.9896750450134277)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.8028513789176941, -0.22689279913902283, -1.7976889610290527)), 'skirt_h_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hairside_l_01_wj': NoeVec3((0.0, -0.05235987901687622, -1.7453290224075317)), 'hairside_l_02_wj': NoeVec3((0.0, -0.24434609711170197, 0.0872664600610733)), 'hairside_l_03_wj': NoeVec3((0.0, -0.0872664600610733, 0.0872664600610733)), 
    'hairside_r_01_wj': NoeVec3((0.0, -0.05235987901687622, -1.3962630033493042)), 'hairside_r_02_wj': NoeVec3((0.0, -0.24434609711170197, -0.0872664600610733)), 'hairside_r_03_wj': NoeVec3((0.0, -0.0872664600610733, -0.0872664600610733)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_c_03_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 
    'hairback_l_03_wj': NoeVec3((0.0, 0.1221729964017868, 0.10471980273723602)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778)), 'hairback_r_03_wj': NoeVec3((0.0, 0.1221729964017868, -0.10471980273723602))},
    'WG2': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.21816620230674744, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.8028513789176941, -0.22689279913902283, -1.3439040184020996)), 'skirt_b_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.1519169807434082)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.2863810062408447, 0.34033921360969543, -1.2042770385742188)), 'skirt_d_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.6616270542144775, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.16580629348754883, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.2863810062408447, 0.34033921360969543, -1.9373149871826172)), 'skirt_f_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.9896750450134277)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.8028513789176941, -0.22689279913902283, -1.7976889610290527)), 'skirt_h_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hairside_l_01_wj': NoeVec3((0.0, 0.02972296066582203, -1.7001780271530151)), 'hairside_l_02_wj': NoeVec3((0.002234020968899131, -0.139923095703125, -0.07490953058004379)), 'hairside_r_01_wj': NoeVec3((0.0, 0.029618240892887115, -1.4492859840393066)), 
    'hairside_r_02_wj': NoeVec3((-0.0024434609804302454, -0.13943439722061157, 0.0817861333489418)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 0.20437809824943542, -1.570796012878418)), 
    'hairback_c_02_wj': NoeVec3((-3.1415929794311523, -0.11711160093545914, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 'hairback_l_01_wj': NoeVec3((-0.0030892330687493086, 0.029373889788985252, -1.7486799955368042)), 
    'hairback_l_02_wj': NoeVec3((-2.5180039405822754, 0.0930260494351387, 0.26459190249443054)), 'hairback_l_03_wj': NoeVec3((0.0, 0.1221729964017868, 0.10471980273723602)), 'hairback_r_01_wj': NoeVec3((0.00321140605956316, 0.02926917001605034, -1.3860180377960205)), 
    'hairback_r_02_wj': NoeVec3((2.5180740356445312, 0.09311331808567047, -0.2714860141277313)), 'hairback_r_03_wj': NoeVec3((0.0, 0.1221729964017868, -0.10471980273723602))},
    'WG3': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.21816620230674744, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.8028513789176941, -0.22689279913902283, -1.3439040184020996)), 'skirt_b_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.1519169807434082)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.2863810062408447, 0.34033921360969543, -1.2042770385742188)), 'skirt_d_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.6616270542144775, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.16580629348754883, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.2863810062408447, 0.34033921360969543, -1.9373149871826172)), 'skirt_f_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.9896750450134277)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.8028513789176941, -0.22689279913902283, -1.7976889610290527)), 'skirt_h_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hair_tail_l_01_wj': NoeVec3((-0.010367260314524174, 0.3887721002101898, -1.1831589937210083)), 'hair_tail_r_01_wj': NoeVec3((-0.02466150000691414, 0.38870230317115784, -1.9651880264282227)), 'hairside_l_01_wj': NoeVec3((0.0, 0.05450662970542908, -1.6814149618148804)), 
    'hairside_l_02_wj': NoeVec3((0.005305801052600145, -0.04113740846514702, -0.09744173288345337)), 'hairside_r_01_wj': NoeVec3((0.0, 0.056810468435287476, -1.4559359550476074)), 'hairside_r_02_wj': NoeVec3((-0.002338740974664688, -0.04548327997326851, 0.04111995920538902)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_c_03_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 
    'hairback_l_03_wj': NoeVec3((0.0, 0.1221729964017868, 0.10471980273723602)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778)), 'hairback_r_03_wj': NoeVec3((0.0, 0.1221729964017868, -0.10471980273723602))},
    'WG4': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.21816620230674744, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.8028513789176941, -0.22689279913902283, -1.3439040184020996)), 'skirt_b_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.1519169807434082)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.2863810062408447, 0.34033921360969543, -1.2042770385742188)), 'skirt_d_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.6616270542144775, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.16580629348754883, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.2863810062408447, 0.34033921360969543, -1.9373149871826172)), 'skirt_f_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.9896750450134277)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.8028513789176941, -0.22689279913902283, -1.7976889610290527)), 'skirt_h_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hairside_l_01_wj': NoeVec3((0.0, -0.12622219324111938, -1.6348329782485962)), 'hairside_l_02_wj': NoeVec3((0.0031066860537976027, -0.27029910683631897, 0.02275908924639225)), 'hairside_l_03_wj': NoeVec3((-0.00043633230961859226, 0.19624480605125427, -0.0011170109501108527)), 
    'hairside_r_01_wj': NoeVec3((0.0, -0.1264490932226181, -1.534248948097229)), 'hairside_r_02_wj': NoeVec3((-0.00022689279285259545, -0.2704387903213501, -0.0017104230355471373)), 'hairside_r_03_wj': NoeVec3((-0.0042236968874931335, 0.19641940295696259, -0.010681410320103168)), 
    'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.037169933319092, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, -0.07838273793458939, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, 0.03595377877354622, 0.0)), 
    'hairback_c_04_wj': NoeVec3((0.0, 0.157306507229805, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.5008649826049805, 0.10782639682292938, -1.5036189556121826)), 'hairback_l_02_wj': NoeVec3((-0.133657306432724, -0.07934267073869705, 0.025795970112085342)), 
    'hairback_l_03_wj': NoeVec3((-0.09567894786596298, 0.0426383912563324, 0.014713129960000515)), 'hairback_l_04_wj': NoeVec3((0.0, 0.15067429840564728, -0.09096655994653702)), 'hairback_r_01_wj': NoeVec3((2.328339099884033, 0.10290460288524628, -1.6607329845428467)), 
    'hairback_r_02_wj': NoeVec3((0.4272739887237549, -0.04237658903002739, -0.07597418129444122)), 'hairback_r_03_wj': NoeVec3((-0.2675414979457855, 0.014451329596340656, 0.04672246053814888)), 'hairback_r_04_wj': NoeVec3((0.0, 0.1584583967924118, 0.07962191849946976))},
    'WG5': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.21816620230674744, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.8028513789176941, -0.22689279913902283, -1.3439040184020996)), 'skirt_b_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.1519169807434082)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.2863810062408447, 0.34033921360969543, -1.2042770385742188)), 'skirt_d_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.6616270542144775, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.16580629348754883, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.2863810062408447, 0.34033921360969543, -1.9373149871826172)), 'skirt_f_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.9896750450134277)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.8028513789176941, -0.22689279913902283, -1.7976889610290527)), 'skirt_h_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hairside_l_01_wj': NoeVec3((0.0, -0.05331981182098389, -1.5734139680862427)), 'hairside_l_02_wj': NoeVec3((-0.008691739290952682, -0.14008009433746338, -0.160657599568367)), 'hairside_r_01_wj': NoeVec3((0.0, -0.05335471034049988, -1.5911120176315308)), 
    'hairside_r_02_wj': NoeVec3((0.011885689571499825, -0.139347106218338, 0.22069689631462097)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 2.8959031105041504, 1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, 0.10997319966554642, 0.0)), 
    'hairback_c_03_wj': NoeVec3((0.0, 0.11510449647903442, 0.0)), 'hairback_c_04_wj': NoeVec3((0.0, 0.030281459912657738, 0.0)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 'hairback_l_03_wj': NoeVec3((0.0, 0.1221729964017868, 0.10471980273723602)), 
    'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778)), 'hairback_r_03_wj': NoeVec3((0.0, 0.1221729964017868, -0.10471980273723602))},
    'WG6': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.21816620230674744, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.8028513789176941, -0.22689279913902283, -1.3439040184020996)), 'skirt_b_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.1519169807434082)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.2863810062408447, 0.34033921360969543, -1.2042770385742188)), 'skirt_d_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_e_01_wj': NoeVec3((0.0, 2.6616270542144775, 1.570796012878418)), 'skirt_e_02_wj': NoeVec3((0.0, 0.16580629348754883, 0.0)), 
    'skirt_f_01_wj': NoeVec3((2.2863810062408447, 0.34033921360969543, -1.9373149871826172)), 'skirt_f_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.9896750450134277)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.8028513789176941, -0.22689279913902283, -1.7976889610290527)), 'skirt_h_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 
    'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 
    'hairside_l_01_wj': NoeVec3((0.0, -0.05071926862001419, -1.6083029508590698)), 'hairside_l_02_wj': NoeVec3((-0.005358160939067602, -0.19034560024738312, -0.10273010283708572)), 'hairside_l_03_wj': NoeVec3((0.14528119564056396, -0.12596039474010468, 0.6139370203018188)), 
    'hairside_l_04_wj': NoeVec3((-0.19854870438575745, 0.6864728927612305, -0.6099228262901306)), 'hairside_r_01_wj': NoeVec3((0.0, -0.05071926862001419, -1.5332889556884766)), 'hairside_r_02_wj': NoeVec3((0.0029845130629837513, -0.19142769277095795, 0.05721189081668854)), 
    'hairside_r_03_wj': NoeVec3((-0.1275137960910797, -0.12021829932928085, -0.5261644124984741)), 'hairside_r_04_wj': NoeVec3((0.18784980475902557, 0.6998072266578674, 0.5597270727157593)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((0.0, -0.023177970200777054, -1.570796012878418)), 'hairback_c_02_wj': NoeVec3((0.0, 0.5400747060775757, 0.0)), 'hairback_c_03_wj': NoeVec3((0.0, -0.32155948877334595, 0.0)), 'hairback_c_04_wj': NoeVec3((0.0, -0.3722088932991028, 0.0)), 
    'hairback_l_01_wj': NoeVec3((0.0018325960263609886, -0.03153809905052185, -1.4660769701004028)), 'hairback_l_02_wj': NoeVec3((0.0033510320354253054, 0.5454503297805786, 0.06023130938410759)), 'hairback_l_03_wj': NoeVec3((0.04712389037013054, -0.31642821431159973, -0.09744173288345337)), 
    'hairback_l_04_wj': NoeVec3((-0.014660770073533058, -0.3607945144176483, 0.08148942142724991)), 'hairback_r_01_wj': NoeVec3((-0.00160570302978158, -0.023177970200777054, -1.6632989645004272)), 'hairback_r_02_wj': NoeVec3((-0.0037873650435358286, 0.5274385213851929, -0.08253662288188934)), 
    'hairback_r_03_wj': NoeVec3((-0.04398230090737343, -0.30691608786582947, 0.09260717034339905)), 'hairback_r_04_wj': NoeVec3((0.008168141357600689, -0.3617194890975952, -0.04536110907793045))},
    'WG7': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.1047196015715599, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.1047196015715599, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.21816620230674744, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.8028513789176941, -0.22689279913902283, -1.3439040184020996)), 'skirt_b_02_wj': NoeVec3((0.0, 0.04363323003053665, 0.0)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.1519169807434082)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.2863810062408447, 0.34033921360969543, -1.2042770385742188)), 'skirt_d_02_wj': NoeVec3((2.4621709115990598e-08, 0.2042035013437271, 0.0)), 'skirt_e_01_wj': NoeVec3((-4.768378971675702e-07, 2.6616270542144775, 1.570796012878418)), 
    'skirt_e_02_wj': NoeVec3((0.0, 0.16580629348754883, 0.0)), 'skirt_f_01_wj': NoeVec3((2.2863810062408447, 0.34033921360969543, -1.9373149871826172)), 'skirt_f_02_wj': NoeVec3((0.0, 0.2042035013437271, 0.0)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 8.940693163594915e-08, -1.9896750450134277)), 
    'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.8028513789176941, -0.22689279913902283, -1.7976889610290527)), 'skirt_h_02_wj': NoeVec3((1.9765849401665037e-08, 0.04363323003053665, 0.0)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'hair_chara_root': NoeVec3((-0.050385911017656326, 0.0020432400051504374, -1.610834002494812)), 
    'hairside_l_01_wj': NoeVec3((-0.784270703792572, 0.042309220880270004, -1.6196880340576172)), 'hairside_l_02_wj': NoeVec3((0.037803828716278076, -0.2680476903915405, -0.2901434898376465)), 'hairside_r_01_wj': NoeVec3((0.7926954030990601, 0.04149625077843666, -1.431264042854309)), 
    'hairside_r_02_wj': NoeVec3((-0.052062999457120895, -0.3225542902946472, 0.23261749744415283)), 'hairtwintail_l_01_wj': NoeVec3((3.101327896118164, 0.04660448059439659, -1.4349240064620972)), 'hairtwintail_l_02_wj': NoeVec3((0.041588399559259415, -0.004207133781164885, 0.16269420087337494)), 
    'hairtwintail_a_l_01_wj': NoeVec3((0.01139593031257391, 3.0963189601898193, -3.202522039413452)), 'hairtwintail_a_l_02_wj': NoeVec3((-9.536740890325746e-07, 0.13923540711402893, 0.002703985897824168)), 'hairtwintail_b_l_01_wj': NoeVec3((-0.04509685933589935, 0.010574930347502232, -0.07445521652698517)), 
    'hairtwintail_b_l_02_wj': NoeVec3((3.450568101470708e-06, 0.0013176429783925414, 0.009059794247150421)), 'hairtwintail_r_01_wj': NoeVec3((0.048352599143981934, 0.04737957939505577, -1.626518964767456)), 'hairtwintail_r_02_wj': NoeVec3((-0.04159066826105118, 0.004208722151815891, 0.1626943051815033)), 
    'hairtwintail_a_r_01_wj': NoeVec3((3.1301960945129395, -0.045268431305885315, -0.06093014031648636)), 'hairtwintail_a_r_02_wj': NoeVec3((-1.9072609802606166e-06, -0.13923560082912445, 0.0027041779831051826)), 'hairtwintail_b_r_01_wj': NoeVec3((0.04507505148649216, -0.010575749911367893, -0.07445575296878815)), 
    'hairtwintail_b_r_02_wj': NoeVec3((9.293372386309784e-06, -0.001317501999437809, 0.009059898555278778)), 'hair_root': NoeVec3((-0.03490640968084335, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_c_03_wj': NoeVec3((0.0, 0.13962629437446594, 0.0)), 
    'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 'hairback_l_03_wj': NoeVec3((0.0, 0.1221729964017868, 0.10471980273723602)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778)), 
    'hairback_r_03_wj': NoeVec3((3.377945034799268e-08, 0.1221729964017868, -0.1047196015715599))},
    'YRA': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 
    'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 
    'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'hair_l_01_wj': NoeVec3((-0.7853981852531433, 0.1745329052209854, -1.3089970350265503)), 'hair_r_01_wj': NoeVec3((0.7853981852531433, 0.1745329052209854, -1.832595944404602)), 'hair_t_01_wj': NoeVec3((3.0083720684051514, 0.37980979681015015, 1.2239190340042114)), 
    'hairside_l_01_wj': NoeVec3((0.0, -0.19198620319366455, -1.815142035484314)), 'hairside_r_01_wj': NoeVec3((0.0, -0.19198620319366455, -1.326449990272522)), 'hairsideback_l_01_wj': NoeVec3((-0.7853981852531433, 0.1745329052209854, -1.3089970350265503)), 
    'hairsideback_r_01_wj': NoeVec3((0.7853981852531433, 0.1745329052209854, -1.832595944404602)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 
    'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'YRC': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.3317365050315857, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.7958701252937317, 0.09674359858036041, -1.3962630033493042)), 
    'hair_r_01_wj': NoeVec3((0.7958701252937317, 0.09673783928155899, -1.7453290224075317)), 'hairosage_l_01_wj': NoeVec3((-0.3490658104419708, 0.25307270884513855, -0.9128072261810303)), 'hairosage_l_02_wj': NoeVec3((0.0, 0.0, -0.5929285287857056)), 
    'hairosage_r_01_wj': NoeVec3((0.3490658104419708, 0.25307270884513855, -2.211332082748413)), 'hairosage_r_02_wj': NoeVec3((0.0, 0.0, 0.5929232239723206)), 'hairside_l_01_wj': NoeVec3((-0.19198620319366455, 0.01745329052209854, -1.483530044555664)), 
    'hairside_r_01_wj': NoeVec3((-0.19198620319366455, -0.01745329052209854, -1.6580630540847778)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 
    'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'YRK': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.7853981852531433, 0.1745329052209854, -1.3089970350265503)), 
    'hair_r_01_wj': NoeVec3((0.7853981852531433, 0.1745329052209854, 4.450590133666992)), 'hairside_l_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.6580630540847778)), 'hairside_l_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.0)), 
    'hairside_l_03_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 'hairside_r_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.483530044555664)), 'hairside_r_02_wj': NoeVec3((0.0, -0.1745329052209854, 0.0)), 'hairside_r_03_wj': NoeVec3((0.0, -0.0872664600610733, 0.0)), 
    'ribbon_l_01_wj': NoeVec3((0.14091910421848297, 0.1607035994529724, 0.11081510037183762)), 'ribbon_r_01_wj': NoeVec3((-0.14091910421848297, 0.1607035994529724, 3.0307819843292236)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 
    'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))},
    'YRY': {'lskirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'lskirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4486229419708252)), 'lskirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 
    'lskirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'lskirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'lskirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'lskirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'lskirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6929689645767212)), 'skirt_a_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 
    'skirt_b_01_wj': NoeVec3((-0.7853981852531433, -0.10471980273723602, -1.4660769701004028)), 'skirt_c_01_wj': NoeVec3((-1.570796012878418, 0.0, -1.3089970350265503)), 'skirt_c_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 
    'skirt_d_01_wj': NoeVec3((-2.3387410640716553, 0.1745329052209854, -1.3962630033493042)), 'skirt_e_01_wj': NoeVec3((0.0, 2.8797929286956787, 1.570796012878418)), 'skirt_f_01_wj': NoeVec3((2.3387410640716553, 0.1745329052209854, -1.7453290224075317)), 
    'skirt_g_01_wj': NoeVec3((1.570796012878418, 0.0, -1.832595944404602)), 'skirt_g_02_wj': NoeVec3((0.0, 0.0872664600610733, 0.0)), 'skirt_h_01_wj': NoeVec3((0.7853981852531433, -0.10471980273723602, -1.6755160093307495)), 'spine_wj': NoeVec3((0.0, 0.0, 1.570796012878418)), 
    'breast_c_wj': NoeVec3((0.0, 3.1415929794311523, 0.0)), 'breast_l_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'breast_r_wj': NoeVec3((0.0, -1.3962630033493042, -3.1415929794311523)), 'face_root': NoeVec3((0.0, 0.01745329052209854, 0.0)), 
    'hair_chara_root': NoeVec3((-0.01745329052209854, 0.0, -1.570796012878418)), 'hair_c_01_wj': NoeVec3((0.0, -0.0872664600610733, -1.570796012878418)), 'hair_l_01_wj': NoeVec3((-0.8522722125053406, 0.20905029773712158, -1.5035719871520996)), 
    'hair_r_01_wj': NoeVec3((0.8522791862487793, 0.20905549824237823, 4.658073902130127)), 'hairback02_l_01_wj': NoeVec3((0.006805458106100559, 0.7035037875175476, -1.5682499408721924)), 'hairback02_r_01_wj': NoeVec3((0.007229119073599577, 0.7700269818305969, -1.567620038986206)), 
    'hairside02_l_01_wj': NoeVec3((1.686110019683838, -0.6346017122268677, -2.0487899780273438)), 'hairside02_r_01_wj': NoeVec3((1.2001229524612427, -0.6244019865989685, -1.0632719993591309)), 'hairside_l_01_wj': NoeVec3((0.04065081104636192, -0.3347192108631134, -1.996917963027954)), 
    'hairside_r_01_wj': NoeVec3((-0.0291555505245924, -0.34686151146888733, -1.1593539714813232)), 'hair_root': NoeVec3((-0.03490658104419708, 0.0, -1.570796012878418)), 'hairback_c_01_wj': NoeVec3((0.0, 3.054326057434082, 1.570796012878418)), 
    'hairback_l_01_wj': NoeVec3((-2.5132739543914795, 0.1221729964017868, -1.483530044555664)), 'hairback_r_01_wj': NoeVec3((2.5132739543914795, 0.1221729964017868, -1.6580630540847778))}}
    boneRotExtra = {'ARH_002': {'ribbon_chara_root': NoeVec3((0.1745329052209854, 0.0, -1.570796012878418))}, 'ARI_002': {'ribbon_chara_root': NoeVec3((0.0, 3.1415929794311523, 0.0))}, 'ART_002': {'ribbon_chara_root': NoeVec3((0.0, 3.1415929794311523, 0.0))},
    'GCG_002': {'ribbon_chara_root': NoeVec3((0.0, 0.0, -1.570796012878418))}, 'GCM_002': {'ribbon_chara_root': NoeVec3((0.0, 0.0, -1.570796012878418))}}
    return boneRot, boneRotExtra

def initF2XHashDict():
    hashDict = {0xCC71E092: 'CMN_EYES_CENTER_D', 0xEB62BACB: 'CMN_EYES_CENTER_U', 0x3DA92482: 'CMN_EYES_DOWN', 0x20B63BDB: 'CMN_EYES_DOWN_LEFT', 0x1BF515A6: 'CMN_EYES_DOWN_LEFT_M',
    0xAD70A0B9: 'CMN_EYES_DOWN_M', 0xAB1940E9: 'CMN_EYES_DOWN_RIGHT', 0x1F73D792: 'CMN_EYES_DOWN_RIGHT_M', 0x4131C6CE: 'CMN_EYES_LEFT', 0x0063C185: 'CMN_EYES_LEFT_M', 0xAC58836D: 'CMN_EYES_MOVE_L_R',
    0x04342A94: 'CMN_EYES_MOVE_U_D', 0x68894937: 'CMN_EYES_MOVE_UL_DR', 0xE83BC978: 'CMN_EYES_MOVE_UR_DL', 0xDEA33C57: 'CMN_EYES_RESET', 0x23C0B0F0: 'CMN_EYES_RIGHT', 0x5EC07882: 'CMN_EYES_RIGHT_M',
    0xB2FC99A0: 'CMN_EYES_UP', 0x2C50E37F: 'CMN_EYES_UP_LEFT', 0x2BF0AFE2: 'CMN_EYES_UP_LEFT_M', 0x99FCBB7C: 'CMN_EYES_UP_M', 0xA94A7B5E: 'CMN_EYES_UP_RIGHT', 0xE9024D9F: 'CMN_EYES_UP_RIGHT_M',
    0x5248F064: 'CMN_HAND_BOTTLE', 0x8941AEAC: 'CMN_HAND_CHOP', 0x4EDB7807: 'CMN_HAND_CLOSE', 0x63AA275F: 'CMN_HAND_FAN', 0xBEEEA116: 'CMN_HAND_FLASHLIGHT', 0x51946790: 'CMN_HAND_FOX',
    0x9A14C085: 'CMN_HAND_FULLOPEN', 0x135DAC82: 'CMN_HAND_GOOD', 0xC6C3F044: 'CMN_HAND_GUN', 0xEB7A8562: 'CMN_HAND_HEART', 0x7B5BB67A: 'CMN_HAND_HOLD', 0xED31BAC8: 'CMN_HAND_MIC',
    0xF60C8D75: 'CMN_HAND_NEGI', 0xF79E5B56: 'CMN_HAND_NORMAL', 0x74C8C7E5: 'CMN_HAND_OK', 0x05595758: 'CMN_HAND_ONE', 0xE75D0A15: 'CMN_HAND_OPEN', 0x24A93124: 'CMN_HAND_PEACE',
    0xCC8E9920: 'CMN_HAND_PEACECLOSE', 0xB838F585: 'CMN_HAND_PHONE', 0x47171BDD: 'CMN_HAND_PICK', 0xB5918A0C: 'CMN_HAND_PICK2', 0xC8CA0A99: 'CMN_HAND_PLATE', 0x14FE02BF: 'CMN_HAND_PUNCH',
    0xD122599A: 'CMN_HAND_RESET', 0x151E3BBA: 'CMN_HAND_SIZEN', 0x84E43E6B: 'CMN_HAND_THREE', 0xA48BA7F5: 'MIK_FACE_ADMIRATION', 0x1925F549: 'MIK_FACE_ADMIRATION_CL', 0xDC1AF4F8: 'MIK_FACE_CLARIFYING',
    0xB0800D79: 'MIK_FACE_CLARIFYING_CL', 0x3453BE04: 'MIK_FACE_CLOSE', 0xAC364D56: 'MIK_FACE_COOL', 0xC78E8DA1: 'MIK_FACE_COOL_CL', 0x1E5A8164: 'MIK_FACE_DAZZLING', 0x5601694D: 'MIK_FACE_DAZZLING_CL',
    0x4486321E: 'MIK_FACE_EYEBROW_UP_LEFT', 0x2A884ED5: 'MIK_FACE_EYEBROW_UP_LEFT_CL', 0x96C7FD2A: 'MIK_FACE_EYEBROW_UP_RIGHT', 0xD5EAC491: 'MIK_FACE_EYEBROW_UP_RIGHT_CL',
    0xB5C228D2: 'MIK_FACE_GENKI', 0x7116FF76: 'MIK_FACE_GENKI_CL', 0x8D88857E: 'MIK_FACE_GENTLE', 0x35A03B75: 'MIK_FACE_GENTLE_CL', 0x9CA098A0: 'MIK_FACE_KIRI', 0xD0423BB1: 'MIK_FACE_KIRI_CL',
    0xD1EE03AD: 'MIK_FACE_KOMARIEGAO', 0xCE74137C: 'MIK_FACE_KOMARIWARAI', 0x81B7238D: 'MIK_FACE_KOMARIWARAI_CL', 0x4BD9C988: 'MIK_FACE_KONWAKU', 0xC1710C97: 'MIK_FACE_KONWAKU_CL',
    0x0BA4A548: 'MIK_FACE_KUMON', 0x7891EAB3: 'MIK_FACE_KUMON_CL', 0x351E8FB3: 'MIK_FACE_KUTSUU', 0xCD915DF7: 'MIK_FACE_KUTSUU_CL', 0x67921A1C: 'MIK_FACE_LASCIVIOUS',
    0xF4D467F3: 'MIK_FACE_LASCIVIOUS_CL', 0x0B423D16: 'MIK_FACE_LAUGH', 0x7FA01BDB: 'MIK_FACE_NAGASI', 0x6BBC2A4E: 'MIK_FACE_NAGASI_CL', 0x9619BB34: 'MIK_FACE_NAKI', 0x0655CE85: 'MIK_FACE_NAKI_CL',
    0xA69F3640: 'MIK_FACE_NAYAMI', 0xBD0BC34D: 'MIK_FACE_NAYAMI_CL', 0xAADAC5FD: 'MIK_FACE_OMOU', 0x30D08CEE: 'MIK_FACE_OMOU_CL', 0x1C071A15: 'MIK_FACE_RESET', 0xD7C1DA42: 'MIK_FACE_SAD',
    0x70C43C9D: 'MIK_FACE_SAD_CL', 0xE11659A5: 'MIK_FACE_SETTLED', 0xAE1054D5: 'MIK_FACE_SETTLED_CL', 0x9E697E02: 'MIK_FACE_SETUNA', 0x2BFFC1CB: 'MIK_FACE_SETUNA_CL', 0x0EE65D7B: 'MIK_FACE_SMILE',
    0xC65DCBCB: 'MIK_FACE_SMILE_CL', 0x68C2A780: 'MIK_FACE_STRONG', 0x038594DF: 'MIK_FACE_STRONG_CL', 0xA1D6ECD7: 'MIK_FACE_SUPSERIOUS', 0x3667062A: 'MIK_FACE_SUPSERIOUS_CL',
    0x6DFA429B: 'MIK_FACE_SURPRISE', 0x6EF0F796: 'MIK_FACE_SURPRISE_CL', 0x0E318E47: 'MIK_FACE_TSUYOKIWARAI', 0x942B7539: 'MIK_FACE_TSUYOKIWARAI_CL', 0x369176D6: 'MIK_FACE_UTURO',
    0xE704376B: 'MIK_FACE_UTURO_CL', 0xD86E2250: 'MIK_FACE_WINK_L', 0x37C0C575: 'MIK_FACE_WINK_R', 0x91E4A429: 'MIK_FACE_WINKG_L', 0xAFC80288: 'MIK_FACE_WINKG_R', 0x60943A41: 'MIK_FACE_YARU',
    0x1BC8C7F8: 'MIK_FACE_YARU_CL', 0x8D679789: 'MIK_KUCHI_A', 0x27256E52: 'MIK_KUCHI_CHU', 0x9834C866: 'MIK_KUCHI_E', 0x33838A11: 'MIK_KUCHI_E_DOWN', 0xC288A2B6: 'MIK_KUCHI_HAMISE',
    0x2EE45D78: 'MIK_KUCHI_HAMISE_DOWN', 0xD42ACE8B: 'MIK_KUCHI_HAMISE_E', 0xBD509253: 'MIK_KUCHI_HE', 0x8C96BE4C: 'MIK_KUCHI_HE_S', 0xD1CC9C6B: 'MIK_KUCHI_HERAHERA', 0x5FED5E14: 'MIK_KUCHI_I',
    0xAAD5F001: 'MIK_KUCHI_MOGUMOGU', 0xEDEAD6C9: 'MIK_KUCHI_NEKO', 0x8AAAB09E: 'MIK_KUCHI_NEUTRAL', 0xB9808D8F: 'MIK_KUCHI_NIYA', 0x2B9AA94D: 'MIK_KUCHI_O', 0xE472692C: 'MIK_KUCHI_PSP_A',
    0x4A88205A: 'MIK_KUCHI_PSP_E', 0xAA2BD9D4: 'MIK_KUCHI_PSP_NIYA', 0x1444FEAA: 'MIK_KUCHI_PSP_NIYARI', 0x64030BB3: 'MIK_KUCHI_PSP_O', 0x72354540: 'MIK_KUCHI_PSP_SURPRISE',
    0x61198CF4: 'MIK_KUCHI_RESET', 0x9218C1AC: 'MIK_KUCHI_SAKEBI', 0x57037C4B: 'MIK_KUCHI_SAKEBI_L', 0x932BBDAC: 'MIK_KUCHI_SANKAKU', 0x23EC5921: 'MIK_KUCHI_SHIKAKU', 0x349493AB: 'MIK_KUCHI_SMILE',
    0x48A15672: 'MIK_KUCHI_SMILE_L', 0x47BB071D: 'MIK_KUCHI_SURPRISE', 0x6BF6E5B4: 'MIK_KUCHI_U'}
    return hashDict