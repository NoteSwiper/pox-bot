import sys
import time
import psutil
from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg

pg.setConfigOptions(antialias=True)

class DataStabilizer:
    def __init__(self, p_lead=0.5, v_weight=0.3):
        self.smooth = 0.0
        self.velocity = 0.0
        self.p_lead = p_lead
        self.v_weight = v_weight
    
    def update(self, raw_value):
        instant_vel = raw_value - self.smooth
        self.velocity = (self.velocity * (1 - self.v_weight)) + (instant_vel * self.v_weight)
        
        delta = abs(raw_value - self.smooth)
        alpha = 0.1 + min(0.5, delta / 100)
        
        predicted = max(0, min(100, raw_value + (self.velocity * self.p_lead)))
        self.smooth = (predicted * alpha) + (self.smooth * (1 - alpha))
        return self.smooth

class MonitorWindow(QtWidgets.QMainWindow):
    def __init__(self, core_count):
        super().__init__()
        self.setWindowTitle("System Monitor (Optimized)")
        self.resize(1000, 600)
        
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QtWidgets.QVBoxLayout(self.central)
        
        self.cpu_plot = self.create_plot("CPU Usage (Stacked, %)")
        self.mem_plot = self.create_plot("Memory Usage (Dynamic Zoom, %)")
        self.main_layout.addWidget(self.cpu_plot)
        self.main_layout.addWidget(self.mem_plot)
        
        self.core_count = core_count
        self.max_points = 300 # 30 seconds at 10Hz
        self.start_time = time.time()
        
        self.mem_stabilizer = DataStabilizer(p_lead=0.4, v_weight=0.5)
        self.cpu_stabilizers = [DataStabilizer(p_lead=0.74, v_weight=0.55) for _ in range(core_count)]

        self.timestamps = []        
        self.cpu_data = [[] for _ in range(core_count)]
        self.mem_data = [0.0] * self.max_points
        
        self.cpu_ymax = 100
        self.mem_ymin = 0
        self.mem_ymax = 100
        
        self.setup_cpu_curves()
        
        #self.mem_glow = self.mem_plot.plot(pen=pg.mkPen(color=(255, 170, 0, 80), width=8))
        
        self.mem_line = self.mem_plot.plot(pen=pg.mkPen(color=(255, 170, 0), width=1))
        
        self.mem_dots = pg.ScatterPlotItem(size=6, brush=(255, 170, 0), pen=None)
        self.mem_plot.addItem(self.mem_dots)
        
        self.poll_timer = QtCore.QTimer()
        self.poll_timer.timeout.connect(self.poll_data)
        self.poll_timer.start(10000) 
        
        self.gfx_timer = QtCore.QTimer()
        self.gfx_timer.timeout.connect(self.refresh_graphics)
        self.gfx_timer.start(33)

    def create_plot(self, title):
        plot = pg.PlotWidget(title=title)
        plot.showGrid(x=True, y=True)
        plot.setLabel("left", "Usage (%)")
        plot.setLabel("bottom", "Time (s)")
        return plot

    def setup_cpu_curves(self):
        self.cpu_curves = []
        #self.cpu_glow = []
        self.cpu_dots = []
        
        prev_curve = None
        
        for i in range(self.core_count):
            color = pg.intColor(i, hues=self.core_count, alpha=180)
            
            #glow_color = pg.mkColor(color)
            #glow_color.setAlpha(60)
            
            #glow = self.cpu_plot.plot(
            #    pen=pg.mkPen(
            #        color=glow_color,
            #        width=6
            #    )
            #)
            #self.cpu_glow.append(glow)
            
            curve = self.cpu_plot.plot(pen=pg.mkPen(color=color, width=1))
            self.cpu_curves.append(curve)
            
            dots = pg.ScatterPlotItem(size=4, brush=color, pen=None)
            self.cpu_plot.addItem(dots)
            self.cpu_dots.append(dots)
            
            if prev_curve:
                area = pg.FillBetweenItem(curve, prev_curve, brush=color)
                self.cpu_plot.addItem(area)
            
            prev_curve = curve

    def poll_data(self):
        now = time.time() - self.start_time
        self.timestamps.append(now)
        if len(self.timestamps) > self.max_points:
            self.timestamps.pop(0)
        
        raw_cpu = psutil.cpu_percent(percpu=True)
        for i, val in enumerate(raw_cpu):
            smooth_val = self.cpu_stabilizers[i].update(val)
            self.cpu_data[i].append(smooth_val)
            if len(self.cpu_data[i]) > self.max_points:
                self.cpu_data[i].pop(0)
        
        raw_mem = psutil.virtual_memory().percent
        self.mem_data.append(self.mem_stabilizer.update(raw_mem))
        self.mem_data.pop(0)

    def refresh_graphics(self):
        if not self.timestamps: return
        
        t_slice = self.timestamps
        
        current_stack = [0.0] * len(t_slice)
        for i in range(min(self.core_count, len(self.cpu_dots))):
            data_slice = self.cpu_data[i]
            
            min_len = min(len(t_slice), len(data_slice))
            t_local = t_slice[-min_len:]
            data_slice = data_slice[-min_len:]

            layer = []
            
            for j, val in enumerate(data_slice):
                current_stack[j] += val / self.core_count
                layer.append(current_stack[j])
            
            ix, iy = self.interpolate(t_local, layer)
            
            #self.cpu_glow[i].setData(ix, iy)
            self.cpu_curves[i].setData(ix, iy)
            self.cpu_dots[i].setData([ix[-1]], [iy[-1]])
                
        self.cpu_plot.setXRange(t_slice[0], t_slice[-1])
        
        target_ymax = (max(current_stack) if current_stack else 0) + 10
        self.cpu_ymax = (self.cpu_ymax * 0.9) + (target_ymax * 0.1)
        self.cpu_plot.setYRange(0, self.cpu_ymax)
        
        m_slice = self.mem_data[-len(t_slice):]
        ix, iy = self.interpolate(t_slice, m_slice)
        
        #self.mem_glow.setData(ix, iy)
        self.mem_line.setData(ix, iy)
        
        self.mem_dots.setData([ix[-1]], [iy[-1]])
        
        d_min, d_max = min(m_slice), max(m_slice)
        padding = max(1.0, (d_max - d_min) * 0.1)
        self.mem_ymin = (self.mem_ymin * 0.9) + ((d_min - padding) * 0.1)
        self.mem_ymax = (self.mem_ymax * 0.9) + ((d_max + padding) * 0.1)
        
        self.mem_plot.setYRange(self.mem_ymin, self.mem_ymax)
        self.mem_plot.setXRange(t_slice[0], t_slice[-1])

    def interpolate(self, x, y, factor=3):
        if len(x) < 4: return x, y
        
        new_x, new_y = [], []
        
        for i in range(1, len(x) - 2):
            x0, x1, x2, x3 = x[i - 1], x[i], x[i + 1], x[i + 2]
            y0, y1, y2, y3 = y[i - 1], y[i], y[i + 1], y[i + 2]
            
            for j in range(factor):
                t = j / factor
                t2 = t * t
                t3 = t2 * t
                
                xt = 0.5 * (
                    (2 * x1) +
                    (-x0 + x2) * t +
                    (2*x0 - 5*x1 + 4*x2 - x3) * t2 +
                    (-x0 + 3*x1 - 3*x2 + x3) * t3
                )
                yt = 0.5 * (
                    (2 * y1) +
                    (-y0 + y2) * t +
                    (2*y0 - 5*y1 + 4*y2 - y3) * t2 +
                    (-y0 + 3*y1 - 3*y2 + y3) * t3
                )
                
                yt = max(0, min(100, yt))
                
                new_x.append(xt)
                new_y.append(yt)
        new_x.append(x[-2])
        new_y.append(y[-2])
        new_x.append(x[-1])
        new_y.append(y[-1])
        return new_x, new_y

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MonitorWindow(psutil.cpu_count(logical=True))
    window.show()
    sys.exit(app.exec())