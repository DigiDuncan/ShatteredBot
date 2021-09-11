from os import PathLike


class FileList:
    def __init__(self, file: PathLike):
        self.file = file
        self._items: list[str] = []

        with open(file, "r+") as f:
            self._items = f.readlines()

        for item in self._items:
            item = item.strip()

        self._items = [item for item in self._items if item != ""]

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self):
        pass

    def _save(self):
        with open(self.file, "w+") as f:
            f.writelines([item + "\n" for item in self._items])

    def append(self, i: str):
        self._items.append(i.strip())
        self._save()

    def remove(self, i: str):
        self._items.remove(i.strip())
        self._save()

    def pop(self, i: int):
        self._items.pop(i)
        self._save()

    def clear(self):
        self._items.clear()
        self._save()

    def sort(self):
        self._items.sort()
        self._save()

    def __len__(self):
        return len(self._items)


class UniqueFileList(FileList):
    def append(self, i: str):
        icf = i.casefold().strip()
        for item in self._items:
            if item == icf:
                raise ValueError(f"{i} is already in this list!")
        super().append(i)

    def remove(self, i: str):
        icf = i.casefold().strip()
        for item in self._items:
            if item == icf:
                super().remove(i)
                return
        raise ValueError(f"No item {i} in list!")
