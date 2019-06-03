"""
Example project, plotting van der waals interaction
"""
from traits.api import HasTraits, Array, Range, Float, Enum, on_trait_change, Property
from traitsui.api import View, Item
from chaco.chaco_plot_editor import ChacoPlotItem
from numpy import arange


class Data(HasTraits):
    """
    Traits class and elements required to model the equation.
    Volume and pressure hold lists for X,Y coords. attraction and
    total volume are provided by the user. Plot type will be
    shown as a drop down list.
    """
    volume = Array
    attraction = Range(low=-50.0, high=50.0, value=0.0)
    totalVolume = Range(low=0.01, high=100.0, value=0.01)
    temperature = Range(low=-50.0, high=50.0, value=50.0)
    r_constant = Float(8.314472)
    plot_type = Enum('line', 'scatter')
    
    pressure = Property(Array, depends_on=['temperature',
                                           'attraction',
                                           'totalVolume'])

    def _volume_default(self):
        return arange(0.1, 100)
    
    def _get_pressure(self):
        return ((self.r_constant*self.temperature)
                /(self.volume - self.totalVolume)
               -(self.attraction/(self.volume*self.volume)))
    
    # Main GUI window defined by View instance
    # Contains all GUI elements including the plot
    # Link gui element by using an Item instance with the same name
    traits_view = View(ChacoPlotItem("volume", "pressure",
                            type_trait="plot_type",
                            resizable=True,
                            x_label="Volume",
                            y_label="Pressure",
                            x_bounds=(-10,120),
                            x_auto=False,
                            y_bounds=(-2000,4000),
                            y_auto=False,
                            color="blue",
                            bgcolor="white",
                            border_visible=True,
                            border_width=1,
                            title='Pressure vs. Volume',
                            padding_bg_color="lightgray"),
                        Item(name='attraction'),
                        Item(name='totalVolume'),
                        Item(name='temperature'),
                        Item(name='r_constant', style='readonly'),
                        Item(name='plot_type'),
                        resizable=True,
                        buttons=["OK"],
                        title='Van der Waal Equation',
                        width=900, height=800)

    # Re-calculate when attraction, totVolume, or temperature are changed.
    @on_trait_change('attraction, totVolume, temperature')
    def calc(self):
        """ Update the data based on the numbers specified by the user. """
        self.volume = arange(.1, 100)
        self.pressure = ((self.r_constant*self.temperature)
                         /(self.volume - self.totalVolume)
                        -(self.attraction/(self.volume*self.volume)))


if __name__ == "__main__":
    viewer = Data()
    viewer.configure_traits()
