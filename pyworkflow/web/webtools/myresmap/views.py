# **************************************************************************
# *
# * Authors:    Jose Gutierrez (jose.gutierrez@cnb.csic.es)
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

from os.path import exists, join, basename
from pyworkflow.web.app.views_util import getResourceCss, getResourceJs, getResourceIcon, getServiceManager
from pyworkflow.web.app.views_base import base_grid, base_flex
from pyworkflow.web.app.views_project import contentContext
from pyworkflow.web.app.views_protocol import contextForm
from django.shortcuts import render_to_response
from pyworkflow.web.pages import settings as django_settings
from pyworkflow.manager import Manager
from django.http import HttpResponse
from pyworkflow.tests.tests import DataSet
from pyworkflow.utils import copyFile
from pyworkflow.utils.utils import prettyDelta

def resmap_projects(request):
   
    if 'projectName' in request.session: request.session['projectName'] = ""
    if 'projectPath' in request.session: request.session['projectPath'] = ""

    myresmap_utils = join(django_settings.STATIC_URL, "js/", "myresmap_utils.js")

    context = {'projects_css': getResourceCss('projects'),
               'project_utils_js': getResourceJs('project_utils'),
               'scipion_mail': getResourceIcon('scipion_mail'),
               'myresmap_utils': myresmap_utils,
               'hiddenTreeProt': True,
               }
    
    context = base_grid(request, context)
    return render_to_response('resmap_projects.html', context)


def writeCustomMenu(customMenu):
    if not exists(customMenu):
        f = open(customMenu, 'w+')
        f.write('''
[PROTOCOLS]

Local_Resolution = [
    {"tag": "section", "text": "2. Import your data", "children": [
        {"tag": "protocol", "value": "ProtImportVolumes", "text": "Import Volumes", "icon": "bookmark.png"}]},
    {"tag": "section", "text": "3. Analysis with ResMap", "children": [
        {"tag": "protocol", "value": "ProtResMap", "text": "resmap - local resolution"}]}]
        ''')
        f.close()
        
def create_resmap_project(request):
    if request.is_ajax():
        import os
        from pyworkflow.object import Pointer
        from pyworkflow.em.protocol import ProtImportVolumes
        from pyworkflow.em.packages.resmap.protocol_resmap import ProtResMap
        
        # Create a new project
        projectName = request.GET.get('projectName')
        
        # Filename to use as test data 
        testDataKey = request.GET.get('testData')
        
        manager = getServiceManager('myresmap')
        writeCustomMenu(manager.protocols)
        project = manager.createProject(projectName, runsView=1, 
                                        hostsConf=manager.hosts,
                                        protocolsConf=manager.protocols
                                        ) 
         
#         copyFile(customMenu, project.getPath('.config', 'protocols.conf'))
        
        # 1. Import volumes
        
        
        # If using test data execute the import averages run
        # options are set in 'project_utils.js'
#         dsMDA = DataSet.getDataSet('initial_volume')
#         
#         if testDataKey :
#             fn = dsMDA.getFile(testDataKey)
#             newFn = join(project.uploadPath, basename(fn))
#             copyFile(fn, newFn)
#             
#             label_import = 'import averages ('+ testDataKey +')'
#             protImport = project.newProtocol(ProtImportAverages, objLabel=label_import)
#             protImport.filesPath.set(newFn)
#             protImport.samplingRate.set(1.)
# #             protImport.setObjectLabel('import averages (%s)' % testDataKey)
#             project.launchProtocol(protImport, wait=True)
#         else:
        protImport = project.newProtocol(ProtImportVolumes, objLabel='import volumes')
        project.saveProtocol(protImport)
            
        
        # 2. ResMap 
        protResMap = project.newProtocol(ProtResMap)
        protResMap.setObjLabel('resmap - local resolution')
        protResMap.inputVolume.set(protImport)
        protResMap.inputVolume.setExtendedAttribute('outputVolume')
        project.saveProtocol(protResMap)
        
    return HttpResponse(mimetype='application/javascript')

# def get_testdata(request):
#     # Filename to use as test data 
#     testDataKey = request.GET.get('testData')
#     dsMDA = DataSet.getDataSet('initial_volume')
#     fn = dsMDA.getFile(testDataKey)
#     return HttpResponse(fn, mimetype='application/javascript')

def resmap_form(request):
    from django.shortcuts import render_to_response
    context = contextForm(request)
    context.update({'path_mode':'upload',
                    'formUrl': 'my_form'})
    return render_to_response('form/form.html', context)

 
def resmap_content(request):
    projectName = request.GET.get('p', None)
    path_files = django_settings.ABSOLUTE_URL + '/resources_myresmap/img/'
    
    # Get info about when the project was created
    manager = getServiceManager('myresmap')
    project = manager.loadProject(projectName, 
                                  protocolsConf=manager.protocols,
                                  hostsConf=manager.hosts)
    daysLeft = prettyDelta(project.getLeftTime(14))
    if daysLeft is None: 
        daysLeft = 14
    
    context = contentContext(request, project)
    context.update({'importVolumes': path_files + 'importVolumes.png',
                    'useResMap': path_files + 'useResMap.png',
                    'protResMap': path_files + 'protResMap.png',
                    'analyzeResults': path_files + 'analyzeResults.png',
                    'formUrl': 'r_form',
                    'mode':'service',
                    'daysLeft': daysLeft,
                    })
    
    return render_to_response('resmap_content.html', context)
