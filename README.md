cosbench-plot: plot utility for COSBench
========================================

cosbench-plot is a tool to analyze the statistics produced by COSBench (https://github.com/intel-cloud/cosbench) and create charts to compare different workstages and workloads.

NOTE: this tool is developed independently from COSBench.

Usage
-----

The most important concept in cosbench-plot is how relationships between workloads are established.

Every analysis requires one or more lists of workloads as input. Since there is no metadata to inform cosbench-plot about the nature of the workloads, a relationship is established according to the relative ordering of the workload IDs in the lists.

In COSBench, workloads have unique IDs. If, for example, workloads 4 and 5 relate to Ceph and workloads 18 and 21 contain matching workstages for Swift, two lists consisting of [4,5] and [18,21] could be setup to be used in cosbench-plot.

Currently, this usage model may impose limitations in case workloads and workstages are organized in different ways (e.g., if there is only a single workload containing many workstages, some more high-level graph that compare workloads cannot be effectively used).

Five main categories of graphs can be currently generated by cosbench-plot (refer to the "charts-example" folder for examples):
  * A comparison of a single metric of a single workstage for each workstage in each corresponding workload (charts-examples/SingleWorkstageAndMetric.svg)
  * A comparison of a single metric for all the workstages of a workload and matching workstages of corresponding workloads (charts-examples/WorkstagesThroughput.svg)
  * A scatter plot of values of a certain metric for each workstage of each workload (charts-examples/WorkloadScatter.svg)
  * A response time and CDF curve for workstages of different workloads (charts-examples/ResponseTime-CDF.svg)
  * A high level overview showing, for a certain metric, for each workload, the highest average value across some determined workstages (charts-examples/WorkloadsThroughput.svg)

At the moment, cosbench-plot is a Python library, so there is no CLI/GUI.
The intended usage entails writing some Python code to describe the charts that must be plotted.

For some usage examples, please check the examples package.

Some more user-friendly documentation will be available soon, in the meantime, please use the contact information if you are interested in using this sofwtare and need some help.

Versions
--------

There are no releases at the moment other than the HEAD on the master branch!

Requirements
------------

 * Python >= 2.7
 * matplotlib for python: http://matplotlib.org/ (probably available in your distro repositories)





Contact
-------

Vincenzo Pii - piiv@zhaw.ch

www.cloudcomp.ch
