"""
Simple models of rainfall intensity.

App: 
- User provides duration of the storm, year and location.
- Use slider to specify 'curve number'
"""
from traits.api \
    import HasTraits, Int, Range, Array, Enum, on_trait_change
from traitsui.api import View, Item
from chaco.chaco_plot_editor import ChacoPlotItem


class Hyetograph(HasTraits):
    timeline = Array()
    intensity = Array()
    nrcs = Array()
    duration = Int(12, desc='hours')
    year= Enum(1, 2, 3, 4)
    country = Enum('Wales', 'Scotland', 'Northern Ireland', 'England')
    curve_number = Range(70, 100)
    plot_type = Enum('line', 'scatter')
    
    # multiple views can be defined, the default one used is named
    # traits_view
    v1 = View(Item('plot_type'),
              ChacoPlotItem('timeline', 'intensity',
                            type_trait='plot_type',
                            resizable=True,
                            x_label='Time (hrs)',
                            y_label='Intensity',
                            color='blue',
                            bgcolor='white',
                            border_visible=True,
                            border_width=1,
                            padding_bg_color='lightgray'),
              Item('duration'),
              Item(name='year'),
              Item(name='country'),

              # After infiltration using the nrcs curve number method.
              ChacoPlotItem('timeline', 'nrcs',
                             type_trait='plot_type',
                             resizable=True,
                             x_label='Time',
                             y_label='Intensity',
                             color='blue',
                             bgcolor='white',
                             border_visible=True,
                             border_width=1,
                             padding_bg_color='lightgray'),
              Item('curve_number'),
              resizable=True,
              width=800, height=900)

    def calculate_intensity(self):
        """Calculate hyetograph"""
        counties = {'England': 12, 'Scotland': 21, 'Wales': 13, 'Northern Ireland': 123}
        years = {
            1 : [65, 8, .806, 54, 8.3, .791, 24, 9.5, .797, 68, 7.9, .800],
            2: [80, 8.5, .763, 78, 8.7, .777, 42, 12., .795,81, 7.7, .753],
            3: [89, 8.5, .754, 90, 8.7, .774, 60, 12.,.843, 81, 7.7, .724],
            4: [96, 8., .730, 106, 8.3, .762, 65, 9.5, .825, 91, 7.9, .706]
            }
        


if __name__ == "__main__":
    graph = Hyetograph()
    graph.configure_traits()

