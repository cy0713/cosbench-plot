# -*- coding: utf-8 -*-

'''
Copyright 2014 ZHAW (Zürcher Hochschule für Angewandte Wissenschaften)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


'''
Created on May 20, 2014

@author: vince
'''
import matplotlib.pyplot as plt
from plotter.FilePlotter import FilePlotter

class WorkloadMaxPlotter(FilePlotter):

    class PointDescriptor:
        def __init__(self, xlabel, values, yannotations):
            self.xlabel = xlabel
            self.values = values
            self.yannotations = yannotations

    def __init__(self, title):
        super(WorkloadMaxPlotter, self).__init__(title)
        self._points = []
        self._positionalLabels = []
        self._unit = None

    def setUnit(self, unit):
        self._unit = unit

    def addPoint(self, xlabel, values, yannotations):
        point = WorkloadMaxPlotter.PointDescriptor(xlabel, values, yannotations)
        self._points.append(point)
        self._dataArrays['dummy'] = 0

    def setPositionalLabels(self, labels):
        self._positionalLabels = labels

    def plotImpl(self):
        _, data_ax = plt.subplots()
        xticks = []
        yvalues = [[] for _ in range(len(self._points[0].values))]
        annotations = [[] for _ in range(len(self._points[0].values))]
        for point in self._points:
            xticks.append(point.xlabel)
            for index,value in enumerate(point.values):
                yvalues[index].append(value)
                annotations[index].append(point.yannotations[index])
        for index,values in enumerate(yvalues):
            color = self._getNextColor()
            data_ax.plot(range(len(xticks)), values, color=color, linewidth='2.0', label=self._positionalLabels[index], marker='o')
            for index2,annotation in enumerate(annotations[index]):
                annotation_text = annotation
                point_coordinates = (index2,values[index2])
                text_coordinates = (index2,values[index2])
                data_ax.annotate(annotation_text, xy=point_coordinates, xytext=text_coordinates)
        data_ax.set_xlabel('Workload configuration')
        plt.xticks(range(len(xticks)), xticks, rotation=45, fontsize=10)
        plt.grid(True)
        #plt.autoscale(True, 'both', True)
        #fig.set_tight_layout(True)
        if self._unit is not None:
            data_ax.set_ylabel(self._unit)
        data_ax.legend(loc='best', fancybox=True, shadow=True, prop={'size':11})
        plt.title(self._title)
        plt.tight_layout()
        return plt