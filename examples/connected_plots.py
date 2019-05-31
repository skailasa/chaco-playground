from numpy import linspace, sin
from traits.api import HasTraits, Instance
from traitsui.api import Item, View
from chaco.api import ArrayPlotData, Plot, HPlotContainer
from chaco.tools.api import PanTool, ZoomTool
from enable.api import ComponentEditor


class ConnectedRange(HasTraits):
    container = Instance(HPlotContainer)

    traits_view = View(Item('container', editor=ComponentEditor(), show_label=False),
                       width=1000, height=600, resizable=True,
                       title="Connected")

    def _container_default(self):
        x = linspace(-10, 10, 100)
        y = sin(x) * x
        plotdata = ArrayPlotData(x=x, y=y)

        scatter = Plot(plotdata)
        scatter.plot(('x', 'y'), type='scatter', color='blue')

        line = Plot(plotdata)
        line.plot(('x', 'y'), type='line', color='green')

        container = HPlotContainer(scatter, line)

        scatter.tools.append(PanTool(scatter))
        scatter.tools.append(ZoomTool(scatter))

        line.tools.append(PanTool(line))
        line.tools.append(ZoomTool(line))
        
        # Chaco has the concept of data range to express bounds in data space
        # Standard 2D plots all have 2D ranges on them
        # Here two plots now share same range object, and will change together
        # In response to changes to the data space bounds.
        scatter.range2d = line.range2d
        return container


if __name__ == "__main__":
    ConnectedRange().configure_traits()
