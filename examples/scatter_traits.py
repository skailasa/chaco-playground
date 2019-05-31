from numpy import linspace, sin
from traits.api import HasTraits, Instance, Int
from traitsui.api import Item, Group, View
from chaco.api import ArrayPlotData, marker_trait, Plot
from enable.api import ColorTrait, ComponentEditor


class ScatterPlotTraits(HasTraits):

    plot = Instance(Plot)
    color = ColorTrait("blue")
    marker = marker_trait
    marker_size = Int(4)

    traits_view = View(
            Group(Item('color', label="Color", style="custom"),
                  Item('marker', label="Marker"),
                  Item('marker_size', label="Marker Size"),
                  Item('plot', editor=ComponentEditor(), show_label=False),
                  orientation="vertical"),
            width=800, height=600, resizable=True, title='title')


    def _plot_default(self):
        x = linspace(-10, 10, 100)
        y = sin(x)*x
        plotdata = ArrayPlotData(x=x, y=y)

        plot = Plot(plotdata)

        self.renderer = plot.plot(("x", "y"), type="scatter", color="blue")[0]

        return plot

    def _color_changed(self):
        self.renderer.color = self.color

    def _marker_changed(self):
        self.renderer.marker = self.marker

    def _marker_size_changed(self):
        self.renderer.marker_size = self.marker_size

if __name__ == "__main__":
    ScatterPlotTraits().configure_traits()
