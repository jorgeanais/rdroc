from itertools import chain

from rdroc.data_loader import DataLoader
from rdroc.plots import dash_plot
from rdroc.redcor import apply_reddening_correction


def main():
    dl = DataLoader()
    catalogs = dl.run()
    clusters = {k: v for c in catalogs for k, v in c.get_all_clusters().items()}
    apply_reddening_correction(clusters)  # Not working with Hao clusters
    app = dash_plot(clusters)
    app.run_server(debug=False)

if __name__ == "__main__":
    clusters = main()
