from rdroc.data_loader import DataLoader


def main():
    dl = DataLoader()
    catalogs = dl.run()
    for catalg in catalogs:
        print(catalg)


if __name__ == "__main__":
    main()
