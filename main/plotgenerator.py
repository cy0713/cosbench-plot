'''
Created on May 16, 2014

@author: vince
'''
import os
import re
from cosbenchplot.parser.StageFileParser import StageFileParser
from cosbenchplot.plotter.StageFilePlotter import StageFilePlotter
from cosbenchplot.parser.FileParser import FileParser

class PlotGenerator(object):
    '''
    This class takes workload ids, finds the corresponding directories and
    analyze contained CSV files to make comparisons.
    
    The order of the given IDs determines the matching between workload
    directories.
    So, if two lists of ids are given, e.g., [55, 44, 45] and [57, 58, 59],
    the following couples of workloads will be matched against for generating
    plots:
    55-57, 44-58, 45-59
    '''
    def __init__(self, basepath, outdir):
        super(PlotGenerator, self).__init__()
        self._basepath = basepath + '/'
        self._outdir = outdir
        self._workloadids = {}
        self._workloaddirs = {}
        self._workloadregex = ''
        self._filenameregex = ''

    def addWorkloadIds(self, name, ids):
        self._workloadids[name] = ids

    def setWorkloadFilter(self, regex):
        '''
        Adds a regular expression to match the name of the workloads to be
        included. If the regex doesn't match, the workload will not be included
        '''
        self._workloadregex = regex

    def setFilenameFilter(self, regex):
        self._filenameregex = regex

    def _getWorkloadDirectoryLists(self):
        '''
        For each workload id, finds the corresponding workload directory
        '''
        if len(self._workloadids) == 0:
            raise Exception("No directory ids have been provided")
        alldirs = os.listdir(self._basepath)
        for (name,wids) in self._workloadids.items():
            self._workloaddirs[name] = []
            for wid in wids:
                matchingdir = self._findMatchingDirectory(wid, alldirs, self._basepath)
                matchingdir = self._validateWlDirName(matchingdir)
                if len(matchingdir) > 0:
                    self._workloaddirs[name].append(matchingdir)
        return

    def _findMatchingDirectory(self, wid, alldirs, prefix = ''):
        for directory in alldirs:
            if directory.startswith('w' + str(wid) + '-'):
                return prefix + directory
        raise Exception('Cannot find workload directory for id ' + wid)

    def _validateWlDirName(self, dirname):
        if len(self._workloadregex) == 0 or re.search(self._workloadregex, dirname):
            return dirname
        return ''

    def _validateFileName(self, filename):
        if len(self._filenameregex) == 0 or re.search(self._filenameregex, filename):
            return filename
        return ''

    def _validateFileNamesList(self, filenamelist):
        outlist = []
        for filename in filenamelist:
            validatedFilename = self._validateFileName(filename)
            if len(validatedFilename) > 0:
                outlist.append(validatedFilename)
        return outlist

class RTPlotGenerator(PlotGenerator):
    
    def __init__(self):
        super(RTPlotGenerator, self).__init__()

    def createAllRtPlots(self):
        # TODO
        pass

class StagePlotGenerator(PlotGenerator):
    '''
    For stage comparison, this code assumes that the stage name is the same
    across comparable workloads (this also confirms the matching between
    workload directories).
    '''

    def __init__(self, basepath, outdir):
        super(StagePlotGenerator, self).__init__(basepath, outdir)

    def createAllStagePlots(self, outputdir):
        '''
        For each matching stage files tuple, creates a graph for each metric of
        each storage system
        '''
        for ws_dir_files,storage_names in self._generateListsOfComparableFiles():
            titles = []
            for wsfilename in ws_dir_files[0]:
                titles.append(self._extractStageTitleFromFileName(os.path.split(wsfilename)[1]))
            for title in titles:
                to_be_compared = []
                # ws_filename_list is the list of workstage files for a certain workload for a certain storage system
                for ws_filename_list in ws_dir_files:
                    comp = self._findMatchingFile(ws_filename_list, title)
                    to_be_compared.append(comp)
                self._compareWorkstageFiles(to_be_compared, storage_names, title)
        return

    def createAggregatedChart(self, outputdir, title, labelregex, metrics, lineStyleRule):
        '''
        Creates a single chart combining all available files after the previous
        filtering and using only the metrics whose name match one of the regex
        provided in the metrics list.
        Labelregex is a regex that applied to the name of the workstage returns
        the ID for the label in the chart as group(1)
        '''
        #sfpl = StageFilePlotter(title + ' - ' + name + ' - ' + operation)
        labelregex = re.compile(labelregex)
        assert(type(metrics) is list)
        metrics = [re.compile(metric) for metric in metrics]
        sfpl = StageFilePlotter(title)
        sfpl.setLineStyleRule(lineStyleRule)
        for ws_dir_files,storage_names in self._generateListsOfComparableFiles():
            for index,wsfilenames in enumerate(ws_dir_files):
                for filename in wsfilenames:
                    # Ref to storage storage_names[index]
                    wstitle = self._extractStageTitleFromFileName(os.path.split(filename)[1])
                    s = StageFileParser(filename, storage_names[index])
                    stats = s.loadStatistics()
                    for key,data in stats.items():
                        if self._filterStats(key):
                            continue
                        if any(metric.match(key) for metric in metrics):
                            # We want to plot this data
                            sfpl.addDataArray(data.data, stats[FileParser.ANNOTATION] + '_' + re.search(labelregex, wstitle).group(1), data.headerType.unit)
