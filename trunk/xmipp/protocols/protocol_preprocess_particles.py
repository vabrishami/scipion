#!/usr/bin/env python
#------------------------------------------------------------------------------------------------
#
# General script for Xmipp-based pre-processing of single-particles: 
#  - phase flipping
#  - extraction of particles
#  - normalization
#  - sort_junk
#
# It is assumed that you have already ran the preprocess_micrographs protocol,
#  and that you have picked the particles for each micrograph
#
# Example use:
# ./xmipp_preprocess_particles.py
#
# Author: Sjors Scheres, March 2007
#         Carlos Oscar, December 2010
#
from protlib_base import *

class ProtPreprocessParticles(XmippProtocol):
    def __init__(self, scriptname, project):
        XmippProtocol.__init__(self, protDict.preprocess_particles.key, scriptname, project)
        self.Import = 'from protocol_particle_pick import *'

    #FIXME: I guess this is not longer needed with DB structure
    def saveAndCompareParameters(self, listOfParameters):
        import os,shutil
        fnOut=self.WorkingDir + "/protocolParameters.txt"
        linesNew=[];
        for prm in listOfParameters:
            eval("linesNew.append('"+prm +"='+str("+prm+")+'\\n')")
        retval=False
        if os.path.exists(fnOut):
            f = open(fnOut, 'r')
            linesOld=f.readlines()
            f.close()
            same=True;
            if len(linesOld)==len(linesNew):
                for i in range(len(linesNew)):
                    if not linesNew[i]==linesOld[i]:
                        same=False
                        break;
            else:
                same=False
            if not same:
                print("Deleting")
                self.log.info("Deleting working directory since it is run with different parameters")
                shutil.rmtree(self.WorkingDir)
                os.makedirs(self.WorkingDir)
                retval=True
        f = open(fnOut, 'w')
        f.writelines(linesNew)
        f.close()
        return retval

