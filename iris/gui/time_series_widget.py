# -*- coding: utf-8 -*-
"""
Time-series widget
"""

from functools import lru_cache

import numpy as np
from pyqtgraph import PlotWidget, PlotDataItem, QtCore, QtGui, mkBrush, mkPen

from skued import spectrum_colors


@lru_cache(maxsize = 1)
def pens_and_brushes(num):
    qcolors = tuple(map(lambda c: QtGui.QColor.fromRgbF(*c), spectrum_colors(num)))
    pens = list(map(mkPen, qcolors))
    brushes = list(map(mkBrush, qcolors))
    return pens, brushes

class TimeSeriesWidget(QtGui.QWidget):
    """
    Time-series widget with built-in display controls.

    Slots
    -----
    plot : (array, array)
        Plot a time-series.
    """

    # Internal refresh signal
    _refresh_signal = QtCore.pyqtSignal(object, object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.plot_widget = PlotWidget(parent = self,
                                      title = 'Diffraction time-series', 
                                      labels = {'left'  : ('Intensity', 'a. u.'), 
                                                'bottom': ('time', 'ps')})

        self.plot_widget.getPlotItem().showGrid(x = True, y = True)

        # Internal state on whether or not to 'connect the dots'
        self._time_series_connect = False
        self._symbol_size = 5

        # Internal memory on last time-series info
        self._last_times = None
        self._last_intensities = None
        self._refresh_signal.connect(self.plot)

        self.flip_times_widget = QtGui.QCheckBox('(DEBUG) Reverse times', self)
        self.flip_times_widget.setChecked(False)
        self.flip_times_widget.toggled.connect(lambda _: self.refresh())

        # Shortcut for some controls provided by PyQtGraph
        self.horz_grid_widget = QtGui.QCheckBox('Show horizontal grid', self)
        self.horz_grid_widget.setChecked(True)
        self.horz_grid_widget.toggled.connect(self.enable_horz_grid)
        
        self.vert_grid_widget = QtGui.QCheckBox('Show vertical grid', self)
        self.vert_grid_widget.setChecked(True)
        self.vert_grid_widget.toggled.connect(self.enable_vert_grid)

        self.connect_widget = QtGui.QCheckBox('Connect time-series', self)
        self.connect_widget.toggled.connect(self.enable_connect)

        self.symbol_size_widget = QtGui.QSpinBox(parent = self)
        self.symbol_size_widget.setRange(1, 25)
        self.symbol_size_widget.setValue(self._symbol_size)
        self.symbol_size_widget.setPrefix('Symbol size: ')
        self.symbol_size_widget.valueChanged.connect(self.set_symbol_size)

        self.horz_log_widget = QtGui.QCheckBox('Horizontal log mode', self)
        self.horz_log_widget.toggled.connect(self.enable_horz_log)
        
        self.vert_log_widget = QtGui.QCheckBox('Vertical log mode', self)
        self.vert_log_widget.toggled.connect(self.enable_vert_log)

        self.controls = QtGui.QVBoxLayout()
        self.controls.addWidget(self.horz_grid_widget)
        self.controls.addWidget(self.vert_grid_widget)
        self.controls.addWidget(self.horz_log_widget)
        self.controls.addWidget(self.vert_log_widget)
        self.controls.addWidget(self.connect_widget)
        self.controls.addWidget(self.symbol_size_widget)
        self.controls.addWidget(self.flip_times_widget)
        self.controls.addStretch(1)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addLayout(self.controls)
        self.setLayout(layout)
    
    @QtCore.pyqtSlot(object, object)
    def plot(self, time_points, intensity):

        self._last_times = np.asarray(time_points)
        self._last_intensities = np.asarray(intensity)
        self._last_intensities /= self._last_intensities.max()

        if self.flip_times_widget.isChecked():
            self._last_times = self._last_times[::-1]

        # Only compute the colors if number of time-points changes or first time
        pens, brushes = pens_and_brushes(len(time_points))

        connect_kwargs = {'pen': None} if not self._time_series_connect else {}
        self.plot_widget.plot(x = self._last_times, y = self._last_intensities, 
                              symbol = 'o', symbolPen = pens, 
                              symbolBrush = brushes, symbolSize = self._symbol_size, 
                              clear = True, **connect_kwargs)
    
    @QtCore.pyqtSlot()
    def refresh(self):
        self._refresh_signal.emit(self._last_times, self._last_intensities)
    
    @QtCore.pyqtSlot()
    def clear(self):
        self.plot_widget.clear()
    
    @QtCore.pyqtSlot(bool)
    def enable_horz_grid(self, toggle):
        self.plot_widget.getPlotItem().showGrid(x = toggle)
    
    @QtCore.pyqtSlot(bool)
    def enable_vert_grid(self, toggle):
        self.plot_widget.getPlotItem().showGrid(y = toggle)
    
    @QtCore.pyqtSlot(bool)
    def enable_horz_log(self, toggle):
        self.plot_widget.getPlotItem().setLogMode(x = toggle)

    @QtCore.pyqtSlot(bool)
    def enable_vert_log(self, toggle):
        self.plot_widget.getPlotItem().setLogMode(y = toggle)

    @QtCore.pyqtSlot(bool)
    def enable_connect(self, toggle):
        self._time_series_connect = toggle
        self.refresh()
    
    @QtCore.pyqtSlot(int)
    def set_symbol_size(self, size):
        self._symbol_size = size
        self.refresh()