#         sfpl.plotOnlyAvg(True)
        sfpl.plot(show = False, saveto = self._outdir + title + '.png')

    def _generateListsOfComparableFiles(self):
        '''
        This method generates a list of comparable files for each different
        storage system, for each workload directory
        '''
        self._getWorkloadDirectoryLists()
        names = []
        matrix = []
        for storage,wldirs in self._workloaddirs.items():
            names.append(storage)
            matrix.append(wldirs)
        # We now have a matrix of directories and the corresponding storage system names
        # matrix[i] is for names[i]
        assert(len(set(map(len, matrix))) == 1) # all have the same length
        # Transpose the matrix
        tmat = map(list, zip(*matrix))
        # tmat is a list of tuples, each one containing the directories that have related workloads
        # e.g., [(wlx_ceph, wlx_swift), (wly_ceph, wly_swift)]
        for tpl in tmat:
            ws_dir_files = []
            for directory in tpl:
                files = self._filterWorkstageFiles(os.listdir(directory), directory)
                files = self._validateFileNamesList(files)
                if len(files) > 0:
                    ws_dir_files.append(files)
            # ws_dir_files is a list containing the list of files to be compared
            # for each storage system
            yield ws_dir_files, names

    def _filterWorkstageFiles(self, filenames, basepath):
        '''
        Given a list of filenames, returns a list of only the filenames that contain
        workstage statistics
        '''
        outlist = []
        for filen in filenames:
            if re.search('^s[0-9]+-w', filen):
                outlist.append(basepath + '/' + filen)
        return outlist

    def _extractStageTitleFromFileName(self, ws_filename):
        match = re.search('(^s[0-9]+-w)(.*)(\.csv)', ws_filename)
        return match.group(2)

    def _findMatchingFile(self, filenames, title):
        '''
        Given the title of a stage and a list of filenames, finds the file that
        matches with that title
        '''
        for filename in filenames:
            if re.search('^s[0-9]+-w' + re.escape(title) + '\.csv', os.path.split(filename)[1]):
                return filename
        raise Exception('Cannot find file that matches with ' + title)

    def _compareWorkstageFiles(self, filelist, storage_annotations, title):
        stats = []
        for index,fl in enumerate(filelist):
            s = StageFileParser(fl, storage_annotations[index])
            stats.append(s.loadStatistics())
        self._createComparePlots(stats, title)
    
    def _createComparePlots(self, statisticsArray, title):
        '''
        This method takes an array of Stage File statistics and plot the same
        headers of each statistic against the others of the same type.
        
        E.g., for every statistics in the array, creates plots to compare read-tpt,
        read-bdw, ...
        
        Note that the same could be done by simply iterating over the keys of one
        of the elements of statisticsArray and finding the same key in all the
        others.
        '''
        # Assert that the headers are the same for all statistics
        keyset = statisticsArray[0].keys()
        for s in statisticsArray:
            assert(s.keys() == keyset)
        
        title = title.replace('(', "").replace(')','')
        
        for operation in StageFileParser.Operations.ops:
            for name in StageFileParser.HeaderTypes.headers.keys():
                if self._filterStats(name):
                    continue
                sfpl = StageFilePlotter(title + ' - ' + name + ' - ' + operation)
                datakey = name + operation
                for stat in statisticsArray:
                    if stat.has_key(datakey) == False:
                        continue
                    sfpl.addDataArray(stat[datakey].data, stat[FileParser.ANNOTATION], stat[datakey].headerType.unit)
                if sfpl.containsData():
                    # Only if there is data to plot
                    sfpl.plot(show = False, saveto = self._outdir + title + '_' + name + '_' + operation + '.png')
        return

    def _filterStats(self, statname):
        if statname.startswith('Version-Info') or statname.startswith('Timestamp') or statname == FileParser.ANNOTATION:
            return True
        return False