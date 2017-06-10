import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from functools import lru_cache
from skued import spectrum_colors
from skued.baseline import ALL_COMPLEX_WAV, ALL_FIRST_STAGE

@lru_cache(maxsize = 1)
def pens_and_brushes(num):
    qcolors = tuple(map(lambda c: QtGui.QColor.fromRgbF(*c), spectrum_colors(num)))
    pens = list(map(pg.mkPen, qcolors))
    brushes = list(map(pg.mkBrush, qcolors))
    return pens, brushes

class PowderViewer(QtGui.QWidget):

    baseline_parameters_signal = QtCore.pyqtSignal(dict)
    peak_dynamics_roi_signal = QtCore.pyqtSignal(float, float)  #left pos, right pos

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
                
        self.powder_pattern_viewer = pg.PlotWidget(title = 'Radially-averaged pattern(s)', 
                                                   labels = {'left': 'Intensity (counts)', 
                                                             'bottom': 'Scattering length (1/A)'})
        self.peak_dynamics_viewer = pg.PlotWidget(title = 'Peak dynamics measurement', 
                                                  labels = {'left': 'Intensity (a. u.)', 
                                                            'bottom': ('time', 'ps')})
        self.peak_dynamics_viewer.getPlotItem().enableAutoRange()
       
        # Peak dynamics region-of-interest
        self.peak_dynamics_region = pg.LinearRegionItem(values = (0.2, 0.3))
        self.peak_dynamics_viewer.addItem(self.peak_dynamics_region)
        self.peak_dynamics_region.sigRegionChanged.connect(self.update_peak_dynamics)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.powder_pattern_viewer)
        layout.addWidget(self.peak_dynamics_viewer)
        self.setLayout(layout)
        self.resize(self.maximumSize())
    
    @QtCore.pyqtSlot()
    def update_peak_dynamics(self):
        """ Update powder peak dynamics settings on demand. """
        self.peak_dynamics_roi_signal.emit(*self.peak_dynamics_region.getRegion())
    
    @QtCore.pyqtSlot(object, object, object)
    def display_powder_data(self, scattering_length, powder_data_block, powder_error_block):
        """ 
        Display the radial averages of a dataset.

        Parameters
        ----------
        scattering_length : ndarray, shape (N,) or None
            Scattering length of the radial patterns. If None, all
            viewers are cleared.
        powder_data_block : ndarray, shape (M, N) or None
            Array for which each row is an azimuthal pattern for a specific time-delay. If None, all
            viewers are cleared.
        powder_error_block : ndarray, shape (M, N) or None
            Array for which each row is the error for the corresponding azimuthal pattern. If None, all
            viewers are cleared.
        """
        if (scattering_length is None) or (powder_data_block is None) or (powder_error_block is None):
            self.powder_pattern_viewer.clear()
            self.peak_dynamics_viewer.clear()
            return
        
        pens, brushes = pens_and_brushes(num = powder_data_block.shape[0])

        self.powder_pattern_viewer.enableAutoRange()
        self.powder_pattern_viewer.clear()

        # Line plot
        for pen, brush, curve, error in zip(pens, brushes, powder_data_block, powder_error_block):
            self.powder_pattern_viewer.plot(scattering_length, curve, pen = None, symbol = 'o',
                                            symbolPen = pen, symbolBrush = brush, symbolSize = 3)
            error_bars = pg.ErrorBarItem(x = scattering_length, y = curve, height = error)
            self.powder_pattern_viewer.addItem(error_bars)
        
        self.peak_dynamics_region.setBounds([scattering_length.min(), scattering_length.max()])
        self.powder_pattern_viewer.addItem(self.peak_dynamics_region)
        self.update_peak_dynamics() #Update peak dynamics plot if background has been changed, for example
    
    @QtCore.pyqtSlot(object, object)
    @QtCore.pyqtSlot(object, object, object)    # Maybe there's an error to display, maybe not
    def display_peak_dynamics(self, times, intensities, errors = None):
        """ 
        Display the time series associated with the integral between the bounds 
        of the ROI
        """
        pens, brushes = pens_and_brushes(num = len(times))

        intensities /= intensities.max()

        self.peak_dynamics_viewer.plot(times, intensities, 
                                       pen = None, symbol = 'o', 
                                       symbolPen = pens, symbolBrush = brushes, 
                                       symbolSize = 4, clear = True)
        
        if errors is not None:
            error_bars = pg.ErrorBarItem(x = times, y = intensities, height = errors)
            self.peak_dynamics_viewer.addItem(error_bars)
        
        # If the use has zoomed on the previous frame, auto range might be disabled.
        self.peak_dynamics_viewer.getPlotItem().enableAutoRange()