#    #init variables
#    def __init__(self,
#                 WorkingDir,
#                 PickingDir,
#                 ProjectDir,
#                 Size,
#                 DoFlip,
#                 DoLog, 
#                 DoInvert,
#                 BackGroundRadius,
#                 DoRemoveDust,
#                 DustRemovalThreshold,
#                 DoParallel,
#                 NumberOfMpi,
#                 SystemFlavour
#                 ):
#	     
#        import os,sys,time
#        scriptdir=os.path.split(os.path.dirname(os.popen('which xmipp_protocols','r').read()))[0]+'/protocols'
#        sys.path.append(scriptdir) # add default search path
#        import log,xmipp,launch_job
#        
#        self.WorkingDir=WorkingDir.strip()
#        self.PickingDir=PickingDir.strip()
#        self.ProjectDir=ProjectDir.strip()
#        self.LogDir="Logs"
#        self.PosFile="Common"
#        self.Size=Size
#        self.DoFlip=DoFlip
#        self.DoLog=DoLog 
#        self.DoInvert=DoInvert
#        if BackGroundRadius!=0:
#            self.BackGroundRadius=BackGroundRadius
#        else:
#            self.BackGroundRadius=Size/2
#        self.DoRemoveDust=DoRemoveDust
#        self.DustRemovalThreshold=DustRemovalThreshold
#        self.OutSelFile=OutSelFile
#        self.DoParallel=DoParallel
#        self.NumberOfMpi=NumberOfMpi
#        self.SystemFlavour=SystemFlavour
#
#        # Setup logging
#        self.log=log.init_log_system(self.ProjectDir,
#                                     self.LogDir,
#                                     sys.argv[0],
#                                     self.WorkingDir)
#                
#        # Make working directory if it does not exist yet
#        if not os.path.exists(self.WorkingDir):
#            os.makedirs(self.WorkingDir)
#
#        # Save parameters and compare to possible previous runs
#        deleted=self.saveAndCompareParameters([
#                 "PickingDir",
#                 "Size",
#                 "DoFlip",
#                 "DoInvert",
#                 "DoLog",
#                 "BackGroundRadius",
#                 "DoRemoveDust",
#                 "DustRemovalThreshold"]);
#
#        # Update status
#        fh=open(self.WorkingDir + "/status.txt", "a")
#        fh.write("Step 0: Processed started at " + time.asctime() + "\n")
#        fh.close()
#
#        # Backup script
#        log.make_backup_of_script_file(sys.argv[0],
#                                       os.path.abspath(self.WorkingDir))
#    
#        # Preprocess paticles
#        fnScript=self.WorkingDir+'/pickParticles.sh'
#        self.fh_mpi=os.open(fnScript, os.O_WRONLY | os.O_TRUNC | os.O_CREAT, 0700)
#        self.process_all_micrographs()
#        os.close(self.fh_mpi)
#        self.launchCommandFile(fnScript)
#
#        # Join results
#        generalMD=xmipp.MetaData()
#        i=0
#        for selfile in self.outputSel:
#            if not os.path.exists(selfile):
#                fh=open(self.WorkingDir + "/status.txt", "a")
#                fh.write("Step E: Cannot read "+selfile+". Finishing at " + time.asctime() + "\n")
#                fh.close()
#                sys.exit(1)
#            MD=xmipp.MetaData(selfile)
#            if self.isPairTilt:
#                MDtilt=xmipp.MetaData(self.outputTiltedSel[i])
#                for id in MD:
#                    MD.setValue(xmipp.MDL_IMAGE_TILTED,MDtilt.getValue(xmipp.MDL_IMAGE))
#                    MD.setValue(xmipp.MDL_MICROGRAPH_TILTED,MDtilt.getValue(xmipp.MDL_MICROGRAPH))
#                    xtilt=MDtilt.getValue(xmipp.MDL_XINT)
#                    MD.setValue(xmipp.MDL_XINTTILT,xtilt)
#                    MD.setValue(xmipp.MDL_YINTTILT,MDtilt.getValue(xmipp.MDL_YINT))
#                    enabledTilted=MDtilt.getValue(xmipp.MDL_ENABLED)
#                    enabled=MD.getValue(xmipp.MDL_ENABLED)
#                    if enabled==-1 or enabledTilted==-1:
#                        MD.setValue(xmipp.MDL_ENABLED,-1)
#                    else:
#                        MD.setValue(xmipp.MDL_ENABLED,1)
#                    MDtilt.nextObject()
#                i=i+1
#            else:
#                for id in MD:
#                    imageFrom=MD.getValue(xmipp.MDL_MICROGRAPH)
#                    MD.setValue(xmipp.MDL_MICROGRAPH,self.correspondingMicrograph[imageFrom])
#                    if (self.correspondingCTF[imageFrom]!=""):
#                        MD.setValue(xmipp.MDL_CTFMODEL,self.correspondingCTF[imageFrom])
#            generalMD.unionAll(MD)
#        generalMD.write(self.OutSelFile)
#
#        # Sort by statistics
#        rootName,dummy=os.path.splitext(self.OutSelFile)
#        launchJob("xmipp_sort_by_statistics",
#                              "-i "+self.OutSelFile+" --multivariate "+\
#                              "-o "+rootName+"_sorted_by_score",
#                              self.log,
#                              False,1,1,'')
#
#        # Remove intermediate selfiles
#        for selfile in self.outputSel:
#            if os.path.exists(selfile):
#                os.remove(selfile)
#        for selfile in self.outputTiltedSel:
#            if os.path.exists(selfile):
#                os.remove(selfile)
#    
#        # Update status    
#        if os.path.exists(rootName+"_sorted_by_score.sel"):
#            fh=open(self.WorkingDir + "/status.txt", "a")
#            fh.write("Step F: Processed finished at " + time.asctime() + "\n")
#            fh.close()

    def launchCommandFile(self, commandFile):
        import launch_job, log, os
        log.cat(self.log, commandFile)
        if self.DoParallel:
            command=' -i ' + commandFile
            launchJob("xmipp_run", command, self.log, True,
                  self.NumberOfMpi, 1, self.SystemFlavour)
        else:
            self.log.info(commandFile)     
            os.system(commandFile)     

    def process_all_micrographs(self):
        import os, xmipp
        print '*********************************************************************'
        print '*  Pre-processing particles in '+os.path.basename(self.PickingDir)

        self.outputSel=[]
        self.outputTiltedSel=[]
        self.correspondingMicrograph={}
        self.correspondingCTF={}

        fnPickingParameters=self.PickingDir+"/protocolParameters.txt"
        self.isPairTilt=getParameter("IsPairList",fnPickingParameters)=="True"
        MicrographSelfile=getParameter("MicrographSelfile",fnPickingParameters)
        mD=xmipp.MetaData();
        xmipp.readMetaDataWithTwoPossibleImages(MicrographSelfile, mD)
        preprocessingDir,dummy=os.path.split(MicrographSelfile)
        for id in mD:
            micrograph=mD.getValue(xmipp.MDL_IMAGE)
            dummy,micrographWithoutDirs=os.path.split(micrograph)
            if self.isPairTilt:
                micrographTilted=mD.getValue(xmipp.MDL_ASSOCIATED_IMAGE1)
                dummy,tiltedMicrographWithoutDirs=os.path.split(micrographTilted)
            
            # Phase flip
            fnStack=self.WorkingDir+"/"+micrographWithoutDirs+".stk"
            command=''
            filesToDelete=[]
            fnToPick=preprocessingDir+"/"+micrograph
            if self.DoFlip and not self.isPairTilt:
                micrographName,micrographExt=os.path.splitext(micrographWithoutDirs)
                ctf=mD.getValue(xmipp.MDL_CTFMODEL)
                fnToPick=self.WorkingDir+"/"+micrographName+"_flipped.raw"
                command+="xmipp_micrograph_phase_flipping"+\
                         " -i "+preprocessingDir+"/"+micrograph+\
                         " -ctf "+preprocessingDir+"/"+ctf+\
                         " -o "+fnToPick + " ; "
                filesToDelete.append(fnToPick+"*")
            self.correspondingMicrograph[fnToPick]=preprocessingDir+"/"+micrograph
            if mD.containsLabel(xmipp.MDL_CTFMODEL):
                ctf=mD.getValue(xmipp.MDL_CTFMODEL)
                self.correspondingCTF[fnToPick]=preprocessingDir+"/"+ctf
            else:
                self.correspondingCTF[fnToPick]=""
            
            # Extract particles
            arguments=""
            if self.isPairTilt:
                fnStack=self.WorkingDir+"/"+micrographWithoutDirs+".stk"
                fnTiltedStack=self.WorkingDir+"/"+tiltedMicrographWithoutDirs+".stk"
                arguments+="-i "+fnToPick+\
                           " --tilted "+preprocessingDir+"/"+micrographTilted+\
                           " -o "+fnStack+" --tiltfn "+fnTiltedStack+\
                           " --tiltAngles "+self.PickingDir+"/"+micrographWithoutDirs+".angles.txt"\
                           " --pos "+self.PickingDir+"/"+micrographWithoutDirs+"."+self.PosFile+".pos"+\
                           " --tiltPos "+self.PickingDir+"/"+micrographWithoutDirs+".tilted."+self.PosFile+".pos"
                self.outputSel.append(fnStack+".sel")
                self.outputTiltedSel.append(fnTiltedStack+".sel")
            else:
                posfile=""
                candidatePosFile=self.PickingDir+"/"+micrographWithoutDirs+"."+self.PosFile+".pos"
                if os.path.exists(candidatePosFile):
                    posfile=candidatePosFile
                candidatePosFile=self.PickingDir+"/"+micrographWithoutDirs+"."+self.PosFile+".auto.pos"
                if os.path.exists(candidatePosFile):
                    if posfile=="":
                        posfile=candidatePosFile
                    else:
                        MD1=xmipp.MetaData(posfile)
                        MD2=xmipp.MetaData(candidatePosFile)
                        MD1.unionAll(MD2)
                        candidatePosFile=self.PickingDir+"/"+micrographWithoutDirs+"."+self.PosFile+".both.pos"
                        MD1.write(candidatePosFile)
                        filesToDelete.append(candidatePosFile)
                        posfile=candidatePosFile
                if posfile!="":
                    fnStack=self.WorkingDir+"/"+micrographWithoutDirs+".stk"
                    self.outputSel.append(fnStack+".sel")
                    arguments="-i "+fnToPick+" --pos "+posfile+" -o "+fnStack
            if arguments=="":
                print "Cannot find positions for "+micrograph
                continue
            
            arguments+=" --Xdim "+str(self.Size)+" --rmStack"
            if self.DoInvert:
                arguments+=" --invert"
            if self.DoLog:
                arguments+=" --log"
            command+="xmipp_micrograph_scissor "+arguments+" ; "
            
            # Normalize particles
            normalizeArguments=\
                     ' -background circle '+str(self.BackGroundRadius)+\
                     ' -method Ramp'                
            if (self.DoRemoveDust):
                normalizeArguments+=' -thr_black_dust -' + str(self.DustRemovalThreshold)+\
                         ' -thr_white_dust ' + str(self.DustRemovalThreshold)
            command+='xmipp_normalize -i ' +fnStack+normalizeArguments
            if self.isPairTilt:
                command+=' ; xmipp_normalize -i ' +fnTiltedStack+normalizeArguments

            # Remove temporary files
            for fileToDelete in filesToDelete:
                command+=" ; rm -f "+fileToDelete

            # Command done
            command += " ; if [ -e " + fnStack + ' ]; then ' + \
                        'echo "Step: '+micrograph+' processed " `date` >> ' + self.WorkingDir + "/status.txt; " + \
                       "fi"
            os.write(self.fh_mpi, command+"\n")
        
