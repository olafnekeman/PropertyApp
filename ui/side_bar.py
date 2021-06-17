from plotly.subplots import make_subplots
import plotly.graph_objects as go
from data.interface import data, DataInterface
from support.constants import COLOR
from ui.runtime_vars import RuntimeVars


# TODO: Change go.Scatter to go.FigureWidget for speed purposes
class Subplot:
    def __init__(self, data: DataInterface, runtime_vars: RuntimeVars,
                 show_legend: bool = False):
        self.data = data
        self.vars = runtime_vars
        self._parsed = set()
        self.fig = go.FigureWidget()
        self._subplot_var = ""
        self.show_legend = show_legend

    @property
    def subplot_var(self):
        return self._subplot_var

    @subplot_var.setter
    def subplot_var(self, var: str):
        self._subplot_var = var

    def add_trace(self, county_code: str):
        """ Adds a trace to the FigureWidget based on the county code. """

        data = self.data.county_yearly(county_code=county_code,
                                  variable=self._subplot_var)
        self.fig.add_scatter(x=data['Perioden'], y=data[self._subplot_var],
                             name=county_code)

    def remove_trace(self, county_code: str):
        """ Adds a trace to the FigureWidget based on the county code. """
        idx = [i for i, v in enumerate(self.fig.data)
               if v.name == county_code][0]
        lst = list(self.fig.data)
        lst.pop(idx)
        self.fig.data = tuple(lst)

    def update_traces(self):
        """ Updates the figure based on the vars.selections. """
        present = set([i.name for i in self.fig.data])
        left_over = list(present - self.vars.selections) + list(
            self.vars.selections - present)

        for i in left_over:
            if left_over in list(present):
                self.remove_trace(county_code=i)
            else:
                self.add_trace(county_code=i)

    def plot(self):
        fig = go.Figure()
        for s in self.vars.selections:
            data = self.data.county_yearly(county_code=s,
                                           variable=self._subplot_var)
            fig.add_scatter(x=data['Perioden'],
                            y=data[self._subplot_var],
                            name=data['RegioS'].iloc[0])
        fig.update_layout(
            height=150,
            showlegend=self.show_legend,
            legend=dict(orientation='h',
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return fig


if __name__ == "__main__":
    vars = RuntimeVars()
    plot = Subplot(data=data, runtime_vars=vars)
    vars.selections.add('GM0694')
    vars.selections.add('GM1680')
    plot.subplot_var = "Bevolkingsgroei_79"
    fig = plot.plot()
    plot.update_traces()
