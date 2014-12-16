# **************************************************************************
# *
# * Authors:    Laura del Cano (ldelcano@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************

import unittest, sys
from pyworkflow.em import *
from pyworkflow.tests import *
from pyworkflow.em.packages.brandeis import *
from pyworkflow.em.protocol import ProtImportParticles, ProtImportVolumes


class TestBrandeisBase(BaseTest):
    @classmethod
    def setData(cls, dataProject='xmipp_tutorial'):
        cls.dataset = DataSet.getDataSet(dataProject)
        cls.micFn = cls.dataset.getFile('allMics')
        cls.volFn = cls.dataset.getFile('vol2')
        #cls.parFn = cls.dataset.getFile('aligned_particles')

    @classmethod
    def runImportMicrograph(cls, pattern, samplingRate, voltage, scannedPixelSize, magnification, sphericalAberration):
        """ Run an Import micrograph protocol. """
        # We have two options: passe the SamplingRate or the ScannedPixelSize + microscope magnification
        if not samplingRate is None:
            cls.protImport = ProtImportMicrographs(samplingRateMode=0, filesPath=pattern, samplingRate=samplingRate, magnification=magnification, 
                                                   voltage=voltage, sphericalAberration=sphericalAberration)
        else:
            cls.protImport = ProtImportMicrographs(samplingRateMode=1, filesPath=pattern, scannedPixelSize=scannedPixelSize, 
                                                   voltage=voltage, magnification=magnification, sphericalAberration=sphericalAberration)
        
        cls.proj.launchProtocol(cls.protImport, wait=True)
        # check that input micrographs have been imported (a better way to do this?)
        if cls.protImport.outputMicrographs is None:
            raise Exception('Import of micrograph: %s, failed. outputMicrographs is None.' % pattern)
        return cls.protImport

    @classmethod
    def runImportVolumes(cls, pattern, samplingRate,
                         importFrom = ProtImportParticles.IMPORT_FROM_FILES):
        """ Run an Import particles protocol. """
        cls.protImport = cls.newProtocol(ProtImportVolumes,
                                         filesPath=pattern,
                                         samplingRate=samplingRate
                                        )
                                         #not yet implemented
                                         #importFrom=importFrom
                                         #)
        cls.launchProtocol(cls.protImport)
        return cls.protImport

    @classmethod
    def runImportParticles(cls, pattern, samplingRate, checkStack=False,
                           importFrom = ProtImportParticles.IMPORT_FROM_FILES):
        """ Run an Import particles protocol. """
        if importFrom == ProtImportParticles.IMPORT_FROM_SCIPION:
            objLabel = 'from scipion (particles)'
        elif importFrom == ProtImportParticles.IMPORT_FROM_FILES:
            objLabel = 'from file (particles)'


        cls.protImport = cls.newProtocol(ProtImportParticles,
                                         objLabel=objLabel,
                                         filesPath=pattern,
                                         sqliteFile=pattern,
                                         samplingRate=samplingRate,
                                         checkStack=checkStack,
                                         importFrom=importFrom)

        cls.launchProtocol(cls.protImport)
        # check that input images have been imported (a better way to do this?)
        if cls.protImport.outputParticles is None:
            raise Exception('Import of images: %s, failed. outputParticles is None.' % pattern)
        return cls.protImport


    @classmethod
    def runImportMicrographBPV(cls, pattern):
        """ Run an Import micrograph protocol. """
        return cls.runImportMicrograph(pattern,
                                       samplingRate=1.237,
                                       voltage=300,
                                       sphericalAberration=2,
                                       scannedPixelSize=None,
                                       magnification=56000)

    @classmethod
    def runImportParticleGrigorieff(cls, pattern):
        """ Run an Import micrograph protocol. """
        return cls.runImportParticles(pattern,
                                      samplingRate=4.,
                                      checkStack=True,
                            importFrom=ProtImportParticles.IMPORT_FROM_SCIPION)
    @classmethod
    def runImportVolumesGrigorieff(cls, pattern):
        """ Run an Import micrograph protocol. """
        return cls.runImportVolumes(pattern,
                                    samplingRate=4.,
                                    importFrom=ProtImportParticles.IMPORT_FROM_FILES)