# Preconditions
    def validate():
        import os
        errors = []
        # Check if there is workingdir
        if WorkingDir == "":
            errors.append("No working directory given")
        # Check that there is a valid list of micrographs
        if not os.path.exists(PickingDir)>0:
            errors.append("Cannot find "+PickingDir)
        # Check that all micrographs exist
        import xmipp
        fnPickingParameters=PickingDir+"/protocolParameters.txt"
        isPairTilt=getParameter("IsPairList",fnPickingParameters)=="True"
        MicrographSelfile=getParameter("MicrographSelfile",fnPickingParameters)
        print os.path.curdir
        mD=xmipp.MetaData();
        xmipp.readMetaDataWithTwoPossibleImages(MicrographSelfile, mD)
        preprocessingDir,dummy=os.path.split(MicrographSelfile)
        errors.append("Cannot find the following micrographs:\n")
        NnotFound=0
        for id in mD:
            micrograph=mD.getValue(xmipp.MDL_IMAGE)
            if not os.path.exists(preprocessingDir+"/"+micrograph):
                message+=preprocessingDir+"/"+micrograph+"\n"
                NnotFound=NnotFound+1
            if isPairTilt:
                micrographTilted=mD.getValue(xmipp.MDL_ASSOCIATED_IMAGE1)
                if not os.path.exists(preprocessingDir+"/"+micrographTilted):
                    message+=preprocessingDir+"/"+micrographTilted+"\n"
                    NnotFound=NnotFound+1
        if NnotFound>0:
            errors.append(message)
                
        return errors

def getParameter(prm,filename):
    f = open(filename, 'r')
    lines=f.readlines()
    f.close()
    for line in lines:
        tokens=line.split('=')
        if tokens[0]==prm:
            return tokens[1].strip()
    return ""

