import io
import numpy as np
import PIL.Image

from chaco.api import (
    ArrayPlotData, CMapImagePlot, DataRange1D, DataRange2D, Greys,
    GridDataSource, GridMapper, ImageData, Plot, reverse, GridContainer,
    LinearMapper
)
from chaco.tools.api import PanTool, ZoomTool
from chaco.overlays.databox import DataBox
from enable.component_editor import ComponentEditor
from traits.api import Instance, HasTraits, Str
from traitsui.api import Item, ModelView, View


def calculate_intensity_histogram(pixel_data):
    hist, bin_edges = np.histogram(pixel_data.flatten())
    bin_width = np.subtract(bin_edges[1], bin_edges[0])
    return hist, bin_edges[:-1], bin_width


def plot_component(filepath):

    # load image into array
    with open(filepath, 'rb') as f:
        im = PIL.Image.open(io.BytesIO(f.read()))

    im_arr = np.array(im)
    height = len(im_arr[0])
    width = len(im_arr)

    xs = np.arange(0, width)
    ys = np.arange(0, height)

    # define mappers from data to view for chaco
    index = GridDataSource(xdata=xs, ydata=ys)
    index_mapper = GridMapper(range=DataRange2D(index))
    
    color_source = ImageData(
            data=np.flipud(im_arr),
             value_depth=1
    )
    reversed_grays = reverse(Greys)
    color_mapper = reversed_grays(DataRange1D(color_source))

    # define plot object
    image_plot = CMapImagePlot(
        index=index,
        index_mapper=index_mapper,
        value=color_source,
        value_mapper=color_mapper
    )

    # add some tools to plot
    '''image_plot.overlays.append(
        ZoomTool(
            image_plot,
            drag_button="right",
            always_on=True,
            tool_mode="box",
            border_color='blue',
            )
        )'''

    image_plot.overlays.append(
        DataBox(so),
        )

    image_plot.tools.append(
        PanTool(
            image_plot
            )
        )

    # Define intensity histogram plot
    (hist,
    bin_edges,
    bin_width) = calculate_intensity_histogram(
        im_arr.flatten()
    )
    hist_plot_data = ArrayPlotData(x=bin_edges, y=hist)

    hist_plot = Plot(hist_plot_data)
    hist_plot.plot(("x", "y"), type='bar', color='auto', bar_width=bin_width)

    hist_plot.tools.append(
        PanTool(
            hist_plot
            )
        )

    # without padding plot just doesn't seem to show up?
    hist_plot.border_width = 1
    hist_plot.padding = 0
    hist_plot.padding_top = 1

    # define container
    # shape must match number of plots
    container = GridContainer(padding=40, fill_padding=True,
                              use_backbuffer=True, shape=(1,2),
                              spacing=(20,20))

    container.add(hist_plot)
    container.add(image_plot)

    return container


class ImagePlot(HasTraits):

    # file to load
    filepath = Str()

    # define plot as a trait
    plot = Instance(GridContainer)

    traits_view = View(
        Item(
            'plot',
            editor=ComponentEditor(),
            ),
            resizable=True, title='Image:',
            width=800, height=600
        )

    def _plot_default(self):
        return plot_component(self.filepath)


if __name__ == "__main__":
    import sys

    filepath = 'lena512.bmp'
    if len(sys.argv) > 2:
        filepath = sys.argv[2]
    image = ImagePlot()

    image.filepath = filepath

    image.configure_traits()