class TestBrandeisCtffind(TestBrandeisBase):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        TestBrandeisBase.setData()
        cls.protImport = cls.runImportMicrographBPV(cls.micFn)
    
    def testCtffind(self):
        protCTF = ProtCTFFind()
        protCTF.inputMicrographs.set(self.protImport.outputMicrographs)
        protCTF.ctfDownFactor.set(2)
        protCTF.numberOfThreads.set(4)
        self.proj.launchProtocol(protCTF, wait=True)
        self.assertIsNotNone(protCTF.outputCTF, "SetOfCTF has not been produced.")
        
        valuesList = [[23861, 23664, 56], [22383, 22153, 52.6], [22716, 22526, 59.1]]
        for ctfModel, values in izip(protCTF.outputCTF, valuesList):
            self.assertAlmostEquals(ctfModel.getDefocusU(),values[0], delta=1000)
            self.assertAlmostEquals(ctfModel.getDefocusV(),values[1], delta=1000)
            self.assertAlmostEquals(ctfModel.getDefocusAngle(),values[2], delta=1)
            self.assertAlmostEquals(ctfModel.getMicrograph().getSamplingRate(), 2.474, delta=0.001)

    def testCtffind2(self):
        protCTF = ProtCTFFind()
        protCTF.inputMicrographs.set(self.protImport.outputMicrographs)
        protCTF.numberOfThreads.set(4)
        self.proj.launchProtocol(protCTF, wait=True)
        self.assertIsNotNone(protCTF.outputCTF, "SetOfCTF has not been produced.")
        
        valuesList = [[23863, 23640, 64], [22159, 21983, 50.6], [22394, 22269, 45]]
        for ctfModel, values in izip(protCTF.outputCTF, valuesList):
            self.assertAlmostEquals(ctfModel.getDefocusU(),values[0], delta=1000)
            self.assertAlmostEquals(ctfModel.getDefocusV(),values[1], delta=1000)
            self.assertAlmostEquals(ctfModel.getDefocusAngle(),values[2], delta=1)
            self.assertAlmostEquals(ctfModel.getMicrograph().getSamplingRate(), 1.237, delta=0.001)


class TestBrandeisFrealign(TestBrandeisBase):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        dataProject='grigorieff'
        dataset = DataSet.getDataSet(dataProject)
        TestBrandeisBase.setData()
        particlesPattern   = dataset.getFile('particles.sqlite')
        volFn              = dataset.getFile('ref_volume.vol')
        cls.protImportPart = cls.runImportParticleGrigorieff(particlesPattern)
        cls.protImportVol  = cls.runImportVolumesGrigorieff(volFn)

    def testFrealign(self):
        frealign = self.newProtocol(ProtFrealign,
                                    inputParticles = self.protImportPart.outputParticles,
                                    input3DReference = self.protImportVol.outputVolume,
                                    useInitialAngles=True,
                                    mode=MOD_RECONSTRUCTION,
                                    innerRadius=0.,
                                    outerRadius=241.,
                                    symmetry='C1',
                                    numberOfThreads=4,
                                    numberOfIterations=1,
                                    doWienerFilter=False,
                                    resolution=2.,
                                    highResolRefine=2.,
                                    resolClass=2.,
                                    writeMatchProjections=False,
                                    score=0,
                                    )
        frealign.inputParticles.set(self.protImportPart.outputParticles)
        frealign.input3DReference.set(self.protImportVol.outputVolume)
        self.launchProtocol(frealign)
        print "Assert is missing: testFrealign"

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBrandeisCtffind)
    suite = unittest.TestLoader().loadTestsFromName('test_protocols_brandeis.TestBrandeisCtffind.testCtffind')
    unittest.TextTestRunner(verbosity=2).run(suite)