import os


class ExtractTarget:
    def __init__(self, _path_file_: str, target_row=()):
        self.path_file = _path_file_
        (self.path, self.file) = os.path.split(self.path_file)
        (self.filename, self.extension) = os.path.splitext(self.file)

    def open_file(self) -> tuple:
        try:
            fd = open(self.path_file, 'r', errors="ignore")
        except FileNotFoundError:
            return False, None
        return True, fd

    def get_epoch_field(self, next_epoch_row="RMC"):
        is_finish = False
        epoch_filed = []
        flag_, fd = self.open_file()
        if flag_:
            for row in fd:
                if next_epoch_row in row:
                    yield is_finish, epoch_filed
                    epoch_filed.clear()
                epoch_filed.append(row)
        is_finish = True
        return is_finish, epoch_filed


if __name__ == "__main__":
    test = ExtractTarget('/home/ucchip/th/gps_test_rec/2022/0315/5_mengxin_cold_start_sense_test.log')
    for item in test.get_epoch_field():
        print(item)

