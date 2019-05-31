from scipy.special import jn
from numpy import linspace
from traits.api import Enum, HasTraits, Instance
from traitsui.api import Item, View
from chaco.api import ArrayPlotData, Plot
from enable.api import ComponentEditor

class DataChooser(HasTraits):

    plot = Instance(Plot)

    data_name = Enum("jn0", "jn1", "jn2")
    
    # default view for a traits class
    traits_view = View(
            Item('data_name', label="Y data"),
            Item('plot', editor=ComponentEditor(), show_label=False),
            width=800, height=600, resizable=True,
            title="Data Chooser")

    def _plot_default(self):
        x = linspace(-5, 10, 100)

        self.data = {"jn0": jn(0, x),
                     "jn1": jn(1, x),
                     "jn2": jn(2, x)}

        self.plotdata = ArrayPlotData(x = x, y = self.data["jn0"])

        plot = Plot(self.plotdata)
        plot.plot(("x", "y"), type="line", color="blue")
        return plot
    
    # by default Enum trait displayed as a drop down menu
    def _data_name_changed(self):
        self.plotdata.set_data("y", self.data[self.data_name])

if __name__ == "__main__":
    DataChooser().configure_traits()
