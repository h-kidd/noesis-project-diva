#By Minmode
#Special thanks: Chrrox, korenkonder, BlueSkyth, Brolijah, samyuu
from inc_noesis import *
from vmd import Vmd
import noesis
import rapi
import os.path
import math

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
    magic =  bs.readBytes(4).decode("ASCII")
    if magic != "MOSD":
        return 0
    return 1

def osiCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic =  bs.readBytes(4).decode("ASCII")
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
    magic =  bs.readBytes(4).decode("ASCII")
    if magic != "MTXD":
        return 0
    return 1

def txiCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic =  bs.readBytes(4).decode("ASCII")
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
    magic =  bs.readBytes(4).decode("ASCII")
    if magic != "SPRC":
        return 0
    return 1

def spiCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic =  bs.readBytes(4).decode("ASCII")
    if magic != "SPDB":
        return 0
    return 1

def iblCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 7:
        return 0
    magic =  bs.readBytes(7).decode("ASCII")
    if magic != "VF5_IBL":
        return 0
    return 1

def emcsCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 4:
        return 0
    magic =  bs.readBytes(4).decode("ASCII")
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
    magic =  bs.readBytes(4).decode("ASCII")
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
    magic =  bs.readBytes(4).decode("ASCII")
    if magic != "EXPC":
        return 0
    return 1

def objectSetLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))[:-4]
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    texDbData = getFileData(fileDir, "tex_db.bin")
    texDb = TexDb(32)
    texDb.readTexDb(NoeBitStream(texDbData))
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
    obj = ObjectSet(mdlList, txp.texList, objDb.db[fileName.upper()], texDb, boneData, 32, None)
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
        texObj = ObjectSet([], txp2.texList, objDb.db[fileName.upper()], texDb, boneData, 32, None)
        texObj.readObjSet(NoeBitStream(texObjData), texObjData)
        for i in range(len(mdlList[0].modelMats.texList)):
            mdlList[0].modelMats.texList[i] = texObj.texList[texObj.texDict[mdlList[0].modelMats.texList[i].name]]
    return 1

def osdLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
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
        bone.boneData.name.append("gblctr")
        bone.boneData.mtx.append(NoeMat43())
        bone.boneData.parent.append(-1)
        bone.boneData.name.append("kg_ya_ex")
        bone.boneData.mtx.append(NoeMat43())
        bone.boneData.parent.append(0)
    osiData = getFileData(fileDir, fileName + ".osi")
    test = osiCheckType(osiData)
    if test == 0:
        noesis.messagePrompt("Invalid osi file.")
        return 0
    osi = Osi()
    osi.readOsi(NoeBitStream(osiData))
    osd = Osd(mdlList, txd.texList)
    osd.readOsd(data, osi.objDb.db[fileName.upper()], txi.texDb, bone.boneData)
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
    sprDbData = getFileData(fileDir, "spr_db.bin")
    sprDb = SprDb(32)
    sprDb.readSprDb(NoeBitStream(sprDbData))
    spr = Sprite(texList, fileName + ".bin", sprDb, 32)
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
    spr.readSpr(data, fileName, spi.sprDb)
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
    modelPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open Model File", "Select a bin model file to open.", noesis.getSelectedFile(), None)
    if isinstance(modelPath, str):
        fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))[:-4]
        fileDir = rapi.getDirForFilePath(modelPath)
        objData = rapi.loadIntoByteArray(modelPath)
        test = objectSetCheckType(objData)
        if test == 0:
            noesis.messagePrompt("Invalid model file.")
            return 0
        texDbData = getFileData(fileDir, "tex_db.bin")
        texDb = TexDb(32)
        texDb.readTexDb(NoeBitStream(texDbData))
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
        obj = ObjectSet(mdlList, txp.texList, objDb.db[fileName.upper()], texDb, boneData, 32, None)
        obj.isMot = True
        obj.readObjSet(NoeBitStream(objData), objData)
    else:
        noesis.messagePrompt("Invalid input.")
        return 0
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))[4:]
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    motDbData = getFileData(fileDir, "mot_db.bin")
    motDb = MotDb()
    motDb.readDb(NoeBitStream(motDbData))
    mot = Motion(motDb, boneData, obj.boneList[0], obj.boneDict[0])
    mot.readMotion(NoeBitStream(data), fileName)
    mdlList[0].setAnims(mot.animList)
    rapi.setPreviewOption("setAnimSpeed", "60")
    if exportVmd:
        vmdExport(mot.names, mot.frameCounts, mot.animList, None, "diva.bone", "diva.morph")
    return 1

def motLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    modelPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open Model File", "Select a osd model file to open.", noesis.getSelectedFile(), None)
    if isinstance(modelPath, str):
        fileName = rapi.getExtensionlessName(rapi.getLocalFileName(modelPath))
        fileDir = rapi.getDirForFilePath(modelPath)
        osdData = rapi.loadIntoByteArray(modelPath)
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
        isMGF = False
        if boneData != None:
            bone = Bone()
            boneDataName = rapi.getExtensionlessName(rapi.getLocalFileName(boneDataDir))
            if boneDataName != "bone_data":
                skel = boneDataName.upper()
                isMGF = True
            elif fileName[:3].upper() != "CMN":
                skel = fileName[:3].upper()
            else:
                skel = None
            bone.readBone(NoeBitStream(boneData), skel)
        else:
            bone = Bone()
            bone.boneData = BoneData(32)
            bone.boneData.name.append("gblctr")
            bone.boneData.mtx.append(NoeMat43())
            bone.boneData.parent.append(-1)
            bone.boneData.name.append("kg_ya_ex")
            bone.boneData.mtx.append(NoeMat43())
            bone.boneData.parent.append(0)
        osiData = getFileData(fileDir, fileName + ".osi")
        test = osiCheckType(osiData)
        if test == 0:
            noesis.messagePrompt("Invalid osi file.")
            return 0
        osi = Osi()
        osi.readOsi(NoeBitStream(osiData))
        osd = Osd(mdlList, txd.texList)
        osd.readOsd(osdData, osi.objDb.db[fileName.upper()], txi.texDb, bone.boneData, True)
    else:
        noesis.messagePrompt("Invalid input.")
        return 0
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    mot = Motc()
    mot.readMotc(data, bone.boneData, osd.boneList[0], osd.boneDict[0], fileName, fileDir, isMGF)
    mdlList[0].setAnims(mot.animList)
    rapi.setPreviewOption("setAnimSpeed", "60")
    if exportVmd:
        vmdExport(mot.names, mot.frameCounts, mot.animList, None, "diva.bone", "diva.morph")
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
        self.type = {}
        self.name = []
        self.mtx = []
        self.parent = []
        self.addressSpace = addressSpace
        
    def readBoneData(self, bs, skel):
        magic = bs.readUInt()
        skelCount = bs.readInt()
        skelOff = readOff(bs, self.addressSpace)
        skelNames = getOffStringList(bs, self.addressSpace, readOff(bs, self.addressSpace), skelCount)
        boneMtx = NoeMat43()
        self.name.append("gblctr")
        self.mtx.append(NoeMat43())
        self.parent.append(-1)
        self.name.append("kg_ya_ex")
        self.mtx.append(NoeMat43())
        self.parent.append(0)
        bs.seek(skelOff, NOESEEK_ABS)
        for i in range(skelCount):
            off = readOff(bs, self.addressSpace)
            if skelNames[i] == skel:
                pos = bs.tell()
                bs.seek(off, NOESEEK_ABS)
                self.readSkel(bs)
                bs.seek(pos, NOESEEK_ABS)

    def readSkel(self, bs):
        boneOff = readOff(bs, self.addressSpace)
        boneVec3Count = bs.readInt()
        boneVec3Off = readOff(bs, self.addressSpace)
        unk = readOff(bs, self.addressSpace)
        objBoneCount = bs.readInt()
        objBoneNames = getOffStringList(bs, self.addressSpace, readOff(bs, self.addressSpace), objBoneCount)
        motBoneCount = bs.readInt()
        motBoneNames = getOffStringList(bs, self.addressSpace, readOff(bs, self.addressSpace), motBoneCount)
        parentOff = readOff(bs, self.addressSpace)
        self.name.extend(motBoneNames)
        bs.seek(boneOff, NOESEEK_ABS)
        self.readBone(bs)
        bs.seek(boneVec3Off, NOESEEK_ABS)
        vec3 = self.readBoneVec3(bs, boneVec3Count)
        bs.seek(parentOff, NOESEEK_ABS)
        self.parent.extend(self.readBoneParent(bs, motBoneCount))
        self.loadSkel(vec3, objBoneNames, motBoneCount, motBoneNames)

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

    def readBoneParent(self, bs, motBoneCount):
        parent = []
        for i in range(motBoneCount):
            pIdx = bs.readShort() + 2
            if pIdx != 1 and self.name[pIdx].endswith("_cp") and self.name[pIdx] != "n_hara_cp":
                parent.append(parent[pIdx - 2])
            else:
                parent.append(pIdx)
        return parent

    def loadSkel(self, vec3, objBoneNames, motBoneCount, motBoneNames):
        for i in range(motBoneCount):
            if motBoneNames[i] in objBoneNames:
                pos = NoeVec3(vec3[objBoneNames.index(motBoneNames[i]) + 2])
            else:
                pos = NoeVec3((0, 0, 0))
            boneMtx = NoeMat43()
            boneMtx[3] = pos
            self.mtx.append(boneMtx)

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
    
    def __init__(self, mdlList, texList, objDb, texDb, boneData, addressSpace, sectionOff):
        self.mdlList = mdlList
        self.texList = texList
        self.objDb = objDb
        self.texDb = texDb
        self.boneData = boneData
        self.texDict = {}
        self.texHashDict = {}
        self.boneList =[]
        self.boneDict = []
        self.endian = 0
        self.addressSpace = addressSpace
        self.sectionOff = sectionOff
        self.objId = []
        self.skinBoneName = []
        self.clsWeight = []
        self.clsBoneName = []
        self.isMot = False
        
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
                self.texList[i].name = self.texDb.db[texId]
                self.texDict[self.texList[i].name] = i
                self.texHashDict[texId] = self.texList[i].name
            except:
                self.texList[i].name += "_" + str(i)
                self.texDict[self.texList[i].name] = i
                self.texHashDict[texId] = self.texList[i].name

    def readSkin(self, bs, data, objCount):
        skinBoneMtx = []
        skinBoneParent = []
        clsNode = []
        boneFixList = ["n_hara_cp", "n_hara", "cl_mune", "j_mune_wj", "kl_kubi", "n_kao", "cl_kao", "face_root", "c_kata_l", "c_kata_r", "kl_te_l_wj", "kl_te_r_wj", "j_kata_l_wj_cu", "j_kata_r_wj_cu", "cl_momo_l", "cl_momo_r", "j_momo_l_wj", "j_momo_r_wj", "e_ude_l_cp", "e_ude_r_cp", "e_sune_l_cp", "e_sune_r_cp", "skirt_root", "lskirt_root"]
        if self.sectionOff:
            for i in range(objCount):
                if self.sectionOff["OSKN"][i]:
                    skin = Skin(self.boneData, self.addressSpace)
                    if self.addressSpace == 32:
                        ts = NoeBitStream(data[self.sectionOff["OSKN"][i]:], self.endian)
                        ts.seek(0x20, NOESEEK_ABS)
                        skin.readSkin(ts)
                    elif self.addressSpace == 64:
                        skin.readSkin(NoeBitStream(data[self.sectionOff["OSKN"][i]:], self.endian))
                    skinBoneMtx.append(skin.boneMtx)
                    self.skinBoneName.append(skin.boneName)
                    skinBoneParent.append(skin.boneParent)
                    clsNode.append(skin.clsNode)
                    self.clsWeight.append(skin.clsWeight)
                    self.clsBoneName.append(skin.clsBoneName)
                else:
                    skinBoneMtx.append([])
                    self.skinBoneName.append([])
                    skinBoneParent.append([])
                    clsNode.append([])
                    self.clsWeight.append({})
                    self.clsBoneName.append({})
        else:
            for i in range(objCount):
                skinOff = bs.readUInt()
                if skinOff != 0:
                    pos = bs.tell()
                    bs.seek(skinOff, NOESEEK_ABS)
                    skin = Skin(self.boneData, self.addressSpace)
                    skin.readSkin(bs)
                    bs.seek(pos, NOESEEK_ABS)
                    skinBoneMtx.append(skin.boneMtx)
                    self.skinBoneName.append(skin.boneName)
                    skinBoneParent.append(skin.boneParent)
                    clsNode.append(skin.clsNode)
                    self.clsWeight.append(skin.clsWeight)
                    self.clsBoneName.append(skin.clsBoneName)
                else:
                    skinBoneMtx.append([])
                    self.skinBoneName.append([])
                    skinBoneParent.append([])
                    clsNode.append([])
                    self.clsWeight.append({})
                    self.clsBoneName.append({})
        for i in range(objCount):
            self.boneList.append([])
            self.boneDict.append({})
            if skinBoneMtx[i]:
                self.loadBone(boneFixList, i, skinBoneMtx[i], self.skinBoneName[i], skinBoneMtx)
                self.loadParent(i, self.skinBoneName[i], skinBoneParent[i])
                if clsNode[i]:
                    self.loadClsBone(i, clsNode[i])
        if not self.isMot:
            for i in range(objCount):
                if skinBoneMtx[i]:
                    for a in range(len(self.boneList[i])):
                        if self.boneList[i][a].name not in boneFixList or self.boneList[i][a].name in self.skinBoneName[i]:
                            br = self.boneList[i][a]._matrix.inverse()
                            self.boneList[i][a]._matrix[0] = br[0]
                            self.boneList[i][a]._matrix[1] = br[1]
                            self.boneList[i][a]._matrix[2] = br[2]

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

    def loadBone(self, boneFixList, skinIdx, boneMtx, boneName, skinBoneMtx):
        boneDataCount = len(self.boneData.name)
        if boneDataCount != 2:
            for i in range(boneDataCount):
                name = self.boneData.name[i]
                parent = self.boneData.parent[i]
                if i == 0:
                    newBone = NoeBone(i, name, self.boneData.mtx[i], None, parent)
                    self.boneList[skinIdx].append(newBone)
                    self.boneDict[skinIdx][newBone.name] = newBone.index
                elif self.boneData.parent[i] == -1:
                    if any(name in bn for bn in self.skinBoneName):
                        idx = [(a, bn.index(name)) for a, bn in enumerate(self.skinBoneName) if name in bn]
                        mtx = skinBoneMtx[idx[0][0]][idx[0][1]]
                    elif name in boneFixList:
                        mtx = self.mtxFix(skinIdx, name, self.boneData.mtx[i], parent, skinBoneMtx)
                    else:
                        mtx = self.boneData.mtx[i]
                    newBone = NoeBone(i, name, mtx, None, 1)
                    self.boneList[skinIdx].append(newBone)
                    self.boneDict[skinIdx][newBone.name] = newBone.index
                else:
                    if any(name in bn for bn in self.skinBoneName):
                        idx = [(a, bn.index(name)) for a, bn in enumerate(self.skinBoneName) if name in bn]
                        mtx = skinBoneMtx[idx[0][0]][idx[0][1]]
                    elif name in boneFixList:
                        mtx = self.mtxFix(skinIdx, name, self.boneData.mtx[i], parent, skinBoneMtx)
                    else:
                        mtx = self.boneData.mtx[i] * self.boneList[skinIdx][parent]._matrix
                    if name.endswith("_cp") and not name.startswith("tl_up_kata"):
                        parent = 1
                    elif name == "n_momo_l_cd_ex" or name == "n_momo_a_l_wj_cd_ex":
                        parent = self.boneDict[skinIdx]["cl_momo_l"]
                    elif name == "n_momo_r_cd_ex" or name == "n_momo_a_r_wj_cd_ex":
                        parent = self.boneDict[skinIdx]["cl_momo_r"]
                    newBone = NoeBone(i, name, mtx, None, parent)
                    self.boneList[skinIdx].append(newBone)
                    self.boneDict[skinIdx][newBone.name] = newBone.index
            idxOff = boneDataCount
            cnt = 0
            for i in range(len(boneName)):
                name = boneName[i]
                if name not in self.boneDict[skinIdx]:
                    newBone = NoeBone(cnt + idxOff, name, boneMtx[i], None, 1)
                    self.boneList[skinIdx].append(newBone)
                    self.boneDict[skinIdx][newBone.name] = newBone.index
                    cnt += 1
        else:
            for i in range(boneDataCount):
                name = self.boneData.name[i]
                newBone = NoeBone(i, name, self.boneData.mtx[i], None, self.boneData.parent[i])
                self.boneList[skinIdx].append(newBone)
                self.boneDict[skinIdx][newBone.name] = newBone.index
            idxOff = boneDataCount
            for i in range(len(boneName)):
                name = boneName[i]
                newBone = NoeBone(i + idxOff, name, boneMtx[i], None, 1)
                self.boneList[skinIdx].append(newBone)
                self.boneDict[skinIdx][newBone.name] = newBone.index

    def mtxFix(self, skinIdx, name, originalMtx, parent, skinBoneMtx):
        mtx = NoeMat43()
        if name == "n_hara_cp" and any("kl_kosi_etc_wj" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("kl_kosi_etc_wj")) for a, bn in enumerate(self.skinBoneName) if "kl_kosi_etc_wj" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif name == "kl_kubi" and any("n_kubi_wj_ex" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("n_kubi_wj_ex")) for a, bn in enumerate(self.skinBoneName) if "n_kubi_wj_ex" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif name == "kl_te_l_wj" and any("n_ste_l_wj_ex" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("n_ste_l_wj_ex")) for a, bn in enumerate(self.skinBoneName) if "n_ste_l_wj_ex" in bn]
            mtx = skinBoneMtx[idx[0][0]][idx[0][1]]
        elif name == "kl_te_r_wj" and any("n_ste_r_wj_ex" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("n_ste_r_wj_ex")) for a, bn in enumerate(self.skinBoneName) if "n_ste_r_wj_ex" in bn]
            mtx = skinBoneMtx[idx[0][0]][idx[0][1]]
        elif name == "cl_momo_l" and any("j_momo_l_wj" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("j_momo_l_wj")) for a, bn in enumerate(self.skinBoneName) if "j_momo_l_wj" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif name == "cl_momo_l" and "n_momo_l_cd_ex" in self.boneData.name:
            idx = self.boneData.name.index("n_momo_l_cd_ex")
            mtx2 = self.boneData.mtx[idx] * self.boneList[skinIdx][parent]._matrix
            mtx[3] = mtx2[3]
        elif name == "cl_momo_l" and "n_momo_a_l_wj_cd_ex" in self.boneData.name:
            idx = self.boneData.name.index("n_momo_a_l_wj_cd_ex")
            mtx2 = self.boneData.mtx[idx] * self.boneList[skinIdx][parent]._matrix
            mtx[3] = mtx2[3]
        elif name == "cl_momo_r" and any("j_momo_r_wj" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("j_momo_r_wj")) for a, bn in enumerate(self.skinBoneName) if "j_momo_r_wj" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif name == "cl_momo_r" and "n_momo_r_cd_ex" in self.boneData.name:
            idx = self.boneData.name.index("n_momo_r_cd_ex")
            mtx2 = self.boneData.mtx[idx] * self.boneList[skinIdx][parent]._matrix
            mtx[3] = mtx2[3]
        elif name == "cl_momo_r" and "n_momo_a_r_wj_cd_ex" in self.boneData.name:
            idx = self.boneData.name.index("n_momo_a_r_wj_cd_ex")
            mtx2 = self.boneData.mtx[idx] * self.boneList[skinIdx][parent]._matrix
            mtx[3] = mtx2[3]
        elif name == "e_ude_l_cp" and any("n_ste_l_wj_ex" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("n_ste_l_wj_ex")) for a, bn in enumerate(self.skinBoneName) if "n_ste_l_wj_ex" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif name == "e_ude_r_cp" and any("n_ste_r_wj_ex" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("n_ste_r_wj_ex")) for a, bn in enumerate(self.skinBoneName) if "n_ste_r_wj_ex" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif name == "e_sune_l_cp" and any("kl_asi_l_wj_co" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("kl_asi_l_wj_co")) for a, bn in enumerate(self.skinBoneName) if "kl_asi_l_wj_co" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif name == "e_sune_l_cp" and "kl_asi_l_wj_co" in self.boneData.name:
            idx = self.boneData.name.index("kl_asi_l_wj_co")
            mtx2 = self.boneData.mtx[idx] * self.boneList[skinIdx][self.boneData.parent[idx]]._matrix
            mtx[3] = mtx2[3]
        elif name == "e_sune_r_cp" and any("kl_asi_r_wj_co" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("kl_asi_r_wj_co")) for a, bn in enumerate(self.skinBoneName) if "kl_asi_r_wj_co" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif name == "e_sune_r_cp" and "kl_asi_r_wj_co" in self.boneData.name:
            idx = self.boneData.name.index("kl_asi_r_wj_co")
            mtx2 = self.boneData.mtx[idx] * self.boneList[skinIdx][self.boneData.parent[idx]]._matrix
            mtx[3] = mtx2[3]
        elif (name == "n_kao" or name == "cl_kao") and any("j_kao_wj" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("j_kao_wj")) for a, bn in enumerate(self.skinBoneName) if "j_kao_wj" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif (name == "c_kata_l" or name == "j_kata_l_wj_cu") and any("n_skata_l_wj_cd_ex" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("n_skata_l_wj_cd_ex")) for a, bn in enumerate(self.skinBoneName) if "n_skata_l_wj_cd_ex" in bn]
            mtx = skinBoneMtx[idx[0][0]][idx[0][1]]
        elif (name == "c_kata_r" or name == "j_kata_r_wj_cu") and any("n_skata_r_wj_cd_ex" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("n_skata_r_wj_cd_ex")) for a, bn in enumerate(self.skinBoneName) if "n_skata_r_wj_cd_ex" in bn]
            mtx = skinBoneMtx[idx[0][0]][idx[0][1]]
        elif (name == "skirt_root" or name == "lskirt_root") and any("hips_wj" in bn for bn in self.skinBoneName):
            idx = [(a, bn.index("hips_wj")) for a, bn in enumerate(self.skinBoneName) if "hips_wj" in bn]
            mtx[3] = skinBoneMtx[idx[0][0]][idx[0][1]][3]
        elif name == "face_root" or name == "cl_momo_l" or name == "cl_momo_r":
            mtx[3] = self.boneList[skinIdx][parent]._matrix[3]
        elif name == "n_hara" or name == "cl_mune" or name == "j_mune_wj" or name == "j_momo_l_wj" or name == "j_momo_r_wj":
            mtx = self.boneList[skinIdx][parent]._matrix
        else:
            mtx = originalMtx * self.boneList[skinIdx][parent]._matrix
        return mtx
    
    def loadParent(self, skinIdx, boneName, boneParent):
        for i in range(len(boneName)):
            if boneName[i] in boneParent and boneName[i] not in self.boneData.name:
                name = boneName[i]
                parent = boneParent[name]
                if skinIdx == 0 and len(self.boneData.name) > 2:
                    if parent == "e_sune_l_cp":
                        parent = "kl_asi_l_wj_co"
                    elif parent == "e_sune_r_cp":
                        parent = "kl_asi_r_wj_co"
                self.boneList[skinIdx][self.boneDict[skinIdx][name]].parentIndex = self.boneDict[skinIdx][parent]

    def loadClsBone(self, skinIdx, clsNode):
        for i in range(len(clsNode)):
            mtx = NoeMat43()
            mtx[3] = clsNode[i][1]
            name = clsNode[i][0]
            parent = clsNode[i][2]
            newBone = NoeBone(len(self.boneList[skinIdx]), name, mtx, None, self.boneDict[skinIdx][parent])
            self.boneList[skinIdx].append(newBone)
            self.boneDict[skinIdx][newBone.name] = newBone.index

