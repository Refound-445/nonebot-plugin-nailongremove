from .utils import PACKAGES_PATH, system_no_fail


def main():
    for p in PACKAGES_PATH.iterdir():
        system_no_fail("pdm", "publish", cwd=p)


if __name__ == "__main__":
    main()