class Osd:
    
    def __init__(self, mdlList, texList):
        self.mdlList = mdlList
        self.texList = texList
        self.boneList =[]
        self.boneDict = []
        self.objId = []
        self.sectionOff = {"OMDL":[], "OSKN":[], "OIDX":[], "OVTX":[]}

    def readOsd(self, data, objDb, texDb, boneData, isMot = False):
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
        objectSet = ObjectSet(self.mdlList, self.texList, objDb, texDb, boneData, addressSpace, self.sectionOff)
        if isMot:
            objectSet.isMot = True
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
    
    def __init__(self, boneData, addressSpace):
        self.boneData = boneData
        self.addressSpace = addressSpace
        self.boneMtx = []
        self.boneName = []
        self.boneParent = {}
        self.expNode = {}
        self.osgNode = {}
        self.cnsNode = {}
        self.clsNode = []
        self.clsWeight = {}
        self.clsBoneName = {}
        
    def readSkin(self, bs):
        boneIdOff = readOff(bs, self.addressSpace)
        boneMtxOff = readOff(bs, self.addressSpace)
        boneNameOff = readOff(bs, self.addressSpace)
        exDataOff = readOff(bs, self.addressSpace)
        boneCount = bs.readInt()
        boneParentOff = readOff(bs, self.addressSpace)
        if boneCount:
            bs.seek(boneMtxOff, NOESEEK_ABS)
            self.readBoneMtx(bs, boneCount)
            self.boneName = getOffStringList(bs, self.addressSpace, boneNameOff, boneCount)
            bs.seek(boneIdOff, NOESEEK_ABS)
            boneId = self.readBoneId(bs, boneCount)
            if boneParentOff:
                bs.seek(boneParentOff, NOESEEK_ABS)
                self.readBoneParent(bs, boneCount, boneId)
            if exDataOff:
                bs.seek(exDataOff, NOESEEK_ABS)
                #try:
                self.readExData(bs)
                #except:
                #	pass

    def readBoneId(self, bs, boneCount):
        boneId = {}
        for i in range(boneCount):
            boneId[bs.readUInt()] = self.boneName[i]
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
        self.boneMtx = mtx

    def readBoneParent(self, bs, boneCount, boneId):
        for i in range(boneCount):
            parentId = bs.readUInt()
            if parentId != 0xFFFFFFFF:
                self.boneParent[self.boneName[i]] = boneId[parentId]

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
        try:
            self.readBlock(bs, string)
        except:
            pass

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

    def readBlock(self, bs, string):
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
                self.readOsg(bs, string)
            elif signature == "MOT":
                self.readMot(bs, string)
            elif signature == "CNS":
                self.readCns(bs, string)
            elif signature == "CLS":
                self.readCls(bs, string)
            bs.seek(pos, NOESEEK_ABS)

    def readExp(self, bs):
        parentName = getOffString(bs, readOff(bs, self.addressSpace))
        pos = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        rot = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        scl = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        name = getOffString(bs, readOff(bs, self.addressSpace))
        count = bs.readInt()
        exp = []
        for i in range(count):
            exp.append(getOffString(bs, readOff(bs, self.addressSpace)))
        if parentName in self.boneName:
            self.boneParent[name] = parentName
            self.expNode[name] = parentName
        elif parentName in self.expNode:
            pName = self.expNode[parentName]
            while True:
                if pName in self.boneName or pName in self.boneData.name:
                    break
                pName = self.expNode[pName]
            self.boneParent[name] = pName
            self.expNode[name] = parentName
        elif parentName in self.cnsNode:
            self.boneParent[name] = self.cnsNode[parentName]
            self.expNode[name] = self.cnsNode[parentName]
        else:
            self.boneParent[name] = parentName
            self.expNode[name] = parentName

    def readOsg(self, bs, string):
        parentName = getOffString(bs, readOff(bs, self.addressSpace))
        pos = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        rot = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        scl = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        if self.addressSpace == 64:
            bs.seek(0x04, NOESEEK_REL)
        index = bs.readUInt()
        count = bs.readInt()
        externalNameIdx = bs.readUInt() & 0x7FFF
        name = string[bs.readUInt() & 0x7FFF]
        if parentName in self.boneName:
            prevOsgName = parentName
        elif parentName in self.expNode:
            prevOsgName = self.expNode[parentName]
            while True:
                if prevOsgName in self.boneName or prevOsgName in self.boneData.name:
                    break
                prevOsgName = self.expNode[prevOsgName]
        elif parentName in self.cnsNode:
            prevOsgName = self.cnsNode[parentName]
        else:
            prevOsgName = parentName
        for i in range(count):
            osgName = string[externalNameIdx + i + 1]
            if i == 0:
                if prevOsgName in self.osgNode:
                    self.boneParent[osgName] = self.osgNode[prevOsgName]
                    prevOsgName = self.osgNode[prevOsgName]
                else:
                    self.boneParent[osgName] = prevOsgName
            else:
                self.boneParent[osgName] = prevOsgName
            if osgName in self.boneName:
                prevOsgName = osgName
            self.osgNode[osgName] = prevOsgName
        self.osgNode[name] = prevOsgName

    def readMot(self, bs, string):
        parentName = getOffString(bs, readOff(bs, self.addressSpace))
        pos = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        rot = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        scl = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        name = getOffString(bs, readOff(bs, self.addressSpace))
        count = bs.readInt()
        boneNameOff = readOff(bs, self.addressSpace)
        boneMtxOff = readOff(bs, self.addressSpace)
        bs.seek(boneNameOff, NOESEEK_ABS)
        prevMotName = parentName
        for i in range(count):
            motName = string[bs.readUInt() & 0x7FFF]
            if i == 0:
                if parentName in self.expNode:
                    self.boneParent[motName] = self.expNode[prevMotName]
                elif parentName in self.osgNode:
                    self.boneParent[motName] = self.osgNode[prevMotName]
                else:
                    self.boneParent[motName] = prevMotName
            else:
                if "000" in motName:
                    prevMotName = parentName
                self.boneParent[motName] = prevMotName
            prevMotName = motName

    def readCns(self, bs, string):
        parentName = getOffString(bs, readOff(bs, self.addressSpace))
        pos = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        rot = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        scl = [bs.readFloat(), bs.readFloat(), bs.readFloat()]
        cnsType = getOffString(bs, readOff(bs, self.addressSpace))
        name = getOffString(bs, readOff(bs, self.addressSpace))
        coupling = bs.readInt()
        sourceName = getOffString(bs, readOff(bs, self.addressSpace))
        if parentName in self.expNode:
            parentName = self.expNode[parentName]
            while True:
                if parentName in self.boneName or parentName in self.boneData.name:
                    break
                parentName = self.expNode[parentName]
        self.cnsNode[name] = parentName

    def readCls(self, bs, string):
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
            pos = NoeVec3([bs.readFloat(), bs.readFloat(), bs.readFloat()])
            bs.seek(0x1C, NOESEEK_REL)
            bone1 = self.readClsNodeInfo(bs)
            bone2 = self.readClsNodeInfo(bs)
            bone3 = self.readClsNodeInfo(bs)
            bone4 = self.readClsNodeInfo(bs)
            rootBoneName.append([bone1[0], bone2[0], bone3[0], bone4[0]])
            rootWeight.append([bone1[1], bone2[1], bone3[1], bone4[1]])
            name = meshName + "_" + str(i+1).zfill(2) + "_00"
            self.clsNode.append([name, pos, bone1[0]])
            nodeName.append(name)
            for a in range(4):
                if rootBoneName[i][a] and rootBoneName[i][a] not in usedBone:
                    usedBone.append(rootBoneName[i][a])
        bs.seek(nodeOff, NOESEEK_ABS)
        for i in range(columnCount-1):
            for a in range(rowCount):
                nodeType = bs.readUInt()
                pos = NoeVec3([bs.readFloat(), bs.readFloat(), bs.readFloat()])
                bs.seek(0x1C, NOESEEK_REL)
                name = meshName + "_" + str(a+1).zfill(2) + "_" + str(i+1).zfill(2)
                self.clsNode.append([name, pos, meshName + "_" + str(a+1).zfill(2) + "_" + str(i).zfill(2)])
                nodeName.append(name)
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
                for a in range(len(obj.boneList)):
                    br = obj.boneList[a]._matrix.inverse()
                    obj.boneList[a]._matrix[0] = br[0]
                    obj.boneList[a]._matrix[1] = br[1]
                    obj.boneList[a]._matrix[2] = br[2]
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
                for a in range(len(obj.boneList)):
                    br = obj.boneList[a]._matrix.inverse()
                    obj.boneList[a]._matrix[0] = br[0]
                    obj.boneList[a]._matrix[1] = br[1]
                    obj.boneList[a]._matrix[2] = br[2]
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
            tex.name = self.sprDb.db[self.fileName][i]
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
        self.isAC = False
        self.isMGF = False
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
        if self.isMGF:
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
        if len(boneNames) == 173:
            self.isAC = True
            usedBones = initMotionBonesAC()
        else:
            usedBones = initMotionBonesAFT()
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
            if boneName in usedBones:
                boneKey = self.buildAnim(frameCount, boneName, xKeyFrames, yKeyFrames, zKeyFrames)
                kfBones.append(boneKey)
        self.animList.append(NoeKeyFramedAnim(name, self.boneList, kfBones, 1.0))

    def readAnimMot(self, name, frameCount, animMap, boneNames, divData):
        kfBones = []
        cnt = 0
        usedBones = initMotionBonesAFT()
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
            if boneName in usedBones:
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
                    keys = self.loadRotKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, boneName, 2)
                    boneKey.setRotation(keys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
                else:
                    keys = self.loadKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, 2)
                    boneKey.setTranslation(keys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
            else:
                if boneName == "cl_kao":
                    keys = self.loadRotKeys(frameCount, xKeyFrames, zKeyFrames, yKeyFrames, boneName, 2)
                else:
                    keys = self.loadRotKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, boneName, 2)
                boneKey.setRotation(keys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
        elif boneName.endswith("_cp") or boneName == "gblctr":
            keys = self.loadKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, 2)
            boneKey.setTranslation(keys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
        else:
            keys = self.loadRotKeys(frameCount, xKeyFrames, yKeyFrames, zKeyFrames, boneName, 2)
            boneKey.setRotation(keys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
        return boneKey

    def buildAnimMotMgf(self, frameCount, boneName, xTranKeyFrames, yTranKeyFrames, zTranKeyFrames, xRotKeyFrames, yRotKeyFrames, zRotKeyFrames, xSclKeyFrames = None, ySclKeyFrames = None, zSclKeyFrames = None):
        boneKey = NoeKeyFramedBone(self.boneDict[boneName])
        keys = self.loadKeys(frameCount,  xTranKeyFrames, yTranKeyFrames, zTranKeyFrames, 0)
        boneKey.setTranslation(keys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
        keys = self.loadRotKeys(frameCount, xRotKeyFrames, yRotKeyFrames, zRotKeyFrames, boneName, 0)
        boneKey.setRotation(keys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
        if self.boneData.type[boneName] == 0x00:
            keys = self.loadKeys(frameCount, xSclKeyFrames, ySclKeyFrames, zSclKeyFrames, 0)
            boneKey.setScale(keys, noesis.NOEKF_SCALE_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
        return boneKey

    def loadKeys(self, frameCount, xKeyFrames, yKeyFrames, zKeyFrames, interpType):
        keys = []
        if xKeyFrames.keyType <= 0x01 and yKeyFrames.keyType <= 0x01 and zKeyFrames.keyType <= 0x01:
            keys.append(NoeKeyFramedValue(0, [xKeyFrames.keys[0], yKeyFrames.keys[0], zKeyFrames.keys[0]]))
        else:
            xKey = interpolate(frameCount, xKeyFrames, interpType)
            yKey = interpolate(frameCount, yKeyFrames, interpType)
            zKey = interpolate(frameCount, zKeyFrames, interpType)
            keys = cleanupKeys(frameCount, xKey, yKey, zKey)
        return keys

    def loadRotKeys(self, frameCount, xKeyFrames, yKeyFrames, zKeyFrames, boneName, interpType):
        keys = []
        if self.isAC:
            if boneName == "nl_oya_l_wj" or boneName == "nl_oya_b_l_wj" or boneName == "nl_oya_c_l_wj" or boneName == "nl_oya_r_wj" or boneName == "nl_oya_b_r_wj" or boneName == "nl_oya_c_r_wj":
                fix = NoeMat43().toAngles()
            else:
                fix = (self.boneList[self.boneDict[boneName]]._matrix * self.boneList[self.boneList[self.boneDict[boneName]].parentIndex]._matrix.inverse()).toAngles()
        elif self.isMGF:
            fix = NoeMat43().toAngles()
        else:
            fix = (self.boneList[self.boneDict[boneName]]._matrix * self.boneList[self.boneList[self.boneDict[boneName]].parentIndex]._matrix.inverse()).toAngles()
        if xKeyFrames.keyType <= 0x01 and yKeyFrames.keyType <= 0x01 and zKeyFrames.keyType <= 0x01:
            keys.append(NoeKeyFramedValue(0, (NoeAngles([xKeyFrames.keys[0]*noesis.g_flRadToDeg, yKeyFrames.keys[0]*noesis.g_flRadToDeg, zKeyFrames.keys[0]*noesis.g_flRadToDeg]).toMat43_XYZ() * fix.toMat43()).toQuat()))
        else:
            xKey = interpolate(frameCount, xKeyFrames, interpType)
            yKey = interpolate(frameCount, yKeyFrames, interpType)
            zKey = interpolate(frameCount, zKeyFrames, interpType)
            keys = cleanupRotKeys(frameCount, xKey, yKey, zKey, fix)
        return keys

class Motc:

    def __init__(self):
        self.animList = []
        self.names = []
        self.frameCounts = []

    def readMotc(self, data, boneData, boneList, boneDict, fileName, fileDir, isMGF):
        bs = NoeBitStream(data)
        magic = bs.readBytes(4).decode("ASCII")
        fileSize = bs.readUInt()
        dataOff = bs.readUInt()
        endian = bs.readUInt()
        unk = bs.readUInt()
        dataSize = bs.readUInt()
        addressSpace = getAddressSpace(bs, fileSize, dataOff, dataSize)
        motion = Motion(None, boneData, boneList, boneDict)
        motion.isMGF = isMGF
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
        self.frameList = []

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
        animId = robtbl.db[self.performers[performer]][self.mouth[idx]]
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
        animId = robtbl.db[self.performers[performer]][self.hand[idx]]
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
        animId = robtbl.db[self.performers[performer]][self.look[idx]]
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
        animId = robtbl.db[self.performers[performer]][self.exp[idx]]
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
                animId = robtbl.db[self.performers[performer]][self.exp[expKey.idx]]
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

# class Vmd:

#     def __init__(self, name, animList, morphList):
#         self.name = name
#         self.animList = animList
#         self.morphList = morphList

#     def wrtieVmd(self, outDir):
#         writeName = outDir + self.name + ".vmd"
#         f = open(writeName, 'wb')
#         f.write("Vocaloid Motion Data 0002".encode('shift_jis').ljust(30, b'\0'))#magic
#         f.write(self.name.encode('shift_jis').ljust(20, b'\0')[:20])#model name
#         self.writeAnim(f)
#         self.writeMorph(f)
#         f.write(struct.pack('4i',0,0,0,0))
#         f.close()
#         print("Successfully wrote " + self.name + ".vmd")

#     def writeAnim(self, f):
#         f.write(struct.pack('i', len(self.animList)))

#     def writeMorph(self, f):
#         morphDict = self.readMorphDict()
#         f.write(struct.pack('i', len(self.morphList)))
#         for morph in self.morphList:
#             if morph.name in morphDict:
#                 f.write(morphDict[morph.name].encode('shift_jis').ljust(15, b'\0')[:15])
#             else:
#                 f.write(morph.name.encode('shift_jis').ljust(15, b'\0')[:15])
#             f.write(struct.pack('i', morph.frame))
#             f.write(struct.pack('f', morph.blend))

#     def readMorphDict(self):
#         d = {}
#         with io.open(os.getcwd() + "/dicts/diva.morph", mode="r", encoding="utf-8") as f:
#             for line in f:
#                 if not line.startswith("#"):
#                     (key, val) = line.split()
#                     d[key] = val
#         return d

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
    if interpType == 0:
        for i in range(frameCount):
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1 and keyFrames.frameList[idx + 1] == i:
                keyFrames.frameList.pop(idx)
                keyFrames.keys.pop(idx)
                keyFrames.tangents.pop(idx)
            keys.append(interpolateMgf(i, keyFrames, idx))
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1:
                idx += 1
    elif interpType == 2:
        for i in range(frameCount):
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1 and keyFrames.frameList[idx + 1] == i:
                keyFrames.frameList.pop(idx)
                keyFrames.keys.pop(idx)
                keyFrames.tangents.pop(idx)
            keys.append(interpolateMot(i, keyFrames, idx))
            if keyFrames.frameList[idx] == i and idx != len(keyFrames.frameList) - 1:
                idx += 1
    return keys

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

def interpolateMgf(frame, keyFrames, idx):
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
            keys.append(NoeKeyFramedValue(i, [xKey[i], yKey[i], zKey[i]]))
    keys.append(NoeKeyFramedValue(frameCount - 1, [xKey[frameCount - 1], yKey[frameCount - 1], zKey[frameCount - 1]]))
    return keys

def cleanupRotKeys(frameCount, xKey, yKey, zKey, fix):
    keys = []
    keys.append(NoeKeyFramedValue(0, (NoeAngles([xKey[0]*noesis.g_flRadToDeg, yKey[0]*noesis.g_flRadToDeg, zKey[0]*noesis.g_flRadToDeg]).toMat43_XYZ() * fix.toMat43()).toQuat()))
    for i in range(1, frameCount - 1):
        if [xKey[i], yKey[i], zKey[i]] == [xKey[i-1], yKey[i-1], zKey[i-1]] and [xKey[i], yKey[i], zKey[i]] == [xKey[i+1], yKey[i+1], zKey[i+1]]:
            continue
        else:
            keys.append(NoeKeyFramedValue(i, (NoeAngles([xKey[i]*noesis.g_flRadToDeg, yKey[i]*noesis.g_flRadToDeg, zKey[i]*noesis.g_flRadToDeg]).toMat43_XYZ() * fix.toMat43()).toQuat()))
    keys.append(NoeKeyFramedValue(frameCount - 1, (NoeAngles([xKey[-1]*noesis.g_flRadToDeg, yKey[-1]*noesis.g_flRadToDeg, zKey[-1]*noesis.g_flRadToDeg]).toMat43_XYZ() * fix.toMat43()).toQuat()))
    return keys

def initMotionBonesAFT():
    usedBones = ["n_hara_cp", "kg_hara_y", "kl_hara_xz", "kl_hara_etc", "e_mune_cp", "cl_mune", "kl_mune_b_wj", "kl_kubi", "e_kao_cp", "cl_kao", "kl_ago_wj", "tl_tooth_under_wj",
                "kl_eye_l", "kl_highlight_l_wj", "kl_eye_r", "kl_highlight_r_wj", "tl_eyelid_l_a_wj", "tl_eyelid_l_b_wj", "tl_eyelid_r_a_wj", "tl_eyelid_r_b_wj", "tl_kuti_d_wj",
                "tl_kuti_d_l_wj", "tl_kuti_d_r_wj", "tl_kuti_ds_l_wj", "tl_kuti_ds_r_wj", "tl_kuti_l_wj", "tl_kuti_m_l_wj", "tl_kuti_m_r_wj", "tl_kuti_r_wj", "tl_kuti_u_wj",
                "tl_kuti_u_l_wj", "tl_kuti_u_r_wj", "tl_mabu_l_d_a_wj", "tl_mabu_l_d_b_wj", "tl_mabu_l_d_c_wj", "tl_mabu_l_u_a_wj", "tl_mabu_l_u_b_wj", "tl_eyelashes_l_wj",
                "tl_mabu_l_u_c_wj", "tl_mabu_r_d_a_wj", "tl_mabu_r_d_b_wj", "tl_mabu_r_d_c_wj", "tl_mabu_r_u_a_wj", "tl_mabu_r_u_b_wj", "tl_eyelashes_r_wj", "tl_mabu_r_u_c_wj",
                "tl_mayu_l_wj", "tl_mayu_l_b_wj", "tl_mayu_l_c_wj", "tl_mayu_r_wj", "tl_mayu_r_b_wj", "tl_mayu_r_c_wj", "tl_tooth_upper_wj", "kl_waki_l_wj", "e_ude_l_cp",
                "kl_te_l_wj", "nl_hito_l_wj", "nl_hito_b_l_wj", "nl_hito_c_l_wj", "nl_ko_l_wj", "nl_ko_b_l_wj", "nl_ko_c_l_wj", "nl_kusu_l_wj", "nl_kusu_b_l_wj", "nl_kusu_c_l_wj",
                "nl_naka_l_wj", "nl_naka_b_l_wj", "nl_naka_c_l_wj", "nl_oya_l_wj", "nl_oya_b_l_wj", "nl_oya_c_l_wj", "kl_waki_r_wj", "e_ude_r_cp", "kl_te_r_wj", "nl_hito_r_wj",
                "nl_hito_b_r_wj", "nl_hito_c_r_wj", "nl_ko_r_wj", "nl_ko_b_r_wj", "nl_ko_c_r_wj", "nl_kusu_r_wj", "nl_kusu_b_r_wj", "nl_kusu_c_r_wj", "nl_naka_r_wj", "nl_naka_b_r_wj",
                "nl_naka_c_r_wj", "nl_oya_r_wj", "nl_oya_b_r_wj", "nl_oya_c_r_wj", "tl_up_kata_l", "tl_up_kata_r", "kl_kosi_y", "kl_kosi_xz", "kl_kosi_etc_wj", "e_sune_l_cp", "cl_momo_l",
                "kl_asi_l_wj_co", "kl_toe_l_wj", "e_sune_r_cp", "cl_momo_r", "kl_asi_r_wj_co", "kl_toe_r_wj", "gblctr", "kg_ya_ex"]
    return usedBones

def initMotionBonesAC():
    usedBones = ["n_hara_cp", "kg_hara_y", "kl_hara_xz", "kl_hara_etc", "e_mune_cp", "cl_mune", "kl_mune_b_wj", "kl_kubi", "e_kao_cp", "cl_kao", "kl_ago_wj", "tl_tooth_under_wj",
                "kl_eye_l_wj", "kl_eye_r_wj", "tl_eyelid_l_a_wj", "tl_eyelid_l_b_wj", "tl_eyelid_r_a_wj", "tl_eyelid_r_b_wj", "tl_kuti_d_wj",
                "tl_kuti_d_l_wj", "tl_kuti_d_r_wj", "tl_kuti_ds_l_wj", "tl_kuti_ds_r_wj", "tl_kuti_l_wj", "tl_kuti_m_l_wj", "tl_kuti_m_r_wj", "tl_kuti_r_wj", "tl_kuti_u_wj",
                "tl_kuti_u_l_wj", "tl_kuti_u_r_wj", "tl_mabu_l_d_wj", "tl_mabu_l_d_l_wj", "tl_mabu_l_d_r_wj", "tl_mabu_l_u_wj", "tl_mabu_l_u_l_wj", "tl_eyelashes_l_wj",
                "tl_mabu_l_u_r_wj", "tl_mabu_r_d_wj", "tl_mabu_r_d_l_wj", "tl_mabu_r_d_r_wj", "tl_mabu_r_u_wj", "tl_mabu_r_u_l_wj", "tl_eyelashes_r_wj", "tl_mabu_r_u_r_wj",
                "tl_mayu_l_wj", "tl_mayu_b_l_wj", "tl_mayu_c_l_wj", "tl_mayu_r_wj", "tl_mayu_b_r_wj", "tl_mayu_c_r_wj", "tl_tooth_upper_wj", "kl_waki_l_wj", "e_ude_l_cp",
                "kl_te_l_wj", "nl_hito_l_wj", "nl_hito_b_l_wj", "nl_hito_c_l_wj", "nl_ko_l_wj", "nl_ko_b_l_wj", "nl_ko_c_l_wj", "nl_kusu_l_wj", "nl_kusu_b_l_wj", "nl_kusu_c_l_wj",
                "nl_naka_l_wj", "nl_naka_b_l_wj", "nl_naka_c_l_wj", "nl_oya_l_wj", "nl_oya_b_l_wj", "nl_oya_c_l_wj", "kl_waki_r_wj", "e_ude_r_cp", "kl_te_r_wj", "nl_hito_r_wj",
                "nl_hito_b_r_wj", "nl_hito_c_r_wj", "nl_ko_r_wj", "nl_ko_b_r_wj", "nl_ko_c_r_wj", "nl_kusu_r_wj", "nl_kusu_b_r_wj", "nl_kusu_c_r_wj", "nl_naka_r_wj", "nl_naka_b_r_wj",
                "nl_naka_c_r_wj", "nl_oya_r_wj", "nl_oya_b_r_wj", "nl_oya_c_r_wj", "tl_up_kata_l", "tl_up_kata_r", "kl_kosi_y", "kl_kosi_xz", "kl_kosi_etc_wj", "e_sune_l_cp", "cl_momo_l",
                "kl_asi_l_wj_co", "kl_toe_l_wj", "e_sune_r_cp", "cl_momo_r", "kl_asi_r_wj_co", "kl_toe_r_wj", "gblctr", "kg_ya_ex"]
    return usedBones

def initF2XHashDict():
    hashDict = {0xCC71E092:"CMN_EYES_CENTER_D", 0xEB62BACB:"CMN_EYES_CENTER_U", 0x3DA92482:"CMN_EYES_DOWN", 0x20B63BDB:"CMN_EYES_DOWN_LEFT", 0x1BF515A6:"CMN_EYES_DOWN_LEFT_M",
    0xAD70A0B9:"CMN_EYES_DOWN_M", 0xAB1940E9:"CMN_EYES_DOWN_RIGHT", 0x1F73D792:"CMN_EYES_DOWN_RIGHT_M", 0x4131C6CE:"CMN_EYES_LEFT", 0x0063C185:"CMN_EYES_LEFT_M", 0xAC58836D:"CMN_EYES_MOVE_L_R",
    0x04342A94:"CMN_EYES_MOVE_U_D", 0x68894937:"CMN_EYES_MOVE_UL_DR", 0xE83BC978:"CMN_EYES_MOVE_UR_DL", 0xDEA33C57:"CMN_EYES_RESET", 0x23C0B0F0:"CMN_EYES_RIGHT", 0x5EC07882:"CMN_EYES_RIGHT_M",
    0xB2FC99A0:"CMN_EYES_UP", 0x2C50E37F:"CMN_EYES_UP_LEFT", 0x2BF0AFE2:"CMN_EYES_UP_LEFT_M", 0x99FCBB7C:"CMN_EYES_UP_M", 0xA94A7B5E:"CMN_EYES_UP_RIGHT", 0xE9024D9F:"CMN_EYES_UP_RIGHT_M",
    0x5248F064:"CMN_HAND_BOTTLE", 0x8941AEAC:"CMN_HAND_CHOP", 0x4EDB7807:"CMN_HAND_CLOSE", 0x63AA275F:"CMN_HAND_FAN", 0xBEEEA116:"CMN_HAND_FLASHLIGHT", 0x51946790:"CMN_HAND_FOX",
    0x9A14C085:"CMN_HAND_FULLOPEN", 0x135DAC82:"CMN_HAND_GOOD", 0xC6C3F044:"CMN_HAND_GUN", 0xEB7A8562:"CMN_HAND_HEART", 0x7B5BB67A:"CMN_HAND_HOLD", 0xED31BAC8:"CMN_HAND_MIC",
    0xF60C8D75:"CMN_HAND_NEGI", 0xF79E5B56:"CMN_HAND_NORMAL", 0x74C8C7E5:"CMN_HAND_OK", 0x05595758:"CMN_HAND_ONE", 0xE75D0A15:"CMN_HAND_OPEN", 0x24A93124:"CMN_HAND_PEACE",
    0xCC8E9920:"CMN_HAND_PEACECLOSE", 0xB838F585:"CMN_HAND_PHONE", 0x47171BDD:"CMN_HAND_PICK", 0xB5918A0C:"CMN_HAND_PICK2", 0xC8CA0A99:"CMN_HAND_PLATE", 0x14FE02BF:"CMN_HAND_PUNCH",
    0xD122599A:"CMN_HAND_RESET", 0x151E3BBA:"CMN_HAND_SIZEN", 0x84E43E6B:"CMN_HAND_THREE", 0xA48BA7F5:"MIK_FACE_ADMIRATION", 0x1925F549:"MIK_FACE_ADMIRATION_CL", 0xDC1AF4F8:"MIK_FACE_CLARIFYING",
    0xB0800D79:"MIK_FACE_CLARIFYING_CL", 0x3453BE04:"MIK_FACE_CLOSE", 0xAC364D56:"MIK_FACE_COOL", 0xC78E8DA1:"MIK_FACE_COOL_CL", 0x1E5A8164:"MIK_FACE_DAZZLING", 0x5601694D:"MIK_FACE_DAZZLING_CL",
    0x4486321E:"MIK_FACE_EYEBROW_UP_LEFT", 0x2A884ED5:"MIK_FACE_EYEBROW_UP_LEFT_CL", 0x96C7FD2A:"MIK_FACE_EYEBROW_UP_RIGHT", 0xD5EAC491:"MIK_FACE_EYEBROW_UP_RIGHT_CL",
    0xB5C228D2:"MIK_FACE_GENKI", 0x7116FF76:"MIK_FACE_GENKI_CL", 0x8D88857E:"MIK_FACE_GENTLE", 0x35A03B75:"MIK_FACE_GENTLE_CL", 0x9CA098A0:"MIK_FACE_KIRI", 0xD0423BB1:"MIK_FACE_KIRI_CL",
    0xD1EE03AD:"MIK_FACE_KOMARIEGAO", 0xCE74137C:"MIK_FACE_KOMARIWARAI", 0x81B7238D:"MIK_FACE_KOMARIWARAI_CL", 0x4BD9C988:"MIK_FACE_KONWAKU", 0xC1710C97:"MIK_FACE_KONWAKU_CL",
    0x0BA4A548:"MIK_FACE_KUMON", 0x7891EAB3:"MIK_FACE_KUMON_CL", 0x351E8FB3:"MIK_FACE_KUTSUU", 0xCD915DF7:"MIK_FACE_KUTSUU_CL", 0x67921A1C:"MIK_FACE_LASCIVIOUS",
    0xF4D467F3:"MIK_FACE_LASCIVIOUS_CL", 0x0B423D16:"MIK_FACE_LAUGH", 0x7FA01BDB:"MIK_FACE_NAGASI", 0x6BBC2A4E:"MIK_FACE_NAGASI_CL", 0x9619BB34:"MIK_FACE_NAKI", 0x0655CE85:"MIK_FACE_NAKI_CL",
    0xA69F3640:"MIK_FACE_NAYAMI", 0xBD0BC34D:"MIK_FACE_NAYAMI_CL", 0xAADAC5FD:"MIK_FACE_OMOU", 0x30D08CEE:"MIK_FACE_OMOU_CL", 0x1C071A15:"MIK_FACE_RESET", 0xD7C1DA42:"MIK_FACE_SAD",
    0x70C43C9D:"MIK_FACE_SAD_CL", 0xE11659A5:"MIK_FACE_SETTLED", 0xAE1054D5:"MIK_FACE_SETTLED_CL", 0x9E697E02:"MIK_FACE_SETUNA", 0x2BFFC1CB:"MIK_FACE_SETUNA_CL", 0x0EE65D7B:"MIK_FACE_SMILE",
    0xC65DCBCB:"MIK_FACE_SMILE_CL", 0x68C2A780:"MIK_FACE_STRONG", 0x038594DF:"MIK_FACE_STRONG_CL", 0xA1D6ECD7:"MIK_FACE_SUPSERIOUS", 0x3667062A:"MIK_FACE_SUPSERIOUS_CL",
    0x6DFA429B:"MIK_FACE_SURPRISE", 0x6EF0F796:"MIK_FACE_SURPRISE_CL", 0x0E318E47:"MIK_FACE_TSUYOKIWARAI", 0x942B7539:"MIK_FACE_TSUYOKIWARAI_CL", 0x369176D6:"MIK_FACE_UTURO",
    0xE704376B:"MIK_FACE_UTURO_CL", 0xD86E2250:"MIK_FACE_WINK_L", 0x37C0C575:"MIK_FACE_WINK_R", 0x91E4A429:"MIK_FACE_WINKG_L", 0xAFC80288:"MIK_FACE_WINKG_R", 0x60943A41:"MIK_FACE_YARU",
    0x1BC8C7F8:"MIK_FACE_YARU_CL", 0x8D679789:"MIK_KUCHI_A", 0x27256E52:"MIK_KUCHI_CHU", 0x9834C866:"MIK_KUCHI_E", 0x33838A11:"MIK_KUCHI_E_DOWN", 0xC288A2B6:"MIK_KUCHI_HAMISE",
    0x2EE45D78:"MIK_KUCHI_HAMISE_DOWN", 0xD42ACE8B:"MIK_KUCHI_HAMISE_E", 0xBD509253:"MIK_KUCHI_HE", 0x8C96BE4C:"MIK_KUCHI_HE_S", 0xD1CC9C6B:"MIK_KUCHI_HERAHERA", 0x5FED5E14:"MIK_KUCHI_I",
    0xAAD5F001:"MIK_KUCHI_MOGUMOGU", 0xEDEAD6C9:"MIK_KUCHI_NEKO", 0x8AAAB09E:"MIK_KUCHI_NEUTRAL", 0xB9808D8F:"MIK_KUCHI_NIYA", 0x2B9AA94D:"MIK_KUCHI_O", 0xE472692C:"MIK_KUCHI_PSP_A",
    0x4A88205A:"MIK_KUCHI_PSP_E", 0xAA2BD9D4:"MIK_KUCHI_PSP_NIYA", 0x1444FEAA:"MIK_KUCHI_PSP_NIYARI", 0x64030BB3:"MIK_KUCHI_PSP_O", 0x72354540:"MIK_KUCHI_PSP_SURPRISE",
    0x61198CF4:"MIK_KUCHI_RESET", 0x9218C1AC:"MIK_KUCHI_SAKEBI", 0x57037C4B:"MIK_KUCHI_SAKEBI_L", 0x932BBDAC:"MIK_KUCHI_SANKAKU", 0x23EC5921:"MIK_KUCHI_SHIKAKU", 0x349493AB:"MIK_KUCHI_SMILE",
    0x48A15672:"MIK_KUCHI_SMILE_L", 0x47BB071D:"MIK_KUCHI_SURPRISE", 0x6BF6E5B4:"MIK_KUCHI_U"}
    return hashDict